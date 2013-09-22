# Base exception
class XbotppException(Exception):
	'''\
	Base xbot++ exception. All exceptions in xbot++ are sublclasses of this
	exception.
	'''

	pass

class InvalidProtocol(XbotppException):
	'''\
	A protocol library that was specified was invalid or did not inherit from
	:class:`protocol.base.BaseProtocol`.
	'''

# Event exceptions
class EventException(XbotppException):
	'''\
	Raised when an error has occurred during an event handler.
	'''

	pass

class DuplicateSubscriber(EventException):
	'''\
	Raised when a specified callable has already been subscribed to a signal.
	'''

	pass

# Permission exceptions
class UserNotAuthorized(XbotppException):
	'''\
	Raised when a given user does not have the necessary permission to perform
	an action.
	'''
	
	pass
