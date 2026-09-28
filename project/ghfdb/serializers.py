"""DRF serializers for the GHFDB API endpoints."""

from collections.abc import Iterable

from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from rest_framework import serializers

from .columns import PublishedColumns
from .constants import PARENT_COLUMNS


@extend_schema_serializer(
    examples=[OpenApiExample(name="GHFDB Column Metadata", value={})]
)
class MyJSONSchemaSerializer(serializers.Serializer):
    class Meta:
        ref_name = "MyJSONSchema"


@extend_schema_field({"nullable": True})
class PublishedValueField(serializers.Field):
    """Read-only field for one scalar published GHFDB column.

    A Pint quantity renders as its float magnitude. Both ``None`` and the
    empty string render as ``null`` — the two ways a published scalar can
    hold no value are the same thing to a consumer (spec D14, research R5).
    Anything else passes through unchanged.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("read_only", True)
        super().__init__(**kwargs)

    def to_representation(self, value):
        """Render *value* as the API emits a scalar published column."""
        if value is None or value == "":
            return None
        if hasattr(value, "magnitude"):
            return float(value.magnitude)
        return value


@extend_schema_field({"type": "array", "items": {"type": "string"}})
class ConceptLabelsField(serializers.Field):
    """Read-only field for one many-valued published GHFDB column.

    Reads a related manager by a dot-separated source path and renders the
    labels of its members, via ``.all()`` so a prefetched queryset serves
    from cache. A ``None`` anywhere on the path renders as ``[]`` rather
    than raising (spec D14).
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("read_only", True)
        super().__init__(**kwargs)

    def get_attribute(self, instance):
        """Walk ``source_attrs``, stopping at the first ``None`` hop."""
        target = instance
        for segment in self.source_attrs:
            target = getattr(target, segment, None)
            if target is None:
                return None
        return target

    def to_representation(self, value):
        """Render the related manager *value* as its members' labels."""
        if value is None:
            return []
        return [concept.label for concept in value.all()]


def published_fields(
    columns: Iterable[str], overrides: dict[str, str] | None = None
) -> dict[str, serializers.Field]:
    """Build the published-column fields for one record shape, in order.

    Args:
        columns: Published column names, in the order the record should
            carry them — normally ``PARENT_COLUMNS`` or ``CHILD_COLUMNS``.
        overrides: A per-context accessor for a column whose registry
            accessor does not hold here (research R6), keyed by published
            name.

    Returns:
        An ordered mapping of published name to the field that renders it,
        reading each column's group and accessor from
        ``PublishedColumns.ENTRIES``.
    """
    overrides = overrides or {}
    built: dict[str, serializers.Field] = {}
    for name in columns:
        entry = PublishedColumns.ENTRIES[name]
        accessor = overrides.get(name, entry.accessor or name)
        # DRF's Field.bind() refuses a `source` equal to the field name it is
        # bound under, so the common case — accessor and published name
        # coincide — omits `source` and lets bind() default it to the field
        # name itself.
        source_kwargs = {} if accessor == name else {"source": accessor}
        if entry.group == PublishedColumns.MANY_VALUED:
            built[name] = ConceptLabelsField(**source_kwargs)
        else:
            built[name] = PublishedValueField(**source_kwargs)
    return built


class GHFDBParentSerializer(serializers.Serializer):
    """One published parent record: its link, its counts, then its columns.

    The non-published keys are declared here and so come first; the
    published parent columns are appended by ``get_fields()``, which
    satisfies FR-003 by construction (plan.md Design > Parents).
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="api:ghfdb-parents-detail", lookup_field="ghfdb_id"
    )
    total_children = serializers.IntegerField(read_only=True)
    relevant_children = serializers.IntegerField(read_only=True)

    def get_fields(self):
        """Append the published parent columns after the declared keys."""
        fields = super().get_fields()
        fields.update(published_fields(PARENT_COLUMNS))
        return fields
