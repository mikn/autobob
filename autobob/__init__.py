import collections
import sys
import logging
import regex

LOG = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
LOG.addHandler(handler)
error_handler = logging.StreamHandler(sys.stderr)
error_handler.setFormatter(logging.Formatter(format))
error_handler.setLevel(logging.ERROR)
LOG.addHandler(error_handler)

from .decorators import *

## CONSTANTS
PRIORITY_ALWAYS = -1


class Message(object):
    def __init__(self, message, author, reply_path=None):
        assert issubclass(type(reply_path), ChatObject)
        self._message = message
        self._author = author
        self._reply_path = reply_path
        self._mentions = ['botname']

    def mentions(self, username):
        return username in self._mentions

    def mentions_self(self):
        return 'botname' in self._mentions

    def reply(self, message):
        LOG.debug('Sending message {} to appropriate places..'.format(message))
        self._reply_path.say(message)

    def __str__(self):
        return self._message

    @property
    def author(self):
        return self._author


class ChatObject(object):
    def say(self, message):
        raise NotImplementedError()


class Room(ChatObject):
    def __init__(self, name, topic, roster, reply_path):
        self._roster = roster
        self._topic = topic
        self._reply_path = reply_path

    def say(self, message):
        self._reply_path(self, message)


class User(ChatObject):
    pass


class MetaPlugin(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        for method in namespace.values():
            if hasattr(method, '_attach_class'):
                setattr(method, '_class_name', name)
        return type.__new__(cls, name, bases, namespace, **kwargs)


class Plugin(metaclass=MetaPlugin):
    def __init__(self, factory):
        self._factory = factory
        # Let's namespace the plugin's storage
        storage = factory.get_storage()
        name = type(self).__name__
        if name not in storage:
            storage[name] = {}
        self.storage = storage[name]

    @property
    def service(self):
        return self._factory.get_service()


class Storage(collections.UserDict):
    def sync(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()


class Service(object):
    def __init__(self):
        pass

    def run(self):
        raise NotImplementedError()

    def join_room(self, room):
        raise NotImplementedError()

    def get_room(self, name):
        raise NotImplementedError()

    def send_message(self, message):
        raise NotImplementedError()


class Callback(object):
    def __init__(self, func, priority=100):
        self._callback = None
        self._func = func
        self.priority = priority
        if hasattr(func, '_priority'):
            self.priority = func._priority
        self.lock = ''

    def get_callback(self, factory):
        if not self._callback:
            self._callback = factory.get_callback(self._func)
        return self._callback

class Matcher(Callback):
    def __init__(self, func, pattern, priority=50, condition=lambda x: True):
        super().__init__(func, priority)
        self.pattern = regex.compile(pattern)
        self.condition = condition
