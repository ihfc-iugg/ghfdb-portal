import geoluminate
from django.utils.translation import gettext_lazy as _

# pprint(INSTALLED_APPS)


LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
]


geoluminate.setup(
    apps=[
        "heat_flow",
        "earth_science",
        "earth_science.location",
        "earth_science.geology.lithology",
        "earth_science.geology.stratigraphy",
        "earth_science.geology.geologic_time",
    ]
)


EASY_ICONS = globals().get("EASY_ICONS", {})

EASY_ICONS["aliases"].update(
    {
        "geology": "fas fa-mountain",
        "lithology": "fas fa-layer-group",
        "stratigraphy": "fas fa-layer-group",
        "geologic_time": "fas fa-clock",
        "location": "fas fa-map-marker-alt",
        "map": "fas fa-map-location-dot",
        "heat_flow": "fas fa-fire",
        "review": "fas fa-highlighter",
    }
)

# DEPLOYMENT_PIPELINE = {}

DJANGO_SETUP_TOOLS = globals().get("DJANGO_SETUP_TOOLS", {})

# this line is only required during staging because no migrations are being committed to the geoluminate repo
DJANGO_SETUP_TOOLS[""]["always_run"].insert(0, ("makemigrations", "--no-input"))


PARLER_LANGUAGES = {
    1: (
        {"code": "en"},
        {"code": "de"},
    ),
    "default": {
        "fallback": "en",  # Default fallback language
        "hide_untranslated": False,  # Show entries even if no translation exists
    },
}

EARTH_SCIENCE_X_COORD = {
    "decimal_places": 5,
    "max_digits": None,
}

EARTH_SCIENCE_Y_COORD = {
    "decimal_places": 5,
    "max_digits": None,
}


COMPRESS_ENABLED = True
COMPRESS_OFFLINE = False

# if DEBUG:
#     INSTALLED_APPS += [
#         "django_browser_reload",
#     ]

# DJANGO_SETUP_TOOLS = {
#     "": {
#         "on_initial": [
#             ("makemigrations", "--no-input"),
#             ("migrate", "--no-input"),
#             ("createsuperuser", "--no-input", "--first_name", "Super", "--last_name", "User"),
#             ("loaddata", "creativecommons"),
#         ],
#         "always_run": [
#             ("makemigrations", "--no-input"),
#             ("migrate", "--no-input"),
#             "django_setup_tools.scripts.sync_site_id",
#             ("collectstatic", "--noinput"),
#             ("compress",),
#         ],
#     },
#     # "development": {
#     #     "on_initial": [
#     #         ("loaddata", "myapp"),
#     #     ],
#     #     "always_run": [
#     #         "django_setup_tools.scripts.some_extra_func",
#     #     ],
#     # },
#     # "production": {
#     #     "on_initial": [
#     #         # ("loaddata", "myapp"),
#     #     ],
#     #     "always_run": [
#     #         ("collectstatic", "--noinput"),
#     #         ("compress",),
#     #     ],
#     # },
# }


# print(env.str("POSTGRES_USER"))
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": env.str("POSTGRES_DB"),
#         "PASSWORD": env.str("POSTGRES_PASSWORD"),
#         "USER": env.str("POSTGRES_USER"),
#         "HOST": env.str("POSTGRES_HOST"),
#         "PORT": env.str("POSTGRES_PORT"),
#     }
# }


# pprint(DATABASES)

# INSTALLED_APPS += [
#     "django_classy_doc",
# ]


# CLASSY_DOC_BASES = ["heat_flow", "earth_science"]
# # CLASSY_DOC_NON_INSTALLED_APPS = ['django.views.generic']
# CLASSY_DOC_MODULE_TYPES = [
#     "models",
# ]

# CLASSY_KNOWN_APPS = {
#     "django": ["django"],
#     "samples": ["samples"],
#     "polymorphic_treebeard": ["polymorphic_treebeard"],
#     "polymorphic": ["polymorphic"],
#     "treebeard": ["treebeard"],
# }
