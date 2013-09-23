__xbotpp_module__ = "uguu"

import xbotpp
from xbotpp import bot
from xbotpp import logging
from xbotpp.util import *

import json
import urllib.parse
import urllib.request

@bot.signal.on_signal('url::uguu.us/.*')
def uguuscan(url):
	url = url + '/stats.json'
	r = urllib.request.Request(url, headers={'User-Agent': 'xbot++/{} OpenGraphScanner'.format(xbotpp.__version__)})
	d = json.loads(str(urllib.request.urlopen(r, timeout=5).read(), 'utf-8'))
	if not d['error']:
		kw = {
			'first': urllib.parse.unquote(''.join(urllib.parse.urlsplit(d['short'])[1:3])),
			'hits': str(d['hits']['all']),
			'link': urllib.parse.urlsplit(d['long'])[1],
		}
		return '{first}: {hits} hits, links to {link}'.format(**kw)
