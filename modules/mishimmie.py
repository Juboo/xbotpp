# vim: noai:ts=4:sw=4:expandtab:syntax=python
__xbotpp_module__ = "mishimmie"

import re
import urllib
import xbotpp
import xbotpp.modules
import xbotpp.debug
from lxml import html


@xbotpp.modules.on_command('mi')
def search(info, args, buf):
    """\
    Command to search the Mishimmie for a given search term.

    Constructs a search URL and feeds it to :py:func:`miscan` to get information on it.
    """

    if len(args) >= 1:
        url = ""
        if re.match("id:", args[0]):
            terms = re.sub('id:', '', args[0])
            url = "http://shimmie.katawa-shoujo.com/post/view/%s" % urllib.parse.quote(terms)
        else:
            terms = ' '.join(args)
            url = "http://shimmie.katawa-shoujo.com/post/list/%s/1" % urllib.parse.quote(terms)

        res = miscan(url)
        if res:
            return "\x02Mishimmie:\x02 %s // %s" % (res['desc'], res['url'])
        else:
            return "\x02Mishimmie:\x02 No results."

    else:
       return "Usage: %smi <query> -- search the Mishimmie for <query>" % xbotpp.config['bot']['prefix']

def miscan(url):
    """\
    Mishimmie URL scanning function.

    Grabs the HTML for the given URL, and scans it.
    In the case of being given a single post URL, returns the tags and the canonical page URL.
    In the case of being given a search page URL, returns the tags and the canonical page URL of the
    first post on the search page.

    Returns a dict with 'desc', 'url' entries, or None if no information could be found.

    :rtype: dict or None
    """

    xbotpp.debug.write("Scanning Mishimmie for info on %s..." % url)
    rawres = urllib.request.urlopen(url, timeout=5)
    result = str(rawres.read(), 'utf8')
    doc = html.document_fromstring(result)

    try:
        posturl = ""
        postdesc = ""
        xbotpp.debug.write('URL: %s' % rawres.geturl())

        if re.search('/post/view/', rawres.geturl()):
            xbotpp.debug.write('On a post page.')
            posturl = rawres.geturl()
            postdesc = doc.get_element_by_id('imgdata').xpath('form/table/tr/td/input')[0].get('value')
        else:
            xbotpp.debug.write('On a search result page.')
            posturl = "http://shimmie.katawa-shoujo.com%s" % doc.find_class('thumb')[0].xpath('a')[0].get('href')
            postdesc = doc.find_class('thumb')[0].xpath('a/img')[0].get("alt").partition(' // ')[0]

        posturl = re.sub('\?.*', '', posturl)
        return {'desc': postdesc, 'url': posturl}

    except IndexError:
        return None
