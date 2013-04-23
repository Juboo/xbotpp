# -*- coding: utf-8 -*-
# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import sys
import imp
import inspect
import importlib

class Module:
    """\
    Base class for xbot++ modules.
    """

    def __init__(self):
        """\
        Define module information, among other things.
        """

        self.name = self.name if getattr(self, 'name', None) else  self.__class__.__name__
        """\
        The name of the module. Defaults to the class name if not explicitly specified.
        """

        self.bind = self.bind if getattr(self, "bind", None) else [["command", self.name, self.action, "common"]]
        """\
        A list of bot functions to bind to. Each entry is of the format:

            [ `type`, `name`, `callback`, `permission_level` ]

        * `type` is one of "command", "url", "privmsg".
        * `name` is the name of the command in case of `type == "command"`,
           the regular expression to match a URL as a string in case of `type == "url"`,
           else the friendly name for the callback.
        * `callback` is the function to call (with parameters of :py:func:`xbotpp.modules.Module.action`)
        * `permission_level` is one of "common", "admin".
        """

    def action(self, bot, event, args, buf):
        """\
        Default event handler.

        If `self.bind` is not set in the module, this function is called when a bot command
        matching the module's name is called. 

        :param bot: the bot that the function is being called by
        :type bot: :py:class:`xbotpp.Bot`
        :param event: the :py:class:`irc.client.Event` which initiated this command
        :type event: :py:class:`irc.client.Event`
        :param args: list of the arguments to the command
        :type args: list
        :param buf: output from the previous command in a sequence of chained commands,
                    or the empty string if there was no output
        :type buf: str
        :rtype: str
        """

        pass

    def load(self):
        """\
        Function that is run when the module is loaded.
        """

        pass

    def unload(self):
        """\
        Function that is run when the module is unloaded.
        """

        pass

def isModule(member):
    """\
    Returns true if `member` is a module, else False.

    :param member: class to check
    :type member: class
    :rtype: bool
    """

    if member in Module.__subclasses__():
        return True
    return False

class Modules:
    """\
    Class to handle loading, reloading and unloading of xbot++ modules.
    """

    def __init__(self, bot):
        """\
        Initialize module loading routines.

        :param bot: the :py:class:`xbotpp.Bot` that this class will be handling modules foc
        :type bot: :py:class:`xbotpp.Bot`
        """

        self.bot = bot
        self.modules = {
            "command": {},
            "url": {},
            "privmsg": {},
        }
        self.paths = []

    def add_path(self, path):
        """\
        Add `path` to the search path for modules.

        :param path: path to add to the search path
        :type path: str
        """

        if not path in sys.path:
            self.paths.append(path)
            sys.path.insert(0, path)

    def modules_from_path(self, path):
        """\
        Get a list of all the available modules in `path`.

        :param path: path to search for modules
        :type path: str
        :rtype: list
        """

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
        """\
        Load all modules in `path`. Called when the bot starts.

        :param path: path to search for modules
        :type path: str
        """

        self.add_path(path)
        modules = self.modules_from_path(path)
        for module in modules:
            status = self.load(module)
            self.bot._debug("Loading module %s: %s" % (module, 'OK' if status else 'failed'))

    def load(self, name):
        """\
        Load the module named `name`, looking in the search path for the module, and calls the
        module's :py:func:`load() <xbotpp.modules.Module.load()>` function after loading it.

        Returns :py:const:`True` on success, :py:const:`False` on failure.

        :param name: name of module to load
        :type name: str
        :rtype: bool
        """

        try:
            module = importlib.import_module(name)
            imp.reload(module)

            count = 0
            for member in inspect.getmembers(module, isModule):
                mod = member[1]()
                mod.bot = self.bot
                for type, name, func, perms in mod.bind:
                    self.modules[type][name] = (func, perms)
                mod.load()
                count += 1

            if count > 0:
                return True
            else:
                return False

        except:
            return False

    def unload(self, name):
        """\
        Unload the module `name`, calling the module's :py:func:`unload() <xbotpp.modules.Module.unload()>`
        function before doing so.

        Returns :py:const:`True` on success, :py:const:`False` on failure.

        :param name: name of module to unload
        :type name: str
        :rtype: bool
        """

        if name not in self.modules:
            return False

        self.modules[name].unload()
        del self.modules[name]
        return True
 
