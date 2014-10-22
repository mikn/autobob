import autobob


class HelloPlugin(autobob.Plugin):

    def __init__(self, factory):
        super().__init__(factory)
        if not 'hello_replies' in self.storage:
            self.storage['hello_replies'] = []

    @autobob.respond_to('^(H|h)i,? ({mention_name})')
    @autobob.respond_to('^(H|h)ello,? ({mention_name})')
    def hi(self, message):
        if message.author not in self.storage['hello_replies']:
            message.reply('Hi!')
            self.storage['hello_replies'].append(message.author)

    @autobob.eavesdrop(always=True)
    def listen(self, message):
        pass
