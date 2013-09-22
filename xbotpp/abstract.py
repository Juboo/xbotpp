import inspect

from .exceptions import *
from .permission import *
from .info import *

class Channel:
	'''\
	A channel.
	'''

	def __init__(self, name):
		self.name = name
		'''Name of the channel.'''

		self.users = []
		'''\
		List of tuples of the format ``(user, rank)``.

		*user* in this tuple is a :class:`.User` object.

		*rank* in this tuple is a list with the following possible values:

		- 'o': user is a channel operator.
		- 'v': user is voiced in the channel.
		'''

	def __eq__(self, other):
		return repr(self) == repr(other)

	def __repr__(self):
		return 'Channel({})'.format(repr(self.name))

class User:
	'''\
	A user.
	'''

	def __init__(self, nick, ident="", hostname="", realname=""):
		self.nick = nick
		'''User nickname/username.'''

		self.ident = ident
		'''Ident string. Typically the same as the nickname.'''

		self.hostname = hostname
		'''Hostname the user is connecting from.'''

		self.realname = realname
		'''User's real name as specified by the protocol.'''

		self.previous_nicks = []
		'''A list of the previous nicks the user has used.'''

		self.channels = []
		'''A list of :class:`.Channel` objects that the user is in.'''

	def __eq__(self, other):
		return repr(self) == repr(other)

	def __repr__(self):
		# i'm stupid

		l = []
		for attr in ['nick', 'ident', 'hostname', 'realname']:
			if hasattr(self, attr):
				l.append(attr + '=' + repr(getattr(self, attr, None)))
		return "{}({})".format(self.__class__.__name__, ', '.join(l))

	@classmethod
	def from_irc_usermask(cls, mask):
		'''\
		Return a User from an IRC usermask string.

		>>> User.from_irc_usermask('akiaki!~aki@shizune.aki.pw')
		User(nick='akiaki', ident='~aki', hostname='shizune.aki.pw')
		'''

		_nick = mask.split('!')[0]
		_ident = mask.split('!')[1].split('@')[0]
		_host = mask.split('@')[1]

		return cls(_nick, ident=_ident, hostname=_host)

	def change_nick(self, nick):
		'''\
		Change the user's nick, and append their previous nick to 
		:attr:`.previous_nicks`, if it wasn't in that list already.
		'''

		if not self.nick in self.previous_nicks:
			self.previous_nicks.append(self.nick)
		self.nick = nick

	def can(self, permission, message):
		'''\
		Determines whether a user satisfies the requirements of the
		:class:`.PermissionLevel` `permission`, based on the information
		about the message this request arose from in `message`.

		`permission` is a :class:`.PermissionLevel` object, and `message` is
		an :class:`.MessageInformation` object. This function will raise an
		:exc:`AssertionError` if the parameters are not valid. Returns 
		`True` if the user satisfies the permission, or raises an 
		:exc:`.UserNotAuthorized` exception if the user does not satisfy the
		given permission.
		'''

		# make sure we have a PermissionLevel object...
		assert PermissionLevel in inspect.getmro(permission)
		# ...and that we have an ActionInformation object too
		assert MessageInformation in inspect.getmro(message.__class__)

		if len(permission.requires) is 0:
			return True

		satisfies = []

		from xbotpp import bot
		for admin in bot.options.admins:
			if admin.compare(self):
				satisfies.append('botadmin')

		if isinstance(message.target, Channel):
			for channel in self.channels:
				if message.target == channel:
					# action happened in a channel that user was in
					for u in channel.users:
						if u[0] == self:
							if 'o' in u[1]:
								satisfies.append('channelop')
							if 'v' in u[1]:
								satisfies.append('channelvoice')

		for req in permission.requires:
			if req in satisfies:
				# if we satisfy at least one of the permission requires, return
				return True

		# if we get here, we haven't satisfied any requirements of the
		# permission, so raise a UserNotAuthorized
		raise UserNotAuthorized(permission)
