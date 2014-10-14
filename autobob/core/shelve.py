import autobob
import shelve


class ShelveStorage(autobob.Storage):
    def __init__(self, config):
        self._file = shelve.open(config['path'])
