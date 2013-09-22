import xbotpp
from xbotpp import bot
from xbotpp import util
from xbotpp import info
from xbotpp import logging
from xbotpp import abstract
from .base import BaseProtocol

import ssl
import socket
import inspect
import threading

__xbotpp_protocol__ = 'irc'

class ServerSpec:
	'''\
	An IRC server specification.

	>>> ServerSpec('irc.stormbit.net')
	ServerSpec(host='irc.stormbit.net', port=6667, ssl=False)
	>>> ServerSpec('irc.stormbit.net', port=6697, ssl=True)
	ServerSpec('irc.stormbit.net', port=6697, ssl=True)

	Specifying a password will store it but it won't show in a repr():

	>>> a = ServerSpec('irc.stormbit.net', password='password')
	>>> a
	ServerSpec('irc.stormbit.net', port=6667, ssl=False)
	>>> a.password
	'password'
	'''

	def __init__(self, host, port=6667, ssl=False, password=None):
		self.host = host
		if isinstance(port, str):
			port = int(port)
		self.port = port
		self.password = password
		self.ssl = ssl

	def __str__(self):
		return '%s:%d' % (self.host, self.port)

	def as_tuple(self):
		return (self.host, self.port)


	def __repr__(self):
		s = "ServerSpec(host={host}, port={port}, ssl={ssl})"
		return s.format(host=repr(self.host),
		                port=repr(self.port),
		                ssl=repr(self.ssl))


class IrcMessage:
	def __init__(self):
		self.source = None
		self.target = None
		self.mid = None
		self.trailing = None
		self.misc = None

	def __repr__(self):
		l = []
		for attr in ['source', 'target', 'mid', 'trailing', 'misc']:
			if hasattr(self, attr):
				l.append(attr + '=' + repr(getattr(self, attr, None)))
		return "{}({})".format(self.__class__.__name__, ', '.join(l))

class _sendq(list):
	termop = "\r\n"

	def __call__(self, left, right=None):
		logging.debug('\x1b[1msendq\x1b[0m {} {}'.format(repr(left), repr(right)))
		if right:
			limit = 445
			for line in right.splitlines():
				if line:
					lines = [line[i:i+limit] for i in range(0, len(line), limit)]
					for n in range(len(lines)):
						self.append("{} :{}{}".format(' '.join(left), lines[n], self.termop))
		else:
			self.append("{}{}".format(' '.join(left), self.termop))

class _recvq(list):
	termop = '\r\n'
	def __call__(self):
		for b in self:
			logging.debug('\x1b[1mrecvq\x1b[0m {}'.format(repr(b)))
			for line in b.split(self.termop):
				if line:
					yield line
		del self[:]

class irc(BaseProtocol):
	def __init__(self, network):
		self.network = network
		self.logprefix = '{p}[{n}]: '.format(p=self.__class__.__name__, n=repr(self.network))
		self.termop = b'\r\n'
		self.mutex = threading.RLock()

		self.users = []
		self.channels = []

		self.connected_server = None
		self.socket = None
		self._socket = None
		self._send_timed = False
		self.closing = False

		self.i = util.ObjectDict()
		self.i.done = False
		self.i.auth = False
		self.i.retries = 0

		self.sendq = _sendq()
		self.recvq = _recvq()

		self.servers = []
		for server in bot.options.networks[self.network]['servers']:
			s = server.split(':')
			ssl = False
			host = s[0]
			if len(s) >= 2:
				if s[-1][0] == '+':
					ssl = True
					port = s[-1][1:]
				else:
					port = s[-1]
			else:
				port = 6667

			password = None
			if 'authentication' in bot.options.networks[self.network] \
			and 'server' in bot.options.networks[self.network]['authentication']:
				password = bot.options.networks[self.network]['authentication']['server']

			s = ServerSpec(host, port=port, ssl=ssl, password=password)
			logging.debug(self.logprefix + repr(s))
			self.servers.append(s)

		for n, f in [c for c in inspect.getmembers(self, predicate=inspect.ismethod) if c[0].startswith('mid_')]:
			bot.signal.subscribe('irc::mid::{}'.format(n[4:]), f)

	def connect(self):
		socket.setdefaulttimeout(300)
		for server in self.servers:
			try:
				self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				if server.ssl:
					# so that we have access to the underlying socket still even if we're ssl'd
					logging.debug(self.logprefix + 'SSL enabled, wrapping socket')
					self.socket = ssl.wrap_socket(self._socket)
				else:
					# and do this so that we can always just use self.socket to send/recv
					self.socket = self._socket

				logging.info(self.logprefix + 'Connecting to {}...'.format(str(server)))
				self.socket.connect(server.as_tuple())

				if server.ssl:
					ciph = self.socket.cipher()
					if ciph:
						logging.debug(self.logprefix + 'Cipher: %s (%s/%d-bit).' % ciph)
						self.connected_server = server
						return
					else:
						logging.error(self.logprefix + 'Error connecting securely, trying next server.')
						self.connected_server = None
						continue
				else:
					# just assume we're connected for now
					self.connected_server = server
					return

			except Exception as e:
				logging.error(self.logprefix + 'Exception connecting to server {s}:\n'
				              '{} {}'.format(e.__class__.__name__, str(e), s=str(server)))
				self.connected_server = None
				continue

		if not self.connected_server:
			logging.error(self.logprefix + 'Could not connect to any servers for this network.')

	def _send(self, block=False):
		burst = 5
		delay = 1
		logging.debug(repr(self.sendq))
		if len(self.sendq) is not 0:
			if not self._send_timed and len(self.sendq) <= burst:
				logging.debug(self.logprefix + '_send burst')
				self.socket.send(''.join(self.sendq[:burst]).encode())
				del self.sendq[:burst]
			else:
				logging.debug(self.logprefix + '_send delayed')
				self.socket.send(self.sendq[0].encode())
				del self.sendq[0]

			if len(self.sendq) is not 0:
				# call back in `delay` seconds to send the rest
				self._send_timed = True
				if block:
					logging.debug(self.logprefix + '_send blocking to send')
					self._send(block=True)
				else:
					logging.debug(self.logprefix + '_send setting callback')
					bot.timer.execute_delayed(delay, self._send)
			else:
				logging.debug(self.logprefix + '_send done')
				self._send_timed = False
		else:
			logging.debug(self.logprefix + '_send no send queue')
			self._send_timed = False

	def _recv(self, nbytes):
		buf = []
		while True:
			data = self.socket.recv(nbytes)
			if not data:
				logging.debug(self.logprefix + '_recv no data')
				break
			if data.endswith(self.termop):
				with self.mutex:
					if buf:
						self.recvq.append(b''.join(buf + [data]).decode('utf-8'))
					else:
						self.recvq.append(data.decode('utf-8'))
				return True
			else:
				buf.append(data)
		del buf[:]

	def parse(self, line):
		message = IrcMessage()
		if line.startswith(':'):
			if ' :' in line:
				args, trailing = line[1:].split(' :', 1)
				args = args.split()
			else:
				args = line[1:].split()
				trailing = args[-1]

			# get message source
			if '@' in args[0]:
				user = abstract.User.from_irc_usermask(args[0].lower())
				has = None
				for u in self.users:
					if u.nick.lower() == user.nick.lower():
						has = u
						break
				if has:
					message.source = has
				else:
					message.source = user
					self.users.append(user)
			else:
				message.source = args[0]

			# get message target
			if len(args) >= 3:
				if args[2].startswith('#'):
					channel = abstract.Channel(args[2].lower())
					has = None
					for c in self.channels:
						if c.name.lower() == channel.name.lower():
							has = c
							break
					if has:
						message.target = has
					else:
						message.target = channel
						self.channels.append(channel)

					if isinstance(message.source, abstract.User) and message.source.nick.lower() not in [u[0].nick.lower() for u in message.target.users]:
						message.target.users.append((message.source, []))
				else:
					message.target = args[2]

			if len(args) >= 4:
				message.misc = args[3:]

			message.mid = args[1]
			message.trailing = trailing

			if message.mid == '001':
				# take this as our server name
				self.i.host = message.source

			# ident if nick taken/unavailable or we haven't already
			if message.mid in ['433', '437'] or not self.i.done:
				self.i.done = False
				self.ident()

			# set +B and do the nickserv auth if we get a MOTD end/missing
			if message.mid in ['376', '422']:
				logging.debug(self.logprefix + 'mid is {}, authenticating'.format(str(message.mid)))
				self.authenticate()

			bot.signal('irc::mid::{}'.format(message.mid.lower()), message)

		else:
			arg = line.split(" :")[0]
			message = line.split(" :", 1)[1]

			if arg == "PING":
				self.sendq(['PONG'], message)

	def ident(self):
		if not self.i.done:
			with self.mutex:
				self.i.done = True
				logging.debug(self.logprefix + 'ident() try ' + str(self.i.retries))
				self.nick = bot.options.networks[self.network]['nick'] + '_' * self.i.retries
				if self.connected_server.password:
					self.sendq(['PASS', self.connected_server.password])
				self.sendq(['NICK', self.nick])
				self.sendq(['USER', self.nick, self.nick, self.nick], bot.options.owner.nick)
				self.i.retries += 1

	def authenticate(self):
		if not self.i.auth:
			with self.mutex:
				self.i.auth = True
				logging.debug(self.logprefix + 'authenticate()')
				self.sendq(['MODE', self.nick], '+B')
				if 'authentication' in bot.options.networks[self.network] \
				and 'nickserv' in bot.options.networks[self.network]['authentication']:
					self.sendq(['PRIVMSG', 'NickServ'], 'IDENTIFY {}'.format(
					           bot.options.networks[self.network]['authentication']['nickserv']))

				# we should join channels here
				for c in bot.options.networks[self.network]['channels']:
					self.sendq(['JOIN', c])

	def parse_modes(self, mode_string, unary_modes="bklvohqa"):
		'''\
		Given an IRC mode string, return a list of triplets with the mode
		changed, whether it's being set or cleared, and the target of the
		change:

		>>> parse_modes('+ao-v akiaki akiaki akiaki')
		[('+', 'a', 'akiaki'), ('+', 'o', 'akiaki'), ('-', 'v', 'akiaki')]

		'''

		# mode_string must be non-empty and begin with a sign
		if not mode_string or not mode_string[0] in '+-':
			return []

		modes = []
		parts = mode_string.split()
		mode_part, args = parts[0], parts[1:]

		for ch in mode_part:
			if ch in "+-":
				sign = ch
				continue
			arg = args.pop(0) if ch in unary_modes and args else None
			modes.append((sign, ch, arg))
		return modes

	def mid_join(self, message):
		assert isinstance(message, IrcMessage)

		with self.mutex:
			logging.debug(self.logprefix + '\x1b[1mJOIN\x1b[0m')
			if message.source.nick == self.nick:
				self.sendq(['WHO', message.trailing])
				#self.sendq(['PRIVMSG', message.trailing], repr(bot.threads))
				self._send()
				c = abstract.Channel(message.trailing)
				if not c in self.channels:
					self.channels.append(c)
			else:
				if isinstance(message.target, abstract.Channel):
					if not message.source in message.target.users:
						message.target.users.append((message.source, []))
					if not message.source in self.users:
						self.users.append(message.source)

	def mid_352(self, message):
		assert isinstance(message, IrcMessage)

		with self.mutex:
			# response to WHO
			channel = message.misc[0]
			try:
				achannel = [c for c in self.channels if c.name.lower() == channel.lower()][0]
			except:
				# something for a channel we're not in, perhaps from a WHO <user> rather than a WHO <channel>
				# so we might as well just bail
				return

			ident = message.misc[1]
			hostmask = message.misc[2]
			nick = message.misc[4]
			realname = ' '.join(message.trailing.split()[1:])
			try:
				auser = [u for u in self.users if u.nick.lower() == nick.lower()][0]
			except:
				auser = abstract.User(nick, ident, hostmask, realname)
				self.users.append(auser)

			modes = []
			if len(message.misc[5]) > 1:
				for modechar in message.misc[5]:
					# get the user modes for this channel
					if modechar in ['~', '.']:
						modes.append('q')
						modes.append('o')
					elif modechar in ['&', '!']:
						modes.append('a')
						modes.append('o')
					elif modechar == '@':
						modes.append('o')
					elif modechar == '%':
						modes.append('h')
					elif modechar == '+':
						modes.append('v')

			logging.debug(self.logprefix + '\x1b[1mWHO\x1b[0m {} {} {}'.format(repr(achannel), repr(auser), repr(modes)))

			if achannel not in auser.channels:
				auser.channels.append(achannel)

			if auser.nick.lower() in [u[0].nick.lower() for u in achannel.users]:
				for i, _ in enumerate(achannel.users):
					if auser.nick.lower() == achannel.users[i][0].nick.lower():
						achannel.users[i] = (auser, modes)
			else:
				achannel.users.append((auser, modes))

	def mid_nick(self, message):
		assert isinstance(message, IrcMessage)

		with self.mutex:
			if message.mid == "NICK":
				logging.debug(self.logprefix + '\x1b[1mNICK\x1b[0m')
				for u in self.users:
					if message.source == u:
						u.change_nick(message.trailing)
						logging.debug(repr(u))

	def mid_invite(self, message):
		assert isinstance(message, IrcMessage)

		with self.mutex:
			logging.debug(self.logprefix + '\x1b[1mINVITE\x1b[0m')
			if 'invite' in bot.options.networks[self.network] and bot.options.networks[self.network]['invite']:
				logging.info(self.logprefix + 'Joining {} (invited by {})'.format(message.trailing, message.source.nick))
				self.join_channel(message.trailing)
				self.send_message(message.trailing, 'Thanks for inviting me, {}~'.format(message.source.nick))

	def mid_part(self, message):
		assert isinstance(message, IrcMessage)

		with self.mutex:
			logging.debug(self.logprefix + '\x1b[1mPART\x1b[0m')
			if message.source.nick.lower() == self.nick.lower():
				for i, _ in enumerate(self.users):
					if message.target in self.users[i].channels:
						self.users[i].channels.remove(message.target)
				self.channels.remove(message.target)
			for i, _ in enumerate(message.target.users):
				if message.target.users[i][0] == message.source:
					del message.target.users[i]

	def mid_kick(self, message):
		assert isinstance(message, IrcMessage)

		with self.mutex:
			logging.debug(self.logprefix + '\x1b[1mKICK\x1b[0m')
			if message.misc[0].lower() == self.nick.lower():
				logging.info(self.logprefix + 'Kicked from {}, rejoining.'.format(message.target.name))
				bot.timer.execute_delayed(2, self.join_channel, args=(message.target, True))
			else:
				for i, _ in enumerate(message.target.users):
					if message.target.users[i][0].nick.lower() == message.misc[0].lower():
						del message.target.users[i]

	def mid_quit(self, message):
		assert isinstance(message, IrcMessage)

		with self.mutex:
			logging.debug(self.logprefix + '\x1b[1mQUIT\x1b[0m')
			if isinstance(message.source, abstract.User):
				for channel in self.channels:
					for i, _ in enumerate(channel.users):
						if channel.users[i][0].nick.lower() == message.source.nick.lower():
							del channel.users[i]
				for i, _ in enumerate(self.users):
					if self.users[i].nick.lower() == message.source.nick.lower():
						del self.users[i]

	def mid_mode(self, message):
		assert isinstance(message, IrcMessage)

		with self.mutex:
			logging.debug(self.logprefix + '\x1b[1mMODE\x1b[0m')
			if message.misc and isinstance(message.target, abstract.Channel):
				modes = self.parse_modes(" ".join(message.misc), 'qaohv')
				logging.debug(repr(modes))
				changed_users = []
				for mode in modes:
					if not mode[2]:
						logging.debug('Ignoring MODE with no argument')
						continue
					for i, _ in enumerate(message.target.users):
						if message.target.users[i][0].nick.lower() == mode[2].lower():
							if not mode[2].lower() in changed_users:
								changed_users.append(mode[2].lower())
							mlist = message.target.users[i][1]
							if mode[0] == "+":
								mlist.append(mode[1])
							elif mode[0] == "-":
								if mode[1] in mlist:
									mlist.remove(mode[1])
							message.target.users[i] = (message.target.users[i][0], mlist)
							logging.debug(repr(message.target.users[i]))
				for u in changed_users:
					self.sendq(['WHO', u])
				self._send()

	def mid_privmsg(self, message):
		assert isinstance(message, IrcMessage)

		with self.mutex:
			a = info.MessageInformation()
			a.source = message.source
			a.target = message.target
			a.message = message.trailing
			a.network = self.network

			if message.trailing.startswith('\x01') and message.trailing.endswith('\x01'):
				# possible ctcp?
				t = message.trailing[1:-1].split()
				sendto = message.source.nick
				if t[0] == "VERSION":
					self.sendq(['NOTICE', sendto], '\x01VERSION xbot++ v' + xbotpp.__version__ + '\x01')
				elif t[0] == "PING":
					self.sendq(['NOTICE', sendto], '\x01PING '+ ' '.join(t[1:]) + '\x01')

			bot.signal('message', a)

	def disconnect(self, message="Bye~"):
		if self.socket:
			with self.mutex:
				self.sendq(['QUIT'], message)
				self._send(block=True)
				self.socket.shutdown(socket.SHUT_RDWR)
				self.socket.close()
				self.connected_server = None

	def process_once(self):
		if self.connected_server:
			with self.mutex:
				if len(self.sendq) is not 0 and not self._send_timed:
					# don't invoke send if we've got a timed send runnning
					self._send()
				if not self._recv(4096):
					logging.debug(self.logprefix + 'process_once recv failed')
					self.connected_server = None
					return
				for line in self.recvq():
					bot.signal('irc::raw', line)
					self.parse(line)
				return
		else:
			# if we're not connected, connect
			self.connect()
			return

	def send_message(self, target, message):
		if isinstance(target, abstract.Channel):
			target = target.name
		self.sendq(['PRIVMSG', target], message)

	def join_channel(self, channel, force=False):
		with self.mutex:
			if isinstance(channel, abstract.Channel):
				channel = channel.name
			logging.info(self.logprefix + 'join_channel: {}'.format(channel))
			t = False
			for c in self.channels:
				if c.name == channel:
					t = True
			if force or not t:
				self.sendq(['JOIN', channel])
				self._send()

	def leave_channel(self, channel):
		with self.mutex:
			if isinstance(channel, abstract.Channel):
				channel = channel.name
			logging.info(self.logprefix + 'leave_channel: {}'.format(channel))
			self.sendq(['PART', channel])
			self._send()

	def get_channels(self):
		'''\
		Return a list of channels the bot is in as :class:`.Channel` objects.
		'''

		return self.channels
