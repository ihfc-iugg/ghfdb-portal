"""
The callable entry point for importing one GHFDB upload template file.

FR-001: importing is callable from code, taking one file and one dataset
named by the caller — a script or management command has no admin request
to hand the resources, so this is the surface that does not need one.

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

import tablib
from django.db import transaction
from import_export.results import Result

from .constants import validate_official_header
from .resources import (
    GHFDBChildImportResource,
    GHFDBImportFormat,
    GHFDBParentImportResource,
)


@dataclass
class GHFDBImportOutcome:
    """The combined result of one GHFDB template import: the parent pass,
    then the child pass."""

    parent: Result
    child: Result

    def has_errors(self) -> bool:
        return (
            self.parent.has_errors()
            or self.parent.has_validation_errors()
            or self.child.has_errors()
            or self.child.has_validation_errors()
        )


def import_ghfdb_template(
    file: Any, dataset: Any, check_only: bool = False
) -> GHFDBImportOutcome:
    """Import one official GHFDB upload template *file* into *dataset*.

    *file* is either the raw XLSX bytes (or a binary file-like object) of an
    upload template, or an already-parsed ``tablib.Dataset`` — the shape a
    caller already holding one (the admin import wizard, for instance) can
    pass straight through without re-serialising it back to bytes first.

    Runs the parent pass — sites and their parent heat flow values — before
    the child pass — the determinations beneath them — since a child row
    resolves its parent from the site the parent pass has already created
    (plan.md "Sequencing"). Each pass gets its own copy of the parsed rows:
    the parent resource's ``before_import`` deduplicates rows in place, and
    the child pass needs every row that dedup would otherwise have removed.
    Both passes run inside one transaction and are wired to *dataset*
    through the ``fairdm_dataset`` keyword every resource hook reads.

    *check_only* (US-3, FR-008/FR-010): when true, both passes still run for
    real — nothing here calls either resource with ``dry_run=True``. Doing
    so was tried and rejected (specs/004-import-upload-template/decisions.md
    D16): ``import_data()`` wraps each resource in its own savepoint, and a
    literal ``dry_run=True`` rolls that savepoint back at the end of that
    same call, before the next pass starts — so the child pass, which
    resolves its parent through ``ID_parent`` and coordinates, can no longer
    see the parent pass's rows, and every file is refused, clean ones
    included, for a reason that has nothing to do with the file. Instead the
    transaction this function already opens is rolled back unconditionally
    on the way out when *check_only* is set, the same ``set_rollback``
    mechanism already used below for the error case.
    """
    if isinstance(file, tablib.Dataset):
        rows = file
    else:
        content = file.read() if hasattr(file, "read") else file
        rows = GHFDBImportFormat().create_dataset(content)

    # FR-003: a file that is not the official template is refused on its
    # header, before a single row is read and before the transaction opens,
    # so nothing is written for it (FR-010).
    validate_official_header(list(rows.headers or []))

    with transaction.atomic():
        parent_result = GHFDBParentImportResource().import_data(
            copy.deepcopy(rows),
            dry_run=False,
            fairdm_dataset=dataset,
            rollback_on_validation_errors=True,
        )
        child_result = GHFDBChildImportResource().import_data(
            copy.deepcopy(rows),
            dry_run=False,
            fairdm_dataset=dataset,
            rollback_on_validation_errors=True,
        )

        outcome = GHFDBImportOutcome(parent=parent_result, child=child_result)
        if check_only or outcome.has_errors():
            # Each pass already rolls back its own rows on its own faults
            # (rollback_on_validation_errors above). This covers the cases
            # that cannot: one pass faults while the other has nothing
            # wrong with it and would otherwise commit its rows on its own
            # (FR-010) — both passes share this transaction, so marking it
            # here discards both once either one is at fault — and the
            # checking mode, which must write nothing at all regardless of
            # whether either pass found a fault (FR-010, D16 above).
            transaction.set_rollback(True)

    return outcome
