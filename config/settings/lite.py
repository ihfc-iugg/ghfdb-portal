import os
from pathlib import Path

# import geoluminate
from geoluminate.conf.setup import setup

from .base import *

os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("CACHE", "False")

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

setup(development=True)

# OVERRIDE DEFAULT LOCAL SETTINGS BELOW HERE
# -------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# use django's local memory cache for development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ghfdblite",
    }
}
# STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"
