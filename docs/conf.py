import os
import sys

sys.path.insert(0, os.path.abspath("../extensions"))

os.environ.setdefault("DJANGO_ENV", "development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DJANGO_SECURE", "False")

from docs.conf import *

autodoc2_packages = ["heat_flow"]

html_short_title = "Heatflow.world"
# html_theme_options.update(
#     {
#         "icon_links": [
#             {
#                 "name": "Heat Flow World",
#                 "url": "https://heatflow.world",
#                 "icon": "_static/icon.svg",
#                 "type": "local",
#             },
#         ],
#     }
# )


extensions.remove("autodoc2")
extensions += [
    "sphinx_exec_code",
    "extensions.modelinfo",
    "extensions.mycustomdirective",
]

myst_allow_raw_html = True
myst_title_to_header = False

myst_html_meta = {
    "description lang=en": "Documentation and guides for the Heatflow.world web portal.",
    "keywords": "heat flow, Global Heat Flow Database, geothermal, heat flow, geophysics, geology",
}


autodoc2_parse_docstrings = True

autodoc2_docstring_parser_regexes = [("myst", r".*choices*")]
