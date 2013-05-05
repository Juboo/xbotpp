.. _modules:

Modules
=======

Module storage
--------------

.. _modulesdict:

The `modules.modules` dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An example of a `modules.modules` dictionary with two loaded commands and one
loaded URL handler would look somewhat like the following::

    modules.modules = {
        "command": {
            "help": BoundCommand("help", <type 'function'>, "command", "common", {'parent': 'help', 'basename': 'help'})
            "reload": BoundCommand("reload", <type 'function'>, "command", "admin", {'parent': 'module', 'basename': 'admin'})
        },
        "url": {
            "shimmie\.katawa-shoujo\.com": BoundCommand("shimmie\.katawa-shoujo\.com", <type 'function'>, "url", "common", {'parent': 'mishimmie', 'basename': 'mishimmie'})
        },
        "privmsg: {},
    }

See the :py:class:`xbotpp.modules.BoundCommand` docs for how the BoundCommand object works.

.. _commandtypes:

Command Types
~~~~~~~~~~~~~

The first level under the `modules.modules` dictionary is the command type.
The possible command types in xbot++ are currently:

- Commands (type ``command``)
- URL handlers (type ``url``)
- Message handlers (type ``privmsg``)

A command module is called when it's explicitly told to run by a user running
the command, like so::

    May 02 2013 05:21:24 <<< :akiaki!~akiaki@im.hiding.my.host PRIVMSG ##xbotpp :^help
    May 02 2013 05:21:24 >>> ##xbotpp -> Available commands: info, man, mi, help, grep, sprunge, list, calc, np, lolcrypt, echo

A URL handler isn't used by the bot itself, but instead is called by the
:py:func:`modules.open_graph.open_graph.do_og` function when a URL is found
that matches the regular expression set in the command's name. Take a look
at the :ref:`module_open_graph` documentation.

A message handler is called for every message that is received by the bot.
The name of this type of command is not used by the bot, but should still be
unique.


.. _actualmodulesdict:

The `modules.actualmodules` dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `modules.actualmodules` dictionary contains the raw loaded module classes.
When a module is loaded, it is stored in this dictionary in the following
format::

    module_name: (module_base_name, module_object)

- ``module_name`` is the name of the module (usually the name of the module`s
  class, but can be overridden by the module with the `self.name` property in
  the module)
- ``module_object`` is a loaded object of the module, with the module's
  `self.bot` property set to the bot object.
- ``module_base_name`` contains the name of the module file from which the
  module was loaded.

Methods
-------

.. autoclass:: xbotpp.modules.Modules
   :members:

.. automethod:: xbotpp.modules.isModule

