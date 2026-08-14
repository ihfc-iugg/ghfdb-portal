"""
Shared pytest fixtures for the test_heat_flow test suite.

Constructs the complete object graph (site → interval → sub-measurements →
parent + child heat flow) used across US1–US3 tests.  All fixtures use
direct ORM calls – NOT factories – so they exercise the model validation
paths that the factories may bypass.
"""

import pytest
from fairdm.factories import DatasetFactory


@pytest.fixture
def dataset():
    """A minimal Dataset – infrastructure, not under test."""
    return DatasetFactory()


@pytest.fixture
def site_fixture(dataset):
    """A saved HeatFlowSite linked to *dataset*."""
    from heat_flow.models import HeatFlowSite

    return HeatFlowSite.objects.create(
        dataset=dataset,
        name="Test Site",
        country="Germany",
        continent="Europe",
        environment="onshore_continental",
    )


@pytest.fixture
def interval_fixture(dataset, site_fixture):
    """A depth interval (0–500 m) attached to *site_fixture*."""
    from heat_flow.models import HeatFlowInterval

    return HeatFlowInterval.objects.create(
        dataset=dataset,
        sample=site_fixture,
        name="Test Interval",
        top=0,
        bottom=500,
    )


@pytest.fixture
def gradient_fixture(dataset, interval_fixture):
    """A ThermalGradient sub-measurement linked to *interval_fixture*."""
    from heat_flow.models import ThermalGradient

    return ThermalGradient.objects.create(
        dataset=dataset,
        sample=interval_fixture,
        name="Test Gradient",
        value=25.0,
    )


@pytest.fixture
def conductivity_fixture(dataset, interval_fixture):
    """An IntervalConductivity sub-measurement linked to *interval_fixture*."""
    from heat_flow.models import IntervalConductivity

    return IntervalConductivity.objects.create(
        dataset=dataset,
        sample=interval_fixture,
        name="Test Conductivity",
        value=2.5,
    )


@pytest.fixture
def parent_fixture(dataset, site_fixture):
    """A ParentHeatFlow linked to *site_fixture*."""
    from heat_flow.models import ParentHeatFlow

    return ParentHeatFlow.objects.create(
        dataset=dataset,
        sample=site_fixture,
        name="Test Parent",
        value=70.0,
    )


@pytest.fixture
def child_fixture(
    dataset, interval_fixture, parent_fixture, gradient_fixture, conductivity_fixture
):
    """A HeatFlow child with all sub-measurement FKs set."""
    from heat_flow.models import HeatFlow

    return HeatFlow.objects.create(
        dataset=dataset,
        sample=interval_fixture,
        name="Test Child",
        value=70.0,
        parent=parent_fixture,
        thermal_gradient=gradient_fixture,
        thermal_conductivity=conductivity_fixture,
    )
