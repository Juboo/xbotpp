# vim: noai:ts=4:sw=4:expandtab:syntax=python

import sys
import collections


'''Various debugging information functions.'''

print_flagged = False
'''Whether or not to print lines with 'flagged' DebugLevels.'''

class levels:
    '''Debug levels for write().'''

    DebugLevel = collections.namedtuple('DebugLevel', ['prefix', 'flagged'])
    Error = DebugLevel(prefix='EE', flagged=False) 
    Warn = DebugLevel(prefix='!!', flagged=False)
    Info = DebugLevel(prefix='II', flagged=False)
    Debug = DebugLevel(prefix='DD', flagged=True)

def write(message, level=levels.Debug):
    '''Write a debug message to stderr, with the given DebugLevel.'''

    if not isinstance(level, levels.DebugLevel):
        write('''debug.write() got level of %s, expected <class 'debug.DebugLevel'>''' % type(level), levels.Error)
        return

    if level.flagged and not print_flagged:
        return

    for index, line in enumerate(message.split('\n')):
        if index is 0:
            pad = '[' + level.prefix + ']'
        else:
            pad = ' ' * (len(level.prefix) + 2)
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
