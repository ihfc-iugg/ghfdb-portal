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
        elevation=ureg.Quantity(250, "m"),
        elevation_datum="MSL",
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


@pytest.fixture
def api_schema(db, client):
    # The generated OpenAPI schema's components, as the schema route serves them.
    response = client.get("/api/v1/schema/", {"format": "json"})

    assert response.status_code == 200
    return response.json()["components"]["schemas"]


@pytest.fixture
def constant_query_count(django_assert_num_queries):
    # Assert a callable's query count does not grow with row count (FR-016).

    def assert_constant(build, call, low=1, high=3):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        build(low)
        # A cold process pays a one-off ContentType lookup on the first call, so
        # call() once, uncounted, before the baseline measures steady-state cost.
        call()
        with CaptureQueriesContext(connection) as baseline:
            call()

        build(high)
        with django_assert_num_queries(len(baseline.captured_queries)):
            call()

    return assert_constant


@pytest.fixture
def private_dataset(db):
    # DatasetFactory defaults to a private dataset, which an anonymous request
    # never sees.
    return DatasetFactory()


@pytest.fixture
def site_graph(public_dataset):
    # A public site with its parent, two intervals and three children: the first
    # interval carries two (one not marked relevant), the second one.
    from tests.factories import (
        HeatFlowFactory,
        HeatFlowIntervalFactory,
        HeatFlowSiteFactory,
        ParentHeatFlowFactory,
    )

    site = HeatFlowSiteFactory(dataset=public_dataset)
    parent = ParentHeatFlowFactory(
        dataset=public_dataset, sample=site, value=65.5, uncertainty=4.5
    )
    shallow = HeatFlowIntervalFactory(
        dataset=public_dataset, site=site, top=0, bottom=100
    )
    deep = HeatFlowIntervalFactory(
        dataset=public_dataset, site=site, top=100, bottom=200
    )
    relevant = HeatFlowFactory(
        dataset=public_dataset, sample=shallow, parent=parent, is_relevant=True
    )
    other = HeatFlowFactory(
        dataset=public_dataset, sample=shallow, parent=parent, is_relevant=False
    )
    lone = HeatFlowFactory(
        dataset=public_dataset, sample=deep, parent=parent, is_relevant=True
    )
    # The children's saves recalculate the parent's stored quality.
    parent.refresh_from_db()
    return {
        "site": site,
        "parent": parent,
        "intervals": [shallow, deep],
        "children": {shallow.pk: [relevant, other], deep.pk: [lone]},
        "all_children": [relevant, other, lone],
    }


@pytest.fixture
def api_document(db, client):
    # The whole generated OpenAPI document, as the schema route serves it.
    response = client.get("/api/v1/schema/", {"format": "json"})

    assert response.status_code == 200
    return response.json()
