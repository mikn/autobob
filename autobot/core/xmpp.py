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

        super().__init__(self, jid, password)

        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # Ping
        self.register_plugin('xep_0203')  # Delayed messages
        self.register_plugin('xep_0045')  # MUC
        self.register_plugin('xep_0004')  # MUC compatibility (join room)
        self.register_plugin('xep_0249')  # MUC invites

        self.add_event_handler('message', self.message_received)
        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler("disconnected", self.disconnected)
        # presence related handlers
        self.add_event_handler("got_online", self.user_online)
        self.add_event_handler("got_offline", self.user_offline)
        self.add_event_handler("changed_status", self.user_changed_status)
        # MUC subject events
        self.add_event_handler("groupchat_subject", self.chat_topic)
