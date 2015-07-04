import shelve
import logging

import autobot

LOG = logging.getLogger(__name__)


class ShelveStorage(autobot.Storage):
    config_defaults = {'path': './shelve'}

    def __init__(self, config):
        self.data = shelve.open(config['path'], writeback=True)
        LOG.debug('Loading file with contents: %s', dict(self.data))

    def sync(self):
        self.data.sync()

    def close(self):
        LOG.debug('Closing database...')
        self.data.close()
