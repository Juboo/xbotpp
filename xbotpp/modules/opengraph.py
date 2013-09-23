__xbotpp_module__ = "opengraph"

import xbotpp
from xbotpp import bot
from xbotpp import logging

import re
import lxml.html
import traceback
import urllib.parse
import urllib.request


'''\
Open Graph URL scanning module.
'''

class HeadRequest(urllib.request.Request):
	def get_method(self):
		return "HEAD"

@bot.signal.on_signal('message')
def scan(message):
	for url in re.findall('(?P<url>(https?://|www.)[^\s]+)', message.message):
		logging.info("Found URL: {}".format(url[0]))
		
		try:
			result = do_og(url[0])
			if result:
				message.reply(result)
		except Exception as e:
			tr = traceback.extract_tb(e.__traceback__)
			logging.error("Exception in URL scan: [{} at {}:{}] {}".format(
			              e.__class__.__name__, tr[-1][0], tr[-1][1], str(e)))

def do_og(url):
	url = urllib.parse.quote(url, safe='/:')
	logging.debug(repr(url))

	# Check for registered URL modules
	logging.info("Checking for registered URL modules...")
	for signal in bot.signal.subscribers:
		if signal.startswith('url::'):
			if re.search(signal[5:], url):
				logging.info("Found matching URL module, calling ({})".format(signal))
				return bot.signal.send_to_first(signal, url)

	# Get the headers of the URL
	logging.debug("Sending HEAD request...")

	r = HeadRequest(url, headers={'User-Agent': 'xbot++/{} OpenGraphScanner'.format(xbotpp.__version__)})
	response = urllib.request.urlopen(r, timeout=2)

	# Check if we have an HTML document
	conttype = response.info().get_content_type()
	logging.info("Content-Type: %s" % conttype)
	if not re.search("html", conttype):
		logging.info("Abort Open Graph scan.")
		return None

	logging.info("Fetching OpenGraph data...")

	og = {}
	r = urllib.request.Request(url, headers={'User-Agent': 'xbot++/{} OpenGraphScanner'.format(xbotpp.__version__)})
	html = lxml.html.document_fromstring(urllib.request.urlopen(r, timeout=5).read())
	for element in html.xpath('//meta'):
		prop = element.get('property')
		if prop and prop.startswith('og:'):
			og[prop[3:]] = element.get('content')

	if og and 'title' in og:
		logging.info("Found Open Graph data.")

		if 'site_name' in og:
			return "%s: \x02%s\x02" % (og['site_name'], og['title'])
		else:
			return "\x02%s\x02" % og['title']
	else:
		try:
			logging.info("Falling back to <title> element.")
			title = html.xpath("//title/text()")[0]
			title = " ".join([s.strip() for s in title.split()])
			return "\x02%s\x02" % title
		except:
			return None
