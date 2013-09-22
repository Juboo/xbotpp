from .exceptions import *
from . import logging
import threading
import inspect

class SignalManager:
	all_signals = '__all_signals__'
	'''\
	Subscribers to this signal are called every time any other signal is sent.

	Subscribers should have a signature of ``name(signal, *args, **kwargs)``.

	Example:

	>>> a = SignalManager()
	>>> @a.on_signal(a.all_signals)
	... def everything(signal, *args, **kwargs):
	... 	print(signal, repr(args), repr(kwargs))
	... 
	>>> a('test::1', param=1)
	test::1 () {'param': 1}
	>>> a('test::2', param=1)
	test::2 () {'param': 1}
	'''

	def __init__(self):
		# This is a dictionary of the callable objects subscribed to each signal.
		# Keys in this dictionary are the signal name (or * for 'all signals'), and
		# the value of each key is a list of callables that are subscribed to the
		# signal.
		self.subscribers = {}
		self.mutex = threading.RLock()

	def subscribe(self, signal, f):
		'''\
		Subscribe the callable `f` to the signal `signal`.

		Raises :exc:`.DuplicateSubscriber` if `f` is already subscribed to the
		specified signal.
		'''

		if signal not in self.subscribers:
			with self.mutex:
				self.subscribers[signal] = []

		if f not in self.subscribers[signal]:
			with self.mutex:
				logging.debug('Signal {0} += {1}'.format(repr(signal), repr(f)))
				self.subscribers[signal].append(f)
		else:
			raise DuplicateSubscriber(f)

	def on_signal(self, signal):
		'''\
		Function decorator for subscribing to a signal.
		'''

		def decorator(f):
			self.subscribe(signal, f)
			return f
		return decorator

	def remove_module(self, module):
		'''\
		Removes all signal callbacks belonging to the module 'module'.

		Returns the number of callbacks removed.
		'''

		logging.info('Removing signal callbacks from module {}'.format(repr(module)))

		count = 0
		with self.mutex:
			for signal in self.subscribers:
				for i, _ in enumerate(self.subscribers[signal]):
					if inspect.getmodule(self.subscribers[signal][i]) == module:
						count += 1
						del self.subscribers[signal][i]
		return count

	def send_to_first(self, signal, *args, **kwargs):
		'''\
		Call the first callable for the signal `signal`.
		'''

		logging.debug('Signal (first): {} {} {}'.format(repr(signal), repr(args), repr(kwargs)))

		if self.all_signals in self.subscribers:
			for f in self.subscribers[self.all_signals]:
				f(*args, **kwargs)

		if signal in self.subscribers and len(self.subscribers[signal]) > 0:
			return self.subscribers[signal][0](*args, **kwargs)
		else:
			raise EventException('Signal {} does not exist.'.format(repr(signal)))

	def send(self, signal, *args, **kwargs):
		'''\
		Call all the registered callables for the signal `signal`.

		This function is also available by calling the SignalManager directly:

		>>> a = SignalManager()
		>>> @a.on_signal('test')
		... def test(*args, **kwargs):
		...     print('test', repr(args), repr(kwargs))
		... 
		>>> a('test', param=1)
		test () {'param': 1}
		>>> a.send('test', param=2)
		test () {'param': 2}
		'''

		logging.debug('Signal: {} {} {}'.format(repr(signal), repr(args), repr(kwargs)))

		if signal in self.subscribers:
			for f in self.subscribers[signal]:
				f(*args, **kwargs)

		if self.all_signals in self.subscribers:
			for f in self.subscribers[self.all_signals]:
				f(signal, *args, **kwargs)

	__call__ = send
