from decimal import Decimal

import pytest
from django.core.management import call_command
from fairdm.models import Dataset
from ghfdb.resources import GHFDBResource
from ghfdb.views import GHFDBImportFormat
from heat_flow.models import (
    HeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    SurfaceHeatFlow,
    ThermalGradient,
)
from research_vocabs.models import Concept

pytestmark = pytest.mark.django_db


def get_file(filename):
    """Helper function to get the file path for the test data."""
    with open(filename, "rb") as f:
        return f.read()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        Concept.preload()
        call_command("loaddata", "creativecommons")


@pytest.fixture
def dataset():
    """Fixture to create the dataset instance."""
    return Dataset.objects.create(name="Test Dataset")


@pytest.fixture
def importer_fail(dataset):
    """Fixture to create the importer instance."""
    resource = GHFDBResource(dataset)
    file = get_file("tests/data/importer_fail.xlsx")
    input_format = GHFDBImportFormat(encoding="utf-8-sig")
    input_data = input_format.create_dataset(file)
    return resource.import_data(input_data, raise_errors=True, dry_run=True)


@pytest.fixture
def success_resource(dataset):
    """Fixture to create a resource instance for successful import."""
    resource = GHFDBResource(dataset=dataset)
    return resource


@pytest.fixture
def importer_success(success_resource):
    """Fixture to create the importer instance."""
    file = get_file("tests/data/importer_success.xlsx")
    input_format = GHFDBImportFormat(encoding="utf-8-sig")
    input_data = input_format.create_dataset(file)
    return success_resource.import_data(input_data, raise_errors=True, dry_run=False)


@pytest.fixture
def row(importer_success):
    """Fixture to create a row instance."""
    return importer_success.df.iloc[0]


# class TestGHFDBImporterMixin:
#     """Test the GHFDBImporterMixin class. The mixin contains common functionality across all GHFDB importers."""

#     def test_importer_loads_dataset(self, importer_success):
#         assert importer_success.df is not None
#         assert importer_success.df.shape[0] == 3
#         # make sure the column headers contain the expected values (or at least one of them)
#         assert "q" in importer_success.df.columns
#         # make sure the square brackets are removed from controlled vocabulary columns (the portal does not use them)
#         assert importer_success.df.loc[0, "T_method_top"] == "cLOG"

#     @pytest.mark.parametrize(
#         "geo_lithology, expected_lithology",
#         [
#             ("sandstone; shale; limestone", ["sandstone", "shale", "limestone"]),
#             ("sandstone ;    shale; limestone  ", ["sandstone", "shale", "limestone"]),  # Test with extra whitespace
#             ("basalt; granite", ["basalt", "granite"]),
#             ("", []),  # Test with an empty string
#             (None, []),
#             ("clay", ["clay"]),  # Test with a single lithology
#             ("sandstone; ; shale", ["sandstone", "shale"]),  # Test with extra separators
#         ],
#     )
#     def test_clean_geo_lithology(self, importer_success, geo_lithology, expected_lithology):
#         """Mkae sure geo_lithology is cleaned properly during import"""
#         # Create a row with the provided geo_lithology value
#         row = importer_success.df.iloc[0]
#         row["geo_lithology"] = geo_lithology

#         # Call the modify_row method
#         new_row = importer_success.modify_row(row, ParentHeatFlow, {})

#         # Assert that the modified row has the expected lithology list
#         assert new_row["geo_lithology"] == expected_lithology


def relation_contains(qs, field, value):
    """Helper function to check if a relation exists in the list of relations."""
    all_values = qs.values_list(field, flat=True)
    return value.issubset(all_values)


class TestSuccesfulImport:
    def test_resource_has_no_errors(self, importer_success):
        """Test that the resource has no errors after a successful import."""
        result = importer_success
        assert result.has_errors() is False
        assert result.has_validation_errors() is False

    def test_heat_flow_site_created(self, success_resource, importer_success):
        # Test that the HeatFlowSite is created and has the expected fields
        assert HeatFlowSite.objects.count() == 1
        obj = HeatFlowSite.objects.first()
        assert obj.elevation.magnitude == 67.00
        assert obj.elevation_datum.name == "MSL"
        assert obj.name == "Test name"
        assert obj.environment.label() == "Offshore (continental)"
        assert obj.explo_method.label() == "Drilling"
        assert obj.explo_purpose.filter(label__in=["Hydrocarbon"]).exists()
        assert obj.age.filter(name__in=["Cenozoic"]).exists()
        assert obj.country == "Spain"
        assert obj.region == "Southern Europe"
        assert obj.continent == "Europe"
        assert obj.domain == "Continental"
        assert relation_contains(obj.lithology, "name", {"granite", "sediment"})
        assert obj.length.magnitude == 105.00
        assert obj.top.magnitude == 0  # Note: this is using a defult value of 0 for the top field
        assert obj.bottom.magnitude == 100  # Note: this is being calculated from the vertical depth and top fields
        assert obj.vertical_depth.magnitude == 100.00
        assert obj.location is not None
        assert obj.location.x == Decimal("-5.61667")
        assert obj.location.y == Decimal("43.63333")

        # Test relations
        assert obj.dataset == success_resource.dataset
        assert obj.measurements.count() == 1
        assert obj.measurements.instance_of(SurfaceHeatFlow).count() == 1

    def test_heat_flow_parent_created(self, success_resource, importer_success):
        """Test that the SurfaceHeatFlow instance is created and has the expected fields."""
        assert SurfaceHeatFlow.objects.count() == 1
        obj = SurfaceHeatFlow.objects.first()

        assert obj.value.magnitude == 45.0
        assert obj.uncertainty.magnitude == 5.0
        assert obj.name == "Test name"  # this is the current behavior but it is unclear if it is desirable
        assert obj.is_ghfdb is False  # this is the current behavior but it is unclear if it is desirable
        assert obj.corr_HP_flag is True  # failing

        # test relations
        assert obj.dataset == success_resource.dataset
        assert obj.sample == HeatFlowSite.objects.first()  # related to the correct heat flow site

    def test_heat_flow_interval_created(self, success_resource, importer_success):
        assert HeatFlowInterval.objects.count() == 1
        obj = HeatFlowInterval.objects.first()
        # test import fields
        assert obj.top.magnitude == 10
        assert obj.bottom.magnitude == 45
        assert obj.vertical_depth.magnitude == 35
        assert obj.age.filter(name__in=["Cenozoic"]).exists()
        assert relation_contains(obj.lithology, "name", {"granite", "sediment"})

        # test relations
        assert obj.dataset == success_resource.dataset
        # there should be a HeatFlow, IntervalConductivity and ThermalGradient measurement
        assert obj.measurements.count() == 3
        assert obj.measurements.instance_of(HeatFlow).count() == 1
        assert obj.measurements.instance_of(IntervalConductivity).count() == 1
        assert obj.measurements.instance_of(ThermalGradient).count() == 1

        # make sure the location data is correct
        assert obj.location is not None
        assert obj.location.x == Decimal("-5.61667")
        assert obj.location.y == Decimal("43.63333")

        # site = HeatFlowSite.objects.first()

        # make sure the relation to the HeatFlowSite is established
        # assert obj.related_samples.filter(related_to=site, type="child_of").exists()

    def test_heat_flow_created(self, success_resource, importer_success):
        assert HeatFlow.objects.count() == 1
        obj = HeatFlow.objects.first()

        assert obj.name == "Test name"  # unclear if this is desirable
        assert obj.value.magnitude == 63
        assert obj.uncertainty.magnitude == 3.6
        assert obj.expedition == "Test Expedition"
        assert obj.relevant_child is True  # "Yes"
        assert obj.probe_penetration.magnitude == 6.5
        assert obj.probe_length.magnitude == 12
        assert obj.probe_tilt.magnitude == 20
        assert relation_contains(obj.probe_type, "name", {"bullard"})
        assert obj.water_temperature.magnitude == 10
        # Note below that date_acquired is a PartialDate object so we cannot do a direct comparison.
        assert str(obj.date_acquired) == "1990-04"  # "1990-04"
        assert obj.IGSN is None
        assert relation_contains(obj.corr_IS_flag, "label", {"not considered"})
        assert obj.corr_T_flag.exists() is False  # "Unspecified"
        assert obj.corr_S_flag.name == "present_not_significant"  # "Present not significant"
        assert obj.corr_E_flag.name == "not_recognized"  # "Not recognized"
        assert obj.corr_TOPO_flag.name == "present_not_corrected"  # "Present and not corrected"
        assert obj.corr_PAL_flag.name == "present_corrected"  # "Present and corrected"
        assert obj.corr_SUR_flag is None  # "Unspecified"
        assert obj.corr_CONV_flag is None  # "Unspecified"
        assert obj.corr_HR_flag is None  # "Unspecified"

        assert relation_contains(obj.method, "label", {"Interval method"})
        assert obj.c_comment == "Test comment"

    def test_thermal_gradient_created(self, success_resource, importer_success):
        """Test that the ThermalGradient instance is created and has the expected fields."""
        assert ThermalGradient.objects.count() == 1
        obj = ThermalGradient.objects.first()

        assert obj.value.magnitude == 22
        assert obj.uncertainty.magnitude == 2
        assert obj.corrected_value.magnitude == 27
        assert obj.corrected_uncertainty.magnitude == 2.5
        assert obj.shutin_top.magnitude == 1
        assert obj.shutin_bottom.magnitude == 20
        assert obj.number == 250
        assert relation_contains(obj.method_top, "name", {"cLOG"})
        assert relation_contains(obj.method_bottom, "name", {"DTSeq"})
        assert relation_contains(obj.correction_top, "name", {"hornerPlot"})
        assert relation_contains(obj.correction_bottom, "name", {"lineSourceExplosion"})

        # test relations
        assert obj.dataset == success_resource.dataset
        assert obj.sample == HeatFlowInterval.objects.first()
        assert obj.heat_flow_child == HeatFlow.objects.first()

    def test_interval_conductivity_created(self, success_resource, importer_success):
        """Test that the ThermalGradient instance is created and has the expected fields."""
        assert IntervalConductivity.objects.count() == 1
        obj = IntervalConductivity.objects.first()

        assert obj.value.magnitude == Decimal("2.1")
        assert obj.uncertainty.magnitude == Decimal("0.45")
        assert obj.number == 100
        assert relation_contains(obj.source, "name", {"assumed_from_literature"})
        assert relation_contains(obj.location, "name", {"literature"})
        assert relation_contains(obj.method, "name", {"lithology"})
        assert relation_contains(obj.saturation, "name", {"saturatedInSitu"})
        assert relation_contains(obj.pT_conditions, "name", {"replicatedP"})
        assert relation_contains(obj.pT_function, "name", {"Tikhomirov1968"})
        assert relation_contains(obj.strategy, "name", {"characterize"})

        # test relations
        assert obj.dataset == success_resource.dataset
        assert obj.sample == HeatFlowInterval.objects.first()
        assert obj.heat_flow_child == HeatFlow.objects.first()
