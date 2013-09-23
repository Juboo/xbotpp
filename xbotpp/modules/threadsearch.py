__xbotpp_module__ = "threadsearch"

import re
import json
import urllib
from xbotpp import bot
from xbotpp import logging
from xbotpp.util import *

fields = {
	# 'friendly name': '4chan API field name',
	'name': 'name',
	'trip': 'trip',
	'subject': 'sub',
	'comment': 'com',
}

@bot.signal.on_signal(r'url::boards.4chan.org/\w+/res/\d+')
def on_url(url):
	m = re.search(r'boards.4chan.org/(\w+)/res/(\d+)', url)
	if m:
		url = "https://api.4chan.org/{0}/res/{1}.json".format(*m.group(1, 2))
		return get_post(url)

def get_post(url):
	data = json.loads(str(urllib.request.urlopen(url, timeout=5).read(), 'utf-8'))
	kw = {
		'sub': data['posts'][0]['sub'] if 'sub' in data['posts'][0] else smart_truncate(data['posts'][0]['com'], 50),
		'reltime': pretty_date(data['posts'][0]['time']),
		'replies': str(data['posts'][0]['replies']),
		'images': str(data['posts'][0]['images']),
	}
	return "4chan: {sub} ({reltime}, {replies} replies, {images} images)".format(**kw)

@bot.signal.on_signal('command::4ch')
def search(info, args, buf):
	if len(args) < 2:
		return "Usage: <board> [~<field>] <search term> (where <field> is one of: {})".format(", ".join(fields.keys()))

	b = args[0]

	if len(args) >= 3 and args[1][0] == "~":
		sf = [fields[args[1][1:]]]
		term = " ".join(args[2:])
	else:
		sf = ['sub', 'com']
		term = " ".join(args[1:])

	success, thread = actual_search(b, term, sf)

	if success:
		tu = "http://boards.4chan.org/{b}/res/{id}".format(b=b, id=str(thread['no']))
		url = "https://api.4chan.org/{0}/res/{1}.json".format(b, str(thread['no']))
		return "{} {}".format(get_post(url), tu)
	else:
		return thread

def actual_search(board, term, fields=['sub', 'com']):
	url = "https://api.4chan.org/{board}/catalog.json"
	try:
		data = json.loads(str(urllib.request.urlopen(url.format(board=board)).read(), 'utf-8'))
	except Exception as e:
		tr = traceback.extract_tb(ex.__traceback__)
		logging.error("Exception in 4chan thread search: [{} at {}:{}] {}".format(
		              e.__class__.__name__, tr[-1][0], tr[-1][1], str(e)))
		return (False, "Invalid board or error retrieving catalog.")

	logging.debug('Board: {}'.format(repr(board)))
	logging.debug('Search field(s): {}'.format(repr(fields)))
	logging.debug('Search term: {}'.format(repr(term)))

	for field in fields:
		logging.debug('Field: {}'.format(field))
		for page in data:
			logging.debug('Page: {}'.format(page['page']))
			for thread in page['threads']:
				try:
					if field in thread and re.search(term, thread[field], re.I):
						return (True, thread)
				except Exception as e:
					logging.error("Exception in 4chan thread search (page {} thread {}): [{} at {}:{}] {}".format(
					              page['page'], e.__class__.__name__, thread, tr[-1][0], tr[-1][1], str(e)))

	return (False, "No thread matching the search terms was found.")
