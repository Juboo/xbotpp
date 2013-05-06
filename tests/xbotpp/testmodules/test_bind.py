# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp.modules import Module


class test_bind(Module):
    def __init__(self):
        self.bind_command("test_bind", self.custom_action)
        Module.__init__(self)

    def custom_action(self, bot, event, args, buf):
        return "Test Module"
