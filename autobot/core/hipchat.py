import autobot
from .xmpp import XMPPService
import regex
# import hypchat


class HipChatService(XMPPService):
    def __init__(self, config=None):
        super().__init__(config)
        self.mention_regexp = regex.compile('@\w+')

    def _mention_parse(self, message):
        mentions = []
        mention_name = self._config['mention_name']
        if mention_name in message:
            mentions.append(autobot.SELF_MENTION)

        return mention_name, mentions

    def get_room(self, room_name):
        pass
