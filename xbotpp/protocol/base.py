from xbotpp import bot
from xbotpp import logging


__xbotpp_protocol__ = 'BaseProtocol'

class BaseProtocol:
	'''\
	Protocol base class.
	'''

	def __init__(self, network):
		'''\
		`network` is the name of the network entry in *bot.config.networks*.
		'''

		self.network = network
		self.logprefix = '{p}[{n}]: '.format(p=self.__class__.__name__, n=repr(self.network))
		logging.debug(self.logprefix + 'init')

	def connect(self):
		'''\
		Connect to the server using information from the bot configuration.
		'''

		logging.debug(self.logprefix + 'connect')

	def disconnect(self):
		'''\
		Disconnect from the server.
		'''

		logging.debug(self.logprefix + 'disconnect')

	def process_once(self):
		'''\
		Check for new data from the connection and process it.
		'''

		#logging.debug(self.logprefix + 'process_once')
		pass

	def send_message(self, target, message):
		'''\
		Send `message` to `target`.
		'''

		logging.debug(self.logprefix + 'send_message({}, {})'.format(repr(target), repr(message)))

	def change_nick(self, nick):
		'''\
		Change the bot's nick on the network to `nick`.
		'''

		logging.debug(self.logprefix + 'send_message({})'.format(repr(nick)))

	def get_channels(self):
		'''\
		Return a list of channels the bot is in as :class:`.Channel` objects.
		'''

		logging.debug(self.logprefix + 'get_channels')
		return []
