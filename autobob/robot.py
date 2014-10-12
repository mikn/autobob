import regex
import logging
LOG = logging.getLogger(__name__)


class Message(object):
    def __init__(self, message, author, reply_path=None):
        self._message = message
        self._author = author
        self._reply_path = reply_path
        # TODO: Parse for mentions through Service
        self._mentions = ['botname']

    def mentions(self, username):
        return username in self._mentions

    def reply(self, message):
        LOG.debug('Sending message {} to appropriate places..'.format(message))
        pass

    def __str__(self):
        return self._message


class Room(object):
    def __init__(self, topic, roster):
        self._roster = roster
        self._topic = topic

    def say(self, message):
        pass


class User(object):
    pass


class Plugin(object):
    pass


class Storage(object):
    pass


class Service(object):
    def __init__(self):
        pass

    def run(self):
        raise NotImplementedError()

    def join_room(self, room):
        raise NotImplementedError()

    def send_message(self, message):
        raise NotImplementedError()


class Matcher(object):
    def __init__(self, func, pattern, priority=50):
        self._callback = None
        self._func = func
        self.pattern = regex.compile(pattern)
        self.priority = priority
        # TODO: Share lock for all methods on same object
        self.lock = ''

    def get_callback(self, factory):
        if not self._callback:
            self._callback = factory.get_callback(self._func)
        return self._callback
