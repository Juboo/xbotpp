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
        privlevel = "common"

        if len(args) == 1:
            privlevel = args[0]

        for module in enumerate(self.bot.modules.modules['command']):
            command = self.bot.modules.modules['command'][module[1]]
            if command[1] == privlevel:
                bot_commands.append(module[1])

        return "Available commands: %s" % ", ".join(bot_commands)
