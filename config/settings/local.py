import environ

from geoluminate.conf.local_defaults import *

from .base import *  # noqa
from .base import env

DEBUG = True

HIDE_DEBUG_TOOLBAR = True
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))


DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        # "HOST": env("POSTGRES_HOST"),
        # "PORT": env("POSTGRES_PORT"),
        # "CONN_MAX_AGE": 0,
        # "ATOMIC_REQUESTS": True,
    },
}

# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="HoVcnlU2IqQN1YqvsY7dQ1xtdhLavAeXn1mUEAI0Wu8vkDbodEqRKkJbHyMEQS5F",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = env("EMAIL_HOST", default="mailhog")
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025

# WhiteNoise
# ------------------------------------------------------------------------------

INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa F405


INSTALLED_APPS += [
    "debug_toolbar",
]


# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405


DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}

# DEBUG_TOOLBAR_PANELS += [
#     "template_profiler_panel.panels.template.TemplateProfilerPanel",
# ]

INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]


# if env("USE_DOCKER") == "yes":
#     import socket

#     hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
#     INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]


INSTALLED_APPS += ["django_extensions"]  # noqa F405


# Celery
# ------------------------------------------------------------------------------

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True


# ADDITIONAL SETTINGS
# ------------------------------------------------------------------------------
COMPRESS_OFFLINE = False

COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)
