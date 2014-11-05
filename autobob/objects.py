import functools
import collections
import datetime
import logging
import regex
import autobob

LOG = logging.getLogger(__name__)


class Message(object):
    def __init__(self, message, author, reply_path=None, mention_parse=None):
        assert issubclass(type(reply_path), ChatObject)
        self._message = message
        self._author = author
        self._reply_path = reply_path
        if not mention_parse:
            self._mentions = []
        else:
            self._mentions = mention_parse(self._message)

    def mentions(self, username):
        return username in self._mentions

    def mentions_self(self):
        return autobob.SELF_MENTION in self._mentions

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
    def __init__(self, name, topic=None, roster=None, reply_path=None):
        self.name = name
        self.roster = roster
        self.topic = topic
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
    def default_room(self):
        return self._factory.get_service().default_room

    @property
    def service(self):
        return self._factory.get_service()


class Storage(collections.UserDict):
    def sync(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()


class Service(object):
    def __init__(self, config=None):
        self._config = config
        self._default_room = None

    def run(self):
        if 'rooms' not in self._config:
            raise Exception('No rooms to join defined!')

    def join_room(self, room):
        raise NotImplementedError()

    def get_room(self, name):
        raise NotImplementedError()

    def send_message(self, message):
        raise NotImplementedError()

    @property
    def default_room(self):
        if not self._default_room:
            room_name = self._config['rooms'][0]
            if 'default_room' in self._config:
                room_name = self._config['default_room']
            self._default_room = self.get_room(room_name)
        return self._default_room

    @property
    def mention_name(self):
        if 'mention_name' in self._config:
            return self._config['mention_name']
        else:
            return None


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
        self.pattern = pattern
        self.condition = condition
        self.regex = None

    def compile(self, **format_args):
        self.regex = regex.compile(self.pattern.format(**format_args))


@functools.total_ordering
class ScheduledCallback(Callback):
    def __init__(self, func, cron):
        self._cron = cron
        self.get_next()
        super().__init__(func, self.timestamp)

    def get_next(self):
        self.timestamp = self._cron.get_next(datetime.datetime).timestamp()
        return self.timestamp

    def _is_comparable(self, other):
        return hasattr(other, 'timestamp')

    def __eq__(self, other):
        if not self._is_comparable(other):
            return NotImplemented
        return self.timestamp == other.timestamp

    def __lt__(self, other):
        if not self._is_comparable(other):
            return NotImplemented
        return self.timestamp < other.timestamp
