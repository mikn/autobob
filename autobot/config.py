import os.path
import autobot

defaults = {
    'scheduler_resolution': 0.5,
    'storage_plugin': 'shelve',
    'service_plugin': 'stdio',
    'core_path': os.path.join(autobot.__path__.pop(), 'core'),
    'plugin_path': os.path.join(os.path.curdir, 'plugins'),
}
