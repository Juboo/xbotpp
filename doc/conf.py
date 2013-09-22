#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

import xbotpp

extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.doctest',
	'sphinx.ext.intersphinx',
	'sphinx.ext.coverage',
	'sphinx.ext.viewcode'
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = 'xbot++'
copyright = '2013, Aki Jenkinson and contributors'
version = ' '.join([str(s) for s in xbotpp.__version_tuple__[:2]])
release = xbotpp.__version__

exclude_patterns = ['_build']
pygments_style = 'sphinx'

html_theme = 'default'
html_static_path = ['_static']
htmlhelp_basename = 'xbotdoc'

latex_elements = {
	# The paper size ('letterpaper' or 'a4paper')
	'papersize': 'a4paper',

	# The font size ('10pt', '11pt' or '12pt').
	#'pointsize': '10pt',

	# Additional stuff for the LaTeX preamble.
	#'preamble': '',
}

latex_documents = [
  ('index', 'xbot.tex', 'xbot++ Documentation',
   'Aki Jenkinson and contributors', 'manual'),
]

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'xbot', 'xbot++ Documentation',
     ['Aki Jenkinson and contributors'], 1)
]
man_show_urls = False

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'xbot', 'xbot++ Documentation',
   'Aki Jenkinson and contributors', 'xbot', 
   'One line description of project.', 'Miscellaneous'),
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'http://docs.python.org/': None}
