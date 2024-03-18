import os

import geoluminate

from .common import *
from .geoluminate import *

# need to fix this in geoluminate package
SHOW_DEBUG_TOOLBAR = False

geoluminate.setup(development=False)

STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            # "format": "{levelname} {asctime} {module}:{funcName} {message}",
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",  # Adjust the level as needed
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",  # Adjust the level as needed
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "debug.log"),
            "formatter": "verbose",
        },
        # "mail_admins": {"level": "ERROR", "class": "django.utils.log.AdminEmailHandler", "formatter": "simple"},
    },
    "loggers": {
        # "django": {
        #     # "handlers": ["console", "file"],
        #     "handlers": ["console"],
        #     "level": "INFO",  # Adjust the level as needed
        #     "propagate": True,
        # },
        "geoluminate": {  # Replace with the name of your Django app
            "handlers": ["file", "console"],
            "level": "DEBUG",  # Adjust the level as needed
            "propagate": False,
        },
        # "django.request": {
        #     "handlers": ["mail_admins"],
        #     "level": "ERROR",
        #     "propagate": True,
        # },
    },
}
