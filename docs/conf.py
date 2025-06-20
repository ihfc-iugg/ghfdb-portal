import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

sys.path.append(str(BASE_DIR / "project"))
sys.path.insert(0, os.path.abspath("../extensions"))
# sys.path.append(os.path.join(os.path.dirname(__file__), "project"))

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
    "sphinx_design",
    "docs.extensions.auto_django_model",
    # "sphinx_tippy",
    "sphinx_exec_code",
    # "docs.extensions.modelinfo",
    # "extensions.mycustomdirective",
]

myst_allow_raw_html = True
myst_title_to_header = False

myst_html_meta = {
    "description lang=en": "Documentation and guides for the Heatflow.world web portal.",
    "keywords": "heat flow, Global Heat Flow Database, geothermal, heat flow, geophysics, geology",
}


autodoc2_parse_docstrings = True

autodoc2_docstring_parser_regexes = [("myst", r".*choices*")]


autodjango_model_extra = {"about": ""}

autodjango_model_apps = [
    "heat_flow",
]

autodjango_model_config = {
    "global": {
        "exclude": ["id", "created"],  # exclude fields from any model
    },
    "heat_flow": {
        "exclude": ["id", "created"],  # exclude fields from any model in heat_flow app
    },
    "heat_flow.HeatFlowSite": {
        "exclude": ["id", "created"],  # exclude fields from the HeatFlowSite model
        # "include": ["name", "location"],  # include only these fields from the HeatFlowSite model
    },
}

tippy_skip_anchor_classes = ("headerlink", "sd-stretched-link", "sd-rounded-pill")
tippy_anchor_parent_selector = "article.bd-article"
tippy_rtd_urls = [
    "https://www.sphinx-doc.org/en/master",
    "https://markdown-it-py.readthedocs.io/en/latest",
]
