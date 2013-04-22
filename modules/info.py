# -*- coding: utf-8 -*-
# vim: noai:ts=4:sw=4:expandtab:syntax=python

import json
from xbotpp.modules import CommandModule

class info(CommandModule):
    def __init__(self):
        CommandModule.__init__(self)

    def action(self, bot, event, args, buf):
        pretty_json = json.dumps(self.bot.config.items("bot"))
        return pretty_json

