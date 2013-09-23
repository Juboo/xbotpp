class Nothing:
	'''\
	An empty class.
	'''
	
	pass

class ObjectDict(dict):
	'''\
	A dict that has it's *__getattr__* and *__setattr__* methods act as
	*__getitem__* and *__setitem__*.
	'''

	def __getattr__(self, key):
		return super().__getitem__(key)

	def __setattr__(self, key, value):
		super().__setitem__(key, value)

class CaseInsensitiveDict(dict):
	'''\
	A dict where item keys are converted to lowercase before getting/setting.
	'''

	def __getitem__(self, key):
		return super().__getitem__(key.lower())

	def __setitem__(self, key, value):
		super().__setitem__(key.lower(), value)

class CaseInsensitiveObjectDict(CaseInsensitiveDict):
	'''\
	A dict that has it's *__getattr__* and *__setattr__* methods act as
	*__getitem__* and *__setitem__*. This dict converts item keys to lowercase
	before getting/setting, as it inherits from :class:`.CaseInsensitiveDict`.
	'''

	def __getattr__(self, key):
		return super().__getitem__(key)

	def __setattr__(self, key, value):
		super().__setitem__(key, value)

def time_metric(secs=60):
	"""Returns user-readable string representing given number of seconds."""
	time = ''
	for metric_secs, metric_char in [[7*24*60*60, 'w'], [24*60*60, 'd'], [60*60, 'h'], [60, 'm']]:
		if secs > metric_secs:
			time += '{}{}'.format(int(secs / metric_secs), metric_char)
			secs -= int(secs / metric_secs) * metric_secs
	if secs > 0:
		time += '{}s'.format(secs)
	return time

def metric(num):
	"""Returns user-readable string representing given number."""
	for metric_raise, metric_char in [[9, 'B'], [6, 'M'], [3, 'k']]:
		if num > (10 ** metric_raise):
			return '{:.1f}{}'.format((num / (10 ** metric_raise)), metric_char)
	return str(num)

def pretty_date(time=False):
	"""
	Get a datetime object or a int() Epoch timestamp and return a
	pretty string like 'an hour ago', 'Yesterday', '3 months ago',
	'just now', etc
	"""

	from datetime import datetime
	now = datetime.now()
	if type(time) is int:
		diff = now - datetime.fromtimestamp(time)
	elif isinstance(time,datetime):
		diff = now - time 
	elif not time:
		diff = now - now
	second_diff = diff.seconds
	day_diff = diff.days

	if day_diff < 0:
		return ''

	if day_diff == 0:
		if second_diff < 10:
			return "just now"
		if second_diff < 60:
			return str(int(second_diff)) + " seconds ago"
		if second_diff < 120:
			return  "a minute ago"
		if second_diff < 3600:
			return str(int(second_diff / 60)) + " minutes ago"
		if second_diff < 7200:
			return "an hour ago"
		if second_diff < 86400:
			return str(int(second_diff / 3600)) + " hours ago"
	if day_diff == 1:
		return "Yesterday"
	if day_diff < 7:
		return str(int(day_diff)) + " days ago"
	if day_diff < 31:
		return str(int(day_diff/7)) + " weeks ago"
	if day_diff < 365:
		return str(int(day_diff/30)) + " months ago"
	return str(int(day_diff/365)) + " years ago"

def smart_truncate(content, length=100, suffix='...'):
	return (content if len(content) <= length else content[:length].rsplit(' ', 1)[0]+suffix)
