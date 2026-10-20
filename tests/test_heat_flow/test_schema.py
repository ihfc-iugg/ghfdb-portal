import pytest
from drf_spectacular.drainage import GENERATOR_STATS
from drf_spectacular.generators import SchemaGenerator
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


SITES = "/api/v1/samples/heat-flow-sites/"
PARENTS = "/api/v1/measurements/parent-heat-flow/"


def response_schema(document, path):
    operation = document["paths"][path]["get"]
    return operation["responses"]["200"]["content"]["application/json"]["schema"]


def component_name(reference):
    return reference["$ref"].rsplit("/", 1)[1]


def list_item_component(document, path):
    schema = response_schema(document, path)
    page = document["components"]["schemas"][component_name(schema)]
    return component_name(page["properties"]["results"]["items"])


@pytest.mark.django_db
class TestHeatFlowRecordSchema:
    def test_the_site_list_item_is_the_summary_with_a_parent_and_no_intervals(
        self, api_document
    ):
        name = list_item_component(api_document, SITES)

        properties = api_document["components"]["schemas"][name]["properties"]
        assert "parent" in properties
        assert "intervals" not in properties

    def test_the_single_site_is_the_full_record_with_intervals(self, api_document):
        schema = response_schema(api_document, f"{SITES}{{uuid}}/")

        properties = api_document["components"]["schemas"][component_name(schema)][
            "properties"
        ]
        assert "intervals" in properties
        assert "parent" in properties

    def test_the_parent_list_item_has_no_children_and_the_single_parent_has(
        self, api_document
    ):
        components = api_document["components"]["schemas"]

        item = components[list_item_component(api_document, PARENTS)]["properties"]
        single = components[
            component_name(response_schema(api_document, f"{PARENTS}{{uuid}}/"))
        ]["properties"]

        assert "children" not in item
        assert "children" in single

    def test_generating_the_schema_emits_no_component_warnings(self, db, capsys):
        GENERATOR_STATS.reset()

        SchemaGenerator().get_schema(request=None, public=True)

        emitted = capsys.readouterr().err
        assert "components with identical names" not in emitted
        assert "re-register" not in emitted
