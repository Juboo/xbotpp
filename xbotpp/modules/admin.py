__xbotpp_module__ = "admin"

import xbotpp
from xbotpp import bot
from xbotpp import abstract
from xbotpp import permission
from xbotpp import exceptions

@bot.signal.on_signal('command::reload')
def reload(message, args, buf):
	if message.source.can(permission.AdminPermissionLevel, message):
		if len(args) > 0:
			fail = []
			for modname in args:
				try:
					bot.loadmod(modname)
				except Exception as e:
					fail.append("{} ({}: {})".format(modname, e.__class__.__name__, str(e)))
			successmessage = "Reloaded {} of {} modules.".format((len(args) - len(fail)), len(args))
			if len(fail) is 0:
				return successmessage
			else:
				failmessage = "Failed: {}".format(', '.join(fail))
				return "{} {}".format(successmessage, failmessage)
		else:
			return "Usage: reload <modname> [<modname> [...]] -- [re]load modules"

@bot.signal.on_signal('command::unload')
def unload(message, args, buf):
	if message.source.can(permission.AdminPermissionLevel, message):
		if len(args) > 0:
			fail = []
			for modname in args:
				try:
					bot.unloadmod(modname)
				except Exception as e:
					fail.append("{} ({}: {})".format(modname, e.__class__.__name__, str(e)))
			successmessage = "Unloaded {} of {} modules.".format((len(args) - len(fail)), len(args))
			if len(fail) is 0:
				return successmessage
			else:
				failmessage = "Failed: {}".format(', '.join(fail))
				return "{} {}".format(successmessage, failmessage)
		else:
			return "Usage: unload <modname> [<modname> [...]] -- unload modules"

@bot.signal.on_signal('command::join')
def join(message, args, buf):
	if message.source.can(permission.JoinChannel, message):
		if len(args) > 0:
			bot.connections[message.network].join_channel(args[0])
		else:
			return "Usage: join <channel> -- joins channel"

@bot.signal.on_signal('command::part')
def part(message, args, buf):
	if message.source.can(permission.LeaveChannel, message):
		if isinstance(message.target, abstract.Channel):
			bot.connections[message.network].leave_channel(message.target)
		else:
			return "Not in a channel, lol."

@bot.signal.on_signal('command::eval')
def evalcmd(message, args, buf):
	if message.source.can(permission.AdminPermissionLevel, message):
		if len(args) > 0:
			return repr(eval(' '.join(args), locals(), globals()))
		else:
			return "Usage: eval <expression> -- evaluate expression"

@bot.signal.on_signal('command::prefix')
def prefix(message, args, buf):
	if message.source.can(permission.AdminPermissionLevel, message):
		if len(args) > 0:
			old = bot.config.prefix
			bot.config.prefix = args[0]
			return "Prefix is now {} (was {})".format(args[0], old)
		else:
			return "Usage: prefix <new prefix> -- changes bot prefix character"

@bot.signal.on_signal('command::rehash')
def rehash(message, args, buf):
	if message.source.can(permission.AdminPermissionLevel, message):
		bot._load_config()
		return "Done."
