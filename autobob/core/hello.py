import autobob


class HelloPlugin(autobob.Plugin):

    def __init__(self, factory):
        autobob.Plugin.__init__(self, factory)
        if not 'hello_replies' in self.storage:
            self.storage['hello_replies'] = []

    @autobob.respond_to('^(H|h)i,? botname')
    @autobob.respond_to('^(H|h)ello,? botname')
    def hi(self, message):
        if message.author not in self.storage['hello_replies']:
            message.reply('Hi!')
            self.storage['hello_replies'].append(message.author)
