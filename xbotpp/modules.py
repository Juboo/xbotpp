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
from xbotpp import error


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
        if parent in xbotpp.state.modules.loaded:
            for function in xbotpp.state.modules.loaded[parent]['events']:
                if xbotpp.state.modules.loaded[parent]['events'][function][0] == getattr(r, '__name__', None):
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
        if parent not in xbotpp.state.modules.loaded:
            xbotpp.state.modules.create_table(parent)
        xbotpp.state.modules.loaded[parent]['events'][sid] = (getattr(r, '__name__', None), r)

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
    ... def admin_command_handler(info, args, buf):
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
        xbotpp.state.modules.bind_command(command, privlevel, r)
        return r
    return constructor

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

        #: List containing the modules that are being loaded in depends().
        self.depends_stack = []

        #: Dictionary of SQLiteShelf objects for storage of module data.
        self.moddata = {}

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
            u = False
            if name in self.loaded:
                if 'reload' in self.loaded[name]:
                    u = True
                    debug.write("Module loaded, going to unload it first")
            if u:
                self.unload(name)

            module = importlib.import_module(name)
            imp.reload(module)

            if module.__xbotpp_module__:
                if module.__xbotpp_module__ not in self.loaded:
                    # if this module binds events, this will be done already
                    debug.write("Creating module table")
                    self.create_table(module.__xbotpp_module__)

                self.loaded[module.__xbotpp_module__]['module'] = module
                self.moddata[module.__xbotpp_module__] = xbotpp.vendor.sqliteshelf.SQLiteShelf(xbotpp.config['modules']['data_db'], module.__xbotpp_module__)
                debug.write("Loaded {} successfully.".format(module.__xbotpp_module__))
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
                'target': event.source if event.type == 'privmsg' or event.type == 'privnotice' else event.target
            }

            debug.write("message_information: {}".format(repr(message_information)))

            commands = []
            temp = []

            try:
                if len(event.message) > 1 and event.message[1] == xbotpp.config['bot']['prefix']:
                    debug.write("using shlex to split command")
                    splitfunc = shlex.split
                    messagetosplit = event.message[2:]
                else:
                    debug.write("using str.split to split command")
                    splitfunc = lambda x: x.split(" ")
                    messagetosplit = event.message[1:]

                if len(messagetosplit) is 0:
                    debug.write('empty message, returning')
                    return

                debug.write('starting split')
                for i in splitfunc(messagetosplit):
                    debug.write('split: {}'.format(i))
                    if i != "|":
                        debug.write('Appending argument to temp array (currently {})'.format(repr(temp)))
                        temp.append(i)
                    else:
                        debug.write('End of command: {}'.format(repr(temp)))
                        commands.append(temp)
                        temp = []
            except Exception as e:
                debug.exception("Exception while parsing command", e)
                xbotpp.state.connection.send_message(message_information['target'], "Error: {}".format(str(e)))
                return

            debug.write('End of command: {}'.format(repr(temp)))
            commands.append(temp)
            del temp

            debug.write('Command sequence: {}'.format(repr(commands)))
            
            buf = ""

            for br in commands:
                if br[0] in self.commands:
                    debug.write('Command {0} found, privlevel {1}'.format(br[0], self.commands[br[0]]['privlevel']))

                    if self.commands[br[0]]['privlevel'] >= 1:
                        if message_information['source'] != xbotpp.config['bot']['owner']:
                            buf = "{}: Not authorized.".format(br[0])
                            debug.write(buf)
                            break
                    try:
                        message_information['command_name'] = br[0]
                        buf = self.commands[br[0]]['function'](message_information, br[1:], buf)
                    except Exception as e:
                        debug.exception("Exception while handling command {}".format(br[0]), e)
                        buf = "Exception in {0}: {1}".format(br[0], e)
                    debug.write('Buffer: {}'.format(buf))
                else:
                    debug.write('Command {} not found'.format(br[0]))
                    return
            
            try:
                for line in buf.split('\n'):
                    xbotpp.state.connection.send_message(message_information['target'], line)
            except Exception as e:
                debug.exception("Exception in writing buffer to target", e)
                message = "Error [{0}]: {1}".format(e.__class__.__name__, e)
                xbotpp.state.connection.send_message(message_information['target'], message)

    def unload(self, name):
        '''\
        Unload the module `name`.

        If the module is not loaded, raises :exc:`error.ModuleNotLoaded`.
        '''

        if name not in self.loaded:
            debug.write("Module being unloaded does not exist ({}), raising exception".format(name))
            raise error.ModuleNotLoaded(name)

        if name in self.moddata:
            del self.moddata[name]

        try:
            # Remove event handlers
            for sid in self.loaded[name]['events']:
                types = [(i, e) for i, e in enumerate(handler.handlers.dispatch)]
                for e_index, e_type in types:
                    debug.write("Loop: Checking type {}".format(e_type))
                    typed = [(i, e) for i, e in enumerate(handler.handlers.dispatch[e_type])]
                    for i, e in typed:
                        debug.write("Loop: handler {0} in type {1}".format(str(handler.handlers.dispatch[e_type][i]), e_type))
                        if handler.handlers.dispatch[e_type][i] == self.loaded[name]['events'][sid][1]:
                            debug.write("Removing event handler {0} ({1})".format(sid, self.loaded[name]['events'][sid][0]))
                            del handler.handlers.dispatch[e_type][i]

            # Remove command handlers
            commands = [(i, e) for i, e in enumerate(self.commands)]
            for index, command in commands:
                if self.commands[command]['module'] == name:
                    debug.write("Removing command {}".format(command))
                    del self.commands[command]

            del self.loaded[name]

            debug.write("Unloaded {} successfully.".format(name))

        except Exception as e:
            debug.exception("Exception while unloading module '{}'.".format(name), e)
            raise

    def depends(self, caller, deplist):
        '''\
        To be called at the top of a module.

        Allows inclusion of dependencies on other modules 
        (eg. a URL module depending on Open Graph).
        '''

        if caller in self.depends_stack:
            text = """depends: Recursive dependencies detected!
            Being called by {caller}, and is already on the stack.
            Stack is currently {stack}.""".format(caller=caller, stack=self.depends_stack)
            debug.write(text, debug.levels.Info)
            del text
            return None

        self.depends_stack.insert(0, caller)
        debug.write("depends: stack is {}".format(repr(self.depends_stack)))

        error = False
        for module in deplist:
            if not module in self.loaded:
                debug.write("depends: {module} (required by {caller}) is being loaded".format(module=module, caller=caller))
                try:
                    self.load(module)
                except:
                    debug.write("depends: couldn't load dep {module} (required by {caller})".format(module=module, caller=caller), debug.levels.Error)
                    ex = error.DependencyException(list(self.depends_stack))
                    self.depends_stack = []
                    raise

        debug.write("depends: dependencies for module {caller} satisfied".format(caller=caller))
        del self.depends_stack[0]
