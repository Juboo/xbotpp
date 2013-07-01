# vim: noai:ts=4:sw=4:expandtab:syntax=python
__xbotpp_module__ = "sprunge"

import urllib.parse
import urllib.request
import xbotpp.debug
import xbotpp.modules

@xbotpp.modules.on_command('sprunge')
def sprunge(info, args, buf):
    """\
    Paste the input buffer to sprunge.us and return a link to the paste.

    :rtype: str
    """

    data = urllib.parse.urlencode({'sprunge': buf})
    req = urllib.request.Request("http://sprunge.us", bytes(data.encode('utf-8')))
    url = urllib.request.urlopen(req).read().strip()
    return str(url, 'utf-8')
