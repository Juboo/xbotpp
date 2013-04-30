#!/usr/bin/env python3

import sys, os, importlib, io, inspect

sys.path.insert(0, os.path.abspath('..'))
xbotpp_config = importlib.import_module("configparser").ConfigParser()
xbotpp_config.readfp(io.StringIO("[bot]\nprefix=!\nskip_load=True"))

from xbotpp import Bot
from xbotpp.modules import Module, Modules

xbotpp_version = Bot(xbotpp_config).version

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode']
templates_path = ['_templates']
source_suffix = '.rst'
source_encoding = 'utf-8-sig'
master_doc = 'index'
project = 'xbot++'
copyright = '2013, aki--aki'

version = xbotpp_version
release = xbotpp_version

exclude_patterns = ['_build']
pygments_style = 'sphinx'

class Mock(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return Mock()

    @classmethod
    def __getattr__(cls, name):
        if name in ('__file__', '__path__'):
            return '/dev/null'
        elif name[0] == name[0].upper():
            mockType = type(name, (), {})
            mockType.__module__ = __name__
            return mockType
        else:
            return Mock()

for mod_name in ['lxml', 'lxml.html', 'lxml.etree']:
    sys.modules[mod_name] = Mock()

# generate help pages for modules in the modules/ directory

def isModule(member):
    if member in Module.__subclasses__():
        return True
    return False

with open("modules/index.rst", "w") as moduleindex:
    moduleindex.write(".. _moduledocs:\n\n")
    moduleindex.write("Modules\n")
    moduleindex.write("=======\n\n")
    moduleindex.write(".. toctree::\n")

    for obj in Modules("").modules_from_path(os.path.join('..', 'modules')):
        module = importlib.import_module("modules.%s" % obj)
        moduleindex.write("    " + obj + "\n")
        with open("modules/%s.rst" % obj, 'w') as mod:
            mod.write(obj + "\n")
            mod.write("=" * len(obj) + "\n\n")
            for member in inspect.getmembers(module, isModule):
                titlestr = member[1]().name
                if titlestr != obj:
                    mod.write(titlestr + "\n")
                    mod.write("-" * len(titlestr) + "\n\n")
                
                bind = { "command": [], "url": [], "privmsg": [] }
                for line in member[1]().bind:
                    bind[line[0]].append("%s (`%s`)" % (line[1], line[2].__name__))

                command = ", ".join(bind['command'])
                url = ", ".join(bind['url'])
                privmsg = ", ".join(bind['privmsg'])

                mod.write("Bound functions\n")
                mod.write("~~~~~~~~~~~~~~~\n\n")
                mod.write("- Commands: %s\n" % (command if command != "" else "none"))
                mod.write("- URLs: %s\n" % (url if url != "" else "none"))
                mod.write("- Message handlers: %s\n" % (privmsg if privmsg != "" else "none"))
                mod.write("\n")

                mod.write("Module documentation\n")
                mod.write("~~~~~~~~~~~~~~~~~~~~\n\n")
                mod.write(".. autoclass:: modules.%s.%s\n" % (obj, titlestr))
                mod.write("   :members:\n\n")

