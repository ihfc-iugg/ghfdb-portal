"""Turn a ``GHFDBImportOutcome`` into a checking report (T009, FR-009,
FR-011, FR-012).

Counts separate sites from determinations and created from updated
records, and each failure carries its row number, the template's own
column heading and a specific reason.

Column headings for a full ``full_clean()`` validation failure are read
from the importing resource's own field declarations (``attribute`` ->
``column_name`` in ``project/ghfdb/resources/parent.py`` and ``child.py``)
rather than from ``project/ghfdb/columns.py``: that module's
``PublishedColumns`` covers only the columns a *published* changelist
displays, and is missing several input-only template columns this report
also has to name (``lat_NS``, ``elevation``, ``Country``, …). The resource
declarations are the complete, authoritative map from a Django model field
to the template column that feeds it, and this codebase already builds
``list_display`` from that same kind of declaration elsewhere.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from import_export.results import Result

from .importers import GHFDBImportOutcome
from .resources import GHFDBChildImportResource, GHFDBParentImportResource

#: Every widget in this app that names a column in its own error message
#: does so one of two ways: ``"Column 'name': ..."`` (``ConceptWidget``,
#: ``MultiConceptWidget``) or a leading ``"name: ..."`` (the IGSN claim
#: conflict in ``child.py``). Tried in that order.
_COLUMN_IN_QUOTES = re.compile(r"Column '([^']+)'")
_LEADING_COLUMN_PREFIX = re.compile(r"^([A-Za-z][A-Za-z0-9_]*): ")


@dataclass(frozen=True)
class RowFailure:
    """One failure a checked file produced: its row, its column (the
    template's own spelling, or "" when a column could not be identified),
    and a reason specific enough to act on."""

    row_number: int
    column: str
    reason: str


@dataclass(frozen=True)
class GHFDBImportReport:
    """The report US-3/US-4 render: what a checked file would do, and
    everything wrong with it."""

    sites_created: int
    sites_updated: int
    determinations_created: int
    determinations_updated: int
    failures: tuple[RowFailure, ...]

    @property
    def has_failures(self) -> bool:
        return bool(self.failures)


def _field_to_column(resource_cls: type) -> dict[str, str]:
    """Map *resource_cls*'s Django model attribute names to the template
    column that feeds each one, from the resource's own field
    declarations."""
    resource = resource_cls()
    return {
        field.attribute: field.column_name
        for field in resource.fields.values()
        if field.attribute
    }


def _counts(result: Result) -> tuple[int, int]:
    created = sum(1 for row in result.rows if row.is_new())
    updated = sum(1 for row in result.rows if row.is_update())
    return created, updated


def _column_from_message(message: str) -> str:
    match = _COLUMN_IN_QUOTES.search(message)
    if match:
        return match.group(1)
    match = _LEADING_COLUMN_PREFIX.match(message)
    return match.group(1) if match else ""


def _base_error_failures(result: Result) -> list[RowFailure]:
    """Failures raised as exceptions — a widget or a hook refusing a value —
    reaching ``result.row_errors()``."""
    return [
        RowFailure(
            row_number=number,
            column=_column_from_message(str(error.error)),
            reason=str(error.error),
        )
        for number, errors in result.row_errors()
        for error in errors
    ]


def _invalid_row_failures(
    result: Result, field_to_column: dict[str, str]
) -> list[RowFailure]:
    """Failures from ``full_clean()`` model validation, reaching
    ``result.invalid_rows`` with Django field names rather than column
    names."""
    return [
        RowFailure(
            row_number=invalid.number,
            column=field_to_column.get(field_name, field_name),
            reason=str(message),
        )
        for invalid in result.invalid_rows
        for field_name, messages in invalid.field_specific_errors.items()
        for message in messages
    ]


def build_report(outcome: GHFDBImportOutcome) -> GHFDBImportReport:
    """Turn *outcome* — the combined result of one checked or confirmed
    import — into the counts and failures a checking report needs."""
    sites_created, sites_updated = _counts(outcome.parent)
    determinations_created, determinations_updated = _counts(outcome.child)

    failures = [
        *_base_error_failures(outcome.parent),
        *_invalid_row_failures(outcome.parent, _field_to_column(GHFDBParentImportResource)),
        *_base_error_failures(outcome.child),
        *_invalid_row_failures(outcome.child, _field_to_column(GHFDBChildImportResource)),
    ]
    failures.sort(key=lambda failure: failure.row_number)

    return GHFDBImportReport(
        sites_created=sites_created,
        sites_updated=sites_updated,
        determinations_created=determinations_created,
        determinations_updated=determinations_updated,
        failures=tuple(failures),
    )
