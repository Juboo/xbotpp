__xbotpp_module__ = "threadsearch"

import re
import json
import urllib
import xbotpp
import xbotpp.modules
import xbotpp.debug
from lxml import html

xbotpp.state.modules.depends(__xbotpp_module__, ['opengraph'])
og_register = xbotpp.state.modules.loaded['opengraph']['module'].register

fields = {
	# 'friendly name': '4chan API field name',
	'name': 'name',
	'trip': 'trip',
	'subject': 'sub',
	'comment': 'com',
}

def smart_truncate(content, length=100, suffix='...'):
	return (content if len(content) <= length else content[:length].rsplit(' ', 1)[0]+suffix)

@xbotpp.modules.on_command('4ch')
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

		if 'sub' in thread:
			r = thread['sub']
		else:
			r = thread['com']


		return "{content} - {url}".format(content=smart_truncate(r, length=50), url=tu)
	else:
		return thread

def actual_search(board, term, fields=['sub', 'com']):
	url = "https://api.4chan.org/{board}/catalog.json"
	try:
	    data = json.loads(str(urllib.request.urlopen(url.format(board=board)).read(), 'utf-8'))
	except Exception as e:
		xbotpp.debug.exception("4chan thread search", e)
		return (False, "Invalid board or error retrieving catalog.")

	xbotpp.debug.write('Board: {}'.format(repr(board)))
	xbotpp.debug.write('Search field(s): {}'.format(repr(fields)))
	xbotpp.debug.write('Search term: {}'.format(repr(term)))


	for field in fields:
		xbotpp.debug.write('Field: {}'.format(field))
		for page in data:
			xbotpp.debug.write('Page: {}'.format(page['page']))
			for thread in page['threads']:
				try:
					if field in thread and re.search(term, thread[field], re.I):
						return (True, thread)
				except Exception as e:
					xbotpp.debug.exception("Page {0}, thread {1}".format(page['page'], thread), e)
	
	return (False, "No thread matching the search terms was found.")
