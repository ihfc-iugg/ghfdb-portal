from .common import *
from .geoluminate import *

# need to fix this in geoluminate package
SHOW_DEBUG_TOOLBAR = False


STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}

GEOLUMINATE_LABELS["sample"] = {"verbose_name": "Heat Flow Site", "verbose_name_plural": "Heat Flow Sites"}

# STATIC_URL = "/django-static/"
# COMPRESS_URL = STATIC_URL
