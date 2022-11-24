# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from datetime import datetime
# import pathlib
import django

for p in sys.path:
    x = '/global-heat-flow-database/'
    if x in p:
        sys.path.append(p.replace(x, '/'))

sys.path.insert(0, os.path.abspath('../..'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
django.setup()


project = 'World Heat Flow Database Project'
copyright = f'{datetime.now().year}, Sam Jennings'
author = 'Sam Jennings'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    # 'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    # "sphinx_rtd_theme",
]

templates_path = ['_templates']
exclude_patterns = [
    'static',
    'media',
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_favicon = 'icon.svg'

autodoc_default_options = {
    "exclude-members": "__weakref__",
}
