import sys
import threading
import logging
import autobob

LOG = logging.getLogger(__name__)


class StdioService(autobob.Service):
    def __init__(self):
        self._thread = threading.Thread(name='service', target=self._loop)

    def _loop(self):
        room = autobob.Room('stdin',
                                  'stdin fake room',
                                  ['botname', 'mikn'],
                                  self.send_to_room)
        for line in sys.stdin:
            msg = autobob.Message(line, 'system', room)
            autobob.brain.messageq.put(msg)

    def run(self):
        self._thread.daemon = True
        self._thread.start()

    def send_to_room(self, room, message):
        sys.stdout.write(message + '\n')
