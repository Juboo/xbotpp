#!/usr/bin/env python3

import sys, os, importlib, io, inspect

sys.path.insert(0, os.path.abspath('..'))
xbotpp_config = importlib.import_module("configparser").ConfigParser()
xbotpp_config.readfp(io.StringIO("[bot]\nprefix=!\nskip_load=True"))
xbotpp_version = importlib.import_module("xbotpp").Bot(xbotpp_config).version

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
html_theme = 'nature'

# generate help pages for modules in the modules/ directory
with open("modules/index.rst", "w") as moduleindex:
    moduleindex.write(".. _modules:\n\n")
    moduleindex.write("Modules\n")
    moduleindex.write("=======\n\n")
    moduleindex.write(".. toctree::\n")

    for obj in importlib.import_module("xbotpp").modules.Modules("").modules_from_path(os.path.join('..', 'modules')):
        module = importlib.import_module("modules.%s" % obj)
        moduleindex.write("    " + obj + "\n")
        with open("modules/%s.rst" % obj, 'w') as mod:
            mod.write(obj + "\n")
            mod.write("=" * len(obj) + "\n\n")
            mod.write(".. automodule:: modules.%s\n" % obj)
            mod.write("   :members:\n")
