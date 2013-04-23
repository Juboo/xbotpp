# -*- coding: utf-8 -*-
# vim: noai:ts=4:sw=4:expandtab:syntax=python

import urllib.parse
import urllib.request
from xbotpp.modules import Module

class sprunge(Module):
    """\
    Sprunge pastebin module
    """

    def __init__(self):
        Module.__init__(self)

    def action(self, bot, event, args, buf):
        """\
        Paste the input buffer to sprunge.us and return a link to the paste.

        :rtype: str
        """

        data = urllib.parse.urlencode({'sprunge': buf})
        req = urllib.request.Request("http://sprunge.us", bytes(data.encode('utf-8')))
        url = urllib.request.urlopen(req).read().strip()
        return str(url, 'utf-8')

