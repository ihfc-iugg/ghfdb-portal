import os

import geoluminate
from geoluminate.conf.setup import setup

from .base import *

os.environ.setdefault("DJANGO_DEBUG", "False")
os.environ.setdefault("CACHE", "False")

setup(development=False)


# PRODUCTION OVERRIDES BELOW
# ------------------------------------------------

COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"


# Fixes issue with missing static files https://stackoverflow.com/a/71686908
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

ALLOWED_HOSTS = ["139.17.54.176", "ghfdb.localhost", "ghfdb.local"]

# production email settings
# ---------------------------

# SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
# """"""
# EMAIL_HOST = "smtp.sendgrid.net"
# """"""
# EMAIL_HOST_USER = "apikey"  # this is exactly the value 'apikey'
# """"""
# EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
# """"""
# EMAIL_PORT = 587
# """"""
# EMAIL_USE_TLS = True
# """"""
