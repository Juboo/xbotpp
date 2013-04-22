# -*- coding: utf-8 -*-
# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import sys
import imp
import inspect
import importlib

class Module:
    def __init__(self):
        if not getattr(self, 'perms', None):
            self.perms = "common"

        if not getattr(self, 'name', None):
            self.name = self.__class__.__name__

    def action(self, event, args, buf):
        pass

    def load(self):
        pass

    def unload(self):
        pass

def isModule(member):
    if member in Module.__subclasses__():
        return True
    return False

class Modules:
    def __init__(self, bot):
        self.bot = bot
        self.modules = {}
        self.paths = []

    def add_path(self, path):
        if not path in sys.path:
            self.paths.append(path)
            sys.path.insert(0, path)

    def modules_from_path(self, path):
        modules = []
        for entry in os.listdir(path):
            if os.path.isfile(os.path.join(path, entry)):
                (name, ext) = os.path.splitext(entry)
                if ext == os.extsep + 'py' and name != '__init__':
                    modules.append(name)
            elif os.path.isfile((os.path.join(path, entry, os.extsep.join(['__init__', 'py'])))):
                modules.append(entry)
        return modules

    def load_init(self, path):
        self.add_path(path)
        modules = self.modules_from_path(path)
        for module in modules:
            status = self.load(module)
            self.bot._debug("Loading module %s: %s" % (module, 'OK' if status else 'failed'))

    def load(self, name):
        try:
            module = importlib.import_module(name)
            imp.reload(module)

            for member in inspect.getmembers(module, isModule):
                mod = member[1]()
                mod.bot = self.bot
                self.modules[member[0]] = mod

            return True

        except:
            return False

    def unload(self, name):
        if name not in self.modules:
            return False

        self.modules[name].unload()
        del self.modules[name]
        return True
 
