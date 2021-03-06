import inspect
import logging

import autobot

LOG = logging.getLogger(__name__)


class HelpPlugin(autobot.Plugin):
    def __init__(self, factory):
        super().__init__(factory)
        self.docs = {
            'events': None,
            'plugins': {}
        }

    @autobot.subscribe_to(autobot.event.ALL_PLUGINS_LOADED)
    def _load_events(self, context, event_args):
        self.docs['events'] = autobot.event

    @autobot.subscribe_to(autobot.event.ALL_PLUGINS_LOADED)
    def _load_plugin_docs(self, context, event_args):
        self.docs['plugins'] = {}
        plugin_classes = event_args['plugins']
        LOG.debug('Loading help for classes: %s', plugin_classes.keys())

        for plugin_class in plugin_classes.values():
            docs = _PluginDoc(plugin_class)
            if docs:
                self.docs['plugins'][docs.plugin_name] = docs

    @autobot.respond_to(r'^(H|h)elp')
    def print_user_help(self, message):
        msg = 'General Information\n'
        for plugin in self.docs['plugins'].values():
            msg += '%s\n%s' % (
                    plugin.plugin_name,
                    plugin.plugin_help
                    )
            if plugin.method_help:
                msg += '\nMethods:\n'
            for m_help in plugin.method_help:
                msg += '%s\nPatterns: %s\n%s' % (
                        m_help['name'],
                        ', '.join(m_help['patterns']),
                        m_help['help']
                        )
        message.reply(msg)

    @autobot.respond_to(r'^dev(eloper)? help')
    def print_developer_help(self, message):
        message.reply(repr(self.docs))


class _PluginDoc(object):
    def __init__(self, cls):
        self.plugin_name = cls.__class__.__name__.replace('Plugin', '')
        self.plugin_help = cls.__doc__
        if self.plugin_help:
            self.plugin_help = self.plugin_help.strip()
        self.method_help = self._parse_methods(cls.__class__)

    def _parse_methods(self, cls):
        method_help = []
        for _, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # Checking for _is_decorator means only including decorated methods
            if method.__doc__ and hasattr(method, '_is_decorator'):
                LOG.debug('Found method %s with help text!', method.__name__)
                # Find all patterns that executes the method
                objs = method._callback_objects
                matchers = [m for m in objs if isinstance(m, autobot.Matcher)]
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
