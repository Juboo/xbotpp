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
            ["command", "tee", self.tee, "common"],
        ]
        Module.__init__(self)

    def echo(self, bot, event, args, buf):
        """\
        Return the input buffer (if given) or the command arguments.
        """

        if buf != "":
            return buf
        else:
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
            if re.search(" ".join(args), x):
                matches.append(x)

        if len(matches) is not 0:
            return "\n".join(matches)
        else:
            return "No matches for /%s/ in input buffer." % " ".join(args)

    def tee(self, bot, event, args, buf):
        """\
        Acts like UNIX ``tee``: runs the command given in it's arguments with
        the input buffer, explicitly sends the return value of that command to
        the target, and passes the input buffer to the next command.

        If there is a ``>`` character in the arguments, instead of sending the
        return value of the tee-executed command to the event target, it pipes
        it to the command specified after the ``>``.

        An example of the usage of both forms of this command is as follows::

            ^help | tee lolcrypt | echo
            ^help | tee lolcrypt > sprunge | echo
        """

        if len(args) is 0:
            return "%scommand | tee <command> [> <command>] | command (the man page will probably help more, see %sman tee)"  % (self.bot.prefix, self.bot.prefix)

        try:
            func = ""
            content = ""
            pipe = ""

            for t in self.bot.modules.modules:
                if args[0] in self.bot.modules.modules[t]:
                    func = self.bot.modules.modules[t][args[0]][0]

            if func == "":
                content = "tee: command not found: %s" % args[0]
            else:
                if ">" in args:
                    name = args[args.index(">")+1]
                    for t in self.bot.modules.modules:
                        if name in self.bot.modules.modules[t]:
                            pipe = self.bot.modules.modules[t][name][0]


            if pipe != "":
                content = func(bot, event, args[1:args.index(">")-1], buf)
                self.bot.connection.privmsg(event.target, pipe(bot, event, args[args.index(">")+2:], content))
            else:
                content = func(bot, event, args[1:], buf)
                self.bot.connection.privmsg(event.target, content)

        except:
            self.bot.connection.privmsg(event.target, "tee: error occurred trying to redirect buffer")
            error_message = "Traceback (most recent call last):\n" + '\n'.join(traceback.format_exc().split("\n")[-4:-1])
            self.bot._debug(error_message, event=event)

        return buf

