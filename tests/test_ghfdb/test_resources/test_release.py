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
