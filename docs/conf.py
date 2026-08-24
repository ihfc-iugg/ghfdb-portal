import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

sys.path.append(str(BASE_DIR / "project"))

os.environ.setdefault("DJANGO_ENV", "development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DJANGO_SECURE", "False")

os.environ.setdefault("FAIRDM_DOCS_DJANGO", "true")

from fairdm_docs.conf import *  # noqa: E402  (must follow the DJANGO_* environment setup above)

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
    # fairdm_docs.extensions.autodoc_models is deliberately not enabled. It reads
    # the FairDM registry as a sequence of dicts, while the registry yields model
    # classes, so its build hook raises "type 'HeatFlowSite' is not subscriptable"
    # and the whole build fails. Its directive is broken independently: the field
    # template calls `hasattr`, which is not a Jinja global, so every model would
    # render as an error box even with the hook fixed. fairdm-docs comments the
    # extension out of its own default list for the same reason. The data model
    # pages under docs/data_models/ are written by hand instead.
    # "sphinx_tippy",
    "sphinx_exec_code",
    # Without this, MyST emits every ```mermaid block as a highlighted code block and
    # the build reports nothing wrong, so a diagram reaches readers as source text.
    "sphinxcontrib.mermaid",
]

myst_allow_raw_html = True

# Hand ```mermaid fences to the Mermaid directive. Without this MyST treats them as
# code blocks whatever extensions are loaded, and the diagrams reach readers as source
# text. The plain fence is kept rather than the directive syntax so the same source
# also renders on GitHub.
myst_fence_as_directive = ["mermaid"]

myst_html_meta = {
    "description lang=en": "Documentation and guides for the Heatflow.world web portal.",
    "keywords": "heat flow, Global Heat Flow Database, geothermal, heat flow, geophysics, geology",
}
