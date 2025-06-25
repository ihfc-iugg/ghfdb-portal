import fairdm
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
]

fairdm.setup(
    apps=[
        "heat_flow",
        "ghfdb",
        "review",
        "fairdm_geo",
        # "fairdm_geo.geology.lithology",
        "fairdm_geo.geology.stratigraphy",
        # "fairdm_geo.geology.geologic_time",
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
        "submit_review": "fa-solid fa-clipboard-check",
    }
)

DJANGO_SETUP_TOOLS = globals().get("DJANGO_SETUP_TOOLS", {})

# this line is only required during staging because no migrations are being committed to the fairdm repo
DJANGO_SETUP_TOOLS[""]["always_run"].insert(0, ("makemigrations", "--no-input"))
DJANGO_SETUP_TOOLS[""]["on_initial"].append(("loaddata", "ghfdb_review_group.json"))


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

LOGIN_BACKGROUND_IMAGE = "img/stock/community.jpg"


FAIRDM_CONFIG = {
    "colors": {
        "primary": "#354b9b",
        "secondary": "#699bd1",
    },
    "home": {
        "explore": [
            "home.map-viewer",
            "fdm.dashboard.research-projects",
            "fdm.dashboard.latest-activity",
        ],
        "create": [
            "fdm.dashboard.create-project",
            "fdm.dashboard.create-dataset",
            "home.digitize",
        ],
        "more": [
            "fdm.dashboard.login-signup",
            "home.whfdb_project",
            "fdm.dashboard.user-guide",
            "fdm.dashboard.fairdm-framework",
        ],
    },
    "external_links": [
        {
            "url": "https://heatflow.world/",
            "name": "World Heat Flow Database Project",
        },
        {
            "url": "https://ihfc-iugg.com/",
            "name": "International Heat Flow Commission",
        },
    ],
    "documentation_url": "https://heatflowworld.readthedocs.io/en/latest/",
    "repository_url": "https://github.com/ihfc-iugg/ghfdb-portal",
    "header_links_before_dropdown": 5,
    "welcome_message": "Explore, create, and share heat flow data with the global research community.",
    "logo": {
        "text": _("Global Heat Flow Database Portal"),
        "image_dark": "img/brand/logo.svg",
        "image_light": "img/brand/logo.svg",
    },
    "announcement": "",
    # "navbar_start": [
    #     "pst.components.navbar-logo",
    # ],
    "navbar_persistent": ["sections.navbar.search"],
    "footer_start": ["copyright"],
    "footer_center": ["sphinx-version"],
    "back_to_top_button": True,
    "search_bar": False,
    "search_as_you_type": False,
    "sponsors": [
        {
            "name": "GFZ German Research Centre for Geosciences",
            "url": "https://www.gfz-potsdam.de/en/",
            "image": "img/brand/gfz-logo.png",
        },
        {
            "name": "International Heat Flow Commission",
            "url": "https://ihfc-iugg.com/",
            "image": "img/brand/ihfc-logo.png",
        },
        {
            "name": "DFG - Deutsche Forschungsgemeinschaft",
            "url": "https://www.dfg.de/en/",
            "image": "img/brand/dfg-logo.png",
        },
    ],
}
