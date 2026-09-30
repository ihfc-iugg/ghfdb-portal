"""App configuration for the heat flow schema."""

from django.apps import AppConfig
from django.db.models.signals import m2m_changed, post_save
from django.utils.translation import gettext_lazy as _


class HeatFlowSchemaConfig(AppConfig):
    """Config for the heat flow schema."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "heat_flow"
    verbose_name = _("Heat Flow")

    keywords: list[str] = []
    repository_url = "https://github.com/ihfc-iugg/ghfdb-portal"

    def ready(self):
        """Connect the receivers that keep stored quality scores current."""
        from . import signals
        from .models import IntervalConductivity, ThermalGradient

        for model in (ThermalGradient, IntervalConductivity):
            post_save.connect(
                signals.refresh_measurement_on_save,
                sender=model,
                dispatch_uid=f"refresh_score_on_save_{model.__name__}",
            )
            for name in model.SCORED_CONCEPT_FIELDS:
                m2m_changed.connect(
                    signals.refresh_measurement_on_concepts,
                    sender=getattr(model, name).through,
                    dispatch_uid=f"refresh_score_on_{model.__name__}_{name}",
                )
