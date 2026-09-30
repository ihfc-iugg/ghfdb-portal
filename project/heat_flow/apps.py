"""App configuration for the heat flow schema."""

from django.apps import AppConfig
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
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
        from .models import (
            HeatFlow,
            HeatFlowCorrection,
            IntervalConductivity,
            ThermalGradient,
        )

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

        pre_save.connect(
            signals.remember_parent_before_save,
            sender=HeatFlow,
            dispatch_uid="remember_parent_before_save_HeatFlow",
        )
        post_save.connect(
            signals.refresh_child_on_save,
            sender=HeatFlow,
            dispatch_uid="refresh_quality_on_save_HeatFlow",
        )
        post_save.connect(
            signals.refresh_child_on_correction_save,
            sender=HeatFlowCorrection,
            dispatch_uid="refresh_quality_on_save_HeatFlowCorrection",
        )
        post_delete.connect(
            signals.refresh_parent_on_child_delete,
            sender=HeatFlow,
            dispatch_uid="refresh_parent_on_delete_HeatFlow",
        )
        post_delete.connect(
            signals.refresh_child_on_correction_delete,
            sender=HeatFlowCorrection,
            dispatch_uid="refresh_quality_on_delete_HeatFlowCorrection",
        )
