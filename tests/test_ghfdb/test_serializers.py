from decimal import Decimal
from types import SimpleNamespace

from quantityfield.units import ureg
from rest_framework import serializers

from project.ghfdb.constants import PARENT_COLUMNS
from project.ghfdb.serializers import (
    ConceptLabelsField,
    PublishedValueField,
    published_fields,
)


class _FakeManager:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


def _bound(field, *, field_name):
    field.bind(field_name=field_name, parent=serializers.Serializer())
    return field


class TestPublishedValueField:
    def test_a_quantity_renders_as_its_float_magnitude(self):
        field = _bound(PublishedValueField(source="value"), field_name="q")
        instance = SimpleNamespace(value=ureg.Quantity(70.0, "mW/m^2"))

        assert field.to_representation(field.get_attribute(instance)) == 70.0

    def test_none_renders_as_null(self):
        field = _bound(PublishedValueField(source="value"), field_name="q")
        instance = SimpleNamespace(value=None)

        assert field.to_representation(field.get_attribute(instance)) is None

    def test_empty_string_renders_as_null(self):
        field = _bound(PublishedValueField(source="value"), field_name="q")
        instance = SimpleNamespace(value="")

        assert field.to_representation(field.get_attribute(instance)) is None

    def test_anything_else_passes_through(self):
        field = _bound(PublishedValueField(source="value"), field_name="q")
        instance = SimpleNamespace(value="onshore_continental")

        assert (
            field.to_representation(field.get_attribute(instance))
            == "onshore_continental"
        )

    def test_a_concept_renders_as_its_stored_code(self):
        # The annotation for a concept-valued column (e.g. `environment`) returns a
        # `research_vocabs.core.Concept`, the same object the field's `to_python()`
        # produces from its stored code (COR-001).
        from heat_flow.models import HeatFlowSite

        concept = HeatFlowSite._meta.get_field("environment").to_python(
            "onshore_continental"
        )
        field = _bound(PublishedValueField(source="value"), field_name="environment")
        instance = SimpleNamespace(value=concept)

        assert (
            field.to_representation(field.get_attribute(instance))
            == "onshore_continental"
        )

    def test_a_decimal_renders_as_a_float(self):
        # A coordinate column annotates a Decimal field; every other numeric column
        # is a JSON number, so a Decimal renders the same way a Pint quantity does
        # (COR-002).
        field = _bound(PublishedValueField(source="value"), field_name="lat_NS")
        instance = SimpleNamespace(value=Decimal("48.12340"))

        representation = field.to_representation(field.get_attribute(instance))

        assert representation == 48.1234
        assert isinstance(representation, float)


class TestConceptLabelsField:
    def test_a_prefetched_related_manager_renders_as_its_members_labels(self):
        field = _bound(
            ConceptLabelsField(source="method"), field_name="q_method"
        )
        members = _FakeManager(
            [SimpleNamespace(label="Bullard"), SimpleNamespace(label="Interval")]
        )
        instance = SimpleNamespace(method=members)

        assert field.to_representation(field.get_attribute(instance)) == [
            "Bullard",
            "Interval",
        ]

    def test_a_none_hop_on_the_path_renders_as_an_empty_list(self):
        field = _bound(
            ConceptLabelsField(source="sample.heatflowsite.explo_purpose"),
            field_name="explo_purpose",
        )
        instance = SimpleNamespace(sample=SimpleNamespace(heatflowsite=None))

        assert field.to_representation(field.get_attribute(instance)) == []


class TestPublishedFields:
    def test_returns_every_column_in_order_reading_registry_accessors(self):
        built = published_fields(PARENT_COLUMNS)

        assert list(built) == PARENT_COLUMNS

        class _Serializer(serializers.Serializer):
            def get_fields(self):
                return built

        bound = _Serializer().fields

        assert bound["name"].source == "site_name"
        assert bound["explo_purpose"].source == (
            "sample.heatflowsite.explo_purpose"
        )
        assert bound["q"].source == "q"
        assert isinstance(bound["q"], PublishedValueField)
        assert isinstance(bound["explo_purpose"], ConceptLabelsField)

    def test_an_override_replaces_the_accessor_for_one_column(self):
        built = published_fields(["name"], overrides={"name": "custom_accessor"})

        assert built["name"].source == "custom_accessor"
