import os

import geoluminate

from .base import *

geoluminate.setup(development=True)

# OVERRIDE DEFAULT LOCAL SETTINGS BELOW HERE
# -------------------------------------------

os.environ.setdefault("SHOW_DEBUG_TOOLBAR", "True")

ALLOWED_HOSTS = ["139.17.54.176", "ghfdb.localhost", "ghfdb.local"]
