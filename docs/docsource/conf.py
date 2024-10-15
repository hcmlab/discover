import os
import sys
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../..'))
import discover

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DISCOVER'
copyright = '2023, Dominik Schiller'
author = 'Dominik Schiller'
release = discover.__version__


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx_mdinclude',
    #'myst_parser'

]
source_suffix = ['.rst']
autodoc_typehints = "none"
#napoleon_use_param = False
napoleon_google_docstring = True  # Enable parsing of Google-style pydocs.
napoleon_use_ivar = True  # to correctly handle Attributes header in class pydocs

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'press'
#html_static_path = ['_static']

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'globaltoc_collapse': True,
    'globaltoc_maxdepth': -1,
}
html_static_path = ['_static']
html_sidebars = {"**": ["globaltoc.html", "localtoc.html", "searchbox.html"]}

# autodoc_default_options = {
#     'undoc-members': True,
#     #'special-members': True
# }
