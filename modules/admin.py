# -*- coding: utf-8 -*-
# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp.modules import Module

class reload(Module):
    def __init__(self):
        self.perms = "admin"
        Module.__init__(self)

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
