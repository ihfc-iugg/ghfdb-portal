import geoluminate

from .common import *
from .geoluminate import *

SHOW_DEBUG_TOOLBAR = False
DEBUG = False
geoluminate.setup(development=True)
# geoluminate.setup(development=False)
DEBUG = False

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# removing validators for local development
AUTH_PASSWORD_VALIDATORS = []

# Verifying emails in development is annoying
# For testing, uncomment the following line
ACCOUNT_EMAIL_VERIFICATION = "optional"


AWS_USE_SSL = False

ALLOWED_HOSTS = ["*"]
COMPRESS_OFFLINE = True
COMPRESS_ENABLED = True

print("Compress offline: ", COMPRESS_OFFLINE)
print("Compress enabled: ", COMPRESS_ENABLED)

STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}
