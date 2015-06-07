import inspect
import logging

import autobot

LOG = logging.getLogger(__name__)


class HelpPlugin(autobot.Plugin):
    def __init__(self, factory):
        super().__init__(factory)
        self.docs = {}

    @autobot.subscribe_to(autobot.event.ALL_PLUGINS_LOADED)
    def _load_handler(self, event_args):
        plugin_classes = event_args['plugins']
        LOG.debug('Loading help for classes: %s', plugin_classes.keys())

        for plugin_class in plugin_classes.values():
            docs = _PluginDoc(plugin_class)
            if docs:
                self.docs[docs.plugin_name] = docs

    @autobot.respond_to(r'^{mention_name}\s+(H|h)elp')
    def print_user_help(self, message):
        message.reply(repr(self.docs))

    @autobot.respond_to(r'^{mention_name}\s+dev(eloper)? help')
    def print_developer_help(self, message):
        message.reply(repr(self.docs))


class _PluginDoc(object):
    def __init__(self, cls):
        self.plugin_name = cls.__class__.__name__.replace('Plugin', '')
        self.plugin_help = cls.__doc__
        self.method_help = self._parse_methods(cls.__class__)

    def _parse_methods(self, cls):
        method_help = []
        for _, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # Checking for _is_decorator means only including decorated methods
            if method.__doc__ and hasattr(method, '_is_decorator'):
                LOG.debug('Found method %s with help text!', method.__name__)
                # Find all patterns that executes the method
                matchers = autobot.brain.matchers
                patterns = [m.pattern for m in matchers if method == m._func]
                method_help.append({
                    'name': method.__name__,
                    'patterns': patterns,
                    'help': method.__doc__.strip()})

        return method_help

    def __repr__(self):
        repr_dict = {
            'plugin_name': self.plugin_name,
            'plugin_help': self.plugin_help,
            'method_help': self.method_help
        }
        return repr(repr_dict)

    def __bool__(self):
        return bool(self.method_help or self.plugin_help)
