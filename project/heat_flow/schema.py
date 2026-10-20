"""How the OpenAPI schema describes the heat flow serializers' terms and units."""

from typing import Any

from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_object_type
from drf_spectacular.utils import Direction

from .serializers import QuantityNumber


class TermFieldSchema(OpenApiSerializerFieldExtension):
    """Describes a single vocabulary term as an object naming its vocabulary."""

    target_class = "heat_flow.serializers.TermChoiceField"

    def map_serializer_field(self, auto_schema: Any, direction: Direction) -> dict:
        """Describe the term the field gives.

        Args:
            auto_schema: The schema generator for the operation.
            direction: Whether the field is read or written.

        Returns:
            An object with ``name``, ``label``, ``uri`` and ``vocabulary``, the last
            limited to the field's vocabulary, and nullable when the field allows null.
        """
        schema = build_object_type(
            properties={
                "name": {"type": "string"},
                "label": {"type": "string"},
                "uri": {"type": "string", "format": "uri"},
                "vocabulary": {"type": "string", "enum": [self.target.vocabulary]},
            },
            required=["name", "label", "uri", "vocabulary"],
        )
        if self.target.allow_null:
            schema["nullable"] = True
        return schema


class TermRelatedFieldSchema(TermFieldSchema):
    """Describes each entry of a many-valued vocabulary field as a term object."""

    target_class = "heat_flow.serializers.TermRelatedField"


class UnitsFieldSchema(OpenApiSerializerFieldExtension):
    """Describes a record's units as an object with a property for each quantity."""

    target_class = "heat_flow.serializers.UnitsField"

    def map_serializer_field(self, auto_schema: Any, direction: Direction) -> dict:
        """Describe the units of the quantity fields beside the field.

        Args:
            auto_schema: The schema generator for the operation.
            direction: Whether the field is read or written.

        Returns:
            An object with one property for each quantity field, each limited to its unit.
        """
        return build_object_type(
            properties={
                name: {"type": "string", "enum": [field.unit]}
                for name, field in self.target.parent.fields.items()
                if isinstance(field, QuantityNumber)
            },
            required=[],
        )
