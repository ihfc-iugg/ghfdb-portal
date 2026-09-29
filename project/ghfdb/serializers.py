"""DRF serializers for the GHFDB API endpoints."""

from collections.abc import Iterable

from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from rest_framework import serializers

from .columns import PublishedColumns
from .constants import CHILD_COLUMNS, PARENT_COLUMNS


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
    hold no value are the same thing to a consumer (FS-006 FR-012).
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
    than raising (FS-006 FR-011, FR-012).
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
            accessor does not hold here, keyed by published
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
    satisfies FS-006 FR-003 by construction.
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


class GHFDBChildListSerializer(serializers.Serializer):
    """One published determination record: its link, its parent link, its
    site's coordinates, then its columns, then its own identifier.

    The registry carries no entry for the determination's own identifier
    (``ID``), so it is added beside ``published_fields()``'s output rather
    than through it, reading the proxy's ``ghfdb_id``.
    """

    url = serializers.HyperlinkedIdentityField(
        view_name="api:ghfdb-children-detail", lookup_field="ghfdb_id"
    )

    def get_fields(self):
        """Append the parent link, the site coordinates, the child columns,
        then ``ID``.

        ``parent`` is built here rather than declared as a class attribute
        because ``Field.parent`` is DRF's own name for a field's owning
        serializer; a class attribute of that name would shadow it.
        """
        fields = super().get_fields()
        fields["parent"] = serializers.HyperlinkedRelatedField(
            view_name="api:ghfdb-parents-detail",
            lookup_field="ghfdb_id",
            read_only=True,
        )
        fields.update(published_fields(["lat_NS", "long_EW"]))
        fields.update(published_fields(CHILD_COLUMNS))
        fields["ID"] = PublishedValueField(source="ghfdb_id")
        return fields


class GHFDBChildDetailSerializer(GHFDBChildListSerializer):
    """A determination's single-record shape: ``parent`` nests the parent's
    full record instead of linking to it, so the nesting stops at one level
    (FS-006 FR-008).
    """

    def get_fields(self):
        """Replace the ``parent`` link with the nested parent record."""
        fields = super().get_fields()
        fields["parent"] = GHFDBParentSerializer(read_only=True)
        return fields


class GHFDBFlatSerializer(serializers.Serializer):
    """One released row: every published parent column, then every published
    child column, then the determination's own identifier.

    Carries no link, no counts and no portal identifier — the released row is
    published columns and nothing else.
    """

    def get_fields(self):
        """Append the parent columns, the child columns, then ``ID``.

        ``explo_purpose`` reads a different path than it does on a parent
        row, because a determination reaches its site through its own
        interval rather than directly.
        """
        fields = super().get_fields()
        fields.update(
            published_fields(
                PARENT_COLUMNS,
                overrides={
                    "explo_purpose": "sample.heatflowinterval.site.explo_purpose"
                },
            )
        )
        fields.update(published_fields(CHILD_COLUMNS))
        fields["ID"] = PublishedValueField(source="ghfdb_id")
        return fields


class GHFDBParentDetailSerializer(GHFDBParentSerializer):
    """A parent's single-record shape: ``children`` carries the
    determinations belonging to it, in the determination list shape, ahead
    of the published columns (FS-006 FR-006).

    ``get_fields()`` skips ``GHFDBParentSerializer.get_fields()`` and calls
    the base ``Serializer.get_fields()`` directly, so ``children`` can be
    inserted before the published columns are appended, rather than after.
    Read from ``children_list`` rather than the field's own name: the
    proxy's ``children`` is the model's real reverse relation manager, which
    the view cannot reassign to a filtered queryset.
    """

    def get_fields(self):
        """Insert ``children`` between the declared keys and the columns."""
        fields = serializers.Serializer.get_fields(self)
        fields["children"] = GHFDBChildListSerializer(
            many=True, read_only=True, source="children_list"
        )
        fields.update(published_fields(PARENT_COLUMNS))
        return fields
