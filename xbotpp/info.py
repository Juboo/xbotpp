class Admin:
	'''\
	A class that describes a bot administrator.
	'''

	def __init__(self, nick=None, ident=None, hostname=None, realname=None, owner=False):
		self.nick = nick
		self.ident = ident
		self.hostname = hostname
		self.realname = realname
		self.is_owner = owner

	def __repr__(self):
		# i'm stupid

		l = []
		for attr in ['nick', 'ident', 'hostname', 'realname']:
			if hasattr(self, attr):
				l.append(attr + '=' + repr(getattr(self, attr, None)))
		return "{}({})".format(self.__class__.__name__, ', '.join(l))

	def compare(self, user):
		'''\
		Returns True if the user information in `user` matches this admin.
		'''

		to_check = []
		for attr in ['nick', 'ident', 'hostname', 'realname']:
			if getattr(self, attr) != None:
				to_check.append(attr)

		status = True
		for attr in to_check:
			try: 
				if getattr(self, attr) != getattr(user, attr):
					status = False
					break
			except (NameError, ValueError):
				status = False
				break

		return status

class MessageInformation:
	def __init__(self, source=None, target=None, message=None, network=None):
		self.source = source
		self.target = target
		self.message = message
		self.network = network

	def __repr__(self):
		# i'm stupid

		l = []
		for attr in ['source', 'target', 'message', 'network']:
			if hasattr(self, attr):
				l.append(attr + '=' + repr(getattr(self, attr, None)))
		return "{}({})".format(self.__class__.__name__, ', '.join(l))
