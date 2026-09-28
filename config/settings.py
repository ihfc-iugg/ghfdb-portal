"""Project settings: wires fairdm, then applies project-specific overrides."""

import os

import fairdm

fairdm.setup(
    apps=[
        "ghfdb",
        "heat_flow",
        "review",
        "fairdm_geo",
        "fairdm_geo.geology.stratigraphy",
    ],
    addons=[
        "fairdm_discussions",
    ],
)

DJANGO_SETUP_TOOLS = globals().get("DJANGO_SETUP_TOOLS", {})

# Only required during staging: no migrations are committed to the fairdm repo.
DJANGO_SETUP_TOOLS[""]["always_run"].insert(0, ("makemigrations", "--no-input"))
DJANGO_SETUP_TOOLS[""]["always_run"].append(("compress",))

MVP_CONFIG["layout"]["sidebar"]["title"] = "Heatflow.world"


EASY_ICONS["svg"]["icons"]["ihfc"] = "ihfc.svg"

CSRF_TRUSTED_ORIGINS = [
    f"https://{domain}" for domain in globals().get("ALLOWED_HOSTS", [])
]


# A second connection, used only to migrate an empty database into for testing
# without touching the developer's own; inert unless MIGRATION_CHECK_DATABASE
# is set, which only tests/test_migrations.py does (#173).
if os.environ.get("MIGRATION_CHECK_DATABASE"):
    DATABASES["migration_check"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ["MIGRATION_CHECK_DATABASE"],
    }
