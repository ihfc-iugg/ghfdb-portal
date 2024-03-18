import geoluminate

from .common import *
from .geoluminate import *

# need to fix this in geoluminate package
SHOW_DEBUG_TOOLBAR = False

geoluminate.setup(development=False)

STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}


STATIC_URL = "/django-static/"
COMPRESS_URL = STATIC_URL
