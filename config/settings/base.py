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

GEOLUMINATE_SAMPLE_TYPES = ["Heat Flow Site"]

GEOLUMINATE_KEYWORD_CHOICES = [
    "heat_flow.vocabularies.ISC2020",
    "heat_flow.vocabularies.SimpleLithology",
]

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
    "apps": ["ghfdb", "literature"],
    "show_fields": False,
    "exclude": {"auth": ["user"]},
}
