# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp.modules import Module


class channel(Module):
    """\
    Channel commands.
    """

    def __init__(self):
        self.bind_command("join", self.join, "admin")
        self.bind_command("part", self.part, "admin")
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
        Part from a channel.

        If no channel name specified as first argument, assumes current channel.
        A message can optionally be included.
        """

        if len(args) == 1:
            try:
                self.bot.connection.part(args[0])
            except:
                pass
        elif len(args) > 1 and args[0][0] == "#":
            try:
                self.bot.connection.part(args[0], args[1:])
            except:
                pass
        elif len(args) > 1 and args[0][0] != "#":
            try:
                self.bot.connection.part(event.target, args[0:])
            except:
                pass
        elif len(args) == 0:
            try:
                self.bot.connection.part(event.target)
            except:
                pass
        else:
            return "Usage: %spart <channel> [message]" % bot.prefix
