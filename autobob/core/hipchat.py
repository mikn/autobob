from .xmpp import XMPPService
import regex
# import hypchat


class HipChatService(XMPPService):
    def __init__(self):
        self.mention_regexp = regex.compile('@\w+')

    def send(self, message):
        pass
