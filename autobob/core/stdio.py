import sys
import threading
import logging
import autobob

LOG = logging.getLogger(__name__)


class StdioService(autobob.Service):
    def __init__(self):
        self._thread = threading.Thread(name='service', target=self._loop)

    def _loop(self):
        for line in sys.stdin:
            msg = autobob.robot.Message(line, 'system', self)
            autobob.brain.messageq.put(msg)

    def run(self):
        LOG.debug('Booting service thread...')
        self._thread.daemon = True
        self._thread.start()

    def send_message(self, message):
        sys.stdout.write(message)
