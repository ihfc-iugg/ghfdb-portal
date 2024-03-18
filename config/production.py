import geoluminate

from .common import *
from .geoluminate import *

# need to fix this in geoluminate package
SHOW_DEBUG_TOOLBAR = False

geoluminate.setup(development=False)

STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}

ALLOWED_HOSTS = ["env.rz-vm71.gfz-potsdam.de"]

# print(ALLOWED_HOSTS)
