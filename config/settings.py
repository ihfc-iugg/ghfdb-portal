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


# DJANGO_SETUP_TOOLS[""]["on_initial"].append(("loaddata", "ghfdb_review_group.json"))

# FAIRDM_CONFIG = {
#     "home": {
#         "Explore": [
#             "home.map-viewer",
#             "home.ghfdb_projects",
#             "home.whfdb_project",
#             # "fdm.dashboard.latest-activity",
#         ],
#         "Create": [
#             "fdm.dashboard.login-signup",
#             "fdm.dashboard.create-project",
#             "fdm.dashboard.create-dataset",
#         ],
#         "Feedback & More": [
#             "home.issues",
#             "home.feedback",
#             "home.digitize",
#             "fdm.dashboard.user-guide",
#             "fdm.dashboard.fairdm-framework",
#         ],
#     },
#     "sponsors": [
#         {
#             "name": "GFZ German Research Centre for Geosciences",
#             "url": "https://www.gfz.de/en/",
#             "image": "img/web_logo_box_GFZ-min.png",
#         },
#         {
#             "name": "International Heat Flow Commission",
#             "url": "https://www.ihfc-iugg.org",
#             "image": "img/web_logo_box_IHFC-min.png",
#         },
#         {
#             "name": "DFG - Deutsche Forschungsgemeinschaft",
#             "url": "https://www.dfg.de/en/",
#             "image": "img/web_logo_box_DFG-min.png",
#         },
#     ],
# }

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
