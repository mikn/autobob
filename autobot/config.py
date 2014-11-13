import os.path
import autobot

defaults = {
    'scheduler_resolution': 0.5,
    'storage_plugin': 'ShelveStorage',
    'service_plugin': 'StdioService',
    'core_path': os.path.join(autobot.__path__.pop(), 'core'),
    'ShelveStorage': {
        'path': './shelve'
    },
    'Service': {
        'mention_name': 'bob',
    },
    'StdioService': {
        'rooms': ['stdin'],
    },
}
