import inspect
import pkgutil
import logging
import sys
import os
import traceback

import autobot
from . import helpers

LOG = logging.getLogger(__name__)


class Factory(object):
    def __init__(self, config):
        self._config = config
        self._defaults = {}
        self._plugins = {}
        path = config['core_path']
        self._load_plugins(path, 'core')
        if os.path.exists(config['plugin_path']):
            self._load_plugins(config['plugin_path'])

    def _load_plugins(self, path, namespace='plugins'):
        plugin_path = helpers.abs_path(path)
        LOG.debug('Looking for plugins at {}'.format(plugin_path))
        late_plugins = []

        for finder, name, ispkg in pkgutil.walk_packages(path=[plugin_path]):
            if ispkg:
                continue

            full_name = 'autobot.{}.{}'.format(namespace, name)
            LOG.debug('Found plugin: {}'.format(name))

            if full_name not in sys.modules:
                LOG.debug('Importing plugin: {}'.format(name))
                module = finder.find_module(full_name).load_module(full_name)
                classes = inspect.getmembers(module, inspect.isclass)
                for name, cls in classes:
                    name = name.lower()
                    plugin_config = self._get_plugin_config(cls)
                    try:
                        if issubclass(cls, autobot.Plugin):
                            late_plugins.append((name, cls))
                        elif plugin_config:
                            self._plugins[name] = cls(plugin_config)
                        else:
                            self._plugins[name] = cls()
                    except Exception as e:
                        LOG.warn('Could not load plugin %s' % name)
                        LOG.debug('Error received was %s.', e)
                        LOG.debug(traceback.format_exc())
                        LOG.debug('Started with conf: %s', plugin_config)
                        LOG.debug('Default dict contains: %s', self._defaults)

        for name, plugin in late_plugins:
            try:
                self._plugins[name] = plugin(self)
            except Exception as e:
                LOG.error('Could not load plugin %s... skipping', name)
                LOG.debug('Error received was %s.', e)
                LOG.debug('Config dict contains: %s', self._config)

    def _get_plugin_config(self, cls, defaults=True, config=True):
        config = {}

        for base in cls.__bases__:
            config.update(self._get_plugin_config(base, config=False))

        if hasattr(cls, 'config_defaults') and defaults:
            config.update(cls.config_defaults)
            self._defaults[cls.__name__] = cls.config_defaults

        for base in cls.__bases__:
            config.update(self._get_plugin_config(base, defaults=False))

        if cls.__name__ in self._config and config:
            config.update(self._config[cls.__name__])

        return config

    def get(self, plugin):
        plugin = plugin.lower()
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
        plugin_name = self._config['service_plugin'] + 'service'
        return self.get(plugin_name)

    def get_storage(self):
        plugin_name = self._config['storage_plugin'] + 'storage'
        storage = self.get(plugin_name)
        if '_internal' not in storage:
            storage['_internal'] = {}
        return storage

    def get_config(self):
        return self._config
