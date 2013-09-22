__xbotpp_module__ = "osu"

import json
import urllib.parse
import urllib.request
from xbotpp import bot
from xbotpp import logging


#: Available osu! gamemodes.
gamemodes = {
	0: 'osu!',
	1: 'Taiko',
	2: 'CtB',
	3: 'osu!mania',
}

def get_stats(user, mode=0):
	'''\
	Get statistics for a given user from the osu! API.

	`mode` is an integer, representing the gamemode to retrieve the statistics
	for:

	- 0: osu! (the default)
	- 1: Taiko
	- 2: CtB
	- 3: osu!mania

	Raises a :exc:`KeyError` if the mode is not valid, (re-)raises a urllib
	exception if there was an error retrieving the data, returns None if the
	module is not configured (no API key present), or returns the user's info
	as a dictionary, in the same format presented by the osu! API. For the API
	documentation, see '<https://github.com/peppy/osu-api/wiki#apiget_user>`_.
	'''

	if not 'osu' in bot.options.modules or not 'apikey' in bot.options.modules['osu']:
		logging.debug("osu! API key not in config file, bailing")
		return None

	if mode > 3 or mode < 0:
		# made has to be 0-3
		raise KeyError('mode')

	postdata = urllib.parse.urlencode({
		'k': bot.options.modules['osu']['apikey'],
		'u': user,
		'm': mode,
	})
	logging.debug('postdata: {}'.format(repr(postdata)))

	request = urllib.request.Request('http://osu.ppy.sh/api/get_user', bytes(postdata.encode('utf-8')))
	data = json.loads(str(urllib.request.urlopen(request).read(), 'utf-8').strip())[0]
	return data

def metric(num):
	"""Returns user-readable string representing given number."""
	for metric_raise, metric_char in [[9, 'B'], [6, 'M'], [3, 'k']]:
		if num > (10 ** metric_raise):
			return '{:.1f}{}'.format((num / (10 ** metric_raise)), metric_char)
	return str(num)

@bot.signal.on_signal('command::osu')
def osu_command(message, args, buf):
	# mode number to get info for. default is 0 which is osu!, and this will be
	# changed by the arguments if-block below if it needs to be
	gamemode = 0

	if len(args) > 1 and args[0].startswith('-'):
		# assume starting with '-' means it's a switch, so handle it as one
		if args[0] == '-t':
			gamemode = 1
			args = args[1:]
		elif args[0] == '-c':
			gamemode = 2
			args = args[1:]
		elif args[0] == '-m':
			gamemode = 3
			args = args[1:]

	logging.debug('osu! gamemode: {}'.format(gamemodes[gamemode]))
	dbkey = 'osu::username::{}'.format(message.source.nick).encode('utf-8')
	user = bot.db.get(dbkey)
	logging.debug('DB has osu! username {} for nick {}'.format(repr(user), repr(message.source.nick)))

	if len(args) is not 0:
		user = ' '.join(args)
		bot.db.put(dbkey, user.encode('utf-8'))
	elif user == None:
		return "I don't know your osu! username, {}!".format(message.source.nick)

	# get the info
	try:
		data = get_stats(user, gamemode)
	except KeyError:
		return "osu: Invalid mode."
	except IndexError:
		return "No data for user {}.".format(user)
	except:
		# send this up the chain if something weird happened
		raise

	if not data:
		return "osu: Not configured."

	formatstr = "{mode} stats for {user}: #{rank} ({pp} pp), Level {level} ({level_percent}%), ranked score {ranked}, {plays} plays, {accuracy}% accuracy"
	formatdata = {
		'mode': gamemodes[gamemode],
		'user': data['username'],
		'rank': data['pp_rank'],
		'level': int(float(data['level'])),
		'level_percent': "{0:.2f}".format(float('0.{}'.format(data['level'].split('.')[1])) * 100),
		'pp': data['pp_raw'],
		'ranked': metric(int(data['ranked_score'])),
		'plays': metric(int(data['playcount'])),
		'accuracy': "{0:.2f}".format(float(data['accuracy'])),
	}

	return formatstr.format(**formatdata)
