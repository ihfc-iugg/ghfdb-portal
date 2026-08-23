"""
Shared pytest fixtures for the test_ghfdb test suite.

Constructs the complete object graph used across all GHFDB tests:
  HeatFlowSite → HeatFlowInterval (with ProbeMetadata) → ParentHeatFlow
  → HeatFlow (linked to ThermalGradient, IntervalConductivity, and
    HeatFlowCorrection instances for all 9 correction types).

Also provides a ``sample_ghfdb_row`` fixture with a minimal valid dict of
GHFDB flat-column values for import testing.
"""

import pytest
from fairdm.factories import DatasetFactory


@pytest.fixture(autouse=True)
def load_concepts(db):
    """Ensure all vocabulary concepts are in the test DB before each test.

    Mirrors the autouse fixture in test_resources/conftest.py so that
    admin filter-choice tests (T063) also have vocabulary data available.

    ``Concept.preload()`` only preloads vocabularies already present in
    ``research_vocabs``' global ``vocab_registry``, and registration there is
    normally a side effect of a model field's own ``__init__``.
    ``RelatedConceptMixin`` (``ConceptManyToManyField``) does this. The
    single-valued ``ConceptField`` does not — its registration call is
    commented out in ``research_vocabs.fields.BaseConceptField.__init__``
    (upstream gap, not ours to fix here). ``HeatFlowSite.environment`` and
    ``HeatFlowSite.explo_method`` are both ``ConceptField``, so without this,
    their concepts silently never load and every filter or fixture that
    depends on them finds nothing (T002).
    """
    from research_vocabs import registry
    from research_vocabs.models import Concept

    from heat_flow.vocabularies import ExplorationMethod, GeographicEnvironment

    for vocabulary in (GeographicEnvironment, ExplorationMethod):
        registry.register(vocabulary())

    if not Concept.objects.exists():
        Concept.preload()


@pytest.fixture
def dataset():
    """A minimal Dataset — infrastructure, not under test."""
    return DatasetFactory()


@pytest.fixture
def heat_flow_chain(dataset):
    """
    Complete GHFDB record chain required by all GHFDB tests.

    Returns the child ``HeatFlow`` instance; related objects are accessible
    via its FK/reverse-FK relations.
    """
    from heat_flow.models import (
        HeatFlow,
        HeatFlowCorrection,
        HeatFlowInterval,
        HeatFlowSite,
        IntervalConductivity,
        ParentHeatFlow,
        ProbeMetadata,
        ThermalGradient,
    )

    site = HeatFlowSite.objects.create(
        dataset=dataset,
        name="Test Site",
        country="Germany",
        continent="Europe",
        environment="onshore_continental",
    )

    interval = HeatFlowInterval.objects.create(
        dataset=dataset,
        site=site,
        name="Test Interval",
        top=0,
        bottom=500,
    )

    ProbeMetadata.objects.create(
        interval=interval,
        penetration=3.5,
    )

    gradient = ThermalGradient.objects.create(
        dataset=dataset,
        sample=interval,
        name="Test Gradient",
        value=25.0,
    )

    conductivity = IntervalConductivity.objects.create(
        dataset=dataset,
        sample=interval,
        name="Test Conductivity",
        value=2.5,
    )

    parent = ParentHeatFlow.objects.create(
        dataset=dataset,
        sample=site,
        name="Test Parent",
        value=70.0,
        ghfdb_id=1,
    )

    child = HeatFlow.objects.create(
        dataset=dataset,
        sample=interval,
        name="Test Child",
        value=70.0,
        parent=parent,
        thermal_gradient=gradient,
        thermal_conductivity=conductivity,
        ghfdb_id=1,
    )

    # Create all 9 HeatFlowCorrection instances
    for correction_type, _ in HeatFlowCorrection.CorrectionTypeChoices.choices:
        HeatFlowCorrection.objects.create(
            heat_flow=child,
            correction_type=correction_type,
            status=HeatFlowCorrection.StatusChoices.UNSPECIFIED,
        )

    return child


@pytest.fixture
def sample_ghfdb_row():
    """
    Minimal valid dict of GHFDB flat-column values for import testing.

    Column names match the official GHFDB spreadsheet headers.
    """
    return {
        "ID": "1",
        "ID_parent": "1",
        "name": "test_site",
        "lat_NS": "48.0",
        "long_EW": "11.0",
        "elevation": "",
        "Country": "Germany",
        "Region": "",
        "Continent": "Europe",
        "Domain": "",
        "environment": "onshore_continental",  # internal vocabulary value; vocabulary label is "Onshore (continental)"
        "explo_method": "",
        "explo_purpose": "",
        "total_depth_MD": "",
        "total_depth_TVD": "",
        "q": "70.0",
        "q_uncertainty": "5.0",
        "q_top": "0",
        "q_bottom": "500",
        "q_method": "",
        "q_date": "",
        "T_grad_mean": "25.0",
        "T_grad_uncertainty": "",
        "T_grad_mean_cor": "",
        "T_grad_uncertainty_cor": "",
        "T_method_top": "",
        "T_method_bottom": "",
        "T_shutin_top": "",
        "T_shutin_bottom": "",
        "T_corr_top": "",
        "T_corr_bottom": "",
        "T_number": "",
        "tc_mean": "2.5",
        "tc_uncertainty": "",
        "tc_source": "",
        "tc_location": "",
        "tc_method": "",
        "tc_saturation": "",
        "tc_pT_conditions": "",
        "tc_pT_function": "",
        "tc_number": "",
        "tc_strategy": "",
        "probe_penetration": "",
        "probe_type": "",
        "probe_length": "",
        "probe_tilt": "",
        "water_temperature": "",
        "corr_HP_flag": "No",
        "corr_IS_flag": "",
        "corr_T_flag": "",
        "corr_S_flag": "",
        "corr_E_flag": "",
        "corr_TOPO_flag": "",
        "corr_PAL_flag": "",
        "corr_SUR_flag": "",
        "corr_CONV_flag": "",
        "corr_HR_flag": "",
        "geo_lithology": "",
        "geo_stratigraphy": "",
        "c_comment": "",
        "p_comment": "",
        "Reviewer_name": "Test Reviewer",
        "publication_reference": "test_ref_2024",
    }


# ---------------------------------------------------------------------------
# Phase 1 foundations (T004-T010) for 002-ghfdb-proxy.
#
# Distinct from ``heat_flow_chain`` above, which the pre-existing test suite
# still depends on and which this run leaves alone. These fixtures use the
# naming ``tasks.md`` specifies, and are built by direct ORM calls, per
# ``tests/README.md``.
# ---------------------------------------------------------------------------


def build_site_and_parent(dataset, *, name="Test Site", published=True, ghfdb_id=1):
    """Create a ``HeatFlowSite`` and its ``ParentHeatFlow``.

    Returns the parent; the site is reachable as ``parent.sample``. Shared by
    every fixture below, so the published, unpublished and multi-site
    variants build the same graph rather than each repeating it.
    """
    from heat_flow.models import HeatFlowSite, ParentHeatFlow

    site = HeatFlowSite.objects.create(
        dataset=dataset,
        name=name,
        country="Germany",
        continent="Europe",
        environment="onshore_continental",
    )
    return ParentHeatFlow.objects.create(
        dataset=dataset,
        sample=site,
        name=f"{name} Parent",
        value=70.0,
        ghfdb_id=ghfdb_id if published else None,
    )


def build_child(
    dataset,
    parent,
    *,
    name="Test Child",
    published=True,
    include_gradient=True,
    include_conductivity=True,
    include_probe_metadata=True,
    missing_correction=None,
    is_relevant=False,
    ghfdb_id=1,
):
    """Create one child ``HeatFlow`` under *parent*, with its interval, its
    sub-measurements and all nine corrections.

    Each keyword omits exactly the one piece it names, so the partial-chain
    fixtures reuse this builder rather than each writing their own graph.
    """
    from heat_flow.models import (
        HeatFlow,
        HeatFlowCorrection,
        HeatFlowInterval,
        IntervalConductivity,
        ProbeMetadata,
        ThermalGradient,
    )

    interval = HeatFlowInterval.objects.create(
        dataset=dataset,
        site=parent.sample,
        name=f"{name} Interval",
        top=0,
        bottom=500,
    )

    if include_probe_metadata:
        ProbeMetadata.objects.create(interval=interval, penetration=3.5)

    gradient = None
    if include_gradient:
        gradient = ThermalGradient.objects.create(
            dataset=dataset,
            sample=interval,
            name=f"{name} Gradient",
            value=25.0,
        )

    conductivity = None
    if include_conductivity:
        conductivity = IntervalConductivity.objects.create(
            dataset=dataset,
            sample=interval,
            name=f"{name} Conductivity",
            value=2.5,
        )

    child = HeatFlow.objects.create(
        dataset=dataset,
        sample=interval,
        name=name,
        value=70.0,
        parent=parent,
        thermal_gradient=gradient,
        thermal_conductivity=conductivity,
        is_relevant=is_relevant,
        ghfdb_id=ghfdb_id if published else None,
    )

    for correction_type in HeatFlowCorrection.CorrectionTypeChoices.values:
        if correction_type == missing_correction:
            continue
        HeatFlowCorrection.objects.create(
            heat_flow=child,
            correction_type=correction_type,
            status=HeatFlowCorrection.StatusChoices.UNSPECIFIED,
        )

    return child


def build_published_chain(dataset, *, published=True, ghfdb_id=1, **child_kwargs):
    """Build one complete site -> parent -> child chain (T004)."""
    parent = build_site_and_parent(dataset, published=published, ghfdb_id=ghfdb_id)
    return build_child(
        dataset, parent, published=published, ghfdb_id=ghfdb_id, **child_kwargs
    )


@pytest.fixture
def published_chain(dataset):
    """One complete record chain with the published identifier set (T004)."""
    return build_published_chain(dataset)


@pytest.fixture
def published_chains(dataset):
    """Callable building *n* complete, published record chains (T005, R2).

    Every query-constancy test takes this at two sizes rather than one, per
    R2's decision — a bound satisfied at one row is satisfied by a linear
    query plan as well as by a constant one.
    """

    def build(count):
        return [
            build_published_chain(dataset, ghfdb_id=index)
            for index in range(1, count + 1)
        ]

    return build


@pytest.fixture
def unpublished_chain(dataset):
    """One complete chain with no published identifier at either level.

    This is what SC-005 is proven against (T006).
    """
    return build_published_chain(dataset, published=False)


@pytest.fixture
def chain_without_gradient(dataset):
    """A published chain missing only its thermal gradient (T007)."""
    return build_published_chain(dataset, include_gradient=False)


@pytest.fixture
def chain_without_conductivity(dataset):
    """A published chain missing only its interval conductivity (T007)."""
    return build_published_chain(dataset, include_conductivity=False)


@pytest.fixture
def chain_without_probe_metadata(dataset):
    """A published chain missing only its probe metadata (T007)."""
    return build_published_chain(dataset, include_probe_metadata=False)


@pytest.fixture
def chain_missing_correction(dataset):
    """Callable building a published chain missing one named correction type
    (T007)."""

    def build(correction_type):
        return build_published_chain(dataset, missing_correction=correction_type)

    return build


@pytest.fixture
def sites_by_contribution(dataset):
    """Four sites covering SC-004's contribution shapes (T008).

    Returns a dict keyed by shape name: every determination contributing,
    some, none, and one site with no determinations at all. The
    ``all_contributing`` site also carries two exploration purposes, so the
    one many-valued parent column is exercised — without it nothing would
    notice a site rendering twice.
    """
    from research_vocabs.models import Concept

    from heat_flow.vocabularies import ExplorationPurpose

    purposes = list(Concept.get_for_vocabulary(ExplorationPurpose)[:2])

    def make_site(name, relevance_flags, ghfdb_id):
        parent = build_site_and_parent(dataset, name=name, ghfdb_id=ghfdb_id)
        for offset, is_relevant in enumerate(relevance_flags, start=1):
            build_child(
                dataset,
                parent,
                is_relevant=is_relevant,
                ghfdb_id=ghfdb_id * 10 + offset,
                name=f"{name} child {offset}",
            )
        return parent

    all_contributing = make_site("All contributing", [True, True], ghfdb_id=1)
    all_contributing.sample.explo_purpose.set(purposes)

    some_contributing = make_site("Some contributing", [True, False], ghfdb_id=2)
    none_contributing = make_site("None contributing", [False, False], ghfdb_id=3)
    no_determinations = make_site("No determinations", [], ghfdb_id=4)

    return {
        "all_contributing": all_contributing,
        "some_contributing": some_contributing,
        "none_contributing": none_contributing,
        "no_determinations": no_determinations,
    }
