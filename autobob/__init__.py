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


class Message(object):
    def __init__(self, message, author, reply_path=None):
        assert issubclass(type(reply_path), ChatObject)
        self._message = message
        self._author = author
        self._reply_path = reply_path
        # TODO: Parse for mentions through Service
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


class Plugin(object):
    def __init__(self, factory):
        self._factory = factory

    @property
    def service(self):
        return self._factory.get_service()

    @property
    def storage(self):
        return self._factory.get_storage()


# TODO: Provide a dict interface
class Storage(object):
    pass


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


class Matcher(object):
    def __init__(self, func, pattern, prio=50, condition=lambda x: True):
        self._callback = None
        self._func = func
        self.pattern = regex.compile(pattern)
        self.prio = prio
        self.condition = condition
        # TODO: Share lock for all methods on same object
        self.lock = ''

    def get_callback(self, factory):
        if not self._callback:
            self._callback = factory.get_callback(self._func)
        return self._callback
