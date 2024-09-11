import os

import geoluminate

os.environ.setdefault("DJANGO_ENV", "development")
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


EARTH_SCIENCE_X_COORD = {
    "decimal_places": 5,
    "max_digits": None,
}

EARTH_SCIENCE_Y_COORD = {
    "decimal_places": 5,
    "max_digits": None,
}

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
