# -*- coding: utf-8 -*-
# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp.modules import CommandModule

class reload(CommandModule):
    def __init__(self):
        self.perms = "admin"
        CommandModule.__init__(self)

    def action(self, bot, event, args, buf):
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

class join(CommandModule):
    def __init__(self):
        self.perms = "admin"
        CommandModule.__init__(self)

    def action(self, bot, event, args, buf):
        for channel in args:
            try:
                self.bot.connection.join(channel)
            except:
                return "Couldn't join channel %s." % channel

class part(CommandModule):
    def __init__(self):
        self.perms = "admin"
        CommandModule.__init__(self)

    def action(self, bot, event, args, buf):
        try:
            self.bot.connection.part(args[0], args[1:])
        except:
            pass

class prefix(CommandModule):
    def __init__(self):
        self.perms = "admin"
        CommandModule.__init__(self)

    def action(self, bot, event, args, buf):
        if len(args[0]) == 1:
            self.bot.prefix = args[0]
            return "Prefix set to %s." % args[0]
        else:
            return "Invalid prefix."

