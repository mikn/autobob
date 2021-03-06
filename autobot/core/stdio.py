import sys
import threading
import logging
import autobot

LOG = logging.getLogger(__name__)


class StdioService(autobot.Service):
    config_defaults = {'rooms': ['stdin']}

    def __init__(self, config):
        super().__init__(config)
        self._thread = threading.Thread(name='service', target=self._loop)
        self._rooms = {}
        self._init_rooms()

    def _init_rooms(self):
        users = [self._config['mention_name'], 'system']
        roster = []
        for user in users:
            roster.append(autobot.User(
                user, user, reply_handler=self._send_to_user))

        room = autobot.Room('stdin',
                            topic='stdin fake room',
                            roster=roster,
                            reply_handler=self._send_to_room)
        self._rooms[room.name] = room

    def _loop(self):
        room = self.default_room

        def mention_parse(message):
            matches = [u.name for u in room.roster if u.name in message]
            mention_name = self._config['mention_name']
            if mention_name in matches:
                self_index = matches.index(mention_name)
                matches[self_index] = autobot.SELF_MENTION

            return matches

        for line in sys.stdin:
            reply_path = room
            private_match = '{}:'.format(self._config['mention_name'])
            if line.startswith(private_match):
                line = line[len(private_match):].lstrip()
                user = [u for u in room.roster if u.name == 'system']
                reply_path = user.pop()
            msg = autobot.Message(line,
                                  'system',
                                  reply_path=reply_path,
                                  mentions=mention_parse(line))
            self._messageq.put(msg)

    def run(self):
        self._thread.daemon = True
        try:
            self._thread.start()
        except KeyboardInterrupt:
            print('Exiting read loop...')

    def shutdown(self):
        pass

    def _send_to_user(self, user, message, *args):
        sys.stdout.write('{}: {}\n'.format(user, message % args))

    def _send_to_room(self, room, message, *args):
        sys.stdout.write(message % args + '\n')

    def get_room(self, room):
        return self._rooms[room]
