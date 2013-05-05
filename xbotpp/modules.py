# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import sys
import imp
import inspect
import importlib

class BoundCommand(object):
    """\
    Contains information about a command to bind to a bot function.

    - ``name`` is the name of the command, or the regex to match a URL
      if the module is a URL module. This is ignored for message handler modules.
    - ``func`` is the function to call (with parameters of :py:func:`xbotpp.modules.Module.action`)
    - ``privlevel`` is the permission level of the command, which can be
      either of `common` for normal commands or `admin` for admin-level commands.
      This is ignored for URL handlers and message handlers.
    - ``type`` is the type of command (see :ref:`commandtypes`)
    """

    def __init__(self, name, func, privlevel="common", type="command", parent=None):
        self.name = name
        self.func = func
        self.privlevel = privlevel
        self.type = type

        if parent == None:
            self.parent = {"parent": None, "basename": None}
        else:
            self.parent = parent

class Module:
    """\
    Base class for xbot++ modules.
    """

    def __init__(self):
        """\
        Define module information, among other things.
        """

        self.name = self.name if getattr(self, 'name', None) else self.__class__.__name__
        """\
        The name of the module. Defaults to the class name if not explicitly specified.
        """

        self.bind = self.bind if getattr(self, "bind", None) else [BoundCommand(self.name, self.action)]
        """\
        A list of BoundCommand objects, containing the commands in this module for the bot to bind to.
        """

    def bind_command(self, name, func, privlevel, type):
        """\
        Bind a command.
        """

        self.bind.append(BoundCommand(name, func, privlevel, type, None))

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
        self.paths = []
        self.configpath = ""
        self.actualmodules = {}
        self.modules = {
            "command": {},
            "url": {},
            "privmsg": {},
        }

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
        self.configpath = os.path.join(path, "conf")
        modules = self.modules_from_path(path)
        for module in modules:
            status = self.load(module)
            self.bot._debug("Loading module %s: %s" % (module, 'OK' if status else 'failed'))

    def load(self, name):
        """\
        Load the module named `name`.

        This function imports the named module, and searches for module classes within the module
        file. For each class found, we initialize it, set it's `self.bot` item to the Bot object,
        and iterate through the module's `self.bind` list, and store each item in the bind list
        with it's associated metadata in the `modules.modules` dictionary. We then store the
        module itself it the `modules.actualmodules` dictionary, and call the module's
        :py:func:`xbotpp.modules.Module.load` function.

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
                for command in mod.bind:
                    command.parent = {'parent': member[0], 'basename': name}
                    self.modules[type][command.name] = command
                self.actualmodules[member[0]] = (name, mod)
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
        Unload the module `name`.

        Recursively looks through the `modules.modules` dictionary for items that were created
        by the named module, and removes them, before calling the module's
        :py:func:`xbotpp.modules.Module.unload` function and deleting the module from the 
        `modules.actualmodules` dictionary.

        Returns :py:const:`True` on success, :py:const:`False` on failure.

        :param name: name of module to unload
        :type name: str
        :rtype: bool
        """

        try:
            if name not in self.actualmodules:
                return False

            del_list = []
            for obj in self.actualmodules:
                for type in self.modules:
                    for mod in enumerate(self.modules[type]):
                        if self.modules[type][mod].parent['parent'] == name:
                            del_list.append((type, mod]))

            for type, mod in del_list:
                try:
                    self.bot._debug("Deleting %s module: %s" % (type, mod))
                    del self.modules[type][mod]
                except KeyError:
                    pass

            self.actualmodules[obj][1].unload()
            del self.actualmodules[obj]
            return True

        except:
            return False

