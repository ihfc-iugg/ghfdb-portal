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

myst_allow_raw_html = True

myst_html_meta = {
    "description lang=en": "Documentation and guides for the Heatflow.world web portal.",
    "keywords": "heat flow, Global Heat Flow Database, geothermal, heat flow, geophysics, geology",
}
