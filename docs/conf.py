# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from datetime import datetime

import django

if os.getenv("READTHEDOCS", default=False) == "True":
    sys.path.insert(0, os.path.abspath(".."))
    os.environ["DJANGO_READ_DOT_ENV_FILE"] = "True"
    os.environ["USE_DOCKER"] = "no"
else:
    sys.path.insert(0, os.path.abspath("/app"))

os.environ["DATABASE_URL"] = "sqlite:///readthedocs.db"

os.environ["CELERY_BROKER_URL"] = os.getenv("REDIS_URL", "redis://redis:6379")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()


project = "World Heat Flow Database Project"
copyright = f"{datetime.now().year}, Sam Jennings"
author = "Sam Jennings"
# release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.duration",
    # 'sphinx.ext.doctest',
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx_copybutton",
    "sphinxext.opengraph",
    "myst_parser",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    "static",
    "media",
    "_build",
]

myst_enable_extensions = [
    "deflist",
]

autosectionlabel_prefix_document = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------


# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx"
html_static_path = ["_static"]
html_favicon = "icon.svg"
html_logo = "logo.svg"
html_title = "Documentation for the Global Heat Flow Database application"
html_short_title = "GHFDB Documentation"

# sphinx-book-theme options
html_theme_options = {
    "repository_url": "https://github.com/SSJenny90/world-heat-flow-database",
    "use_repository_button": True,
    "logo_only": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
}


autodoc_default_options = {
    "exclude-members": "__weakref__",
}
