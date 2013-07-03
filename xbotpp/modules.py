# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import imp
import json
import shlex
import inspect
import importlib

import xbotpp
from xbotpp import util
from xbotpp import debug
from xbotpp import handler


def on_event(event):
    '''\
    Function constructor for event handlers.

    >>> @xbotpp.modules.on_event('message')
    ... def message_handler(event):
    ...     print(repr(event))
    
    See the :ref:`event_classes` documentation for what the `event` parameter
    will contain for each event.

    After this constructor has been used, the function will have it's SID and
    the event that it is handling set as attributes:

    >>> getattr(message_handler, '__xbotpp_event__', None)
    'message'
    >>> getattr(message_handler, '__xbotpp_sid__', None)
    'Sd72Hbo72X'

    '''

    def constructor(r):
        # get this event handler's parent module
        parent = inspect.getmodule(r).__xbotpp_module__

        # check if we're running on an already-SID'd object
        if getattr(r, '__xbotpp_event__', None) != None:
            # we've already been run on this object, so die
            debug.write("on_event: Already been called on SID {}".format(getattr(r, '__xbotpp_event__', None)))
            return r

        # compare __name__ against parent module's existing event handlers
        # going on the assumption the module won't have two identically
        # named event handlers - which is a sane assumption to make...
        if parent in xbotpp.state['modules_monitor'].loaded:
            for function in xbotpp.state['modules_monitor'].loaded[parent]['events']:
                if xbotpp.state['modules_monitor'].loaded[parent]['events'][function][0] == getattr(r, '__name__', None):
                    # we're the same, so bail
                    sa = "on_event: Already been called on handler with name {0} from module {1}."
                    debug.write(sa.format(getattr(r, '__name__', None), parent))
                    return r

        # assign event attribute
        setattr(r, '__xbotpp_event__', event)

        # and the SID
        sid = util.random_string()
        setattr(r, '__xbotpp_sid__', sid)

        # give it to the handler dispatch list
        handler.handlers.bind_event(event, r)

        # and put it in it's parent module table
        if parent not in xbotpp.state['modules_monitor'].loaded:
            xbotpp.state['modules_monitor'].create_table(parent)
        xbotpp.state['modules_monitor'].loaded[parent]['events'][sid] = (getattr(r, '__name__', None), r)

        return r

    return constructor

def on_command(command, privlevel=0):
    '''\
    Function constructor for command handlers.

    >>> @xbotpp.modules.on_command('test')
    ... def test_command_handler(info, args, buf):
    ...     return 'Called by {0} with args {1}'.format(info['source'], ", ".join(args))

    Privilege levels can be set with the `privlevel` argument to the constructor:

    >>> @xbotpp.modules.on_command('admincommand', 1)
    ... def admit_command_handler(info, args, buf):
    ...     return 'Woo, admin command!'

    Running this looks like the following:

    .. code-block:: text

         <user> !admincommand
          <bot> admincommand: Not authorized.
        <admin> !admincommand
          <bot> Woo, admin command!

    Denying access to admin-level commands is done by the bot's message handler
    itself, and is not something that modules need to worry about other than
    setting a privilege level setting.
    '''

    def constructor(r):
        xbotpp.state['modules_monitor'].bind_command(command, privlevel, r)
        return r
    return constructor

class error:
    '''\
    Exceptions thrown by the module routines.
    '''

    class ModuleNotLoaded(BaseException):
        '''\
        The module `name` does not exist.
        '''

        def __init__(self, name):
            self.name = name

        def __str__(self):
            return self.name

    class ModuleLoadingException(BaseException):
        '''\
        An error occurred loading a module. More details may or may not be
        found in `innerexception`.
        '''

        def __init__(self, innerexception=None):
            self.innerexception = innerexception

        def __str__(self):
            return str(self.innerexception)

class monitor:
    '''\
    The module monitor.
    '''

    def __init__(self):

        #: Paths to look for modules in.
        self.paths = xbotpp.config['modules']['paths']

        #: .. code-block:: python
        #:
        #:    {
        #:        'module_name': {
        #:            'module': <module ...>,
        #:            'events': {
        #:                'sid': ('function_name', <function ...>),
        #:                'sid': ('function_name', <function ...>),
        #:                ...
        #:            }
        #:        },
        #:        ...
        #:    }
        #:
        self.loaded = {}

        #: .. code-block:: python
        #:
        #:    {
        #:        'command_name': {
        #:            'function': <function ...>,
        #:            'privlevel': 0,
        #:            'module': 'module_name'
        #:        },
        #:        ...
        #:    }
        #:
        self.commands = {}

        for path in self.paths:
            sys.path.insert(0, path)

        handler.handlers.bind_event('message', self.on_message)

    def bind_command(self, command, privlevel, function):
        '''\
        Bind `function` to the command `command`, with the privilege level
        `privlevel`.

        Available privilege levels:

        - ``0``: Normal command
        - ``1``: Admin command
        '''

        self.commands[command] = {
            'function': function,
            'privlevel': privlevel,
            'module': inspect.getmodule(function).__xbotpp_module__
        }

    def load_init(self):
        '''\
        Load all the modules present in the `modules -> load` section of the configuration.
        '''

        for module in xbotpp.config['modules']['load']:
            status = self.load(module)
            debug.write('Loading module %s: %s' % (module, 'OK' if status else 'failed'), debug.levels.Info)

    def load(self, name):
        '''\
        Load the module `name`.

        Raises :exc:`error.ModuleLoadingException` on an error.
        '''

        try:
            # handle reloads right
            if name in self.loaded:
                if 'reload' in self.loaded[name]:
                    self.unload(name)
                    self.create_table(name)

            module = importlib.import_module(name)
            imp.reload(module)

            if module.__xbotpp_module__:
                if module.__xbotpp_module__ not in self.loaded:
                    # if this module binds events, this will be done already
                    self.create_table(module.__xbotpp_module__)

                self.loaded[module.__xbotpp_module__]['module'] = module
                return True
            else:
                raise error.ModuleLoadingException("Not a module: %s" % name)

        except Exception as e:
            debug.exception('Exception while loading module \'%s\'.' % name, e)
            raise error.ModuleLoadingException(e)

    def create_table(self, modulename):
        self.loaded[modulename] = {
            'module': None,
            'events': {},
        }

    def on_message(self, event):
        '''\
        Gets message events, does the command logic with them.
        '''

        if event.message.startswith(xbotpp.config['bot']['prefix']):            
            message_information = {
                'source': event.source,
                'target': event.source if event.type == 'privmsg' else event.target
            }

            debug.write("message_information: {}".format(repr(message_information)))

            commands = []
            temp = []
            
            debug.write('starting split')
            for i in shlex.split(event.message[1:]):
                debug.write('shlex: {}'.format(i))
                if i != "|":
                    debug.write('appending to temp')
                    temp.append(i)
                else:
                    debug.write('temp onto commands')
                    commands.append(temp)
                    temp = []

            commands.append(temp)
            del temp
            debug.write('split ended: {}'.format(repr(commands)))
            
            buf = ""

            for br in commands:
                if br[0] in self.commands:
                    debug.write('command {0} found, privlevel {1}'.format(br[0], self.commands[br[0]]['privlevel']))

                    if self.commands[br[0]]['privlevel'] >= 1:
                        if message_information['source'] != xbotpp.config['bot']['owner']:
                            buf = "{}: Not authorized.".format(br[0])
                            debug.write(buf)
                            break
                    try:
                        message_information['command_name'] = br[0]
                        buf = self.commands[br[0]]['function'](message_information, br[1:], buf)
                    except Exception as e:
                        buf = "Exception in {0}: {1}".format(br[0], e)
                    debug.write('buf: {}'.format(buf))
                else:
                    debug.write('command {} not found'.format(br[0]))
                    return
            
            for line in buf.split('\n'):
                xbotpp.state['connection'].send_message(message_information['target'], line)

    def unload(self, name):
        '''\
        Unload the module `name`.

        If the module is not loaded, raises :exc:`error.ModuleNotLoaded`.
        '''

        if name not in self.loaded:
            raise error.ModuleNotLoaded(name)

        # Remove event handlers
        h = handler.handlers.dispatch
        for sid in self.loaded[name]['events']:
            for e_type in h:
                for i, e in enumerate(h[e_type]):
                    if handler.handlers.dispatch[e_type][i] == self.loaded[name]['events'][sid][1]:
                        del handler.handlers.dispatch[e_type][i]

        # Remove command handlers
        c = self.commands
        for command in c:
            if c[command]['module'] == name:
                del self.commands[command]

        del self.loaded[name]
