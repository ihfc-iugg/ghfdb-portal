"""
Tests for project/ghfdb/resources/release.py (specs/003-ghfdb-release-import).

Phase 2 - US-1, first part: a release file is checked in full before
anything is written (T008, T009, T011-T024, T033). The reader this module
tests does not yet turn a row into the site, interval and determination it
describes (US-3) or create the dataset and literature a row's publication
reference resolves to (US-2) - this story checks a file and reports its
faults.
"""

import csv
from pathlib import Path

import pytest
import tablib

from project.ghfdb.constants import MISSPELLED_COLUMNS
from project.ghfdb.resources.release import (
    GHFDBReleaseCSVFormat,
    GHFDBReleaseImportResource,
)

pytestmark = pytest.mark.ghfdb

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "release"
BASE_FIXTURE = FIXTURES_DIR / "release_sample.csv"


def _corrected_header_and_rows():
    """BASE_FIXTURE's header and data rows, with the two misspelled
    published names corrected (MISSPELLED_COLUMNS) - the file a curator
    would submit after preparing it, not the archive as downloaded (D7).
    """
    text = BASE_FIXTURE.read_text(encoding="utf-8-sig")
    reader = csv.reader(text.splitlines())
    header = [MISSPELLED_COLUMNS.get(name, name) for name in next(reader)]
    rows = list(reader)
    return header, rows


def _make_dataset(header, rows):
    dataset = tablib.Dataset(headers=header)
    for row in rows:
        dataset.append(row)
    return dataset


def _corrected_dataset():
    """A tablib Dataset built from the corrected base fixture, unmodified."""
    header, rows = _corrected_header_and_rows()
    return _make_dataset(header, rows)


def _dataset_from_fixture(path):
    """A tablib Dataset built from a fixture file's header and rows exactly
    as written - no correction applied."""
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.reader(text.splitlines())
    header = next(reader)
    rows = list(reader)
    return _make_dataset(header, rows)


def _with_cell(header, rows, row_index, column, value):
    """``rows`` with a single cell replaced, by column name and row
    position - the rest of the row untouched."""
    changed = [list(row) for row in rows]
    changed[row_index][header.index(column)] = value
    return changed


def _without_column(header, rows, column):
    """``header`` and ``rows`` with one column dropped from both, so the
    result stays a well-formed (non-ragged) dataset."""
    index = header.index(column)
    new_header = header[:index] + header[index + 1 :]
    new_rows = [row[:index] + row[index + 1 :] for row in rows]
    return new_header, new_rows


class TestGHFDBReleaseCSVFormat:
    """T009: the reading format is a comma-separated reader carrying a name
    a curator can recognise, reading the header from the first line and the
    data from the second."""

    def test_get_title_is_curator_recognisable(self):
        assert GHFDBReleaseCSVFormat().get_title() == "GHFDB Release Format"

    def test_reads_the_header_from_the_first_line_and_data_from_the_second(self):
        csv_bytes = "ID,qc\nR24-000001,48.1\nR24-000002,84.1\n".encode("utf-8-sig")
        dataset = GHFDBReleaseCSVFormat(encoding="utf-8-sig").create_dataset(csv_bytes)

        assert dataset.headers == ["ID", "qc"]
        assert dataset.dict == [
            {"ID": "R24-000001", "qc": "48.1"},
            {"ID": "R24-000002", "qc": "84.1"},
        ]


class TestGHFDBReleaseImportResourceCleanFile:
    """T008: a release file whose header is the real published one passes
    the column check and its values are read."""

    def test_clean_file_passes_the_column_check_and_its_values_are_read(self):
        header, rows = _corrected_header_and_rows()
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False
        assert result.total_rows == len(rows)


class TestGHFDBReleaseImportResourceMisspelledColumns:
    """T011, T012: a file carrying a misspelled published column name is
    refused, the error names the misspelled name, the correct name and the
    outdated template, and no record of any kind is created. Asserted
    separately for each of the two misspelled names (SC-001), so a check
    keyed to one cannot leave the other unrefused, and the refusal holds
    without exception for the published release itself, which carries both
    (D7)."""

    def test_only_ref_isgn_misspelled_is_refused(self):
        dataset = _dataset_from_fixture(
            FIXTURES_DIR / "header_misspelled_only_ref_isgn.csv"
        )
        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is True
        message = str(result.base_errors[0].error)
        assert "Ref_ISGN" in message
        assert "Ref_IGSN" in message
        assert "outdated" in message
        assert result.total_rows == 0

    def test_only_tc_pt_fuction_misspelled_is_refused(self):
        dataset = _dataset_from_fixture(
            FIXTURES_DIR / "header_misspelled_only_tc_pt_fuction.csv"
        )
        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is True
        message = str(result.base_errors[0].error)
        assert "tc_pT_fuction" in message
        assert "tc_pT_function" in message
        assert "outdated" in message
        assert result.total_rows == 0

    def test_published_release_header_carrying_both_misspellings_is_refused(self, db):
        """D7: the refusal holds without exception, including for the
        published release itself, which carries both misspelled names, and
        no record of any kind is created."""
        from heat_flow.models import HeatFlow

        dataset = _dataset_from_fixture(BASE_FIXTURE)
        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is True
        message = str(result.base_errors[0].error)
        assert "Ref_ISGN" in message
        assert "Ref_IGSN" in message
        assert "tc_pT_fuction" in message
        assert "tc_pT_function" in message
        assert result.total_rows == 0
        assert HeatFlow.objects.count() == 0


class TestGHFDBReleaseImportResourceUndefinedColumn:
    """T013, T014: a file carrying a column name the release format does
    not define is refused with that column named."""

    def test_undefined_column_is_refused_and_named(self):
        dataset = _dataset_from_fixture(FIXTURES_DIR / "header_undefined_column.csv")
        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is True
        message = str(result.base_errors[0].error)
        assert "p_comment_extra" in message
        assert result.total_rows == 0


class TestGHFDBReleaseImportResourceMissingColumn:
    """T015, T016: a file missing a column the release format requires is
    refused with that column named."""

    def test_missing_required_column_is_refused_and_named(self):
        """The fixture drops only the header cell (T005), leaving its data
        rows one column wider than the new header - read through the
        format itself, as a curator's upload would be, rather than built
        by hand."""
        path = FIXTURES_DIR / "header_missing_required_column.csv"
        dataset = GHFDBReleaseCSVFormat(encoding="utf-8-sig").create_dataset(
            path.read_bytes()
        )

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is True
        message = str(result.base_errors[0].error)
        assert "environment" in message
        assert result.total_rows == 0


class TestGHFDBReleaseImportResourceReportsEveryFault:
    """T019: a file whose header is correct but whose rows carry faults in
    several different rows reports every fault, not the first."""

    def test_every_faulty_row_is_reported(self):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, "qc", "not-a-number")
        rows = _with_cell(header, rows, 2, "qc_uncertainty", "also-not-a-number")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_validation_errors() is True
        assert len(result.invalid_rows) == 2
        faulty_row_numbers = {row.number for row in result.invalid_rows}
        assert faulty_row_numbers == {2, 4}


class TestGHFDBReleaseImportResourceLineNumber:
    """T020, T021: a reported fault carries the row number as it appears
    in the file, counting the header line, so a fault in the first data
    row reports as line 2."""

    def test_fault_in_the_first_data_row_reports_as_line_two(self):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, "qc", "not-a-number")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert len(result.invalid_rows) == 1
        assert result.invalid_rows[0].number == 2

    def test_fault_in_the_third_data_row_reports_as_line_four(self):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 2, "qc", "not-a-number")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert len(result.invalid_rows) == 1
        assert result.invalid_rows[0].number == 4


class TestGHFDBReleaseImportResourceColumnName:
    """T022, T023: a reported fault names the column as it appears in the
    header, not the model attribute the value would have been stored in -
    for every column that can refuse a value."""

    @pytest.mark.parametrize(
        ("column",),
        [
            ("qc",),
            ("qc_uncertainty",),
        ],
    )
    def test_fault_is_keyed_by_the_column_name(self, column):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, column, "not-a-number")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert len(result.invalid_rows) == 1
        error_dict = result.invalid_rows[0].error_dict
        assert column in error_dict
        # The model attribute a curator never sees must not appear instead.
        attribute = {"qc": "value", "qc_uncertainty": "uncertainty"}[column]
        assert attribute not in error_dict


class TestGHFDBReleaseImportResourceValueAndReason:
    """T024: a reported fault carries the offending value and a reason
    that distinguishes it from other reasons."""

    def test_fault_carries_the_offending_value(self):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, "qc", "not-a-number")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        message = str(result.invalid_rows[0].error_dict["qc"][0])
        assert "not-a-number" in message

    def test_two_different_offending_values_carry_two_different_messages(self):
        """The reason is not a generic, value-independent label - a
        curator reading two faults for the same column can tell them
        apart, because each message names the value that was refused."""
        header, rows = _corrected_header_and_rows()
        first_dataset = _make_dataset(
            header, _with_cell(header, rows, 0, "qc", "not-a-number")
        )
        second_dataset = _make_dataset(
            header, _with_cell(header, rows, 0, "qc", "48.1kg")
        )

        resource = GHFDBReleaseImportResource()
        first_result = resource.import_data(
            first_dataset, dry_run=True, raise_errors=False
        )
        second_result = resource.import_data(
            second_dataset, dry_run=True, raise_errors=False
        )

        first_message = str(first_result.invalid_rows[0].error_dict["qc"][0])
        second_message = str(second_result.invalid_rows[0].error_dict["qc"][0])
        assert first_message != second_message


class TestGHFDBReleaseImportResourceHeaderFailureStopsTheRowLoop:
    """T017, T018: after a header refusal, no data row was read at all -
    proven by a row that would itself have raised, which produces no
    second error."""

    def test_no_row_is_read_after_a_header_refusal(self):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, "qc", "not-a-number")
        header_with_fault, rows_with_fault = _without_column(
            header, rows, "environment"
        )
        dataset = _make_dataset(header_with_fault, rows_with_fault)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is True
        assert "environment" in str(result.base_errors[0].error)
        assert result.invalid_rows == []
        assert result.error_rows == []
        assert result.total_rows == 0
