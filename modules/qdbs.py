__xbotpp_module__ = "qdbs"

import re
import urllib
import xbotpp
import xbotpp.modules
import xbotpp.debug
import lxml.html


@xbotpp.modules.on_command('quote')
def quote(info, args, buf):
    if not 'qdbs' in xbotpp.config['modules'] and not 'url' in xbotpp.config['modules']['qdbs']:
        return 'quote: not configured.'

    if len(args) is 1:
        return getquote(args[0])
    else:
        # Get front page and grab the number of quotes
        url = xbotpp.config['modules']['qdbs']['url']
        data = str(urllib.request.urlopen(url, timeout=5).read(), 'utf-8')
        doc = lxml.html.document_fromstring(data)
        elem = ' '.join([s.strip() for s in doc.find_class('border')[-1].text_content().split('\n')])
        total = int(re.search(r'Total Quotes: (\d+)', elem).group(1))
        return getquote(__import__('random').randrange(1, total))

def getquote(num):
    url = "{base}?{num}".format(**{
        'base': xbotpp.config['modules']['qdbs']['url'],
        'num': num,
    })
        
    data = str(urllib.request.urlopen(url, timeout=5).read(), 'utf-8')
    doc = lxml.html.document_fromstring(data)
    title = doc.find_class('title')[0]
    xbotpp.debug.write(title.text)
    quotenum = title.xpath('a')[0].text
    if not quotenum:
        return "Quote not found."
        
    quote = doc.find_class('body')[0].text_content()

    fmt = {
        'num': quotenum,
        'quote': ' '.join([s.strip() for s in quote.split('\n')])
    }

    return "({num}) {quote}".format(**fmt)

@xbotpp.modules.on_command('addquote')
def addquote(info, args, buf):
    if len(args) is 0 and len(buf) is 0:
        return "Usage: addquote <quote>"

    if not 'qdbs' in xbotpp.config['modules'] and not 'url' in xbotpp.config['modules']['qdbs']:
        return 'quote: not configured.'

    if len(buf) is 0:
        buf = " ".join(args)

    data = urllib.parse.urlencode({
        'quote': buf,
        'do': 'add',
    })

    request = urllib.request.Request(xbotpp.config['modules']['qdbs']['url'], bytes(data.encode('utf-8')))
    result = str(urllib.request.urlopen(request).read(), 'utf-8')
    doc = lxml.html.document_fromstring(result)
    return " ".join([s.strip() for s in doc.find_class('title')[0].text_content().split('\n')]).strip()