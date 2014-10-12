
class Message(object):
    def __init__(self, message, author, room=None):
        self._message = message
        self._author = author
        self._room = room
        # TODO: Parse for mentions through Service
        self._mentions = []

    def mentions(self, username):
        return username in self._mentions

    def reply():
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

    def join_room(self, room):
        raise NotImplementedError()

    def send_message(self, message):
        raise NotImplementedError()


class Matcher(object):
    def __init__(self, func, pattern, priority=50):
        self._callback = None
        self._func = func
        self.pattern = pattern
        self.priority = priority
        # TODO: Share lock for all methods on same object
        self.lock = ''

    @property
    def callback(self):
        if not self._callback:
            self._callback = factory.get_callback(self._func)
        return self._callback
