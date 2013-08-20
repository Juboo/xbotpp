'''\
Internal xbot++ exceptions.
'''

class XbotppException(Exception):
    '''\
    Base xbot++ exception.
    '''

    pass

class ModuleNotLoaded(XbotppException):
    pass

class ModuleLoadingException(XbotppException):
    pass

class DependencyException(XbotppException):
    pass
