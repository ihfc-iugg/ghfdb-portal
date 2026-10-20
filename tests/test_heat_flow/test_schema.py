import pytest
from heat_flow.models import HeatFlowSite, ThermalGradient

TERM_PROPERTIES = {"name", "label", "uri", "vocabulary"}


def vocabulary_name(model, field_name):
    return model._meta.get_field(field_name).scheme.scheme().name


@pytest.mark.django_db
class TestTermFieldSchema:
    def test_a_single_term_is_an_object_whose_vocabulary_is_its_own(self, api_schema):
        term = api_schema["HeatFlowSiteSummary"]["properties"]["environment"]

        assert term["type"] == "object"
        assert set(term["properties"]) == TERM_PROPERTIES
        assert term["properties"]["vocabulary"]["enum"] == [
            vocabulary_name(HeatFlowSite, "environment")
        ]

    def test_an_empty_single_term_is_described_as_nullable(self, api_schema):
        term = api_schema["HeatFlowSiteSummary"]["properties"]["explo_method"]

        assert term["nullable"] is True

    def test_each_entry_of_a_many_valued_term_is_an_object(self, api_schema):
        field = api_schema["ThermalGradientSummary"]["properties"]["method_top"]

        assert field["type"] == "array"
        assert field["items"]["type"] == "object"
        assert set(field["items"]["properties"]) == TERM_PROPERTIES
        assert field["items"]["properties"]["vocabulary"]["enum"] == [
            vocabulary_name(ThermalGradient, "method_top")
        ]

    def test_the_vocabulary_differs_between_two_many_valued_terms(self, api_schema):
        properties = api_schema["ThermalGradientSummary"]["properties"]

        top = properties["method_top"]["items"]["properties"]["vocabulary"]["enum"]
        correction = properties["correction_top"]["items"]["properties"]["vocabulary"][
            "enum"
        ]
        assert top != correction


@pytest.mark.django_db
class TestUnitsFieldSchema:
    def test_units_lists_each_quantity_field_with_its_unit(self, api_schema):
        units = api_schema["HeatFlowSiteSummary"]["properties"]["units"]

        assert units["type"] == "object"
        assert {name: spec["enum"] for name, spec in units["properties"].items()} == {
            "azimuth": ["deg"],
            "inclination": ["deg"],
            "length": ["m"],
        }

    def test_a_type_without_quantities_beyond_its_own_lists_only_those(
        self, api_schema
    ):
        units = api_schema["ParentHeatFlowSummary"]["properties"]["units"]

        assert set(units["properties"]) == {"value", "uncertainty"}
