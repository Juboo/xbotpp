__xbotpp_module__ = "text"

import re
import argparse
from xbotpp import bot
from xbotpp import logging

def _tr(str, inAlphabet='aeioubcdfghjklmnpqrstvwxyz', outAlphabet='iouaenpqrstvwxyzbcdfghjklm'):
	buffer = ""
	for value in str:
		if value.lower() in inAlphabet:
			if value in inAlphabet:
				index = inAlphabet.index(value)
			else:
				index = inAlphabet.index(value.lower())

			c = outAlphabet[index] if (value in outAlphabet or value.lower() in outAlphabet) else value
			buffer += c.upper() if re.search("[A-Z]", value) else c
		else:
			buffer += value
	return buffer

@bot.signal.on_signal('command::tr')
def tr(message, args, buf):
	"""\
	FIXME: docs
	"""

	default_in = "abcdefghijklmnopqrstuvwxyz"
	default_out = "nopqrstuvwxyzabcdefghijklm"

	h = '<command> | tr [input-alphabet] [output-alphabet]\nDefault input alphabet: "%s"\nDefault output alphabet: "%s"' % (default_in, default_out)

	parser = argparse.ArgumentParser(prog='tr', add_help=False)
	parser.add_argument('-h', '--help', action='store_true', dest='help')
	parser.add_argument('a_in', nargs='?', type=str, action="store", default=default_in)
	parser.add_argument('a_out', nargs='?', type=str, action="store", default=default_out)

	try:
		options = parser.parse_args(args)
	except SystemExit:
		# assume that a SystemExit on parse is a 'invalid arguments', so print help
		return h

	if options.help or buf == "":
		return h

	return _tr(buf, options.a_in, options.a_out)

@bot.signal.on_signal('command::lolcrypt')
def lolcrypt(message, args, buf):
	"""\
	Lolcrypt the given arguments, or the buffer (if present)

	Pass "-d" as the first parameter to de-lolcrypt.
	"""

	if len(args) is 0 and buf == "":
		return "Usage: lolcrypt [-d] <text> or command | lolcrypt [-d]"

	delol = (len(args) != 0 and args[0] == "-d")
	text = buf if buf != "" else " ".join(args[1:]) if delol else " ".join(args)

	if delol:
		# de-lolcrypt
		return _tr(text, 'iouaenpqrstvwxyzbcdfghjklm', 'aeioubcdfghjklmnpqrstvwxyz')
	else:
		# en-lolcrypt
		return _tr(text, 'aeioubcdfghjklmnpqrstvwxyz', 'iouaenpqrstvwxyzbcdfghjklm')

@bot.signal.on_signal('command::sed')
def sed(message, args, buf):
	if len(args) > 0 and buf != "":
		m = ' '.join(args).split('/')[1:]
		if len(m) == 3:
			flags = m[2]
		else:
			flags = ''

		pattern = m[0]
		repl = m[1]

		if re.search(pattern, buf):
			return re.sub(pattern, repl, buf, count=0 if 'g' in flags else 1, flags=re.IGNORECASE if 'i' in flags else 0)
		else:
			return "sed: no match found"
		
	else:
		return "Usage: command | sed s/pattern/replacement/[i][g]"
