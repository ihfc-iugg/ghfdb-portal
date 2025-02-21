import fairdm
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
]

fairdm.setup(
    apps=[
        "heat_flow",
        "fairdm_geo",
        "fairdm_geo.geology.lithology",
        "fairdm_geo.geology.stratigraphy",
        "fairdm_geo.geology.geologic_time",
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

DJANGO_SETUP_TOOLS = globals().get("DJANGO_SETUP_TOOLS", {})

# this line is only required during staging because no migrations are being committed to the fairdm repo
DJANGO_SETUP_TOOLS[""]["always_run"].insert(0, ("makemigrations", "--no-input"))
DJANGO_SETUP_TOOLS[""]["on_initial"].append(("loaddata", "dump.json"))


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

# INSTALLED_APPS += [
#     "django_model_info.apps.DjangoModelInfoConfig",
# ]


# import os
# import pprint

# pprint.pprint(os.environ.__dict__)


# if not env("POSTGRES_HOST"):
#     print("Using sqlite3")

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "filters": {
#         "require_debug_true": {
#             "()": RequireDebugTrue,  # Only log in DEBUG mode
#         },
#     },
#     "handlers": {
#         "console": {
#             "level": "DEBUG",
#             "filters": ["require_debug_true"],
#             "class": "logging.StreamHandler",
#         },
#     },
#     "loggers": {
#         "django.server": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#             "propagate": False,
#         },
#         "import_export": {
#             "handlers": ["console"],
#             "level": "INFO",
#         },
#     },
# }

#
# INSTALLED_APPS += [
#     "django_classy_doc",
# ]


# CLASSY_DOC_BASES = ["heat_flow", "fairdm_geo"]
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
