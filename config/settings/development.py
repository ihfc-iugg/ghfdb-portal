import geoluminate

from .common import *
from .geoluminate import *

geoluminate.setup(development=True)

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# removing validators for local development
AUTH_PASSWORD_VALIDATORS = []

# Verifying emails in development is annoying
# For testing, uncomment the following line
ACCOUNT_EMAIL_VERIFICATION = "optional"
