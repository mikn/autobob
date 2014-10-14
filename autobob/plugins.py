import os.path
import inspect
import pkgutil
import logging
import sys

import autobob
import autobob.core
import autobob.helpers

LOG = logging.getLogger(__name__)


class Factory(object):
    def __init__(self):
        self._plugins = {}
        # Terribly hard coded
        path = os.path.join(autobob.__path__.pop(), 'core')
        self._plugins.update(self._load_plugins(path))

    def _load_plugins(self, path):
        plugin_path = autobob.helpers.abs_path(path)
        LOG.debug('Looking for plugins at {}'.format(plugin_path))
        plugins = {}

        for finder, name, ispkg in pkgutil.walk_packages(path=[plugin_path]):
            if ispkg:
                continue
            full_name = 'autobob.core.{}'.format(name)
            LOG.debug('Found plugin: {}'.format(name))
            if full_name not in sys.modules:
                LOG.debug('Importing plugin: {}'.format(name))
                module = finder.find_module(full_name
                                            ).load_module(full_name)
                classes = inspect.getmembers(module, inspect.isclass)
                LOG.debug('Found classes: {}'.format(classes))
                for name, cls in classes:
                    if issubclass(cls, autobob.Plugin):
                        plugins[name] = cls(self)
                    else:
                        plugins[name] = cls()
        return plugins

    def get(self, plugin):
        if plugin in self._plugins:
            return self._plugins[plugin]
        raise ImportError('Module does not exist!')
        pass

    def get_callback(self, func):
        if not hasattr(func, 'class_name'):
            log.warning('Sadly, due to the nature of how methods are wrapped '
                        'in python we must do some sorcery with a class '
                        'decorator as well. You must in other words decorate '
                        'your plugin class with @autobob.plugin for it '
                        'to be compatible.')
            raise ImportError()
        obj = self.get(func.class_name)
        return getattr(obj, func.__name__)

    def get_service(self):
        return self.get('StdioService')

    def get_storage(self):
        return self.get('ShelveStorage')
