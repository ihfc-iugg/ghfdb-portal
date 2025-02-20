from decimal import Decimal

import pytest
from fairdm.models import Dataset
from fairdm_geo.geology.geologic_time.models import GeologicalTimescale
from fairdm_geo.geology.lithology.models import SimpleLithology

from heat_flow.importer import ChildHeatFlowImporter, HeatFlowParentImporter  # noqa: F401
from heat_flow.models import ChildHeatFlow, HeatFlowInterval, HeatFlowSite, ParentHeatFlow

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        SimpleLithology.preload()
        GeologicalTimescale.preload()


@pytest.fixture
def dataset():
    """Fixture to create the dataset instance."""
    return Dataset.objects.create(title="Test Dataset")


@pytest.fixture
def importer_fail(dataset):
    """Fixture to create the importer instance."""
    return HeatFlowParentImporter("tests/data/importer_fail.xlsx", dataset)


@pytest.fixture
def importer_success(dataset):
    """Fixture to create the importer instance."""
    return HeatFlowParentImporter("tests/data/importer_success.xlsx", dataset)


@pytest.fixture
def row(importer_success):
    """Fixture to create a row instance."""
    return importer_success.df.iloc[0]


@pytest.fixture
def row_fail(importer_fail):
    """Fixture to create a row instance."""
    return importer_fail.df.iloc[0]


class TestGHFDBImporterMixin:
    """Test the GHFDBImporterMixin class. The mixin contains common functionality across all GHFDB importers."""

    def test_importer_loads_dataset(self, importer_success):
        assert importer_success.df is not None
        assert importer_success.df.shape[0] == 3
        # make sure the column headers contain the expected values (or at least one of them)
        assert "q" in importer_success.df.columns
        # make sure the square brackets are removed from controlled vocabulary columns (the portal does not use them)
        assert importer_success.df.loc[0, "T_method_top"] == "cLOG"

    @pytest.mark.parametrize(
        "geo_lithology, expected_lithology",
        [
            ("sandstone; shale; limestone", ["sandstone", "shale", "limestone"]),
            ("sandstone ;    shale; limestone  ", ["sandstone", "shale", "limestone"]),  # Test with extra whitespace
            ("basalt; granite", ["basalt", "granite"]),
            ("", []),  # Test with an empty string
            (None, []),
            ("clay", ["clay"]),  # Test with a single lithology
            ("sandstone; ; shale", ["sandstone", "shale"]),  # Test with extra separators
        ],
    )
    def test_clean_geo_lithology(self, importer_success, geo_lithology, expected_lithology):
        """Mkae sure geo_lithology is cleaned properly during import"""
        # Create a row with the provided geo_lithology value
        row = importer_success.df.iloc[0]
        row["geo_lithology"] = geo_lithology

        # Call the modify_row method
        new_row = importer_success.modify_row(row, ParentHeatFlow, {})

        # Assert that the modified row has the expected lithology list
        assert new_row["geo_lithology"] == expected_lithology


class TestSuccesfulImport:
    def test_heat_flow_site_created(self, importer_success):
        index, row = next(importer_success.df.iterrows())
        errors = importer_success.process_row(index, row.to_dict())
        assert not errors
        assert HeatFlowSite.objects.count() == 1
        site = HeatFlowSite.objects.first()
        # test import fields
        assert site.elevation.magnitude == 67.00
        assert site.name == "Test name"
        assert site.environment == "offshore_continental"  # "Offshore (continental)"

        assert site.length.magnitude == 105.00
        assert site.vertical_depth.magnitude == 100.00
        assert site.explo_method == "drilling"  # "Drilling"
        assert site.explo_purpose == "hydrocarbon"  # "Hydrocarbon"
        assert site.location is not None
        assert site.location.x == Decimal("-5.61667")
        assert site.location.y == Decimal("43.63333")

        # test relations
        assert site.dataset == importer_success.dataset
        assert site.measurements.count() == 1
        # assert site.lithology.count() == 3
        # assert site.stratigraphy.count() == 1

        # test additional fields (defined on mixin models)
        assert site.top.magnitude == 0
        assert site.bottom.magnitude == 100

    def test_heat_flow_parent_created(self, importer_success):
        index, row = next(importer_success.df.iterrows())
        errors = importer_success.process_row(index, row.to_dict())
        assert not errors
        site = HeatFlowSite.objects.first()
        assert ParentHeatFlow.objects.count() == 1
        hf_parent = ParentHeatFlow.objects.first()

        # test import fields
        assert hf_parent.q.magnitude == 45.0
        assert hf_parent.q_uncertainty.magnitude == 5.0
        assert hf_parent.corr_HP_flag is True

        # test relations
        assert hf_parent.sample.get_real_instance() == site  # related to the correct heat flow site
        assert hf_parent.children.count() == 1  # has one child associated with it

    def test_heat_flow_interval_created(self, importer_success):
        index, row = next(importer_success.df.iterrows())
        errors = importer_success.process_row(index, row.to_dict())
        assert not errors
        site = HeatFlowSite.objects.first()
        assert HeatFlowInterval.objects.count() == 1
        di = HeatFlowInterval.objects.first()
        # test import fields
        assert di.top.magnitude == 10
        assert di.bottom.magnitude == 45
        assert di.vertical_depth.magnitude == 35

        # test relations
        assert di.get_parent() == site  # related to the correct heat flow site
        assert di.dataset == importer_success.dataset
        assert di.measurements.count() == 1
        assert di.lithology.count() == 2
        assert di.age.count() == 1

    def test_heat_flow_child_created(self, importer_success):
        index, row = next(importer_success.df.iterrows())
        errors = importer_success.process_row(index, row.to_dict())
        assert not errors
        di = HeatFlowInterval.objects.first()
        hf_child = ChildHeatFlow.objects.first()
        hf_parent = ParentHeatFlow.objects.first()

        assert ChildHeatFlow.objects.count() == 1
        assert hf_child.parent == hf_parent
        assert hf_child.sample.get_real_instance() == di

        # test import fields
        assert hf_child.qc.magnitude == 63
        assert hf_child.qc_uncertainty.magnitude == 3.6
        assert hf_child.q_method == "interval"  # "Interval method"
        # assert hf_child.relevant_child is True
        assert hf_child.c_comment == "Test comment"
        # assert hf_child.expedition == "Test expedition"
        # assert hf_child.probe_type == "Single Steel probe (Bullard)"  # "Single Steel probe (Bullard)"
        assert hf_child.probe_length.magnitude == 12
        # assert hf_child.probe_tilt.magnitude == 20
        # assert hf_child.length.magnitude == 10 # from probe penetration depth
        assert hf_child.water_temperature.magnitude == 10

        # test temperature fields
        assert hf_child.T_grad_mean.magnitude == 22
        assert hf_child.T_grad_uncertainty.magnitude == 2
        assert hf_child.T_grad_mean_cor.magnitude == 27
        assert hf_child.T_grad_uncertainty_cor.magnitude == 2.5
        assert hf_child.T_method_top == "cLOG"  # "cLOG"
        assert hf_child.T_method_bottom == "DTSeq"  # "DTSeq"
        assert hf_child.T_shutin_top.magnitude == 1
        assert hf_child.T_shutin_bottom.magnitude == 20
        assert hf_child.T_corr_top == "hornerPlot"  # "Horner plot"
        assert hf_child.T_corr_bottom == "lineSourceExplosion"  # "Line source explosion method"
        assert hf_child.T_number == 250

        # test tc fields
        assert hf_child.tc_mean.magnitude == Decimal("2.1")
        assert hf_child.tc_uncertainty.magnitude == Decimal("0.45")
        assert hf_child.tc_source == "assumed_from_literature"  # "Assumed from literature"
        assert hf_child.tc_location == "literature"  # "Literature/unspecified"
        assert hf_child.tc_method == "lithology"  # "Estimation - from lithology and literature"
        assert hf_child.tc_saturation == "saturatedInSitu"  # "Saturated measured In-situ"
        assert hf_child.tc_pT_conditions == "replicatedP"  # "Replicated in-situ (p)"
        assert hf_child.tc_pT_function == "Tikhomirov1968"  # "T - Tikhomirov (1968)"
        assert hf_child.tc_number == 100
        assert hf_child.tc_strategy == "characterize"  # "Single"

        # test flags
        assert hf_child.corr_IS_flag == "unspecified"  # "Unspecified"
        assert hf_child.corr_T_flag == "unspecified"  # "Unspecified"
        assert hf_child.corr_S_flag == "present_not_significant"  # "Present not significant"
        assert hf_child.corr_E_flag == "not_recognized"  # "Not recognized"
        assert hf_child.corr_TOPO_flag == "present_not_corrected"  # "Present and not corrected"
        assert hf_child.corr_PAL_flag == "present_corrected"  # "Present and corrected"
        assert hf_child.corr_SUR_flag == "unspecified"  # "Unspecified"
        assert hf_child.corr_CONV_flag == "unspecified"
        assert hf_child.corr_HR_flag == "unspecified"

        # date fields
        # assert hf_child.q_date.magnitude == 1990
