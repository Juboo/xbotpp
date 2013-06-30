# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import imp
import json
import inspect
import importlib

import xbotpp
from xbotpp import util
from xbotpp import debug
from xbotpp import handler


def on_event(event):
    def constructor(r):
        sid = util.random_string()
        setattr(r, '__xbotpp_event__', event)
        setattr(r, '__xbotpp_sid__', sid)
        handler.handlers.bind_event(event, r)
        parent = inspect.getmodule(r).__xbotpp_module__
        if parent not in xbotpp.state['modules_monitor'].loaded:
            xbotpp.state['modules_monitor'].create_table(parent)
        xbotpp.state['modules_monitor'].loaded[parent]['events'][sid] = r
        return r
    return constructor

def on_command(command, privlevel=0):
    def constructor(r):
        xbotpp.state['modules_monitor'].bind_command(command, privlevel, r)
        return r
    return constructor

class error:
    class ModuleNotLoaded(BaseException):
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return self.name

    class ModuleLoadingException(BaseException):
        def __init__(self, innerexception=None):
            self.innerexception = innerexception

        def __str__(self):
            return str(self.innerexception)

class monitor:
    def __init__(self):
        self.paths = xbotpp.config['modules']['paths']
        self.loaded = {}

        for path in self.paths:
            sys.path.insert(0, path)

        handler.handlers.bind_event('message', self.on_message)

    def load_init(self):
        for module in xbotpp.config['modules']['load']:
            status = self.load(module)
            debug.write('Loading module %s: %s' % (module, 'OK' if status else 'failed'), debug.levels.Info)

    def load(self, name):
        try:
            module = importlib.import_module(name)
            imp.reload(module)

            if module.__xbotpp_module__:
                self.create_table(module.__xbotpp_module__)
                self.loaded[module.__xbotpp_module__]['module'] = module
                return True
            else:
                raise error.ModuleLoadingException("Not a module: %s" % name)

        except Exception as e:
            debug.exception('Exception while loading module \'%s\'.' % name, e)
            raise error.ModuleLoadingException(e)

    def create_table(self, modulename):
        if modulename not in self.loaded:
            self.loaded[modulename] = {
                'module': None,
                'events': {},
            }

    def unload(self, name):
        if name not in self.loaded:
            raise error.ModuleNotLoaded(name)

        # Remove event handlers
        for sid in self.loaded[name]['events']:
            for e_type in handlers.dispatch:
                for e_handler in e_type:
                    if e_handler == self.loaded[name]['events'][sid]:
                        del self.loaded[name]['events'][sid]

        del self.loaded[name]
