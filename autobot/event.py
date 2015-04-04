import logging

import autobot
from .helpers import DictObj

LOG = logging.getLogger(__name__)


class Events(DictObj):
    PLUGIN_LOADED = 'PLUGIN_LOADED'
    ALL_PLUGINS_LOADED = 'ALL_PLUGINS_LOADED'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handlers = {}
        self._factory = None
        self.register(self.ALL_PLUGINS_LOADED, self._get_factory)

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
            LOG.debug('Triggering handler %s for event %s!',
                      handler.__name__, event)
            if isinstance(handler, autobot.Callback):
                if not self._factory:
                    LOG.warning('Tried registering plugin-based handler on '
                                'event: %s before factory was available... '
                                'skipping', event)
                    continue
                handler.get_callback(self._factory)(*args)
            else:
                handler(*args)

    def register(self, event, handler):
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def deregister(self, event, handler):
        if event not in self._handlers or handler not in self._handlers[event]:
            return
        del(self._handlers[event][self._handlers[event].index(handler)])

    def _get_factory(self, event_args):
        if not self._factory:
            self._factory = event_args['factory']
        else:
            LOG.info('We already had a factory when trying to add a new one...')


event = Events()
