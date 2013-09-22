class PermissionLevel:
	'''\
	A permission level.
	'''

	requires = []
	'''\
	A list of criteria for satisfying this permission level.

	The possible options are:
	
	- `channelop`:
	  having Operator status in the channel the command requesting permission
	  is in (if the permission request originated from a command in a channel
	  the bot is in).

	- `channelvoice`:
	  having voice in the channel the command requesting permission is in (if
	  the permission request originated from a command in a channel the bot is
	  in).

	- `botadmin`:
	  being a bot administrator.

	An empty `requires` list means that no requirements are needed for this
	permission level to be satisfied, and as such any requests for permission
	at this level will always return True.
	'''

# Generic permission levels

class AdminPermissionLevel(PermissionLevel):
	'''\
	A generic permission level that requires being a bot administrator.
	'''

	requires = ['botadmin']

class ChannelOpPermissionLevel(PermissionLevel):
	'''\
	A generic permission level that requires either of:
	
	- Being an operator in the channel the action originated in
	- Being a bot administrator
	'''

	requires = ['botadmin', 'channelop']

class ChannelVoicePermissionLevel(PermissionLevel):
	'''\
	A generic permission level that requires one of:

	- Being voiced in the channel the action originated in
	- Being an operator in the channel the action originated in
	- Being a bot administrator
	'''

	requires = ['botadmin', 'channelop', 'channelvoice']

# Channel permissions

class JoinChannel(AdminPermissionLevel):
	pass

class LeaveChannel(ChannelOpPermissionLevel):
	pass

class ToggleBotChannelVoice(ChannelOpPermissionLevel):
	'''\
	Permission to toggle whether or not the bot can speak in a given channel.
	'''

	pass

class ToggleBotVoice(AdminPermissionLevel):
	'''\
	Permission to toggle whether the bot can speak.
	'''
	
	pass

# Bot configuration permissions

class ChangeBotNick(AdminPermissionLevel):
	pass

class ReloadConfig(AdminPermissionLevel):
	pass