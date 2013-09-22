__hello__ = '''\
  .,::      .::::::::.      ...   ::::::::::::
  `;;;,  .,;;  ;;;'';;'  .;;;;;;;.;;;;;;;;''""
    '[[,,[['   [[[__[[\.,[[     \[[,   [[      [      [
     Y$$$P     $$""""Y$$$$$,     $$$   $$    $$$$$  $$$$$
   oP"``"Yo,  _88o,,od8P"888,_ _,88P   88,     8      8
,m"       "Mm,""YUMMMP"   "YMMMMMP"    MMM
'''

__version_tuple__ = (0, 4, 0)
__version_extra__ = "-dev"
__version__ = ".".join([str(s) for s in __version_tuple__]) + __version_extra__

from . import logging
logging.init()
from . import util

bot = None

def parse_options():
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('-c', '--config', help="Configuration file", action="store", dest="config_file", default="config.yml")
	parser.add_argument('-D', '--debug', help="Enable debugging", action="store_true", dest="debug")
	args = parser.parse_args()
	args.__from_parse_options = True
	return args

def init(options=None):
	print(__hello__)
	logging.info('This is xbot++ ' + __version__ + '.')

	options = options or parse_options()

	if hasattr(options, 'debug') and options.debug == True:
		# enable debugging info display
		logging.setdisplaylevel(0)
		logging.debug('Debugging information enabled.')

	try:
		global bot
		from ._bot import Bot
		bot = Bot(options)
		bot._load_config()
		bot._load_classes()

		import signal
		signal.signal(signal.SIGINT, bot.stop)
		signal.signal(signal.SIGTERM, bot.stop)
	except Exception as e:
		raise
		#logging.error('An exception occurred while setting up the bot:\n' \
		#	+ '{}: {}'.format(e.__class__.__name__, str(e)))
		del bot
		raise SystemExit(2)

	if hasattr(options, '__from_parse_options'):
		bot.start()
