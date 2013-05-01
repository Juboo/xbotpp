# vim: noai:ts=4:sw=4:expandtab:syntax=python

import inspect
from xbotpp.modules import Module


class help(Module):
    """\
    Provide help on the bot.
    """

    def __init__(self):
        self.bind = [
            ["command", "help", self.list, "common"],
            ["command", "list", self.list, "common"],
            ["command", "man", self.man, "common"],
        ]
        Module.__init__(self)

    def list(self, bot, event, args, buf):
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

    def man(self, bot, event, args, buf):
        """\
        Return a link to the manual page for the given command.
        """

        if len(args) is 0:
            return "%sman <command>" % self.bot.prefix

        for tup in self.bot.modules.actualmodules:
            basename = self.bot.modules.actualmodules[tup][0]
            obj = self.bot.modules.actualmodules[tup][1]
            for type, name, func, perms in obj.bind:
                if name == args[0]:
                    return "http://xbotpp.readthedocs.org/en/latest/modules/%s.html#modules.%s.%s.%s" % (basename, basename, obj.name, func.__name__)

        return "Can't get manual page for that command."

