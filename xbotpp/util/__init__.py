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
