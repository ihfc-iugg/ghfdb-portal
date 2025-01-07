import os
import sys

os.environ.setdefault("DJANGO_ENV", "development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from docs.conf import *


html_short_title = "Heatflow.world"

sys.path.append(os.path.abspath("../assets"))

html_static_path = [
    "_static",
    "../assets/img",
]

html_logo = "_static/logo.svg"
html_favicon = "_static/icon.svg"

# https://sphinx-book-theme.readthedocs.io/en/stable/reference.html
# https://pydata-sphinx-theme.readthedocs.io/en/latest/user_guide/index.html
# html_theme_options.update(
#     {
#         "announcement": (
#             "⚠️Heatflow.world is in an early development phase and may not work exactly as described in"
#             " this documentation. If you find any inconsistencies, please report to the github repository. ⚠️"
#         ),
#     }
# )

extensions.remove("autodoc2")
extensions += [
    "sphinx_exec_code",
    "extensions.modelinfo",
]
autodoc2_parse_docstrings = True

autodoc2_docstring_parser_regexes = [("myst", r".*choices*")]

epub_theme = "sphinx_book_theme"
