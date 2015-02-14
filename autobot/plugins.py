import inspect
import pkgutil
import logging
import sys

import autobot
from . import helpers

LOG = logging.getLogger(__name__)


class Factory(object):
    def __init__(self, config):
        self._config = config
        self._defaults = {}
        self._plugins = {}
        path = config['core_path']
        self._load_plugins(path)

    def _load_plugins(self, path):
        plugin_path = helpers.abs_path(path)
        LOG.debug('Looking for plugins at {}'.format(plugin_path))
        late_plugins = []

        for finder, name, ispkg in pkgutil.walk_packages(path=[plugin_path]):
            if ispkg:
                continue

            # TODO: Make sure the plugins are loaded in the correct namespace
            full_name = 'autobot.core.{}'.format(name)
            LOG.debug('Found plugin: {}'.format(name))

            if full_name not in sys.modules:
                LOG.debug('Importing plugin: {}'.format(name))
                module = finder.find_module(full_name).load_module(full_name)
                classes = inspect.getmembers(module, inspect.isclass)
                for name, cls in classes:
                    plugin_config = self._get_plugin_config(cls, name)
                    try:
                        if issubclass(cls, autobot.Plugin):
                            late_plugins.append((name, cls))
                        elif plugin_config:
                            self._plugins[name] = cls(plugin_config)
                        else:
                            self._plugins[name] = cls()
                    except Exception as e:
                        LOG.error('Could not load plugin %s... skipping', name)
                        LOG.debug('Error received was %s.', e)
                        LOG.debug('Started with conf: %s', plugin_config)
                        LOG.debug('Default dict contains: %s', self._defaults)

        for name, plugin in late_plugins:
            try:
                self._plugins[name] = plugin(self)
            except Exception as e:
                LOG.error('Could not load plugin %s... skipping', name)
                LOG.debug('Error received was %s.', e)
                LOG.debug('Config dict contains: %s', self._config)

    def _get_plugin_config(self, cls: autobot.Plugin, name: str) -> dict:
        config = {}

        for base in cls.__bases__:
            if hasattr(base, 'config_defaults'):
                config.update(base.config_defaults)
                self._defaults[base.__name__] = base.config_defaults

            if base.__name__ in self._config:
                config.update(self._config[base.__name__])

        if hasattr(cls, 'config_defaults'):
            config.update(cls.config_defaults)
            self._defaults[cls.__name__] = cls.config_defaults

        if name in self._config:
            config.update(self._config[name])

        return config

    def get(self, plugin):
        if plugin in self._plugins:
            return self._plugins[plugin]
        raise ImportError('Module {} does not exist amongst '
                          '{}'.format(plugin, self._plugins.keys()))
        pass

    def get_callback(self, func):
        if not hasattr(func, '_class_name'):
            LOG.warning('Something went terribly wrong here!')
            raise ImportError()
        obj = self.get(func._class_name)
        return getattr(obj, func.__name__)

    def get_service(self):
        return self.get(self._config['service_plugin'])

    def get_storage(self):
        storage = self.get(self._config['storage_plugin'])
        if '_internal' not in storage:
            storage['_internal'] = {}
        return storage

    def get_config(self):
        return self._config
