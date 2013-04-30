# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp.modules import Module


class test_args(Module):
    def __init__(self):
        Module.__init__(self)

    def action(self, bot, event, args, buf):
        return "Arguments: %s" % " ".join(args)
