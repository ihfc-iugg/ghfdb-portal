from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GHFDBConfig(AppConfig):
    """Config for heat flow schema"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ghfdb"
    verbose_name = _("Global Heat Flow Database")

    keywords = []
    repository_url = "https://github.com/ihfc-iugg/ghfdb-portal"
