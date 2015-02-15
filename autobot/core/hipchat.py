from .xmpp import XMPPService
import regex
# import hypchat


class HipChatService(XMPPService):
    def __init__(self, config=None):
        super().__init__(config)
        self.mention_regexp = regex.compile('@\w+')

    def send(self, message):
        pass
