# vim: noai:ts=4:sw=4:expandtab:syntax=python

import re
import irc.client
import lxml.html
import urllib.parse
import urllib.request
from xbotpp.modules import Module


class open_graph(Module):
    """\
    Open Graph URL scanning module.
    """

    class HeadRequest(urllib.request.Request):
        """\
        A :py:class:`urllib.request.Request` object to represent a HTTP HEAD request.
        """

        def get_method(self):
            return "HEAD"

    def __init__(self):
        self.bind_command("open_graph", self.scan, "", "privmsg")
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
                result = self.do_og(url[0], event)
                if result:
                    self.bot.connection.privmsg(event.target, result)
            except:
                raise

    def do_og(self, url, event=None):
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
                return self.bot.modules.modules['url'][module].func(self.bot, event, url, "")

        # Get the headers of the URL
        self.bot._debug("Sending HEAD request...")
        try:
            response = urllib.request.urlopen(self.HeadRequest(url), timeout=2)
        except urllib.request.URLError:
            return None

        # Check if we have an HTML document
        conttype = response.info().get_content_type()
        self.bot._debug("Content-Type: %s" % conttype)
        if not re.search("html", conttype):
            bot._debug("Abort Open Graph scan.")
            return None
        
        self.bot._debug("Fetching OpenGraph data...")

        og = {}
        html = lxml.html.document_fromstring(urllib.request.urlopen(url, timeout = 5).read())
        for element in html.xpath('//meta'):
            prop = element.get('property')
            if prop and prop.startswith('og:'):
                og[prop[3:]] = element.get('content')

        if og and 'title' in og:
            self.bot._debug("Found Open Graph data.")

            if 'site_name' in og:
                return "%s: \x02%s\x02" % (og['site_name'], og['title'])
            else:
                return "\x02%s\x02" % og['title']
        else:
            try:
                self.bot._debug("Falling back to <title> element.")
                title = html.xpath("//title/text()")[0]
                title = str(re.sub("[^a-zA-Z0-9\\.\-\|\s\\\\\\/!@#\$%|^&*(){}\[\]_+=<>,\?'\":;\~\`]", '', title), 'utf-8')
                title = " ".join([s.strip() for s in title.split()])
                return "\x02%s\x02" % title
            except:
                return None

