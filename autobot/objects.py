import functools
import collections
import datetime
import logging
import regex
import autobot
from .helpers import DictObj

LOG = logging.getLogger(__name__)


class Message(object):
    def __init__(self, message, author, reply_path=None, mentions=[]):
        assert issubclass(type(reply_path), ChatObject)
        self._message = message
        self._author = author
        self._reply_path = reply_path
        self._mentions = mentions
        mention_name = ''

    def mentions(self, username):
        return username in self._mentions

    def mentions_self(self):
        return autobot.SELF_MENTION in self._mentions

    def direct_message(self):
        return issubclass(type(self._reply_path), User)

    def reply(self, message, *args):
        LOG.debug('Sending message %s to appropriate places...', message)
        if self._reply_path and hasattr(self._reply_path, 'say'):
            self._reply_path.say(message, *args)
        else:
            NotImplementedError('This message does not provide a reply path')

    def process(self, processor):
        if callable(processor):
            self._message = processor(self._message)

    def __str__(self):
        return self._message

    @property
    def author(self):
        return self._author


class ChatObject(object):
    def __init__(self, name, reply_handler):
        self.name = name
        self._internal = DictObj()
        self._reply_handler = reply_handler

    def say(self, message, *args):
        if not self._reply_handler:
            raise NotImplementedError()
        self._reply_handler(self, message, *args)


class Room(ChatObject):
    def __init__(self, name, topic=None, roster=None, reply_handler=None):
        super().__init__(name, reply_handler)
        self.roster = roster
        self.topic = topic

    def __str__(self):
        return self.name

    def join(self):
        pass

    def leave(self):
        pass


class User(ChatObject):
    def __init__(self, name, real_name=None, reply_handler=None):
        super().__init__(name, reply_handler)
        self.real_name = real_name

    def __str__(self):
        return self.name


class MetaPlugin(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        for method in namespace.values():
            if hasattr(method, '_is_decorator'):
                setattr(method, '_class_name', name)
        return type.__new__(cls, name, bases, namespace, **kwargs)


class Plugin(metaclass=MetaPlugin):
    def __init__(self, factory):
        self._factory = factory
        self._storage = None

    @property
    def default_room(self):
        return self._factory.get_service().default_room

    @property
    def service(self):
        return self._factory.get_service()

    @property
    def storage(self):
        if not self._storage:
            storage = self._factory.get_storage()
            # Let's namespace the plugin's storage
            name = type(self).__name__
            if name not in storage:
                storage[name] = {}
            self._storage = storage[name]

        return self._storage


class Storage(collections.UserDict):
    def sync(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()


class Service(object):
    config_defaults = {'mention_name': 'autobot'}

    def __init__(self, config=None):
        self._config = config
        self._default_room = None
        self._author = None

    def start(self):
        if 'rooms' not in self._config:
            raise Exception('No rooms to join defined!')
        self.run()
        # This is done down here to make sure we don't overwrite mention_name
        # when we have multiple service modules on the path
        autobot.substitutions.add('mention_name', self.mention_name)
        autobot.event.trigger(autobot.event.SERVICE_STARTED, self)

    def run(self):
        raise NotImplementedError()

    def shutdown(self):
        raise NotImplementedError()

    def join_room(self, room):
        raise NotImplementedError()

    def get_room(self, name):
        raise NotImplementedError()

    def send_message(self, message):
        raise NotImplementedError()

    @property
    def default_room(self):
        if not self._default_room:
            room_name = None
            if 'default_room' in self._config:
                room_name = self._config['default_room']
            else:
                room_name = self._config['rooms'][0]
            self._default_room = self.get_room(room_name)
        return self._default_room

    @property
    def mention_name(self):
        if 'mention_name' in self._config:
            return self._config['mention_name']
        else:
            return None

    @property
    def author(self):
        if not self._author:
            self._author = User(self.mention_name)
        return self._author


@functools.total_ordering
class Callback(object):
    def __init__(self, func, priority=100):
        self._callback = None
        self._func = func
        self.priority = priority
        if hasattr(func, '_priority'):
            self.priority = func._priority
        self.lock = ''

    @property
    def __name__(self):
        return self._func.__name__

    def get_callback(self, factory):
        if not self._callback:
            self._callback = factory.get_callback(self._func)
        return self._callback

    def _is_comparable(self, other, attr):
        if not hasattr(other, attr):
            raise NotImplemented('Cannot compare %s and %s',
                                 type(self), type(other))

    def __eq__(self, other):
        self._is_comparable(other, '__name__')
        return len(self.__name__) == len(other.__name__)

    def __lt__(self, other):
        self._is_comparable(other, '__name__')
        return len(self.__name__) > len(other.__name__)

    def __str__(self):
        return self.__name__


class Matcher(Callback):
    '''
    Matchers are sorted on pattern length, assuming that a longer pattern is
    more specific, thus resulting in that when there's two matchers with the
    same priority value, the one with the longer pattern gets picked from the
    queue.
    '''
    def __init__(self, func, pattern, priority=50, condition=lambda x: True,
                 preprocessor=None):
        super().__init__(func, priority)
        self.pattern = pattern
        self.condition = condition
        self.preprocessor = preprocessor
        self.regex = None

    def compile(self, **format_args):
        self.regex = regex.compile(self.pattern.format(**format_args))

    def __eq__(self, other):
        self._is_comparable(other, 'pattern')
        return len(self.pattern) == len(other.pattern)

    def __lt__(self, other):
        self._is_comparable(other, 'pattern')
        return len(self.pattern) > len(other.pattern)

    def __str__(self):
        return self.pattern


class ScheduledCallback(Callback):
    def __init__(self, func, cron):
        self._cron = cron
        self.get_next()
        super().__init__(func, self.timestamp)

    def get_next(self):
        self.timestamp = self._cron.get_next(datetime.datetime).timestamp()
        return self.timestamp

    def __eq__(self, other):
        self._is_comparable(other, 'timestamp')
        return self.timestamp == other.timestamp

    def __lt__(self, other):
        self._is_comparable(other, 'timestamp')
        return self.timestamp < other.timestamp

    def __str__(self):
        return '{}: {}'.format(self.__name__, ' '.join(self._cron.exprs))
