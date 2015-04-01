import autobot
import sleekxmpp
import logging


LOG = logging.getLogger(__name__)


class XMPPService(autobot.Service):
    config_defaults = {
        'server': None,
        'username': None,
        'password': None,
        'real_name': None,
    }

    def __init__(self, config):
        super().__init__(config)
        self.jid = '{}@{}/bot'.format(
            self._config['username'],
            self._config['server'])
        LOG.debug('Initialising client with jid: {}'.format(self.jid))
        self._client = _XMPPClient(self.jid, self._config['password'], self)
        self.real_name = self._config['real_name']
        self.rooms = []

    def start(self):
        LOG.debug('Starting client with jid: {}'.format(self.jid))
        self._client.connect()
        self._client.process()

    def shutdown(self):
        LOG.debug('Disconnecting from xmpp...')
        self._client.disconnect()

    def _send_to_room(self, room, message):
        self._client.send_message(
            mto=room._internal.name,
            mbody=message,
            mtype='groupchat')

    def _send_to_user(self, user, message):
        self._client.send_message(
            mto=user._internal.name,
            mbody=message,
            mtype='message')

    def get_room(self, room_name):
        # TODO: Decide what name of room we should use as input here
        # TODO: validate room existence here
        room_obj = autobot.Room(room_name, reply_handler=self.send_to_room)
        for u in self._client._room_plugin.rooms[room_name].values():
            user = autobot.User(u.name, u.real_name)
            room_obj.roster.append(user)

        room_obj._internal.name = room_name
        return room_obj

    def _mention_parse(self, message):
        mentions = []
        if self._config['mention_name'] in message:
            mentions.append(autobot.SELF_MENTION)

        return mentions

    def _message_received(self, xmpp_message):
        LOG.debug('Message received from %s.', xmpp_message['from'].full)
        if not xmpp_message['from'].resource == self.real_name:
            # TODO: Get User object and its parameters from server
            msg = autobot.Message(xmpp_message['body'],
                                  xmpp_message['from'],
                                  reply_path=self.default_room,
                                  mention_parse=self._mention_parse)
            autobot.brain.messageq.put(msg)

    def _session_start(self, *args):
        self._client.send_presence()
        self._client.get_roster()
        self._client.join_room(self.default_room)

    def _disconnected(self, *args):
        pass

    def _user_online(self, *args):
        pass

    def _user_offline(self, *args):
        pass

    def _user_changed_status(self, *args):
        pass

    def _chat_topic(self, *args):
        pass


class _XMPPClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, handlers):
        self.connected = False
        self._service = handlers

        super().__init__(jid, password)

        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # Ping
        self.register_plugin('xep_0203')  # Delayed messages
        self.register_plugin('xep_0045')  # MUC
        self.register_plugin('xep_0004')  # MUC compatibility (join room)
        self.register_plugin('xep_0249')  # MUC invites
        self._room_plugin = self.plugin['xep_0045']

        self.whitespace_keepalive = True
        self.whitespace_keepalive_interval = 60

        self.add_event_handler('message', handlers._message_received)
        self.add_event_handler('session_start', handlers._session_start)
        self.add_event_handler("disconnected", handlers._disconnected)
        # presence related handlers
        self.add_event_handler("got_online", handlers._user_online)
        self.add_event_handler("got_offline", handlers._user_offline)
        self.add_event_handler("changed_status", handlers._user_changed_status)
        # MUC subject events
        self.add_event_handler("groupchat_subject", handlers._chat_topic)

    def join_room(self, room):
        LOG.debug('Joining room %s...', room)
        self._room_plugin.joinMUC(room, self._service.real_name, wait=True)
