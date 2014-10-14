import os.path
import autobob

defaults = {
    'storage_plugin': 'ShelveStorage',
    'service_plugin': 'StdioService',
    'core_path': os.path.join(autobob.__path__.pop(), 'core'),
    'ShelveStorage': {
        'path': './shelve'
    }
}
