import regex
import sys
import threading
import logging
import autobob

LOG = logging.getLogger(__name__)


class StdioService(autobob.Service):
    def __init__(self):
        self._thread = threading.Thread(name='service', target=self._loop)
        self._mention_match = regex.compile('botname')

    def _loop(self):
        room = autobob.Room('stdin',
                            'stdin fake room',
                            ['botname', 'mikn'],
                            self.send_to_room)

        def mention_parse(message):
            matches = self._mention_match.search(message)
            if matches:
                return ['botname']
            else:
                return []

        for line in sys.stdin:
            msg = autobob.Message(line,
                                  'system',
                                  reply_path=room,
                                  mention_parse=mention_parse)
            autobob.brain.messageq.put(msg)

    def run(self):
        self._thread.daemon = True
        try:
            self._thread.start()
        except KeyboardInterrupt:
            print('Exiting read loop...')

    def send_to_room(self, room, message):
        sys.stdout.write(message + '\n')
