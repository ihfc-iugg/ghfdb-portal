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
            "fdm.dashboard.digitize",
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
    "header_links_before_dropdown": 5,
    "icon_links": [
        {
            "name": "Documentation",
            "url": "https://heatflowworld.readthedocs.io/en/latest/",
            "icon": "fa-solid fa-book",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/FAIR-DM/fairdm",
            "icon": "fa-brands fa-github fa-lg",
        },
        {
            "name": "Login",
            "url": "/account/login/",
            "icon": "fa-solid fa-right-to-bracket fa-lg",
        },
    ],
    "logo": {
        "text": "FairDM",
        "image_dark": "img/brand/logo.svg",
        "image_light": "img/brand/logo.svg",
    },
    "announcement": "",
    "navbar_start": [
        "pst.components.navbar-logo",
    ],
    "navbar_center": [
        "pst.components.navbar-nav",
    ],
    "navbar_end": [
        "pst.components.theme-switcher",
        "pst.components.navbar-icon-links",
        # "dac.sections.user-sidebar",
    ],
    "navbar_persistent": ["pst.components.search-button-field"],
    "footer_start": ["copyright"],
    "footer_center": ["sphinx-version"],
    "back_to_top_button": True,
    "search_bar": False,
    "search_as_you_type": False,
}

html_sidebars = {
    "community/index": [
        "sidebar-nav-bs",
        "custom-template",
    ],  # This ensures we test for custom sidebars
    "examples/no-sidebar": [],  # Test what page looks like with no sidebar items
    "examples/persistent-search-field": ["search-field"],
    # Blog sidebars
    # ref: https://ablog.readthedocs.io/manual/ablog-configuration-options/#blog-sidebars
    "examples/blog/*": [
        "ablog/postcard.html",
        "ablog/recentposts.html",
        "ablog/tagcloud.html",
        "ablog/categories.html",
        "ablog/authors.html",
        "ablog/languages.html",
        "ablog/locations.html",
        "ablog/archives.html",
    ],
}

html_context = {
    "github_user": "pydata",
    "github_repo": "pydata-sphinx-theme",
    "github_version": "main",
    "doc_path": "docs",
}
CSRF_TRUSTED_ORIGINS = [f"https://{domain}" for domain in globals().get("ALLOWED_HOSTS", [])]
