import xbotpp
from . import logging
from . import util
from . import timer
from . import signal
from . import abstract
from . import info
from . import protocol
from . import permission
from . import exceptions

import os
import sys
import bisect
import inspect
import threading
import yaml
import imp
import importlib
import traceback
import plyvel

class Bot:
	def __init__(self, options):
		self.config_file = options.config_file
		self._cleanup = False

		self.connections = util.ObjectDict()
		self.modules = util.ObjectDict()
		self.mutex = threading.RLock()
		self.signal = signal.SignalManager()
		self.timer = timer.TimerManager()

		self.threads = util.ObjectDict()
		self.threads.process_once = util.ObjectDict()

		# for debugging
		self.signal.subscribe('message', self.on_message)
		#self.enable_tick()

	def enable_tick(self):
		self.timer.execute_every(1, self.signal, args=('debug::tick', 1))
		self.timer.execute_every(5, self.signal, args=('debug::tick', 5))

	def _load_config(self):
		logging.debug('Entered _load_config().')
		with self.mutex:
			self.options = util.ObjectDict()
			self._options = yaml.load(open(self.config_file, 'r'))
			
			# Construct list of admins
			self.options.admins = []
			for admin in self._options['admins']:
				a = info.Admin(**admin)
				if 'owner' in admin:
					self.options.owner = a
				self.options.admins.append(a)

			self.options.prefix = self._options['prefix']
			self.options.modules = self._options['modules']
			self.options.networks = self._options['networks']

		logging.debug('Finished _load_config().')

	def _load_classes(self):
		logging.debug('Entered _load_classes().')
		with self.mutex:
			self.db = plyvel.DB(self.options.modules['db'], create_if_missing=True)
			for network in self.options.networks:
				pname = self.options.networks[network]['protocol']
				try:
					pmod = importlib.import_module('xbotpp.protocol.%s' % pname)
					logging.debug(repr(pmod) + ' ' + repr(dir(pmod)))
					if hasattr(pmod, '__xbotpp_protocol__'):
						try:
							p = getattr(pmod, pmod.__xbotpp_protocol__)
							if protocol.base.BaseProtocol in inspect.getmro(p):
								self.connections[network] = p(network)
							else:
								logging.error('The protocol specified for network {} ({}) does not appear to be'
								              ' a valid xbot++ protocol library.'.format(network, repr(pname)))

						except Exception as e:
							logging.error('An error occurred while loading the {} protocol: \n'
							              '{} {}'.format(repr(pname), e.__class__.__name__, str(e)))
					else:
						logging.error('The protocol specified for network {} ({}) does not appear to be'
						              ' a valid xbot++ protocol library.'.format(network, repr(pname)))
				except ImportError:
					logging.error('The protocol {} could not be found.'.format(repr(pname)))

			for modname in self.options.modules['autoload']:
				try:
					self.loadmod(modname)
				except Exception as e:
					logging.error('An error occurred while loading the module {}: \n'
					              '{} {}'.format(repr(modname), e.__class__.__name__, str(e)))

		logging.debug('Finished _load_classes().')

	def loadmod(self, modname):
		'''\
		Load the module named `modname`.
		'''

		with self.mutex:
			if modname in self.modules:
				module = self.modules[modname]
			else:
				module = importlib.import_module('xbotpp.modules.%s' % modname)

			self.signal.remove_module(module)
			imp.reload(module)
			if hasattr(module, '__xbotpp_module__'):
				self.modules[module.__xbotpp_module__] = module
			else:
				raise ImportError('Module {} does not look like an xbot++ module.'.format(repr(modname)))
			return True

	def unloadmod(self, modname):
		'''\
		Unload the module named `modname`.
		'''

		with self.mutex:
			if modname in self.modules:
				self.signal.remove_module(self.modules[modname])
				del self.modules[modname]
			else:
				raise ValueError('Module {} is not loaded.'.format(repr(modname)))

	def on_message(self, m):
		if m.message.startswith(self.options.prefix):
			command = []
			temp = []

			for i in m.message[len(self.options.prefix):].split(' '):
				if i != "|":
					temp.append(i)
				else:
					command.append(temp)
					temp = []
			command.append(temp)
			del temp

			buf = ""
			sendto = m.source.nick if isinstance(m.target, str) and m.target.lower() == self.connections[m.network].nick.lower() else m.target.name

			for i, _ in enumerate(command):
				try:
					buf = self.signal.send_to_first('command::{}'.format(command[i][0]), m, command[i][1:], buf)
				except exceptions.EventException as ex:
					if i != 0:
						buf = "{}: unknown command.".format(command[i][0])
					else:
						buf = ""
					break
				except exceptions.UserNotAuthorized as ex:
					buf = "{}: not authorized.".format(command[i][0])
					break
				except Exception as ex:
					#raise
					tr = traceback.extract_tb(ex.__traceback__)
					buf = "Exception in {}: [{} at {}:{}] {}".format(
					      repr(command[i][0]), ex.__class__.__name__, 
					      tr[-1][0], tr[-1][1], str(ex))
					break

			if not buf in ['', None]:
				for line in buf.split('\n'):
					self.connections[m.network].send_message(sendto, line)

	def cleanup(self):
		'''\
		Cleanup bot temporary files and flush data and configuration to disk.
		'''

		logging.debug('Entered bot.cleanup().')
		with self.mutex:
			if not self._cleanup:
				logging.info('Cleaning up...')
				for c in self.connections:
					self.connections[c].disconnect()

				logging.info('Cleanup complete.')
				self._cleanup = True
		logging.debug('Finished bot.cleanup().')

	def start(self):
		'''\
		Starts the bot.
		'''

		logging.debug('Entered bot.start().')
		with self.mutex:
			for c in self.connections:
				logging.info('Connecting to %s...' % repr(c))
				self.connections[c].connect()

		logging.debug('Calling bot.process_forever().')
		try:
			self.process_forever()
		except Exception as e:
			raise
			#logging.error('An error occurred while starting the bot:\n'
			#	'{}: {}'.format(e.__class__.__name__, str(e)))

	def stop(self, *args, **kwargs):
		logging.info('Bye!')
		sys.exit(1)

	def process_once(self):
		'''\
		Process one iteration of the main loop.
		'''

		with self.mutex:
			for c in self.connections:
				# start a new process_once thread for each connection (but only if one doesn't already exist)
				if c in self.threads.process_once and self.threads.process_once[c].is_alive():
					continue

				self.threads.process_once[c] = threading.Thread(target=self.connections[c].process_once, name='{}.process_once'.format(c), daemon=True)
				self.threads.process_once[c].start()

			self.timer.check()

	def process_forever(self):
		'''\
		The bot main loop. Calls :meth:`.Bot.process_once` in a loop, checking
		for interrupts, and cleaning up the bot as necessary.
		'''

		while True:
			try:
				self.process_once()
			except (KeyboardInterrupt, SystemExit):
				self.cleanup()
				break
