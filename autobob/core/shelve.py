import shelve
import logging

import autobob

LOG = logging.getLogger(__name__)


class ShelveStorage(autobob.Storage):
    def __init__(self, config):
        self.data = shelve.open(config['path'], writeback=True)
        LOG.debug('Loading file with contents: {}'.format(dict(self.data)))

    def sync(self):
        self.data.sync()

    def close(self):
        LOG.debug('Closing database...')
        self.data.close()
