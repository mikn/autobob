import autobot


class HelloPlugin(autobot.Plugin):

    def __init__(self, factory):
        super().__init__(factory)
        if 'hello_replies' not in self.storage:
            self.storage['hello_replies'] = []

    @autobot.respond_to('^(H|h)i,? ({mention_name})')
    @autobot.respond_to('^(H|h)ello,? ({mention_name})')
    def hi(self, message):
        message.reply('Hi, %s!' % message.author)
        self.storage['hello_replies'].append(message.author)

    @autobot.eavesdrop(always=True)
    def listen(self, message):
        pass

    @autobot.scheduled(minutes='*/1')
    def be_obnoxious(self):
        self.default_room.say('Echo on a clock!')
