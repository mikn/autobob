import os.path


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
    def __get__(self, key):
        return self[key]

    def __set__(self, key, value):
        self[key] = value
