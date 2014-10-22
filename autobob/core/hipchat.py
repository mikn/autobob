from .xmpp import XMPPService
import regex
# import hypchat


class HipChatService(XMPPService):
    def __init__(self, config=None):
        self.mention_regexp = regex.compile('@\w+')
        self._config = config

    def send(self, message):
        pass
