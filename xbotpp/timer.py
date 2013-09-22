import datetime
import numbers
import threading
import functools
import bisect

from . import bot

class TimerManager:
	'''\
	Timer manager class.
	'''

	def __init__(self):
		self.mutex = threading.RLock()
		self.delayed_commands = []

	def _schedule_command(self, command):
		with self.mutex:
			bisect.insort(self.delayed_commands, command)
			if bot:
				bot.signal('bot::scheduled', command.delay.total_seconds())

	def check(self):
		'''\
		Check if any of our delayed commands need to be run.

		Usually called from :meth:`.Bot.process_once`.
		'''

		with self.mutex:
			while self.delayed_commands:
				command = self.delayed_commands[0]
				if not command.due():
					break
				command.function()
				if isinstance(command, PeriodicCommand):
					self._schedule_command(command.next())
				del self.delayed_commands[0]

	def execute_at(self, at, function, args=(), kwargs={}):
		'''
		Execute a function at a specified time.
		'''

		function = functools.partial(function, *args, **kwargs)
		self._schedule_command(DelayedCommand.at_time(at, function))

	def execute_delayed(self, delay, function, args=(), kwargs={}):
		'''
		Execute a function after a specified time.
		'''

		function = functools.partial(function, *args, **kwargs)
		self._schedule_command(DelayedCommand.after(delay, function))

	def execute_every(self, period, function, args=(), kwargs={}):
		'''
		Execute a function every `period` seconds.
		'''

		function = functools.partial(function, *args, **kwargs)
		self._schedule_command(PeriodicCommand.after(period, function))

class DelayedCommand(datetime.datetime):
	'''
	A command to be executed after some delay (seconds or timedelta).

	Clients may override .now() to have dates interpreted in a different
	manner, such as to use UTC or to have timezone-aware times.
	'''

	@classmethod
	def now(cls, tzinfo=None):
		return datetime.datetime.now(tzinfo)

	@classmethod
	def from_datetime(cls, other):
		return cls(other.year, other.month, other.day, other.hour,
			other.minute, other.second, other.microsecond,
			other.tzinfo)

	@classmethod
	def after(cls, delay, function):
		if not isinstance(delay, datetime.timedelta):
			delay = datetime.timedelta(seconds=delay)

		due_time = cls.now() + delay
		cmd = cls.from_datetime(due_time)
		cmd.delay = delay
		cmd.function = function
		return cmd

	@classmethod
	def at_time(cls, at, function):
		'''
		Construct a DelayedCommand to come due at `at`, where `at` may be
		a datetime or timestamp. If `at` is a real number, it will be
		interpreted as a naive local timestamp.
		'''

		if isinstance(at, numbers.Real):
			at = datetime.datetime.fromtimestamp(at)

		cmd = cls.from_datetime(at)
		cmd.delay = at - cmd.now()
		cmd.function = function
		return cmd

	def due(self):
		return self.now() >= self

class PeriodicCommand(DelayedCommand):
	'''
	Like a delayed command, but expect this command to run every delay
	seconds.
	'''

	def next(self):
		cmd = self.__class__.from_datetime(self + self.delay)
		cmd.delay = self.delay
		cmd.function = self.function
		return cmd

	def __setattr__(self, key, value):
		if key == 'delay' and not value > datetime.timedelta():
			raise ValueError('A PeriodicCommand must have a positive, non-zero delay.')
		super(PeriodicCommand, self).__setattr__(key, value)
