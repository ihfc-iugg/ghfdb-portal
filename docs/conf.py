# -*- coding: utf-8 -*-
# All configuration values have a default; values that are commented out
# serve to show the default.

import inspect
import os
import sys
from datetime import datetime
from pathlib import Path

import django

# import settings
import toml

# import force_unicode
from django.utils.encoding import force_str

# from django.core.management import setup_environ
# from django.utils.encoding import force_unicode
from django.utils.html import strip_tags

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.


app_dir = Path(__file__).parent.parent.resolve()
sys.path.append(str(app_dir))

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
os.environ["GEOLUMINATE_CONFIG_PATH"] = str(app_dir / "geoluminate.yml")
django.setup()


# -- Project information
# ---------------------------------------------------
package_meta = toml.load("../pyproject.toml")["tool"]["poetry"]
project = package_meta["name"].title()
version = package_meta["version"]  # The short X.Y version.
release = version
authors = ["Sam Jennings"]
copyright = f"{datetime.now().year}, {authors[0]}"
language = "en"

# -- General configuration -----------------------------------------------------

# Any additional Sphinx extension modules go here
extensions = [
    # "sphinx.ext.autodoc",
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
    "autodoc2",
    "sphinx_comments",
    "myst_parser",
]

# The master toctree document.
master_doc = "index"

# Path to additional templates relative to this directory
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

html_theme = "sphinx_book_theme"  # https://sphinx-book-theme.readthedocs.io/en/stable/
html_static_path = ["_static"]
# html_title = None
html_short_title = "GHFDB"
html_logo = "_static/logo.svg"
html_favicon = "_static/icon.svg"
html_show_copyright = True
html_last_updated_fmt = "%b %d, %Y"
html_title = f"GHFDB v{version}"


# https://sphinx-book-theme.readthedocs.io/en/stable/reference.html
# https://pydata-sphinx-theme.readthedocs.io/en/latest/user_guide/index.html
html_theme_options = {
    "repository_url": package_meta["homepage"],
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "announcement": (
        "⚠️The Global Heat Flow Database is in an early development phase and may not work exactly as described in this"
        " documentation. If you find any inconsistencies, please report to the github repository. ⚠️"
    ),
    "home_page_in_toc": True,
    "extra_footer": (
        '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License"'
        ' style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This'
        ' documentation is licensed under a <a rel="license"'
        ' href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons'
        " Attribution-NonCommercial-ShareAlike 4.0 International License</a>."
    ),
}

# https://utteranc.es
# https://sphinx-comments.readthedocs.io/en/latest/utterances.html
comments_config = {
    "utterances": {
        "repo": "/".join(package_meta["homepage"].split("/")[-2:]),
        "issue-term": "pathname",
        "theme": "preferred-color-scheme",
        "label": "documentation",
        "crossorigin": "anonymous",
    }
}


autodoc2_packages = [
    "../project/schemas/heat_flow",
]

autodoc2_render_plugin = "myst"

autodoc2_skip_module_regexes = [
    r".*migrations.*",
    r".*tests.*",
]

autodoc2_parse_docstrings = True

autodoc2_docstring_parser_regexes = [("myst", r".*choices*")]

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    # "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# The reST default role (used for this markup: `text`) to use for all documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False


# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False


autodoc_default_options = {
    "exclude-members": "__weakref__",
}

# myst_enable_extensions = [
#     "deflist",
# ]

autosectionlabel_prefix_document = True


# -- Options for HTML output ---------------------------------------------------


# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []


# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = f"{package_meta['name']}doc"


# Auto list fields from django models - from https://djangosnippets.org/snippets/2533/#c5977
import inspect

from django.utils.encoding import force_str
from django.utils.html import strip_tags

# def process_docstring(app, what, name, obj, options, lines):
#     # This causes import errors if left outside the function
#     from django.db import models

#     # Only look at objects that inherit from Django's base model class
#     if inspect.isclass(obj) and issubclass(obj, models.Model):
#         # Grab the field list from the meta class
#         fields = obj._meta.get_fields()

#         for field in fields:
#             # Skip ManyToOneRel and ManyToManyRel fields which have no 'verbose_name' or 'help_text'
#             if not hasattr(field, "verbose_name"):
#                 continue

#             # Decode and strip any html out of the field's help text
#             help_text = strip_tags(force_str(field.help_text))

#             # Decode and capitalize the verbose name, for use if there isn't
#             # any help text
#             verbose_name = force_str(field.verbose_name).capitalize()

#             if help_text:
#                 # Add the model field to the end of the docstring as a param
#                 # using the help text as the description
#                 lines.append(":param %s: %s" % (field.attname, help_text))
#             else:
#                 # Add the model field to the end of the docstring as a param
#                 # using the verbose name as the description
#                 lines.append(":param %s: %s" % (field.attname, verbose_name))

#             # Add the field's type to the docstring
#             if isinstance(field, models.ForeignKey):
#                 to = field.rel.to
#                 lines.append(
#                     ":type %s: %s to :class:`~%s.%s`"
#                     % (field.attname, type(field).__name__, to.__module__, to.__name__)
#                 )
#             else:
#                 lines.append(":type %s: %s" % (field.attname, type(field).__name__))

#     # Return the extended docstring
#     return lines


# def setup(app):
#     # Register the docstring processor with sphinx
#     app.connect("autodoc2-object", process_docstring)


# END Auto list fields from django models -
