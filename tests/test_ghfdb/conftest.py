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
    """
    from research_vocabs.models import Concept

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
