"""API serializers for the heat flow record types.

Every vocabulary term is an object carrying its label and identifier, every quantity
is a JSON number in the unit its field is stored in, and each record names those units
in ``units`` (FS-010).
"""

from typing import Any, cast

from fairdm.api.serializers import BaseMeasurementSerializer, BaseSampleSerializer
from quantityfield import fields as quantity_fields
from quantityfield.fields import QuantityFieldMixin
from quantityfield.units import ureg
from research_vocabs import models as vocabulary_models
from research_vocabs.fields import BaseConceptField, ConceptManyToManyField
from rest_framework import serializers

from .models import (
    HeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ThermalGradient,
)


def term(concept: Any) -> dict[str, str] | None:
    """Give a vocabulary term as its name, label, identifier and vocabulary.

    Args:
        concept: A ``research_vocabs`` concept, either the value of a ``ConceptField``
            or a stored concept row, or ``None``.

    Returns:
        The term, or ``None`` when there is no concept.
    """
    if concept is None or concept == "":
        return None
    if isinstance(concept, vocabulary_models.Concept):
        return {
            "name": concept.name,
            "label": concept.label,
            "uri": concept.uri,
            "vocabulary": concept.vocabulary.name,
        }
    return {
        "name": concept.name,
        "label": concept.label(),
        "uri": str(concept.URI),
        "vocabulary": concept.vocabulary.scheme().name,
    }


class TermChoiceField(serializers.ChoiceField):
    """A single vocabulary term, written as its name and read as a term object."""

    def __init__(self, *, vocabulary: str, **kwargs: Any) -> None:
        """Remember the vocabulary the choices come from.

        Args:
            vocabulary: The name of the field's vocabulary.
            **kwargs: Passed to ``ChoiceField``, including ``choices``.
        """
        self.vocabulary = vocabulary
        super().__init__(**kwargs)

    def get_attribute(self, instance: Any) -> Any:
        """Read the concept, turning the name a request has just written into one."""
        value = super().get_attribute(instance)
        if isinstance(value, str):
            value = instance._meta.get_field(self.source).to_python(value)
        return value

    def to_representation(self, value: Any) -> Any:
        """Give the term the stored name stands for.

        Args:
            value: The stored concept.

        Returns:
            The term, or ``None`` when the field is empty.
        """
        return term(value)


class TermRelatedField(serializers.RelatedField):
    """A term from a many-valued vocabulary field, read-only."""

    def __init__(self, *, vocabulary: str, **kwargs: Any) -> None:
        """Remember the vocabulary the terms come from.

        Args:
            vocabulary: The name of the field's vocabulary.
            **kwargs: Passed to ``RelatedField``.
        """
        self.vocabulary = vocabulary
        super().__init__(**kwargs)

    def to_representation(self, value: Any) -> dict[str, str] | None:
        """Give one stored concept as a term.

        Args:
            value: The stored concept row.

        Returns:
            The term.
        """
        return term(value)


class QuantityNumber:
    """Reads a quantity as a plain number in the unit the model field is stored in.

    Attributes:
        number: The type the magnitude is given as.
        base_units: The unit the model field is stored in.
        unit: The unit as it is written in a record's ``units``.
    """

    number: type = float

    def __init__(self, *, base_units: str, unit: str, **kwargs: Any) -> None:
        """Remember the model field's unit.

        Args:
            base_units: The unit the model field is stored in.
            unit: The unit as it is written in a record's ``units``.
            **kwargs: Passed to the number field this is mixed into.
        """
        self.base_units = base_units
        self.unit = unit
        super().__init__(**kwargs)

    def to_representation(self, value: Any) -> Any:
        """Give the magnitude in the stored unit.

        Args:
            value: A quantity, or the plain number a request has just written.

        Returns:
            The magnitude as a JSON number.
        """
        if isinstance(value, ureg.Quantity):
            value = value.to(self.base_units).magnitude
        return self.number(value)


class QuantityFloatField(QuantityNumber, serializers.FloatField):
    """A floating point quantity."""


class QuantityDecimalField(QuantityNumber, serializers.DecimalField):
    """A decimal quantity, given as a float because the renderer would write a string."""


class QuantityIntegerField(QuantityNumber, serializers.IntegerField):
    """A whole-number quantity."""

    number = int


class UnitsField(serializers.Field):
    """The unit of every quantity among the serializer's fields, by field name."""

    def __init__(self, **kwargs: Any) -> None:
        """Read the whole record and never write.

        Args:
            **kwargs: Passed to ``Field``.
        """
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, value: Any) -> dict[str, str]:
        """Name the unit of each quantity field, whatever the record holds.

        Args:
            value: The record, unused.

        Returns:
            The unit for each quantity field of the parent serializer.
        """
        return {
            name: field.unit
            for name, field in cast(serializers.Serializer, self.parent).fields.items()
            if isinstance(field, QuantityNumber)
        }


class HeatFlowRecordSerializer(serializers.ModelSerializer):
    """Gives a heat flow record its terms, its numbers and its units."""

    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        quantity_fields.QuantityField: QuantityFloatField,
        quantity_fields.DecimalQuantityField: QuantityDecimalField,
        quantity_fields.PositiveIntegerQuantityField: QuantityIntegerField,
    }

    units = UnitsField()

    def build_standard_field(
        self, field_name: str, model_field: Any
    ) -> tuple[type, dict[str, Any]]:
        """Build a vocabulary field as a term and a quantity field with its unit.

        Args:
            field_name: The model field's name.
            model_field: The model field.

        Returns:
            The serializer field class and its keyword arguments.
        """
        field_class, kwargs = super().build_standard_field(field_name, model_field)
        if isinstance(model_field, BaseConceptField):
            kwargs["vocabulary"] = model_field.scheme.scheme().name
            return TermChoiceField, kwargs
        if isinstance(model_field, QuantityFieldMixin):
            kwargs["base_units"] = model_field.base_units
            kwargs["unit"] = f"{model_field.ureg(model_field.base_units).units:~C}"
        return field_class, kwargs

    def build_relational_field(
        self, field_name: str, relation_info: Any
    ) -> tuple[type, dict[str, Any]]:
        """Build a many-valued vocabulary field as terms and any other relation as text.

        Args:
            field_name: The model field's name.
            relation_info: What DRF found out about the relation.

        Returns:
            The serializer field class and its keyword arguments.
        """
        model_field = relation_info.model_field
        if isinstance(model_field, ConceptManyToManyField):
            return TermRelatedField, {
                "many": True,
                "read_only": True,
                "vocabulary": model_field.scheme.scheme().name,
            }
        return serializers.StringRelatedField, {
            "many": relation_info.to_many,
            "read_only": True,
        }


class HeatFlowSiteSummarySerializer(HeatFlowRecordSerializer, BaseSampleSerializer):
    """A heat flow site."""

    class Meta(BaseSampleSerializer.Meta):
        model = HeatFlowSite
        fields = [
            *BaseSampleSerializer.common_fields,
            "country",
            "region",
            "continent",
            "domain",
            "azimuth",
            "inclination",
            "length",
            "environment",
            "explo_method",
            "explo_purpose",
            "lithology",
            "age",
            "stratigraphy",
            *BaseSampleSerializer.metadata_fields,
            "units",
        ]


class HeatFlowIntervalSummarySerializer(HeatFlowRecordSerializer, BaseSampleSerializer):
    """A depth interval."""

    class Meta(BaseSampleSerializer.Meta):
        model = HeatFlowInterval
        fields = [
            *BaseSampleSerializer.common_fields,
            "top",
            "bottom",
            "vertical_depth",
            "vertical_datum",
            "lithology",
            "age",
            "stratigraphy",
            *BaseSampleSerializer.metadata_fields,
            "units",
        ]


class HeatFlowSummarySerializer(HeatFlowRecordSerializer, BaseMeasurementSerializer):
    """A child heat flow."""

    class Meta(BaseMeasurementSerializer.Meta):
        model = HeatFlow
        fields = [
            *BaseMeasurementSerializer.common_fields,
            "value",
            "uncertainty",
            "method",
            "expedition",
            "c_comment",
            *BaseMeasurementSerializer.metadata_fields,
            "units",
        ]


class ThermalGradientSummarySerializer(
    HeatFlowRecordSerializer, BaseMeasurementSerializer
):
    """A thermal gradient."""

    class Meta(BaseMeasurementSerializer.Meta):
        model = ThermalGradient
        fields = [
            *BaseMeasurementSerializer.common_fields,
            "value",
            "uncertainty",
            "corrected_value",
            "corrected_uncertainty",
            "method_top",
            "method_bottom",
            "shutin_top",
            "shutin_bottom",
            "correction_top",
            "correction_bottom",
            "number",
            *BaseMeasurementSerializer.metadata_fields,
            "units",
        ]


class IntervalConductivitySummarySerializer(
    HeatFlowRecordSerializer, BaseMeasurementSerializer
):
    """An interval conductivity."""

    class Meta(BaseMeasurementSerializer.Meta):
        model = IntervalConductivity
        fields = [
            *BaseMeasurementSerializer.common_fields,
            "value",
            "uncertainty",
            "method",
            "strategy",
            "source",
            "saturation",
            "pT_conditions",
            "pT_function",
            *BaseMeasurementSerializer.metadata_fields,
            "units",
        ]


class ParentHeatFlowSummarySerializer(
    HeatFlowRecordSerializer, BaseMeasurementSerializer
):
    """A parent heat flow."""

    class Meta(BaseMeasurementSerializer.Meta):
        model = ParentHeatFlow
        fields = [
            *BaseMeasurementSerializer.common_fields,
            "value",
            "uncertainty",
            "corr_HP_flag",
            "comment",
            "ghfdb_id",
            *BaseMeasurementSerializer.metadata_fields,
            "units",
        ]
