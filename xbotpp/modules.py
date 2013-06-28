# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import imp
import json
import importlib

import xbotpp
from xbotpp import debug
from xbotpp import handler


def on_event(event):
    def constructor(r):
        handler.handlers.bind_event(event, r)
        return r
    return constructor

def on_command(command, privlevel=0):
    def constructor(r):
        xbotpp.state['modules_monitor'].bind_command(command, privlevel, r)
        return r
    return constructor

class monitor:
    def __init__(self, config, state):
        self.config = config
        self.state = state
        self.paths = self.config['modules']['paths']
        self.loaded = {}

        for path in self.paths:
            sys.path.insert(0, path)

    def load_init(self):
        for module in self.config['modules']['load']:
            status = self.load(module)
            debug.write('Loading module %s: %s' % (module, 'OK' if status else 'failed'), debug.levels.Info)

    def load(self, name):
        try:
            module = importlib.import_module(name)
            imp.reload(module)

            if module.__xbotpp_module__:
                return True
                self.loaded[module.__xbotpp_module__] = module
            else:
                return False

        except Exception as e:
            debug.exception('Exception while loading module \'%s\'.' % name, e)
            return False
