import os.path
import inspect

def abs_path(dir):
    if not dir:
        return None
    if dir.startswith('~'):
        dir = os.path.expanduser(dir)
    if not os.path.isabs(dir):
        dir = os.path.abspath(dir)
    dir = os.path.normpath(dir)
    return os.path.realpath(dir)


class DictObj(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in dir(self):
            value = getattr(self, name)
            if not name.startswith('_') and not inspect.isroutine(value):
                self[name] = value

    def __get__(self, key):
        return self[key]

    def __set__(self, key, value):
        self[key] = value

    def _find_key(self, value):
        for key, val in self.items():
            if value == val:
                return key
        return None
