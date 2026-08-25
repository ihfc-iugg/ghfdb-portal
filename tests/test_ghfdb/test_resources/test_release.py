"""
Tests for the release import (specs/003-ghfdb-release-import).

Phase 1 - Foundations (T001-T005, T007). Mirrors the eventual resource
module this feature adds, ``project/ghfdb/resources/release.py`` - not yet
created; the reader itself lands in US-1 (T009). This module only
establishes what every later story builds on: the module pytest collects
(T001), the release format's column definitions (T002), the read /
recognised-and-discarded / refused split (T003), a fixture cut byte-for-byte
from the published release archive (T004) and its single-change variants
(T005), and the bibliographic fixtures US-2 needs because the portal's
citation keys are not unique (T007).
"""

import csv
import pathlib
import zipfile

import pytest

from project.ghfdb.constants import (
    CHILD_COLUMNS,
    DISCARDED_COLUMNS,
    MISSPELLED_COLUMNS,
    PARENT_COLUMNS,
    READ_COLUMNS,
    REFUSED_COLUMNS,
    RELEASE_COLUMNS,
)

pytestmark = pytest.mark.ghfdb

ARCHIVE_PATH = (
    pathlib.Path(__file__).resolve().parents[3] / "assets" / "ghfdb" / "IHFC_2024_GHFDB.zip"
)
FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures" / "release"
BASE_FIXTURE = FIXTURES_DIR / "release_sample.csv"


def read_csv_rows(path):
    """Every data row of a release-format CSV fixture, as a list of dicts."""
    text = path.read_text(encoding="utf-8-sig")
    return list(csv.DictReader(text.splitlines()))


def read_csv_header(path):
    """The raw header line of a release-format CSV fixture, as field names."""
    text = path.read_text(encoding="utf-8-sig")
    return next(csv.reader(text.splitlines()[:1]))


class TestReleaseImportModule:
    """T001: the module pytest collects for this feature's release reader.

    ``pytest --collect-only`` named nothing at this path before this class
    existed - there was no file here to collect."""

    def test_carries_the_ghfdb_marker(self, request):
        """Every module in this app's suite marks itself ``ghfdb``
        (tests/README.md); this is the release-import module's own proof of
        it, not inherited from a sibling."""
        assert request.node.get_closest_marker("ghfdb") is not None


class TestReleaseColumns:
    """T002: the release format's column definitions, derived from the
    published parent and determination columns rather than restated."""

    def test_begins_with_the_published_parent_columns_in_order(self):
        assert RELEASE_COLUMNS[: len(PARENT_COLUMNS)] == PARENT_COLUMNS

    def test_contains_every_published_determination_column_exactly_once(self):
        for column in CHILD_COLUMNS:
            assert RELEASE_COLUMNS.count(column) == 1


class TestReleaseColumnDisposition:
    """T003: which released columns are read, which are recognised and
    discarded, and which are refused, expressed as data (FR-007)."""

    def test_the_three_sets_are_pairwise_disjoint(self):
        assert READ_COLUMNS.isdisjoint(DISCARDED_COLUMNS)
        assert READ_COLUMNS.isdisjoint(REFUSED_COLUMNS)
        assert DISCARDED_COLUMNS.isdisjoint(REFUSED_COLUMNS)

    def test_their_union_is_the_release_column_list(self):
        assert set(RELEASE_COLUMNS) == READ_COLUMNS | DISCARDED_COLUMNS | REFUSED_COLUMNS

    def test_refused_columns_are_the_misspelled_names(self):
        assert set(MISSPELLED_COLUMNS) == REFUSED_COLUMNS

    def test_the_supplied_quality_code_is_discarded(self):
        """FR-033: the portal computes quality and does not ingest a
        supplied code."""
        assert "Quality_Code" in DISCARDED_COLUMNS

    def test_the_assessment_columns_are_discarded(self):
        """FR-034: the assessment team's own columns are recognised on the
        header and never stored."""
        assert {"Reviewer_name", "Reviewer_comment", "Review_date", "Review_status"} <= (
            DISCARDED_COLUMNS
        )


class TestReleaseFixture:
    """T004: a fixture cut byte-for-byte from the published release archive
    at assets/ghfdb/IHFC_2024_GHFDB.zip - real header, real column order,
    the byte-order mark preserved. A hand-built fixture that matches what a
    reader expects proves nothing about the format, which is how the gap
    this feature exists to close stayed invisible."""

    def test_fixture_header_equals_the_archive_header(self):
        with zipfile.ZipFile(ARCHIVE_PATH) as archive:
            (member_name,) = archive.namelist()
            with archive.open(member_name) as member:
                archive_header_line = member.readline()
        archive_header = archive_header_line.decode("utf-8-sig").rstrip("\r\n")

        fixture_header = BASE_FIXTURE.read_text(encoding="utf-8-sig").splitlines()[0]
        assert fixture_header == archive_header

    def test_fixture_preserves_the_byte_order_mark(self):
        assert BASE_FIXTURE.read_bytes().startswith(b"\xef\xbb\xbf")

    def test_fixture_includes_rows_sharing_a_site(self):
        rows = read_csv_rows(BASE_FIXTURE)
        site_ids = [row["ID_parent"] for row in rows]
        assert len(set(site_ids)) < len(site_ids)

    def test_fixture_includes_rows_sharing_an_interval(self):
        """Two rows at one site reporting the same depth range - not the
        indeterminate (no-depth) case, which is a separate requirement."""
        rows = read_csv_rows(BASE_FIXTURE)
        depths = [
            (row["ID_parent"], row["q_top"], row["q_bottom"])
            for row in rows
            if row["q_top"] or row["q_bottom"]
        ]
        assert len(set(depths)) < len(depths)

    def test_fixture_includes_rows_with_no_depth(self):
        rows = read_csv_rows(BASE_FIXTURE)
        no_depth = [row for row in rows if not row["q_top"] and not row["q_bottom"]]
        assert no_depth

    def test_fixture_includes_rows_from_more_than_one_publication(self):
        rows = read_csv_rows(BASE_FIXTURE)
        references = {row["publication_reference"] for row in rows}
        assert len(references) > 1

    def test_fixture_includes_an_unspecified_value(self):
        rows = read_csv_rows(BASE_FIXTURE)
        assert any("[Unspecified]" in row.values() for row in rows)
