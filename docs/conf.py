# -*- coding: utf-8 -*-
# All configuration values have a default; values that are commented out
# serve to show the default.
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()


os.environ["GEOLUMINATE_CONFIG_PATH"] = str(BASE_DIR / "geoluminate.yml")


from docs.conf import *  # noqa: F401, F403

# app_dir = Path(__file__).parent.parent.resolve()
# sys.path.append(str(app_dir))


# html_short_title = "GHFDB"
# html_logo = "_static/logo.svg"
# html_favicon = "_static/icon.svg"


# https://sphinx-book-theme.readthedocs.io/en/stable/reference.html
# https://pydata-sphinx-theme.readthedocs.io/en/latest/user_guide/index.html
html_theme_options.update({
    "announcement": (
        "⚠️The Global Heat Flow Database is in an early development phase and may not work exactly as described in"
        " this documentation. If you find any inconsistencies, please report to the github repository. ⚠️"
    ),
})


autodoc2_parse_docstrings = True

autodoc2_docstring_parser_regexes = [("myst", r".*choices*")]


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
