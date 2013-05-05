# vim: noai:ts=4:sw=4:expandtab:syntax=python

import urllib.parse
import urllib.request
from xbotpp.modules import Module


class web(Module):
    """\
    Modules to interface with the World Wide Web (oooo)
    """

    def __init__(self):
        self.bind_command("sprunge", self.sprunge)
        self.bind_command("curl", self.curl)
        Module.__init__(self)

    def sprunge(self, bot, event, args, buf):
        """\
        Paste the input buffer to sprunge.us and return a link to the paste.

        :rtype: str
        """

        data = urllib.parse.urlencode({'sprunge': buf})
        req = urllib.request.Request("http://sprunge.us", bytes(data.encode('utf-8')))
        url = urllib.request.urlopen(req).read().strip()
        return str(url, 'utf-8')

    def curl(self, bot, event, args, buf):
        """\
        Get the content of a URL given as the argument(s) to the command and
        return it.
        """

        req = urllib.request.urlopen(" ".join(args)).read().strip()
        return str(req, 'utf-8')

