import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

sys.path.append(str(BASE_DIR / "project"))
# sys.path.append(os.path.join(os.path.dirname(__file__), "project"))

os.environ.setdefault("DJANGO_ENV", "development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DJANGO_SECURE", "False")

# fairdm-docs 0.3.0 made its Django integration opt-in. Without this it never
# calls django.setup(), and the model-documentation extension fails on
# "Apps aren't loaded yet".
os.environ.setdefault("FAIRDM_DOCS_DJANGO", "true")

from fairdm_docs.conf import *  # noqa: E402  (must follow the DJANGO_* environment setup above)

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

html_theme_options["path_to_docs"] = "docs"
extensions.remove("autodoc2")
extensions += [
    "sphinx_design",
    # fairdm-docs 0.3.0 renamed its package from `docs` to `fairdm_docs` and
    # this extension from `auto_django_model` to `autodoc_models`.
    "fairdm_docs.extensions.autodoc_models",
    # "sphinx_tippy",
    "sphinx_exec_code",
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

# Linkcheck configuration (T005)
# Ignore patterns for URLs that should not be checked
linkcheck_ignore = [
    r"https://localhost:\d+/",  # Local development URLs
    # Add more patterns as needed during validation
]

# Allow specific redirects to avoid false positives
linkcheck_allowed_redirects = {
    # Example: all redirects from old domain to new domain
    # r'https://old-domain\.org/.*': r'https://new-domain\.org/.*'
}

# Custom request headers for linkcheck
linkcheck_request_headers = {
    "*": {
        "Accept": "text/html,application/xhtml+xml",
    }
}
