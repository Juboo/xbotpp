# vim: noai:ts=4:sw=4:expandtab:syntax=python

from xbotpp.modules import Module


class nickserv(Module):
    def __init__(self):
        self.bind_command("nickserv", self.action, "", "privmsg")
        Module.__init__(self)

    def load(self):
        if self.bot.config.has_option(self.bot.config.active_network, "nickserv_password"):
            self.bot._debug("NickServ authentication enabled.")

    def action(self, bot, event, args, buf):
        """\
        Automatically authonticate with NickServ when an authentication request is received.
        """

        if self.bot.config.has_option(self.bot.config.active_network, "nickserv_password"):
            if event.source.nick.lower() == "nickserv" and "registered" in " ".join(args):
                self.bot._debug("Sending NickServ authentication...")
                self.bot.connection.privmsg("nickserv", "identify %s" % self.bot.config.get(self.bot.config.active_network, "nickserv_password"))
            
