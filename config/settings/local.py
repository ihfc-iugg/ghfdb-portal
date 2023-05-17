import geoluminate

from .base import *

geoluminate.setup(development=True)

# OVERRIDE DEFAULT LOCAL SETTINGS BELOW HERE
# -------------------------------------------

INSTALLED_APPS += [
    "django_extensions",
]
