"""Project settings: wires fairdm, then applies project-specific overrides."""

import os

import fairdm

fairdm.setup(
    apps=[
        "ghfdb",
        "heat_flow",
        "review",
        "fairdm_geo",
        # "fairdm_geo.geology.lithology",
        "fairdm_geo.geology.stratigraphy",
        # "fairdm_geo.geology.geologic_time",
    ],
    addons=[
        "fairdm_discussions",
    ],
)

DJANGO_SETUP_TOOLS = globals().get("DJANGO_SETUP_TOOLS", {})

# this line is only required during staging because no migrations are being committed to the fairdm repo
DJANGO_SETUP_TOOLS[""]["always_run"].insert(0, ("makemigrations", "--no-input"))
DJANGO_SETUP_TOOLS[""]["always_run"].append(("compress",))

MVP_CONFIG["layout"]["sidebar"]["title"] = "Heatflow.world"


EASY_ICONS["svg"]["icons"]["ihfc"] = "ihfc.svg"

CSRF_TRUSTED_ORIGINS = [
    f"https://{domain}" for domain in globals().get("ALLOWED_HOSTS", [])
]


# A second connection, defined only when the environment names a file for it, so that a
# test can migrate into an empty database without touching the developer's own.  The
# development settings hard-wire the SQLite path, so there is no other way to redirect a
# `migrate` run.  Inert unless MIGRATION_CHECK_DATABASE is set, which only
# tests/test_migrations.py does.
if os.environ.get("MIGRATION_CHECK_DATABASE"):
    DATABASES["migration_check"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ["MIGRATION_CHECK_DATABASE"],
    }
