"""API serializers for the heat flow record types.

Every vocabulary term is an object carrying its label and identifier, every quantity
is a JSON number in the unit its field is stored in, and each record names those units
in ``units`` (FS-010).
"""

from collections import defaultdict
from typing import Any, cast

from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema_field
from fairdm.api.filters import FairDMVisibilityFilter
from fairdm.api.serializers import (
    BaseMeasurementSerializer,
    BaseSampleSerializer,
    GeoJSONPointField,
    RecordListSerializer,
    RecordReferenceField,
)
from fairdm.api.viewsets import load_relations
from quantityfield import fields as quantity_fields
from quantityfield.fields import QuantityFieldMixin
from quantityfield.units import ureg
from research_vocabs import models as vocabulary_models
from research_vocabs.fields import BaseConceptField, ConceptManyToManyField
from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import (
    HeatFlow,
    HeatFlowCorrection,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ThermalGradient,
)

RECORD_REFERENCE = {
    "type": "object",
    "nullable": True,
    "properties": {
        "uuid": {"type": "string"},
        "url": {"type": "string", "format": "uri"},
    },
    "required": ["uuid", "url"],
}


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


class ChoiceLabelField(serializers.ChoiceField):
    """A stored choice, read as its name and its label."""

    def __init__(self, **kwargs: Any) -> None:
        """Read the choice and never write it.

        Args:
            **kwargs: Passed to ``ChoiceField``, including ``choices``.
        """
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, value: Any) -> Any:
        """Give the stored choice with the label it is shown under.

        Args:
            value: The stored choice.

        Returns:
            The choice's ``name`` and ``label``.
        """
        return {"name": value, "label": str(self.choices.get(value, value))}


class SiteLocationField(GeoJSONPointField):
    """The coordinates of the site a record is placed at, as a GeoJSON point."""

    def to_representation(self, value: Any) -> dict | None:
        """Give the point of the record's site, when the requester may see the site.

        Args:
            value: A record placed at a site, read through the serializer's ``site_of``.

        Returns:
            The site's point, or ``None`` when the record has no site, the site has no
            location or the requester may not see the site.
        """
        parent = cast(Any, self.parent)
        site = parent.site_of(value)
        if site is None or not parent.can_see(site):
            return None
        return super().to_representation(site)


def reference(record: Any, request: Any) -> dict[str, str]:
    """Refer to a record by its identifier and its address in the API.

    Args:
        record: A sample or measurement the requester may see.
        request: The request being served, which makes the address absolute.

    Returns:
        The record's ``uuid`` and ``url``.
    """
    url = reverse(
        RecordReferenceField.route_name(record),
        kwargs={"uuid": record.uuid},
        request=request,
    )
    return {"uuid": record.uuid, "url": url}


class RequesterVisibility(serializers.BaseSerializer):
    """Asks the visibility filter of the API's own routes what the requester may see.

    A record, a list of records and the lists nested in a record share one serializer
    context, which keeps the answers for the length of the request.
    """

    @staticmethod
    def records(model: Any) -> Any:
        """Give every record of a model, before any check of who may see it.

        Args:
            model: A sample or measurement model.

        Returns:
            A queryset of the model that reads no subclass rows.
        """
        queryset = model._default_manager.all()
        if hasattr(queryset, "non_polymorphic"):
            queryset = queryset.non_polymorphic()
        return queryset

    def shared(self) -> dict[str, Any]:
        """Give the context every serializer of the request shares.

        Returns:
            The context, which answers kept in it outlast the one serializer.
        """
        return cast(dict[str, Any], self.context)

    def narrow(self, queryset: Any) -> Any:
        """Keep the records the requester may see, by the rule of the record's own route.

        Args:
            queryset: Samples or measurements of one model.

        Returns:
            The queryset limited to what the requester may see.
        """
        return FairDMVisibilityFilter().filter_queryset(
            self.context["request"], queryset, cast(Any, None)
        )

    def mark_visible(self, records: list[Any]) -> None:
        """Ask once which of the records the requester may see, and remember it.

        Args:
            records: Samples or measurements, of any mix of models.
        """
        seen = self.shared().setdefault("visibility", {})
        by_model: dict[Any, list[int]] = defaultdict(list)
        for record in records:
            by_model[record._meta.concrete_model].append(record.pk)
        for model, pks in by_model.items():
            visible = set(
                self.narrow(self.records(model).filter(pk__in=pks)).values_list(
                    "pk", flat=True
                )
            )
            seen.update({(model, pk): pk in visible for pk in pks})

    def can_see(self, record: Any) -> bool:
        """Say whether the requester may see a sample or measurement.

        Args:
            record: The record, checked in one query unless its page already was.

        Returns:
            True when the requester may see it.
        """
        key = (record._meta.concrete_model, record.pk)
        if key not in self.context.get("visibility", {}):
            self.mark_visible([record])
        return bool(self.context["visibility"][key])


class HeatFlowListSerializer(RequesterVisibility, RecordListSerializer):
    """A page of heat flow records, with what the page needs read once."""

    def to_representation(self, data: Any) -> Any:
        """Prime the page's shared context, then serialize each record.

        Args:
            data: The page of records, or a manager or queryset of them.

        Returns:
            One entry for each record.
        """
        records = list(data.all() if hasattr(data, "all") else data)
        cast(Any, self.child).prime_context(records)
        return super().to_representation(records)


class HeatFlowRecordSerializer(RequesterVisibility, serializers.ModelSerializer):
    """Gives a heat flow record its terms, its numbers and its units.

    Attributes:
        summary_serializer: The shorter shape a list of this record gives, or ``None``
            when the list gives the record itself.
    """

    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        quantity_fields.QuantityField: QuantityFloatField,
        quantity_fields.DecimalQuantityField: QuantityDecimalField,
        quantity_fields.PositiveIntegerQuantityField: QuantityIntegerField,
    }

    summary_serializer: type[serializers.ModelSerializer] | None = None

    units = UnitsField()

    @classmethod
    def many_init(cls, *args: Any, **kwargs: Any) -> HeatFlowListSerializer:
        """Build a list of this record's summary, or of the record when it has none.

        Args:
            *args: Passed to the child serializer and the list.
            **kwargs: Passed to the child serializer, and those a list takes to the list.

        Returns:
            The list serializer, whatever the ``Meta`` of the serializer says.
        """
        child_class = cls.summary_serializer or cls
        list_kwargs: dict[str, Any] = {
            key: kwargs.pop(key)
            for key in ("allow_empty", "max_length", "min_length")
            if key in kwargs
        }
        list_kwargs["child"] = child_class(*args, **kwargs)
        list_kwargs.update(
            {
                key: value
                for key, value in kwargs.items()
                if key in serializers.LIST_SERIALIZER_KWARGS
            }
        )
        return HeatFlowListSerializer(*args, **list_kwargs)

    @classmethod
    def load_related(cls, queryset: Any) -> Any:
        """Load the parents, metadata and terms a serialized record reads.

        Args:
            queryset: The records about to be serialized.

        Returns:
            The queryset with each many-valued vocabulary field prefetched with the
            vocabulary its terms name.
        """
        terms = [
            Prefetch(
                field.name,
                queryset=vocabulary_models.Concept.objects.select_related("vocabulary"),
            )
            for field in queryset.model._meta.many_to_many
            if isinstance(field, ConceptManyToManyField)
            and field.name in cls.Meta.fields
        ]
        return super().load_related(queryset).prefetch_related(*terms)  # type: ignore[misc]

    @classmethod
    def loaded(cls, queryset: Any) -> Any:
        """Load everything a list of this serializer reads from the database.

        Args:
            queryset: The records about to be serialized.

        Returns:
            The queryset with its parents selected and its relations prefetched.
        """
        return load_relations(cls.load_related(queryset), cls)

    def prime_context(self, records: list[Any]) -> None:
        """Read in one query what a page of these records needs, when it needs any.

        Args:
            records: The page about to be serialized.
        """

    @staticmethod
    def site_of(record: Any) -> HeatFlowSite | None:
        """Give the site a record is placed at.

        Args:
            record: A site, interval, parent, child, gradient or conductivity, loaded
                with the path to its site selected.

        Returns:
            The site: the record itself for a site, the interval's for an interval, the
            parent's own sample, and the site of the interval a child, gradient or
            conductivity was made over. ``None`` when an interval has no site.
        """
        if isinstance(record, HeatFlowSite):
            return record
        if isinstance(record, HeatFlowInterval):
            return record.site
        sample = record.sample
        if isinstance(record, ParentHeatFlow):
            return sample if isinstance(sample, HeatFlowSite) else sample.heatflowsite
        if not isinstance(sample, HeatFlowInterval):
            sample = sample.heatflowinterval
        return sample.site

    def prime_sites(self, records: list[Any]) -> None:
        """Ask once which of the sites a page of records sit at the requester may see.

        Args:
            records: The page about to be serialized.
        """
        seen = self.context.get("visibility", {})
        sites = {site.pk: site for site in map(self.site_of, records) if site}
        unseen = [site for pk, site in sites.items() if (HeatFlowSite, pk) not in seen]
        if unseen:
            self.mark_visible(unseen)

    @extend_schema_field(RECORD_REFERENCE)
    def get_site(self, record: Any) -> dict[str, str] | None:
        """Refer to the site the record is placed at, when the requester may see it.

        Args:
            record: The record being serialized.

        Returns:
            The site's ``uuid`` and ``url``, or ``None``.
        """
        site = self.site_of(record)
        if site is None or not self.can_see(site):
            return None
        return reference(site, self.context["request"])

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


class SiteParentSerializer(HeatFlowRecordSerializer, BaseMeasurementSerializer):
    """The parent's headline, as a list of sites gives it."""

    class Meta(BaseMeasurementSerializer.Meta):
        model = ParentHeatFlow
        fields = ["url", "uuid", "value", "uncertainty", "quality", "units"]


class HeatFlowSiteSummarySerializer(HeatFlowRecordSerializer, BaseSampleSerializer):
    """A heat flow site.

    Attributes:
        parent_serializer: The shape the site's parent is given in.
    """

    parent_serializer: type[HeatFlowRecordSerializer] = SiteParentSerializer

    # A serializer field is declared by assignment, so mypy reads this as Field.parent.
    parent = serializers.SerializerMethodField()  # type: ignore[assignment]

    class Meta(BaseSampleSerializer.Meta):
        model = HeatFlowSite
        fields = [
            *BaseSampleSerializer.common_fields,
            "type",
            "elevation",
            "elevation_datum",
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
            "parent",
            *BaseSampleSerializer.metadata_fields,
            "units",
        ]

    def prime_context(self, records: list[Any]) -> None:
        """Read the parents of a page of sites in one query, and who may see them.

        Args:
            records: The page of sites about to be serialized.
        """
        parents = self.shared().setdefault("parents", {})
        missing = [site.pk for site in records if site.pk not in parents]
        if not missing:
            return
        found = list(
            self.parent_serializer.loaded(
                self.records(ParentHeatFlow).filter(sample__in=missing)
            )
        )
        self.mark_visible(found)
        parents.update(dict.fromkeys(missing))
        parents.update({parent.sample_id: parent for parent in found})

    @extend_schema_field(SiteParentSerializer(allow_null=True))
    def get_parent(self, site: HeatFlowSite) -> Any:
        """Give the site's parent, or ``None`` when it has none or it is hidden.

        Args:
            site: The site being serialized.

        Returns:
            The parent in ``parent_serializer``'s shape.
        """
        self.prime_context([site])
        parent = self.context["parents"][site.pk]
        if parent is None or not self.can_see(parent):
            return None
        return self.parent_serializer(parent, context=self.context).data


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

    location = SiteLocationField()
    # A serializer field is declared by assignment, so mypy reads this as Field.parent.
    parent = RecordReferenceField(read_only=True)  # type: ignore[assignment]
    thermal_gradient = RecordReferenceField(read_only=True)
    thermal_conductivity = RecordReferenceField(read_only=True)
    site = serializers.SerializerMethodField()

    class Meta(BaseMeasurementSerializer.Meta):
        model = HeatFlow
        fields = [
            *BaseMeasurementSerializer.common_fields,
            "value",
            "uncertainty",
            "surface_temperature",
            "date_acquired",
            "method",
            "expedition",
            "c_comment",
            "U_score",
            "M_score",
            "T_score",
            "T_score_missing",
            "TC_score",
            "TC_score_missing",
            "quality",
            "quality_scheme",
            "ghfdb_id",
            "is_relevant",
            "parent",
            "thermal_gradient",
            "thermal_conductivity",
            "site",
            *BaseMeasurementSerializer.metadata_fields,
            "units",
        ]
        read_only_fields = [
            *BaseMeasurementSerializer.Meta.read_only_fields,
            "surface_temperature",
            "date_acquired",
            "is_relevant",
        ]

    @classmethod
    def load_related(cls, queryset: Any) -> Any:
        """Select the interval and site a child is placed at.

        Args:
            queryset: The children about to be serialized.

        Returns:
            The queryset with the path to each child's site selected.
        """
        return (
            super()
            .load_related(queryset)
            .select_related("sample__heatflowinterval__site")
        )

    def prime_context(self, records: list[Any]) -> None:
        """Ask once which of the sites a page of children sit at the requester may see.

        Args:
            records: The page of children about to be serialized.
        """
        self.prime_sites(records)


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

    site = RecordReferenceField(source="sample", read_only=True)

    class Meta(BaseMeasurementSerializer.Meta):
        model = ParentHeatFlow
        fields = [
            *BaseMeasurementSerializer.common_fields,
            "value",
            "uncertainty",
            "corr_HP_flag",
            "comment",
            "U_score",
            "M_score",
            "quality",
            "quality_scheme",
            "ghfdb_id",
            "site",
            *BaseMeasurementSerializer.metadata_fields,
            "units",
        ]


@extend_schema_field(HeatFlowSummarySerializer(many=True))
class ChildSummaries(serializers.ReadOnlyField):
    """The summaries of the children made over an interval, read from the interval."""


class SiteIntervalSerializer(HeatFlowIntervalSummarySerializer):
    """A depth interval as its site gives it: the summary and the children over it."""

    children = ChildSummaries()

    class Meta(HeatFlowIntervalSummarySerializer.Meta):
        fields = [*HeatFlowIntervalSummarySerializer.Meta.fields, "children"]


class HeatFlowSiteSerializer(HeatFlowSiteSummarySerializer):
    """A heat flow site with its whole parent and every interval with its children."""

    summary_serializer = HeatFlowSiteSummarySerializer
    parent_serializer = ParentHeatFlowSummarySerializer

    intervals = serializers.SerializerMethodField()

    class Meta(HeatFlowSiteSummarySerializer.Meta):
        fields = [*HeatFlowSiteSummarySerializer.Meta.fields, "intervals"]

    @extend_schema_field(ParentHeatFlowSummarySerializer(allow_null=True))
    def get_parent(self, site: HeatFlowSite) -> Any:
        """Give the whole parent in the shape its own list gives.

        Args:
            site: The site being serialized.

        Returns:
            The parent, or ``None`` when it has none or it is hidden.
        """
        return super().get_parent(site)

    @extend_schema_field(SiteIntervalSerializer(many=True))
    def get_intervals(self, site: HeatFlowSite) -> Any:
        """Give every interval the requester may see, each with its children.

        The children of every interval are read and serialized together, then
        handed to the interval they were made over.

        Args:
            site: The site being serialized.

        Returns:
            The site's intervals, shallowest first.
        """
        intervals = list(
            SiteIntervalSerializer.loaded(
                self.narrow(self.records(HeatFlowInterval).filter(site=site))
            ).order_by("top", "bottom", "pk")
        )
        children = list(
            HeatFlowSummarySerializer.loaded(
                self.narrow(self.records(HeatFlow).filter(sample__in=intervals))
            ).order_by("pk")
        )
        rendered = HeatFlowSummarySerializer(
            children, many=True, context=self.context
        ).data
        grouped = defaultdict(list)
        for child, data in zip(children, rendered, strict=True):
            grouped[child.sample_id].append(data)
        for interval in intervals:
            interval.children = grouped[interval.pk]
        return SiteIntervalSerializer(intervals, many=True, context=self.context).data


class HeatFlowCorrectionSerializer(serializers.ModelSerializer):
    """A correction recorded against a child, with its type and status named."""

    correction_type = ChoiceLabelField(
        choices=HeatFlowCorrection.CorrectionTypeChoices.choices
    )
    status = ChoiceLabelField(choices=HeatFlowCorrection.StatusChoices.choices)

    class Meta:
        model = HeatFlowCorrection
        fields = ["correction_type", "status", "comment"]


class HeatFlowSerializer(HeatFlowSummarySerializer):
    """A child heat flow with its gradient and conductivity whole and its corrections."""

    summary_serializer = HeatFlowSummarySerializer

    thermal_gradient = serializers.SerializerMethodField()
    thermal_conductivity = serializers.SerializerMethodField()
    corrections = HeatFlowCorrectionSerializer(many=True, read_only=True)

    class Meta(HeatFlowSummarySerializer.Meta):
        fields = [*HeatFlowSummarySerializer.Meta.fields, "corrections"]

    @classmethod
    def load_related(cls, queryset: Any) -> Any:
        """Select the child's site and prefetch its corrections.

        Args:
            queryset: The children about to be serialized.

        Returns:
            The queryset with the corrections read in one query, in the order recorded.
        """
        corrections = Prefetch(
            "corrections", queryset=HeatFlowCorrection.objects.order_by("pk")
        )
        return super().load_related(queryset).prefetch_related(corrections)

    def nest(self, summary: type[HeatFlowRecordSerializer], pk: int | None) -> Any:
        """Give a record the child was calculated from, whole, when it may be seen.

        Args:
            summary: The serializer that gives the record's own shape.
            pk: The record's primary key, or ``None`` when the child has none.

        Returns:
            The record in the shape of ``summary``, or ``None`` when the child has none
            or the requester may not see it.
        """
        if pk is None:
            return None
        meta = cast(Any, summary).Meta
        visible = summary.loaded(self.narrow(self.records(meta.model).filter(pk=pk)))
        record = visible.first()
        if record is None:
            return None
        return summary(record, context=self.context).data

    @extend_schema_field(ThermalGradientSummarySerializer(allow_null=True))
    def get_thermal_gradient(self, child: HeatFlow) -> Any:
        """Give the thermal gradient the child was calculated from, whole.

        Args:
            child: The child being serialized.

        Returns:
            The gradient, or ``None`` when the child has none or it is hidden.
        """
        return self.nest(ThermalGradientSummarySerializer, child.thermal_gradient_id)

    @extend_schema_field(IntervalConductivitySummarySerializer(allow_null=True))
    def get_thermal_conductivity(self, child: HeatFlow) -> Any:
        """Give the interval conductivity the child was calculated from, whole.

        Args:
            child: The child being serialized.

        Returns:
            The conductivity, or ``None`` when the child has none or it is hidden.
        """
        return self.nest(
            IntervalConductivitySummarySerializer, child.thermal_conductivity_id
        )


class ParentHeatFlowSerializer(ParentHeatFlowSummarySerializer):
    """A parent heat flow with each child made towards it."""

    summary_serializer = ParentHeatFlowSummarySerializer

    children = serializers.SerializerMethodField()

    class Meta(ParentHeatFlowSummarySerializer.Meta):
        fields = [*ParentHeatFlowSummarySerializer.Meta.fields, "children"]

    @extend_schema_field(
        {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "uuid": {"type": "string"},
                    "url": {"type": "string", "format": "uri"},
                    "is_relevant": {"type": "boolean"},
                },
                "required": ["uuid", "url", "is_relevant"],
            },
        }
    )
    def get_children(self, parent: ParentHeatFlow) -> list[dict[str, Any]]:
        """Refer to every child the requester may see, relevant or not.

        Args:
            parent: The parent being serialized.

        Returns:
            Each child's ``uuid`` and ``url`` with whether it counts towards the parent.
        """
        children = self.narrow(self.records(HeatFlow).filter(parent=parent))
        return [
            {
                **reference(child, self.context["request"]),
                "is_relevant": child.is_relevant,
            }
            for child in children.order_by("pk")
        ]
