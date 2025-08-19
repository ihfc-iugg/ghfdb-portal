import fairdm
from botocore.config import Config
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ("en", _("English")),
    # ("de", _("German")),
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
    ],
    addons=[
        "fairdm_discussions",
        "fairdm_api",
    ],
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
DJANGO_SETUP_TOOLS[""]["always_run"].append(("compress",))
# DJANGO_SETUP_TOOLS[""]["on_initial"].append(("loaddata", "ghfdb_review_group.json"))

PARLER_LANGUAGES = {
    1: (
        {"code": "en"},
        # {"code": "de"},
    ),
    "default": {
        "fallback": "en",  # Default fallback language
        "hide_untranslated": False,  # Show entries even if no translation exists
    },
}

# These are required for the switch to GFZ dog service
AWS_STORAGE_BUCKET_NAME = "dog-ext.heatflow-world.ghfdb"
AWS_S3_ENDPOINT_URL = "https://s3.gfz-potsdam.de"
AWS_S3_CLIENT_CONFIG = Config(
    request_checksum_calculation="when_required", response_checksum_validation="when_required"
)


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


FAIRDM_CONFIG = {
    "colors": {
        "primary": "#354b9b",
        "secondary": "#699bd1",
    },
    "home": {
        "Explore": [
            "home.map-viewer",
            "home.ghfdb_projects",
            "home.whfdb_project",
            # "fdm.dashboard.latest-activity",
        ],
        "Create": [
            "fdm.dashboard.login-signup",
            "fdm.dashboard.create-project",
            "fdm.dashboard.create-dataset",
        ],
        "Feedback & More": [
            "home.issues",
            "home.feedback",
            "home.digitize",
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
    "sponsors": [
        {
            "name": "GFZ German Research Centre for Geosciences",
            "url": "https://www.gfz.de/en/",
            "image": "img/web_logo_box_GFZ-min.png",
        },
        {
            "name": "International Heat Flow Commission",
            "url": "https://www.ihfc-iugg.org",
            "image": "img/web_logo_box_IHFC-min.png",
        },
        {
            "name": "DFG - Deutsche Forschungsgemeinschaft",
            "url": "https://www.dfg.de/en/",
            "image": "img/web_logo_box_DFG-min.png",
        },
    ],
}

CSRF_TRUSTED_ORIGINS = [f"https://{domain}" for domain in globals().get("ALLOWED_HOSTS", [])]
