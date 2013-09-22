__xbotpp_module__ = "fun"

import random
from xbotpp import bot

@bot.signal.on_signal('command::choose')
def choose(message, args, buf):
	args_ = list(set(' '.join([arg.lower() if arg.lower() == 'or' else arg for arg in args]).split(' or ')))
	args__ = list(set([arg.lower() for arg in args_]))
	if len(args_) > 1 and len(args_) == len(args__):
		ans = random.choice([
			'Defs', 'Totes', 'I reckon', 'Why not', 'I like *', 'DEFINITELY',
			'Without a doubt', 'Always', 'A must-choose: *', 'You could ^',
			'I recommend *', 'Perhaps', 'Blimey,', 'How about *', 'HAHA,',
			'I say', 'Something tells me', 'Try *', 'Go with *', 'I highly recommend *'
		])
		choice = random.choice(args_)
		intermediary = "choose " if random.random() > 0.5 else ''
		if '*' in ans:
			intermediary = ''
			ans = ans[:-2]
		elif '^' in ans:
			intermediary = "choose "
			ans = ans[:-2]
		if choice.endswith("?") and len(choice) > 1:
			choice = choice[:-1]
		return "%s %s%s." % (ans, intermediary, choice)
	else:
		return "Usage: choose <item 1> or <item 2> [or <item n>] where 1 != 2 != n"

@bot.signal.on_signal('command::8ball')
def m8b(message, args, buf):
	if len(args) > 0:
		responses = [
			"It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Signs point to yes.", "Yes.",
			"Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
			"Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."
		]
		return random.choice(responses)
	else:
		return "Usage: 8ball <herp>"

@bot.signal.on_signal('command::spin')
def spin(message, args, buf):
	try:
		nicks = [c[0].nick for c in [n for n in bot.connections[message.network].channels if n == message.target][0].users]
	except:
		return "Triggering this command privately is not allowed."

	if len(nicks) > 2:
		thing = ' '.join(args).strip()
		if not thing:
			thing = "nothing"
		if thing.lower() != bot.connections[message.network].nick.lower():
			_nicks = list(nicks)
			_nicks.remove(message.source.nick)
			_nicks.remove(bot.connections[message.network].nick)
			winner = random.choice(_nicks)
			return "The winner of %s is %s. Congratulations %s!" % (thing, winner, winner)
		else:
			return "You want to spin me? Ok. Wheeeeeeee~"
	else:
		return "Not enough winrars!"

@bot.signal.on_signal('command::dongs')
def dongs(message, args, buf):
	d = '''\
	           _ 
	          /\) _   
	     _   / / (/\  
	    /\) ( Y)  \ \ 
	   / /   ""   (Y )
	  ( Y)  _      "" 
	   ""  (/\       _  
	        \ \     /\)
	        (Y )   / / 
	         ""   ( Y) 
	               ""'''
	return d

@bot.signal.on_signal('message')
def buttify(message):
	# 0.05% chance of a butt-in in enabled channels
	b = '{}:{}'.format(message.network, message.target.name)
	if 'fun' in bot.options.modules and 'buttify_channels' in bot.options.modules['fun'] and b in bot.options.modules['fun']['buttify_channels']:
		if random.random() < 0.005:
			if not message.message.startswith("\x01"):
				words = message.message.split()
				if len(words) > 2:
					for n in range(random.randint(1, 3)):
						if random.random() > 0.5:
							words[random.randint(1, len(words)-1)] = "butt"
						else:
							for m, word in enumerate(words):
								if len(word) > 4 and m > 0:
									if random.random() > 0.3:
										words[m] = words[m][:-4] + "butt"

					bot.connections[message.network].send_message(message.target, ' '.join(words))
