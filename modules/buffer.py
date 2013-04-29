# vim: noai:ts=4:sw=4:expandtab:syntax=python

import re
from xbotpp.modules import Module


class buffer(Module):
    """\
    Buffer manipulation commands.
    """

    def __init__(self):
        self.bind = [
            ["command", "echo", self.echo, "common"],
            ["command", "grep", self.grep, "common"],
        ]
        Module.__init__(self)

    def echo(self, bot, event, args, buf):
        """\
        Return the given arguments.
        """

        return " ".join(args)
    

    def grep(self, bot, event, args, buf):
        """\
        Splits the input buffer by lines and returns the lines that match the
        regular expression given in the command arguments.

        :rtype: str
        """

        if len(args) is 0 or buf == "":
            return "%scommand | grep <regex>" % self.bot.prefix

        matches = []

        for x in buf.split("\n"):
            if re.match(" ".join(args), x):
                matches.append(x)

        if len(matches) is not 0:
            return "\n".join(matches)
        else:
            return "No matches for /%s/ in input buffer." % " ".join(args)

