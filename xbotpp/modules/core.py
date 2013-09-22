__xbotpp_module__ = "core"

import xbotpp
from xbotpp import bot

@bot.signal.on_signal('command::info')
def info(message, args, buf):
	data = {
		'version': xbotpp.__version__,
		'channels': sum([len(bot.connections[c].get_channels()) for c in bot.connections]),
		'networks': len(bot.connections),
		'modules': len(bot.modules),
	}

	lol = "I'm xbot++ v{version}. I'm on {channels} channels across {networks} networks. I have {modules} modules loaded."
	return lol.format(**data)

@bot.signal.on_signal('command::list')
def list(message, args, buf):
	commandlist = []
	for signal in bot.signal.subscribers:
		if signal.startswith('command::'):
			commandlist.append(signal.split('::')[-1])
	return "Available commands: {}".format(', '.join(commandlist))

@bot.signal.on_signal('command::help')
def help(message, args, buf):
	return "Hi! Use {p}list to get a list of commands I can perform!".format(p=bot.options.prefix)

@bot.signal.on_signal('command::say')
def say(message, args, buf):
	if len(args) > 0:
		return ' '.join(args)
	else:
		return "Usage: say <herp>"
