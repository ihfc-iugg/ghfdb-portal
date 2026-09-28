"""Turn a ``GHFDBImportOutcome`` into a checking report (FS-005 FR-009, FR-011, FR-012).

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

from django.utils.translation import gettext_lazy as _
from import_export.results import Result

from .importers import GHFDBImportOutcome
from .resources import GHFDBChildImportResource, GHFDBParentImportResource

#: Every widget in this app that names a column in its own error message
#: does so one of two ways: ``"Column 'name': ..."`` (``ConceptWidget``,
#: ``MultiConceptWidget``) or a leading ``"name: ..."`` (the IGSN claim
#: conflict in ``child.py``). Tried in that order.
_COLUMN_IN_QUOTES = re.compile(r"Column '([^']+)'")
_LEADING_COLUMN_PREFIX = re.compile(r"^([A-Za-z][A-Za-z0-9_]*): ")

#: ``RelatedModelWidget.clean()``/``set_m2m_relations()`` (widgets.py)
#: prefixes a sub-field's error with the Django model it is building —
#: ``"HeatFlowSite: Column 'environment': ..."`` — to help a developer
#: place the fault. That model name is internal (FS-005 FR-013) and never reaches
#: the report: the useful part of the message already starts at the
#: embedded ``Column '...'`` marker, so everything before it is dropped.
_DJANGO_DOES_NOT_EXIST = re.compile(
    r"^[A-Za-z][A-Za-z0-9_]* matching query does not exist\.$"
)


def _sanitize_reason(message: str) -> str:
    """Strip an internal Django model or class name out of *message* (FS-005 FR-013).

    Applies before *message* becomes a ``RowFailure.reason``.

    Two known leaks, both from third-party or wrapping code this report
    layer does not control: ``RelatedModelWidget``'s own "which model"
    prefix (stripped down to the embedded ``Column '...'`` marker that
    already carries the useful part), and Django's default
    ``Model.DoesNotExist`` message, which names the model class directly —
    raised here when a child row's ``ForeignKeyWidget`` cannot resolve a
    parent that itself failed to import. The row is still reported; only
    the model name is replaced.
    """
    column_match = _COLUMN_IN_QUOTES.search(message)
    if column_match:
        return message[column_match.start() :]
    if _DJANGO_DOES_NOT_EXIST.match(message):
        return str(
            _(
                "This row's related record could not be found — an earlier "
                "row it depends on did not import. Check that row's own "
                "reported problem first."
            )
        )
    return message


@dataclass(frozen=True)
class RowFailure:
    """One failure a checked file produced.

    Carries its row, its column (the template's own spelling, or "" when a
    column could not be identified), and a reason specific enough to act on.
    """

    row_number: int
    column: str
    reason: str


@dataclass(frozen=True)
class GHFDBImportReport:
    """The report US-3/US-4 render.

    Shows what a checked file would do, and everything wrong with it.
    """

    sites_created: int
    sites_updated: int
    determinations_created: int
    determinations_updated: int
    failures: tuple[RowFailure, ...]

    @property
    def has_failures(self) -> bool:
        """Report whether the checked file produced any failures."""
        return bool(self.failures)


def _field_to_column(resource_cls: type) -> dict[str, str]:
    """Map *resource_cls*'s model attributes to their template columns.

    Reads the mapping from the resource's own field declarations.
    """
    resource = resource_cls()
    return {
        field.attribute: field.column_name
        for field in resource.fields.values()
        if field.attribute
    }


def _counts(result: Result) -> tuple[int, int]:
    """Count created and updated rows in an import *result*."""
    created = sum(1 for row in result.rows if row.is_new())
    updated = sum(1 for row in result.rows if row.is_update())
    return created, updated


def _column_from_message(message: str) -> str:
    """Extract the template column name embedded in an error *message*."""
    match = _COLUMN_IN_QUOTES.search(message)
    if match:
        return match.group(1)
    match = _LEADING_COLUMN_PREFIX.match(message)
    return match.group(1) if match else ""


def _base_error_failures(result: Result) -> list[RowFailure]:
    """Build failures from exceptions a widget or hook raised.

    Reads them from ``result.row_errors()``.
    """
    return [
        RowFailure(
            row_number=number,
            column=_column_from_message(str(error.error)),
            reason=_sanitize_reason(str(error.error)),
        )
        for number, errors in result.row_errors()
        for error in errors
    ]


def _invalid_row_failures(
    result: Result, field_to_column: dict[str, str]
) -> list[RowFailure]:
    """Build failures from ``full_clean()`` model validation.

    Reads them from ``result.invalid_rows``, which carries Django field
    names rather than column names.
    """
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
    """Turn *outcome* into the counts and failures a checking report needs.

    *outcome* is the combined result of one checked or confirmed import.
    """
    sites_created, sites_updated = _counts(outcome.parent)
    determinations_created, determinations_updated = _counts(outcome.child)

    failures = [
        *_base_error_failures(outcome.parent),
        *_invalid_row_failures(
            outcome.parent, _field_to_column(GHFDBParentImportResource)
        ),
        *_base_error_failures(outcome.child),
        *_invalid_row_failures(
            outcome.child, _field_to_column(GHFDBChildImportResource)
        ),
    ]
    failures.sort(key=lambda failure: failure.row_number)

    return GHFDBImportReport(
        sites_created=sites_created,
        sites_updated=sites_updated,
        determinations_created=determinations_created,
        determinations_updated=determinations_updated,
        failures=tuple(failures),
    )
