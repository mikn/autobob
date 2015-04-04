import inspect
import logging

import autobot
from autobot import event

LOG = logging.getLogger(__name__)


class HelpPlugin(autobot.Plugin):
    def __init__(self, factory):
        super().__init__(factory)
        event.register(event.ALL_PLUGINS_LOADED, self._load_handler)
        self.docs = {}

    def _load_handler(self, plugin_classes):
        LOG.debug('Loading help for classes: %s', plugin_classes.keys())
        for plugin_class in plugin_classes.values():
            docs = _PluginDoc(plugin_class)
            if docs:
                self.docs[docs.plugin_name] = docs

    @autobot.respond_to('^({mention_name})\s+(H|h)elp')
    def help_someone(self, message):
        message.reply(repr(self.docs))


class _PluginDoc(object):
    def __init__(self, cls):
        self.plugin_name = cls.__class__.__name__.replace('Plugin', '')
        self.plugin_help = cls.__doc__
        self._method_help = []
        self._parse_methods(cls.__class__)

    def _parse_methods(self, cls):
        # TODO: Parse all patterns that match too...
        for method in inspect.getmembers(cls, predicate=inspect.ismethod):
            if method.__doc__ and hasattr(method, '_attach_class'):
                self._method_help.append(method.__doc__)

    def __repr__(self):
        repr_dict = {
            'plugin_name': self.plugin_name,
            'plugin_help': self.plugin_help,
            'method_help': self._method_help
        }
        return repr(repr_dict)

    def __bool__(self):
        return bool(self._method_help or self.plugin_help)
