# Shared pytest fixtures for the test_heat_flow test suite. Constructs the complete
# object graph (site → interval → sub-measurements → parent + child heat flow) used
# across US1–US3 tests.

import pytest
from fairdm.factories import DatasetFactory


@pytest.fixture
def dataset(db):
    return DatasetFactory()


@pytest.fixture
def site_fixture(dataset):
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
    from heat_flow.models import HeatFlowInterval

    return HeatFlowInterval.objects.create(
        dataset=dataset,
        site=site_fixture,
        name="Test Interval",
        top=0,
        bottom=500,
    )


@pytest.fixture
def gradient_fixture(dataset, interval_fixture):
    from heat_flow.models import ThermalGradient

    return ThermalGradient.objects.create(
        dataset=dataset,
        sample=interval_fixture,
        name="Test Gradient",
        value=25.0,
    )


@pytest.fixture
def conductivity_fixture(dataset, interval_fixture):
    from heat_flow.models import IntervalConductivity

    return IntervalConductivity.objects.create(
        dataset=dataset,
        sample=interval_fixture,
        name="Test Conductivity",
        value=2.5,
    )


@pytest.fixture
def parent_fixture(dataset, site_fixture):
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


@pytest.fixture
def public_dataset(db):
    # An anonymous API request reads only a public, published dataset's records.
    from fairdm.utils.choices import Visibility

    return DatasetFactory(visibility=Visibility.PUBLIC, published=True)


@pytest.fixture
def full_records(public_dataset):
    # One record of each of the six types with every vocabulary field and every
    # quantity filled, in a public, published dataset (FS-010).
    from heat_flow.models import HeatFlowSite
    from quantityfield.units import ureg
    from research_vocabs.models import Concept

    from tests.factories import (
        HeatFlowFactory,
        HeatFlowIntervalFactory,
        HeatFlowSiteFactory,
        IntervalConductivityFactory,
        ParentHeatFlowFactory,
        ThermalGradientFactory,
    )

    def concepts(model, field_name, count):
        vocabulary = model._meta.get_field(field_name).vocabulary
        return list(Concept.get_for_vocabulary(vocabulary).order_by("name")[:count])

    site = HeatFlowSiteFactory(
        dataset=public_dataset,
        environment="onshore_continental",
        azimuth=45.5,
        inclination=10.25,
        length=ureg.Quantity(1000, "ft"),
        explo_purpose=concepts(HeatFlowSite, "explo_purpose", 2),
    )
    site.lithology.set(concepts(HeatFlowSite, "lithology", 2))
    site.age.set(concepts(HeatFlowSite, "age", 1))
    interval = HeatFlowIntervalFactory(
        dataset=public_dataset, site=site, top=10.5, bottom=200.5, vertical_depth=190
    )
    gradient = ThermalGradientFactory(
        dataset=public_dataset,
        sample=interval,
        value="25.50",
        uncertainty="1.25",
        corrected_value="26.50",
        corrected_uncertainty="1.50",
        shutin_top=12,
        shutin_bottom=24,
    )
    conductivity = IntervalConductivityFactory(
        dataset=public_dataset, sample=interval, value="2.50", uncertainty="0.25"
    )
    parent = ParentHeatFlowFactory(
        dataset=public_dataset, sample=site, value=65.5, uncertainty=4.5
    )
    child = HeatFlowFactory(
        dataset=public_dataset,
        sample=interval,
        parent=parent,
        thermal_gradient=gradient,
        thermal_conductivity=conductivity,
        value=70.5,
        uncertainty=5.5,
    )
    return {
        "site": site,
        "interval": interval,
        "gradient": gradient,
        "conductivity": conductivity,
        "parent": parent,
        "child": child,
    }
