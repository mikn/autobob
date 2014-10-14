import autobob


@autobob.plugin
class HelloPlugin(autobob.Plugin):

    @autobob.respond_to('^(H|h)i,? botname')
    @autobob.respond_to('^(H|h)ello,? botname')
    def hi(self, message):
        message.reply('Hi!')
