__xbotpp_module__ = "markov"

import random
import threading
import xbotpp.debug
import xbotpp.modules

def _on_load():
	if not 'chain' in xbotpp.state.modules.moddata['markov']:
		xbotpp.state.modules.moddata['markov']['chain'] = {}
	if not 'prob' in xbotpp.state.modules.moddata['markov']:
		xbotpp.state.modules.moddata['markov']['prob'] = {}

def ret_chain(length):
	ret = random.choice(list(xbotpp.state.modules.moddata['markov']['chain'].keys())).split()
	try:
		while len(ret) < length:
			ret.append(random.choice(xbotpp.state.modules.moddata['markov']['chain'][' '.join(ret[len(ret) - 2 : len(ret)])]))
	except:
		pass

	return ' '.join([s.strip() for s in ret])

def feed(text):
	count = 0
	stext = [s.strip() for s in text.split()]
	if len(stext) == 0:
		return 0
	
	global threadchain
	chain = threadchain

	for i, e in enumerate(stext):
		try:
			index = '{0} {1}'.format(stext[i], stext[i+1])
			xbotpp.debug.write('Feed: index {}'.format(repr(index)))
			if not index in chain:
				xbotpp.debug.write("Feed: index didn't already exist")
				chain[index] = []
			if not stext[i+2] in chain[index]:
				count += 1
				xbotpp.debug.write("Feed: [{}].append({})".format(repr(index), repr(stext[i+2])))
				chain[index].append(stext[i+2])

		except Exception as ex:
			xbotpp.debug.exception("i={}, e={}".format(str(i), e), ex)

	threadchain = chain
	return count

def feed_thread(text):
	global thread
	global threadchain
	threadchain = xbotpp.state.modules.moddata['markov']['chain']
	thread = threading.Thread(target=feed, kwargs={'text': text})
	thread.start()

	def check_thread():
		global thread
		global threadchain
		global threadstatuschannel
		if not thread.is_alive():
			xbotpp.state.modules.moddata['markov']['chain'] = threadchain
			if threadstatuschannel:
				xbotpp.state.connection.send_message(threadstatuschannel, "Markov feeding complete.")
		else:
			xbotpp.state.connection.connection.execute_delayed(1, check_thread)

	# TODO: IRC specific until we implement our own timing
	xbotpp.state.connection.connection.execute_delayed(1, check_thread)

@xbotpp.modules.on_event('message')
def feed_on_message(event):
	try:
		global threadstatuschannel
		threadstatuschannel = None
		feed_thread(event.message)
	except:
		pass

	target = event.source if event.type == 'privmsg' or event.type == 'privnotice' else event.target
	if target in xbotpp.state.modules.moddata['markov']['prob']:
		p = float(xbotpp.state.modules.moddata['markov']['prob'][target])
		xbotpp.debug.write('Probability for {}: {}'.format(target, str(p)))
		if random.random() <= p:
			xbotpp.state.connection.send_message(target, ret_chain(random.randint(5, 20)))
	else:
		xbotpp.debug.write('Target {} has no probability value, setting it to 0'.format(target))
		t = xbotpp.state.modules.moddata['markov']['prob']
		t[target] = 0.00
		xbotpp.state.modules.moddata['markov']['prob'] = t

@xbotpp.modules.on_command('markov-feed', 1)
def command_feed(info, args, buf):
	try:
		with open(" ".join(args), 'r') as f:
			global threadstatuschannel
			threadstatuschannel = info.target
			feed_thread(f.read())
			return "Started feeding."
	except:
		return "Can't feed chain."

@xbotpp.modules.on_command('markov-prob', 1)
def set_prob(info, args, buf):
	if len(args) == 1:
		target = info['target']
		prob = float(args[0])
	elif len(args) == 2:
		target = args[0]
		prob = float(args[1])
	else:
		return "Usage: [channel] <probability>"
	
	t = xbotpp.state.modules.moddata['markov']['prob']
	t[target] = prob
	xbotpp.state.modules.moddata['markov']['prob'] = t
	return "Probabitity for {} set to {}.".format(target, str(prob))

@xbotpp.modules.on_command('markov-reset', 1)
def reset(info, args, buf):
	xbotpp.state.modules.moddata['markov']['chain'] = {}
	return 'Done.'

@xbotpp.modules.on_command('markov')
def say(info, args, buf):
	if len(args) == 1 and args[0] == "count":
		chain = xbotpp.state.modules.moddata['markov']['chain']
		count = len(chain)
		for index in chain:
			count += len(chain[index])
		return "There are {} entries.".format(str(count))
	elif len(args) == 1:
		return ret_chain(int(args[0]))
	else:
		return ret_chain(random.randint(5, 20))

