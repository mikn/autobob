import logging
from .helpers import DictObj

LOG = logging.getLogger(__name__)


class Events(DictObj):
    PLUGIN_LOADED = 'PLUGIN_LOADED'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handlers = {}

    def add(self, event_name):
        if event_name in self.__dict__:
            raise ValueError('%s already exists as an event', event_name)
        event_name = event_name.upper()
        setattr(self, event_name, event_name)

    def trigger(self, event, *args):
        if event not in self._handlers:
            LOG.debug('No handlers registered for event %s', event)
        return
        for handler in self._handlers[event]:
            handler(*args)

    def register(self, event, handler):
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def deregister(self, event, handler):
        if event not in self._handlers or handler not in self._handlers[event]:
            return
        del(self._handlers[event][self._handlers[event].index(handler)])


event = Events()
