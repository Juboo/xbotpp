# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp.modules import Module

class help(Module):
    """\
    Provide help on the bot.
    """

    def __init__(self):
        Module.__init__(self)

    def action(self, bot, event, args, buf):
        """\
        Return a list of available commands.
        """

        bot_commands = []

        for module in enumerate(self.bot.modules.modules['command']):
            bot_commands.append(module[1])

        return "Available commands: %s" % ", ".join(bot_commands)
