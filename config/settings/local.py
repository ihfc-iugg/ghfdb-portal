import os

import geoluminate

from .base import *

geoluminate.setup(development=True)

# OVERRIDE DEFAULT LOCAL SETTINGS BELOW HERE
# -------------------------------------------
# INSTALLED_APPS = ["django_werkzeug"] + GEOLUMINATE_APPS + INSTALLED_APPS + ["compressor", "django_extensions"]

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
# ACCOUNT_AUTHENTICATION_METHOD = "email"

ACCOUNT_EMAIL_VERIFICATION = "optional"

LOGIN_REDIRECT_URL = "/profile/"
