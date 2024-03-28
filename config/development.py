import geoluminate

from .common import *
from .geoluminate import *

SHOW_DEBUG_TOOLBAR = False
DEBUG = True
geoluminate.setup(development=True)

GEOLUMINATE_LABELS["sample"] = {"verbose_name": "Heat Flow Site", "verbose_name_plural": "Heat Flow Sites"}


# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# removing validators for local development
AUTH_PASSWORD_VALIDATORS = []

# Verifying emails in development is annoying
# For testing, uncomment the following line
ACCOUNT_EMAIL_VERIFICATION = "optional"


AWS_USE_SSL = False

ALLOWED_HOSTS = ["*"]
# COMPRESS_OFFLINE = False
# COMPRESS_ENABLED = False

# STORAGES["staticfiles"] = {
#     "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
# }
