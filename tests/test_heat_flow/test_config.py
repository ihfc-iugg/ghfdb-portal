"""
Tests for heat_flow FairDM registry configuration – User Story US4.

US4: All models are registered with FairDM (T042–T043, T047–T048).
"""

import fairdm
import pytest

ALL_MODELS_NAMES = [
    "HeatFlowSite",
    "HeatFlowInterval",
    "ParentHeatFlow",
    "HeatFlow",
    "ThermalGradient",
    "IntervalConductivity",
]


def _get_all_models():
    from heat_flow.models import (
        HeatFlow,
        HeatFlowInterval,
        HeatFlowSite,
        IntervalConductivity,
        ParentHeatFlow,
        ThermalGradient,
    )

    return [
        HeatFlowSite,
        HeatFlowInterval,
        ParentHeatFlow,
        HeatFlow,
        ThermalGradient,
        IntervalConductivity,
    ]


def test_all_six_models_registered():
    """
    T042 – All six heat-flow models appear in the FairDM registry (FR-030, SC-005).
    Fails before T044 (ParentHeatFlow not yet registered).
    """
    for model in _get_all_models():
        assert fairdm.registry.is_registered(model), (
            f"{model.__name__} is not registered with the FairDM registry"
        )


def test_registry_config_has_fields():
    """
    T042 – Every registered model config declares a non-empty fields list (FR-024, M3).
    """
    for model in _get_all_models():
        config = fairdm.registry.get_for_model(model)
        assert bool(config.fields), f"{model.__name__} config.fields is empty"


@pytest.mark.django_db
def test_system_checks_pass():
    """
    T043 – Django system checks pass with zero errors after all registrations (SC-001).
    """
    from django.core.management import call_command

    call_command("check")
