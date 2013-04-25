# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp.modules import Module


class channel(Module):
    """\
    Channel commands.
    """

    def __init__(self):
        self.perms = "admin"
        self.bind = [
            ["command", "join", self.join, "admin"],
            ["command", "part", self.part, "admin"],
        ]
        Module.__init__(self)

    def join(self, bot, event, args, buf):
        """\
        Join the specified channel.
        """

        if len(args) == 1:
            try:
                self.bot.connection.join(args[0])
            except:
                return "Couldn't join channel %s." % args[0]
        else:
            return "Usage: %sjoin <channel>" % bot.prefix

    def part(self, bot, event, args, buf):
        """\
        Part from the specified channel, optionally with a message (``args[1:]``)
        """

        if len(args) == 1:
            try:
                self.bot.connection.part(args[0])
            except:
                pass
        elif len(args) > 1:
            try:
                self.bot.connection.part(args[0], args[1:])
            except:
                pass
        else:
            return "Usage: %spart <channel> [message]" % bot.prefix
