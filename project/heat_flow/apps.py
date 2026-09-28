"""App configuration for the heat flow schema."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HeatFlowSchemaConfig(AppConfig):
    """Config for the heat flow schema."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "heat_flow"
    verbose_name = _("Heat Flow")

    keywords: list[str] = []
    repository_url = "https://github.com/ihfc-iugg/ghfdb-portal"
