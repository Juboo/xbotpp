import sys
from datetime import datetime

_loglevels = [
	('debug', 0, 'DD'),
	('info', 1, 'II'),
	('warning', 2, '??'),
	('error', 3, '!!'),
]

_displaylevel = 1

def setdisplaylevel(level):
	assert isinstance(level, int)
	global _displaylevel
	_displaylevel = level

def write(level, text, end='\n'):
	if level[1] >= _displaylevel:
		time = str(datetime.time(datetime.now()))
		realpad = "[{0}] [{1}]".format(time, level[2])
		for index, line in enumerate(text.split('\n')):
			if index is 0:
				pad = realpad
			else:
				pad = ' ' * (len(realpad))

			print("%s %s" % (pad, line.strip()), file=sys.stderr, end=end)
			sys.stderr.flush()

def init():
	# install the wrapper functions. i'm being hacky here and doing this so
	# you can just call logging.info(text) or logging.debug(text) instead of
	# logging.write(_loglevels[0], text). which is nice. keeps the code clean
	# too :D
	for l in _loglevels:
		exec('global {0}\n{0} = lambda *x, **y: write({1}, *x, **y)'.format(l[0], l))