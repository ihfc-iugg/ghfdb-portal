"""
Base settings to build other settings files upon.
"""
from pathlib import Path

import environ
from django.utils.translation import gettext_lazy as _
from geoluminate.conf.local_defaults import *

GEOLUMINATE = {
    "db_name": "Global Heat Flow Database",
    "db_acronym": "GHFDB",
    "governing_body": {
        "name": "International Heat Flow Commission",
        "short_name": "IHFC",
        "website": "https://www.ihfc-iugg.org",
    },
    "base_model": "geoluminate.contrib.gis.base.AbstractSite",
    "keywords": ["heat flow", "geothermal", "geoenergy"],
}

# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("Sam Jennings", "jennings@gfz-potsdam.de")]

# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = "info@heatflow.world"

# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = [
    # "django_json_widget",
    # "menu",
    # "simple_history",
    "treewidget",
    # GHFDB Apps
    "geoscience",
    "geoscience.gis.plates",
    "geoscience.gis.provinces",
    "ghfdb",
    "review",
    # "thermal_data",
    # "well_logs",
]


# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
# MIDDLEWARE.insert("whitenoise.middleware.WhiteNoiseMiddleware", 2)


env = environ.Env()

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

deferred_settings(globals())

# PLACE ADDITIONAL SETTINGS BELOW HERE
# -------------------------------

EARTH_MATERIALS_INCLUDE = [
    "Igneous rock and sediment",
    "Metamorphic rock",
    "Sediment and sedimentary rock",
]


TREEWIDGET_SETTINGS = {
    "search": True,
    # 'show_buttons': True
    "can_add_related": False,
}


TREEWIDGET_TREEOPTIONS = {
    "core": {
        "themes": {
            "variant": "large",
            "icons": False,
        },
    },
    "search": {
        # 'fuzzy':True,
        "show_only_matches": True,
    },
    "checkbox": {
        "three_state": False,
    },
    "plugins": ["checkbox"],
}


SPAGHETTI_SAUCE = {
    "apps": ["database", "literature"],
    "show_fields": False,
    "exclude": {"auth": ["user"]},
}
