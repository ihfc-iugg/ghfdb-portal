"""How the OpenAPI schema describes the heat flow serializers' terms and units."""

from typing import Any

from drf_spectacular.extensions import (
    OpenApiSerializerExtension,
    OpenApiSerializerFieldExtension,
)
from drf_spectacular.plumbing import build_object_type
from drf_spectacular.utils import Direction

from .serializers import QuantityNumber


class HeatFlowRecordSchema(OpenApiSerializerExtension):
    """Describes a list of records as their summary and every other operation in full."""

    target_class = "heat_flow.serializers.HeatFlowRecordSerializer"
    match_subclasses = True

    def listed(self, auto_schema: Any) -> type | None:
        """Name the summary a list operation gives in place of the serializer.

        Args:
            auto_schema: The schema generator for the operation.

        Returns:
            The summary serializer for a list operation on a serializer that has
            one, otherwise ``None``.
        """
        if getattr(auto_schema.view, "action", None) != "list":
            return None
        return self.target.summary_serializer

    def get_name(self, auto_schema: Any, direction: Direction) -> str | None:
        """Give a list operation the component name of the summary.

        Args:
            auto_schema: The schema generator for the operation.
            direction: Whether the serializer is read or written.

        Returns:
            The summary's class name, or ``None`` to keep the serializer's own.
        """
        summary = self.listed(auto_schema)
        return summary.__name__ if summary else None

    def get_identity(self, auto_schema: Any, direction: Direction) -> Any:
        """Count the summary and the serializer a list stands in for as one component.

        Args:
            auto_schema: The schema generator for the operation.
            direction: Whether the serializer is read or written.

        Returns:
            The summary class for a list operation, otherwise ``None``.
        """
        return self.listed(auto_schema)

    def map_serializer(self, auto_schema: Any, direction: Direction) -> dict:
        """Describe the summary for a list operation and the serializer otherwise.

        Args:
            auto_schema: The schema generator for the operation.
            direction: Whether the serializer is read or written.

        Returns:
            The object schema.
        """
        summary = self.listed(auto_schema)
        if summary is None:
            return auto_schema._map_serializer(
                self.target, direction, bypass_extensions=True
            )
        return auto_schema._map_serializer(summary(), direction, bypass_extensions=True)


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
