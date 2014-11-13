import autobot
import sleekxmpp


class XMPPService(autobot.Service):
    pass


class _XMPPClient(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        super(_XMPPClient).__init__(self, jid, password)

        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('message', self.message_received)
