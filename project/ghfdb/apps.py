"""App configuration for the GHFDB product-layer Django app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GhfdbConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "project.ghfdb"
    label = "ghfdb"
    verbose_name = _("GHFDB")
