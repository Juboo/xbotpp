__xbotpp_module__ = "opengraph"

import xbotpp
import xbotpp.debug
import xbotpp.modules
import re
import lxml.html
import urllib.parse
import urllib.request


"""\
Open Graph URL scanning module.
"""

#: {
#:     'url_regex': <function ...>,
#:     'url_regex': <function ...>,
#: }
registered_handlers = {}

class HeadRequest(urllib.request.Request):
    """\
    A :py:class:`urllib.request.Request` object to represent a HTTP HEAD request.
    """

    def get_method(self):
        return "HEAD"

def register(url_regex):
	'''\
	Add a function to the URL scanning helper list.
	'''

	def constructor(r):
		registered_handlers[url_regex] = r
		return r
	return constructor

@xbotpp.modules.on_event('message')
def scan(event):
    """\
    Searches in a received message for URLs.

    Checks URLs against the list of excluded URLs in the config, and calls :py:func:`do_og` for
    each non-excluded URL.
    """

    message = event.message
    target = event.source if event.type == 'privmsg' or event.type == 'privnotice' else event.target
    excludes = xbotpp.config['modules']['opengraph']['excludes'] or []

    for url in re.findall('(?P<url>(https?://|www.)[^\s]+)', message):
        xbotpp.debug.write("Found URL: {}".format(url[0]))
        for k in excludes:
            if re.match(k, url[0]):
                xbotpp.debug.write("URL in excludes, skipping.")
                continue

        try:
            result = do_og(url[0])
            if result:
                xbotpp.state.connection.send_message(target, result)
        except:
            raise

def do_og(url):
    """\
    Checks if the given URL matches a registered URL handler and call the handler if it does,
    otherwise scan the page for Open Graph metadata, falling back to returning the page title
    if no metadata was found.
    """

    # Check for registered URL modules
    xbotpp.debug.write("Checking for registered URL modules...")
    for module in registered_handlers.keys():
        xbotpp.debug.write(" -> %s" % module)

        if re.search(module, url):
            xbotpp.debug.write("Found matching URL module, calling")
            return registered_handlers[module](url)

    # Get the headers of the URL
    xbotpp.debug.write("Sending HEAD request...")
    try:
        response = urllib.request.urlopen(HeadRequest(url), timeout=2)
    except urllib.request.URLError:
        return None

    # Check if we have an HTML document
    conttype = response.info().get_content_type()
    xbotpp.debug.write("Content-Type: %s" % conttype)
    if not re.search("html", conttype):
        xbotpp.debug.write("Abort Open Graph scan.")
        return None
    
    xbotpp.debug.write("Fetching OpenGraph data...")

    og = {}
    html = lxml.html.document_fromstring(urllib.request.urlopen(url, timeout = 5).read())
    for element in html.xpath('//meta'):
        prop = element.get('property')
        if prop and prop.startswith('og:'):
            og[prop[3:]] = element.get('content')

    if og and 'title' in og:
        xbotpp.debug.write("Found Open Graph data.")

        if 'site_name' in og:
            return "%s: \x02%s\x02" % (og['site_name'], og['title'])
        else:
            return "\x02%s\x02" % og['title']
    else:
        try:
            xbotpp.debug.write("Falling back to <title> element.")
            title = html.xpath("//title/text()")[0]
            title = str(re.sub("[^a-zA-Z0-9\\.\-\|\s\\\\\\/!@#\$%|^&*(){}\[\]_+=<>,\?'\":;\~\`]", '', title), 'utf-8')
            title = " ".join([s.strip() for s in title.split()])
            return "\x02%s\x02" % title
        except:
            return None
