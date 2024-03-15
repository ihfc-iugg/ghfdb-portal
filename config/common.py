"""Here you can define the common settings for the project. These are imported by the development and production settings files. Use this file to do things like adding extra apps, geoluminate plugins, middleware, etc. to your project."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = [
    # "django_json_widget",
    # "menu",
    # "simple_history",
    # "treewidget",
    # GHFDB Apps
    # "geoscience",
    # "geoscience.gis.plates",
    # "geoscience.gis.provinces",
    "heat_flow",
    # "glossary",
    # "review",
    # "thermal_data",
    # "well_logs",
]
