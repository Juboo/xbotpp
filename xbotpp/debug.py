# vim: noai:ts=4:sw=4:expandtab:syntax=python

import sys
import collections
from datetime import datetime


'''Various debugging information functions.'''

print_flagged = False
'''Whether or not to print lines with 'flagged' DebugLevels.'''

silence = False
'''A 'shut the hell up' flag.'''

class DebugLevel(object):
    '''\
    A debug information level.

    :param str name: The name of this debug level.
    :param str prefix: The prefix to print before the debug information.
    :param bool flagged: Whether er not the information in this level should\
    be hidden by default (ie. only shown when :py:data:`xbotpp.debug.print_flagged`\
    is True)
    '''

    def __init__(self, name, prefix, flagged):
        self.name = name
        '''The name of this debug level.'''
     
        self.prefix = prefix
        '''The prefix to print before the debug information.'''

        self.flagged = flagged
        '''\
        Whether or not the information in this level should be hidden by default
        (ie. only shown when :py:data:`xbotpp.debug.print_flagged` is True)
        '''

    def __repr__(self):
        s = '''DebugLevel(name='{name}', prefix='{prefix}', flagged={flagged})'''
        f = {'name': self.name, 'prefix': self.prefix, 'flagged': self.flagged}
        return s.format(**f)

class levels:
    '''Debug levels for write().'''

    Error = DebugLevel('Error', prefix='EE', flagged=False) 
    Warn = DebugLevel('Warn', prefix='!!', flagged=False)
    Info = DebugLevel('Info', prefix='II', flagged=False)
    Debug = DebugLevel('Debug', prefix='DD', flagged=True)

def write(message, level=levels.Debug):
    '''Write a debug message to stderr, with the given DebugLevel.'''

    if silence:
        return

    if not isinstance(level, DebugLevel):
        write('''debug.write() got level of %s, expected <class 'debug.DebugLevel'>''' % type(level), levels.Error)
        return

    if level.flagged and not print_flagged:
        return

    time = str(datetime.time(datetime.now()))
    realpad = "[{0}] [{1}]".format(time, level.prefix)

    for index, line in enumerate(message.split('\n')):
        if index is 0:
            pad = realpad
        else:
            pad = ' ' * (len(realpad))
        print("%s %s" % (pad, line.strip()), file=sys.stderr)

def exception(message, exception, level=levels.Error):
    '''\
    Wrapper to write() to make it easier to print exception info.

        >>> import xbotpp.debug
        >>> try:
        ...     t = open('non_existant_file', 'r')
        ... except Exception as e:
        ...     xbotpp.debug.exception('Exception while trying to open file.', e)
        ...
        [EE] An exception occurred!
             Message: Exception while trying to open file.
             Exception: [IOError] [Errno 2] No such file or directory: 'non_existant_file'

    You can also specify a DebugLevel, for if the exception you want to handle
    is non-critical, or you have custom debugging levels.
    '''

    text = '''\
    An exception occurred!
    Message: {0}
    Exception: [{1}] {2}'''

    text = text.format(message, exception.__class__.__name__, exception)
    write(text, level)

def permanent_silence():
    '''\
    Stop debug routines from printing ANYTHING.
    '''

    global silence
    silence = True
