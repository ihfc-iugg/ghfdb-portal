import os

import geoluminate

from .base import *

geoluminate.setup(development=True)

# OVERRIDE DEFAULT LOCAL SETTINGS BELOW HERE
# -------------------------------------------

os.environ.setdefault("SHOW_DEBUG_TOOLBAR", "True")


# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# removing validators for local development
AUTH_PASSWORD_VALIDATORS = []

EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
SERVER_EMAIL = EMAIL_HOST_USER


# print(EMAIL_HOST)
# print(EMAIL_HOST_PASSWORD)
# print(EMAIL_HOST_USER)
# print(DEFAULT_FROM_EMAIL)
# print(SERVER_EMAIL)
