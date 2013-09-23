__xbotpp_module__ = "markov"

from xbotpp import bot
from xbotpp import logging
from xbotpp import permission
import traceback
import random

key_prefix = b'markov::chain::'

def raw_to_tuples(data):
	for r in data.split(b'\x01'):
		y = r.split(b'\x02')
		yield (int(y[0]), y[1])

def raw_to_weighted_list(data):
	for prob, word in raw_to_tuples(data):
		for i in range(0, prob):
			yield word

def tuples_to_raw(l):
	y = []
	for b in l:
		y.append(b'\x02'.join([str(b[0]).encode('utf-8'), b[1]]))
	return b'\x01'.join(y)

def add_word(key, word):
	kd = bot.db.get(key_prefix + key)
	if kd != None:
		l = list(raw_to_tuples(kd))
		logging.debug(repr(l))
		done = False
		for i, _ in enumerate(l):
			if l[i][1] == word:
				done = True
				l[i] = (l[i][0] + 1, word)
				logging.debug(repr(l[i]))
		if not done:
			l.append((1, word))
		logging.debug(repr(l[-1]))
		kw = tuples_to_raw(l)
	else:
		kw = b'1\x02' + word
	logging.debug(repr(kw))
	bot.db.put(key_prefix + key, kw)

def add_string(s):
	if not isinstance(s, bytes):
		# because leveldb needs bytestrings
		s = s.encode('utf-8')
	st = [t.strip() for t in s.split(b' ')]
	count = 0
	for i, _ in enumerate(st):
		try:
			index = st[i] + b' ' + st[i+1]
			logging.debug(repr(index))
			add_word(index, st[i+2])
			count += 1
		except IndexError:
			logging.debug('markov: hit end of chain (i {}, count {})'.format(str(i), count))
			break
	return count

def list_keys():
	return list(bot.db.iterator(prefix=key_prefix, include_value=False))

def random_key():
	return random.choice(list_keys())[len(key_prefix):]

def get_chain(key=None, count=10):
	if not key:
		key = random_key()
	output = key.split()
	c = 0
	while c < count:
		try:
			logging.debug(repr(output))
			s = bot.db.get(key_prefix + b' '.join([output[-2], output[-1]]))
			if not s:
				break
			l = random.choice(list(raw_to_weighted_list(s)))
			logging.debug(repr(l))
			output.append(l)
			c += 1
		except IndexError:
			break
	return b' '.join(output)

def count():
	count = 0
	for key in list_keys():
		count += len(list(raw_to_tuples(bot.db.get(key))))
	return count

@bot.signal.on_signal('message')
def on_message(message):
	# feed on message
	try:
		add_string(message.message.encode('utf-8'))
	except Exception as e:
		tr = traceback.extract_tb(e.__traceback__)
		logging.error("Exception in markov feed: [{} at {}:{}] {}".format(
		              e.__class__.__name__, tr[-1][0], tr[-1][1], str(e)))

@bot.signal.on_signal('command::markov')
def markov(message, args, buf):
	if len(args) >= 1 and args[0] == "say":
		key = None
		if len(args) > 1:
			key = ' '.join(args[1:]).encode('utf-8')
		return get_chain(key).decode('utf-8')
	elif len(args) >= 1 and args[0] == "count":
		return 'There are {} entries.'.format(str(count()))
	elif len(args) >= 1 and args[0] == "reset":
		if message.source.can(permission.AdminPermissionLevel, message):
			with bot.db.write_batch() as wb:
				for key in list_keys():
					wb.delete(key)
			return 'Done.'
	else:
		try:
			if message.source.can(permission.AdminPermissionLevel, message):
				return "Usage: markov <say [key] | count | reset>"
		except:
			return "Usage: markov <say [key] | count>"

