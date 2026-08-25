"""
GHFDB release import resource and reading format (specs/003-ghfdb-release-import).

Implements the first part of US-1: a release file is checked in full before
anything is written. ``GHFDBReleaseCSVFormat`` reads the comma-separated
format a published release is distributed in, and
``GHFDBReleaseImportResource`` validates a file's header against the
release column definitions in ``constants.py`` before any row is read
(FR-003 to FR-007), then reports every refused value by the column name a
curator sees in the header and the line it occupies in the file (FR-009,
FR-010).

This part of the story checks a file and reports its faults. It does not
turn a row into the site, interval and determination it describes, or
create the dataset and literature a row's publication reference resolves
to - that is later work, and ``save_instance`` is a deliberate no-op here
for that reason.

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

import csv
from io import StringIO

import tablib
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower, Trim
from django.utils.encoding import force_str
from fairdm.core.models import Dataset
from heat_flow.models import HeatFlow
from import_export import fields, widgets
from import_export.formats.base_formats import CSV
from import_export.resources import ModelResource
from literature.models import LiteratureItem

from ..constants import MISSPELLED_COLUMNS, READ_COLUMNS, RELEASE_COLUMNS
from .widgets import QuantityWidget

# FR-006: a column the release format requires. DISCARDED_COLUMNS is
# deliberately excluded - two of its members (the legacy per-row quality
# codes) are never present in a real release (R1), so their absence cannot
# be a fault, and the rest are recognised only if a file happens to carry
# them (D13).
REQUIRED_COLUMNS = READ_COLUMNS


def _normalize_publication_reference(reference: str) -> str:
    """FR-017: two publication references are the same reference once
    surrounding whitespace and case are ignored."""
    return reference.strip().lower()


class GHFDBReleaseCSVFormat(CSV):
    """The format a published release is distributed in: one header row,
    one data row per determination (FR-002). The library's own
    comma-separated reader already reads the header from the first line
    and the data from the second; only the title a curator sees in the
    format list is added here.
    """

    def get_title(self) -> str:
        return "GHFDB Release Format"

    def create_dataset(self, in_stream, **kwargs):
        """Read the header from the first line and the data from the
        second (T009). Reimplemented rather than delegated to the
        library's own tablib-backed reader for two reasons: that reader
        looks up its tablib format by ``get_title()``, which the
        curator-facing title above no longer is, and it refuses a row
        that is wider than the header outright rather than reporting the
        header fault a curator can act on (FR-006) - a header missing one
        published column, with its data rows otherwise untouched, is
        exactly the shape a file missing a column takes.
        """
        if isinstance(in_stream, bytes) and self.encoding:
            in_stream = in_stream.decode(self.encoding)
        dataset = tablib.Dataset()
        for i, row in enumerate(csv.reader(StringIO(in_stream))):
            if i == 0:
                dataset.headers = row
            elif row:
                if len(row) < dataset.width:
                    row = row + [""] * (dataset.width - len(row))
                elif len(row) > dataset.width:
                    row = row[: dataset.width]
                dataset.append(row)
        return dataset


class GHFDBReleaseImportResource(ModelResource):
    """Checks a published release file against the release format before
    any row is written.

    Header validation runs in ``before_import`` and refuses the file for a
    misspelled published column name (FR-004, D7), a column the release
    format does not define (FR-005), or a required column the file does
    not carry (FR-006) - naming every offending column, not just the
    first. Emptying the dataset is what stops the row loop; raising alone
    does not, since the library catches ``before_import``'s exception and
    carries on to the row loop (R3). The library re-measures
    ``result.total_rows`` immediately afterwards for exactly this purpose.

    ``import_instance`` is overridden so a refused value is reported by
    the column name a curator sees in the header rather than the model
    attribute it would have been stored in (FR-010) - the library's own
    version keys the error by ``field.attribute``. ``import_data`` is
    overridden to correct the reported row number to count the header
    line, so the first data row reports as line 2 rather than the
    library's own line 1 (FR-010, R3).
    """

    qc = fields.Field(
        attribute="value",
        column_name="qc",
        widget=QuantityWidget("mW/m^2"),
    )
    qc_uncertainty = fields.Field(
        attribute="uncertainty",
        column_name="qc_uncertainty",
        widget=QuantityWidget("mW/m^2"),
    )

    def before_import(self, dataset, **kwargs):
        headers = dataset.headers or []
        header_set = set(headers)

        faults = []

        misspelled_present = [name for name in MISSPELLED_COLUMNS if name in header_set]
        for name in misspelled_present:
            correct = MISSPELLED_COLUMNS[name]
            faults.append(
                f"Column '{name}' is the outdated, misspelled form of the "
                f"published column '{correct}'. This file follows an "
                f"outdated template; correct the header before importing."
            )

        undefined = [name for name in headers if name not in RELEASE_COLUMNS]
        for name in undefined:
            faults.append(f"Column '{name}' is not part of the release format.")

        corrected_present = {MISSPELLED_COLUMNS[name] for name in misspelled_present}
        missing = [
            name
            for name in REQUIRED_COLUMNS
            if name not in header_set and name not in corrected_present
        ]
        for name in sorted(missing):
            faults.append(
                f"The release format requires column '{name}', which this "
                f"file does not carry."
            )

        if faults:
            del dataset[:]
            raise ValueError(" ".join(faults))

        self._datasets_by_reference = self._resolve_publication_datasets(dataset)

    def _resolve_publication_datasets(self, dataset):
        """T035, T036: collect the file's distinct publication references
        once, before any row is read, and create the dataset each one
        belongs to (D4) - a bibliographic record carrying the reference's
        citation key is created where none exists yet (T041, D5).

        Two references differing only by case or surrounding whitespace
        are one reference (FR-017, T037): grouped here by their
        normalised form, keeping the first raw spelling the file gives so
        the citation key created for it is stable rather than whichever
        variant a set happened to iterate first.
        """
        references_by_normalized = {}
        for row in dataset.dict:
            raw_reference = (row.get("publication_reference") or "").strip()
            if not raw_reference:
                continue
            references_by_normalized.setdefault(
                _normalize_publication_reference(raw_reference), raw_reference
            )

        datasets_by_reference = {}
        for normalized, reference in references_by_normalized.items():
            matches = list(
                LiteratureItem.objects.annotate(
                    normalized_citation_key=Lower(Trim("citation_key"))
                ).filter(normalized_citation_key=normalized)
            )
            if matches:
                literature_item = matches[0]
            else:
                literature_item = LiteratureItem.objects.create(citation_key=reference)
            release_dataset, _created = Dataset.all_objects.get_or_create(
                reference=literature_item,
                defaults={
                    "name": literature_item.title or literature_item.citation_key
                },
            )
            datasets_by_reference[normalized] = release_dataset
        return datasets_by_reference

    def import_instance(self, instance, row, **kwargs):
        errors = {}
        for field in self.get_import_fields():
            if isinstance(field.widget, widgets.ManyToManyWidget):
                continue
            try:
                self.import_field(field, instance, row, **kwargs)
            except ValueError as e:
                errors[field.column_name] = ValidationError(
                    force_str(e), code="invalid"
                )
        if errors:
            raise ValidationError(errors)

    def import_data(self, dataset, *args, **kwargs):
        result = super().import_data(dataset, *args, **kwargs)
        for invalid_row in result.invalid_rows:
            invalid_row.number += 1
        for error_row in result.error_rows:
            error_row.number += 1
        return result

    def save_instance(self, instance, is_create, row, **kwargs):
        """A no-op: checking a file writes nothing. Turning a checked row
        into the records it describes is later work, and the library's
        default here would try to save an instance with no sample or
        dataset assigned.
        """
        return

    class Meta:
        model = HeatFlow
        fields = ("qc", "qc_uncertainty")
        # No upsert identity yet: finding a determination by its published
        # identifier is later work (US-4). Every row is a new, unsaved
        # instance until then.
        import_id_fields = ()
