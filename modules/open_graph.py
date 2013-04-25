# -*- coding: utf-8 -*-
# vim: noai:ts=4:sw=4:expandtab:syntax=python

import re
from xbotpp.modules import Module

class open_graph(Module):
    """\
    Open Graph URL scanning module.
    """

    def __init__(self):
        self.bind = [
            ["privmsg", "open_graph", self.scan, "common"],
        ]

        Module.__init__(self)

    def scan(self, bot, event, args, buf):
        """\
        Searches in a received message for URLs.

        Checks URLs against the list of excluded URLs in the config, and calls :py:func:`do_og` for
        each non-excluded URL.
        """

        message = " ".join(args)
        excludes = [k.strip() for k in bot.config.get("module: open_graph", "excludes").split(",")]

        for url in re.findall('(?P<url>(https?://|www.)[^\s]+)', message):
            self.bot._debug("Found URL: %s" % url[0])
            for k in excludes:
                if re.match(k, url[0]):
                    self.bot._debug("URL in excludes, skipping.")
                    continue

            try:
                self.bot.connection.privmsg(event.target, self.do_og(url[0]))
            except:
                raise

    def do_og(self, url):
        """\
        Checks if the given URL matches a registered URL handler and call the handler if it does,
        otherwise scan the page for Open Graph metadata, falling back to returning the page title
        if no metadata was found.
        """

        # Check for registered URL modules
        self.bot._debug("Checking for registered URL modules...")
        for module in enumerate(self.bot.modules.modules['url']):
            module = module[1]
            self.bot._debug(" -> %s" % module)

            if re.search(module, url):
                self.bot._debug("Found matching URL module, calling")
                return self.bot.modules.modules['url'][module][0](self.bot, None, url, "")

