# -*- coding: utf-8 -*-
# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp.modules import Module

class reload(Module):
    """\
    Command module to reload other modules.
    """

    def __init__(self):
        self.bind = [
            ["command", "reload", self.reload, "admin" ],
        ]
        Module.__init__(self)

    def reload(self, bot, event, args, buf):
        """\
        Call :py:func:`xbotpp.modules.Modules.load(arg)` for each argument, returning a formatted
        string with the list of modules that were successfully loaded (if any) and the list of
        modules that failed to load (if any).

        :rtype: str
        """

        done = []
        failed = [] 

        for mod in args:
            status = self.bot.modules.load(mod)

            if status == True:
                done.append(mod)
            else:
                failed.append(mod)

            if len(failed) == 0 and len(done) > 0:
                return "Reloaded %s." % ", ".join(done)
            elif len(failed) > 0 and len(done) > 0:
                return "Reloaded %s but failed to reload %s." % (", ".join(failed), ", ".join(done))
            else:
                return "Failed to reload %s." % ", ".join(failed)

class prefix(Module):
    """\
    Temporarily change bot prefix.
    """

    def __init__(self):
        self.perms = "admin"
        self.bind = [
            [ "command", "prefix", self.action, "admin" ],
            [ "privmsg", "prefix", self.privmsg, "common" ],
        ]
        Module.__init__(self)

    def action(self, bot, event, args, buf):
        if len(args[0]) == 1:
            self.bot.prefix = args[0]
            return "Prefix set to %s." % args[0]
        else:
            return "Invalid prefix."

    def privmsg(self, bot, event, args, buf):
        try:
            if self.bot.connection.get_nickname() in args[0] and "help" in args[1]:
                self.bot.connection.notice(event.target, "Hi, I'm a bot! Try using %shelp to see what I can do." % self.bot.prefix)
        except:
            pass

