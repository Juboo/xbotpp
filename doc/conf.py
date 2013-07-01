#!/usr/bin/env python3

import sys, os, importlib, io, inspect
sys.path.insert(0, os.path.abspath('..'))

import xbotpp
xbotpp_version = xbotpp.__version__

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
