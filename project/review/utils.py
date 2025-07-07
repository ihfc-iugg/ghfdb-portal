from django.utils.translation import gettext as _

DOCUMENTATION_URL = "https://heatflowworld.readthedocs.io/en/latest/"


def docs_link(name):
    """
    Returns the URL for the documentation page with the given name.
    """
    return {
        "text": _("Learn More"),
        "icon": "fa-solid fa-book",
        "url": f"{DOCUMENTATION_URL}/{name}/",
    }
