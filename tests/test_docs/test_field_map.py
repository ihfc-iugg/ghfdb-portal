"""The published-column map in ``docs/ghfdb_fields.md`` is held to the models.

Constitution principle VII makes that page the authoritative record of how the flat
GHFDB columns map onto relational model fields, and requires it to stay current with
every schema change. Nothing checked that it was, and it had drifted: a column pointing
at a field renamed two migrations earlier still resolved, because the old name survives
on a base class.

The canonical published columns are ``PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS`` in
``project/ghfdb/constants.py``.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import pytest
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model

FIELD_MAP = Path(__file__).resolve().parents[2] / "docs" / "ghfdb_fields.md"

MAPPING_HEADER = (
    "GHFDB Name",
    "GHFDB Ref",
    "Database Table",
    "Accessed From",
    "Accessor",
    "Declared By",
)

#: What the Database Table column carries for an accessor that computes its value
#: rather than reading a column.
NO_TABLE = "—"

#: Accessors may carry a parenthetical qualifier naming the record they select,
#: as the correction flags do: ``status (type=IS)``.
QUALIFIER = re.compile(r"\s*\(.*\)\s*$")


@dataclass(frozen=True)
class Mapping:
    """One row of the map: a published column and where its value lives."""

    column: str
    reference: str
    table: str
    accessed_from: str
    accessor: str
    declared_by: str
    line: int

    def __str__(self) -> str:
        return f"{self.column} (docs/ghfdb_fields.md:{self.line})"


def cells(row: str) -> list[str]:
    """The cells of a markdown table row, with the map's escaping undone."""
    return [cell.strip().replace("\\_", "_") for cell in row.strip().strip("|").split("|")]


def read_mappings() -> list[Mapping]:
    """Every row of every mapping table in the field map.

    The page holds other tables — the column key, the valid correction statuses, the
    record of removed fields — so tables are selected by their header rather than by
    being a table.
    """
    rows: list[Mapping] = []
    lines = FIELD_MAP.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        if lines[index].startswith("|") and tuple(cells(lines[index])) == MAPPING_HEADER:
            index += 2  # the header and the alignment row beneath it
            while index < len(lines) and lines[index].startswith("|"):
                values = cells(lines[index])
                if len(values) != len(MAPPING_HEADER):
                    raise AssertionError(
                        f"docs/ghfdb_fields.md:{index + 1} has {len(values)} cells, "
                        f"expected {len(MAPPING_HEADER)}: {lines[index]}"
                    )
                rows.append(Mapping(*values, line=index + 1))
                index += 1
        else:
            index += 1
    return rows


MAPPINGS = read_mappings()


def published_columns() -> list[str]:
    from project.ghfdb.constants import CHILD_COLUMNS, META_FIELDS, PARENT_COLUMNS

    return PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS


def model_named(name: str) -> type[Model] | None:
    return next((m for m in apps.get_models() if m.__name__ == name), None)


def declares(cls: type, attribute: str) -> bool:
    """Whether ``cls`` itself declares ``attribute``, as opposed to inheriting it."""
    if not (isinstance(cls, type) and issubclass(cls, Model)) or cls is Model:
        return False
    local = list(cls._meta.local_fields) + list(cls._meta.local_many_to_many)
    return any(field.name == attribute for field in local) or attribute in vars(cls)


def declaring_classes(model: type[Model], attribute: str) -> list[str]:
    """Every class in the model's ancestry that declares ``attribute`` itself.

    Abstract bases are included: Django copies their fields onto the concrete model,
    so the field a reader is told about may be declared several classes up.
    """
    return [cls.__name__ for cls in model.__mro__ if declares(cls, attribute)]


def owner_and_attribute(mapping: Mapping) -> tuple[type[Model], str]:
    """The model an accessor's final segment resolves on, and that segment.

    An accessor may traverse a relation, as ``location.y`` does.
    """
    model = model_named(mapping.accessed_from)
    assert model is not None, f"{mapping} names no model called {mapping.accessed_from}"
    segments = QUALIFIER.sub("", mapping.accessor).split(".")
    for segment in segments[:-1]:
        field = model._meta.get_field(segment)
        assert field.related_model is not None, (
            f"{mapping} traverses {segment!r}, which is not a relation"
        )
        model = field.related_model
    return model, segments[-1]


def storage_table(model: type[Model], attribute: str) -> str:
    """The table a value is read from, or ``NO_TABLE`` when it is computed.

    Multi-table inheritance and many-to-many relations both put the value somewhere
    other than the table of the model it is read from, which is the whole reason the
    page carries this column.
    """
    try:
        field = model._meta.get_field(attribute)
    except FieldDoesNotExist:
        return NO_TABLE
    if field.many_to_many:
        through = getattr(field, "through", None) or field.remote_field.through
        return through._meta.db_table
    if field.is_relation and not field.concrete:
        return field.related_model._meta.db_table
    return field.model._meta.db_table


class TestFieldMapCoverage:
    """Every published column has a row."""

    def test_every_published_column_appears_in_the_map(self):
        mapped = {mapping.column for mapping in MAPPINGS}
        missing = [column for column in published_columns() if column not in mapped]
        assert not missing, (
            "Columns of the published database that docs/ghfdb_fields.md does not map: "
            f"{missing}"
        )

    def test_no_column_is_mapped_twice(self):
        seen: dict[str, Mapping] = {}
        duplicates = []
        for mapping in MAPPINGS:
            if mapping.column in seen:
                duplicates.append(f"{mapping} also mapped at line {seen[mapping.column].line}")
            seen[mapping.column] = mapping
        assert not duplicates, duplicates


@pytest.mark.parametrize("mapping", MAPPINGS, ids=str)
class TestFieldMapResolves:
    """Every row names a model, an accessor that resolves on it, and a real declarer."""

    def test_accessed_from_names_a_model(self, mapping: Mapping):
        assert model_named(mapping.accessed_from) is not None, (
            f"{mapping} is reached from {mapping.accessed_from}, which is not a model"
        )

    def test_the_accessor_resolves(self, mapping: Mapping):
        model, attribute = owner_and_attribute(mapping)
        assert declaring_classes(model, attribute), (
            f"{mapping} reads {mapping.accessor!r}, which does not resolve on "
            f"{model.__name__}"
        )

    def test_the_declaring_model_declares_it(self, mapping: Mapping):
        """The named declarer must declare the field, not merely inherit it.

        This is the clause that catches a renamed field. ``ID`` pointed at
        ``local_id`` on the child long after migration 0011 replaced it with
        ``ghfdb_id``, and an existence check passed: ``local_id`` still resolves,
        because it is declared on a FairDM base class.
        """
        model, attribute = owner_and_attribute(mapping)
        declarers = declaring_classes(model, attribute)
        named = mapping.declared_by.split(".")[-1]
        assert named in declarers, (
            f"{mapping} says {mapping.declared_by} declares {attribute!r}; "
            f"it is declared by {declarers or 'nothing'}"
        )

    def test_the_database_table_is_where_the_value_is_stored(self, mapping: Mapping):
        model, attribute = owner_and_attribute(mapping)
        assert storage_table(model, attribute) == mapping.table, (
            f"{mapping} says the value is stored in {mapping.table!r}; it is stored in "
            f"{storage_table(model, attribute)!r}"
        )
