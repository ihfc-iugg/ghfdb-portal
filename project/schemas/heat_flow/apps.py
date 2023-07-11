from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HeatFlowConfig(AppConfig):
    """Config for the Global Heat Flow Database application"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "heat_flow"
    verbose_name = _("Heat Flow")
