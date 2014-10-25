import sys
import threading
import logging
import autobob

LOG = logging.getLogger(__name__)


class StdioService(autobob.Service):
    def __init__(self, config):
        super().__init__(config)
        self._thread = threading.Thread(name='service', target=self._loop)
        self._config = config
        self._rooms = {}
        self._init_rooms()

    def _init_rooms(self):
        roster = [self._config['mention_name'], 'input']
        room = autobob.Room('stdin',
                            topic='stdin fake room',
                            roster=roster,
                            reply_path=self.send_to_room)
        self._rooms[room.name] = room

    def _loop(self):
        room = self.default_room

        def mention_parse(message):
            matches = [u for u in room.roster if u in message]
            mention_name = self._config['mention_name']
            if mention_name in matches:
                self_index = matches.index(mention_name)
                matches[self_index] = autobob.SELF_MENTION

            return matches

        for line in sys.stdin:
            msg = autobob.Message(line,
                                  'system',
                                  reply_path=room,
                                  mention_parse=mention_parse)
            autobob.brain.messageq.put(msg)

    def run(self):
        super().run()
        self._thread.daemon = True
        try:
            self._thread.start()
        except KeyboardInterrupt:
            print('Exiting read loop...')

    def send_to_room(self, room, message):
        sys.stdout.write(message + '\n')

    def get_room(self, room):
        return self._rooms[room]
