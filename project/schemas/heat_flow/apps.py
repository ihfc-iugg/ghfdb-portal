from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HeatFlowSchemaConfig(AppConfig):
    """Config for heat flow schema"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "heat_flow"
    verbose_name = _("Heat Flow")

    # HeatFlow = {"list_display": ["q", "q_uncertainty"]}
    # HeatFlowChild = {}
