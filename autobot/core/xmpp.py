import autobot
import sleekxmpp
import logging


LOG = logging.getLogger(__name__)


class XMPPService(autobot.Service):
    config_defaults = {
        'server': None,
        'username': None,
        'password': None,
    }

    def __init__(self, config):
        super().__init__(config)
        jid = '{}@{}'.format(self._config['username'], self._config['server'])
        LOG.debug('starting client with jid: {}'.format(jid))
        self._client = _XMPPClient(str(jid), self._config['password'])


class _XMPPClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        self.connected = False

        super().__init__(jid, password)

        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # Ping
        self.register_plugin('xep_0203')  # Delayed messages
        self.register_plugin('xep_0045')  # MUC
        self.register_plugin('xep_0004')  # MUC compatibility (join room)
        self.register_plugin('xep_0249')  # MUC invites

        self.add_event_handler('message', self._message_received)
        self.add_event_handler('session_start', self._session_start)
        self.add_event_handler("disconnected", self._disconnected)
        # presence related handlers
        self.add_event_handler("got_online", self._user_online)
        self.add_event_handler("got_offline", self._user_offline)
        self.add_event_handler("changed_status", self._user_changed_status)
        # MUC subject events
        self.add_event_handler("groupchat_subject", self._chat_topic)

    def _message_received(self, *args):
        pass

    def _session_start(self, *args):
        pass

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
