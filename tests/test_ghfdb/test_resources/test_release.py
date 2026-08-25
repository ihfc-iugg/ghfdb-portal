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
from literature.models import LiteratureItem

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


class TestReleaseFixtureVariants:
    """T005: each variant differs from the T004 base fixture in exactly the
    intended cell or header, and no other byte."""

    def test_one_variant_per_misspelled_header_holds_the_other_misspelled(self):
        """SC-001, D7: proven for each misspelled name separately, so a
        check keyed to one cannot leave the other unrefused."""
        base_header = read_csv_header(BASE_FIXTURE)

        only_ref_isgn_misspelled = read_csv_header(
            FIXTURES_DIR / "header_misspelled_only_ref_isgn.csv"
        )
        assert only_ref_isgn_misspelled.count("tc_pT_function") == 1
        assert only_ref_isgn_misspelled.count("tc_pT_fuction") == 0
        assert only_ref_isgn_misspelled.count("Ref_ISGN") == 1
        assert set(base_header) - set(only_ref_isgn_misspelled) == {"tc_pT_fuction"}

        only_tc_pt_fuction_misspelled = read_csv_header(
            FIXTURES_DIR / "header_misspelled_only_tc_pt_fuction.csv"
        )
        assert only_tc_pt_fuction_misspelled.count("Ref_IGSN") == 1
        assert only_tc_pt_fuction_misspelled.count("Ref_ISGN") == 0
        assert only_tc_pt_fuction_misspelled.count("tc_pT_fuction") == 1
        assert set(base_header) - set(only_tc_pt_fuction_misspelled) == {"Ref_ISGN"}

    def test_undefined_header_variant_renames_one_column_to_an_unrecognised_name(self):
        base_header = read_csv_header(BASE_FIXTURE)
        variant_header = read_csv_header(FIXTURES_DIR / "header_undefined_column.csv")

        assert len(variant_header) == len(base_header)
        assert "p_comment_extra" not in RELEASE_COLUMNS
        assert set(base_header) - set(variant_header) == {"p_comment"}
        assert set(variant_header) - set(base_header) == {"p_comment_extra"}

    def test_missing_required_header_variant_drops_exactly_one_name(self):
        base_header = read_csv_header(BASE_FIXTURE)
        variant_header = read_csv_header(FIXTURES_DIR / "header_missing_required_column.csv")

        assert len(variant_header) == len(base_header) - 1
        assert set(base_header) - set(variant_header) == {"environment"}
        assert set(variant_header) - set(base_header) == set()

    @pytest.mark.parametrize(
        ("filename", "row_id", "column", "old_value", "new_value"),
        [
            (
                "bad_vocabulary_value.csv",
                "R24-054171",
                "geo_lithology",
                "sediment",
                "[not_a_real_lithology]",
            ),
            (
                "numeric_value_in_text_column.csv",
                "R24-033563",
                "p_comment",
                "",
                "12345",
            ),
            (
                "disagreement_shared_site.csv",
                "R24-054171",
                "elevation",
                "-4520.00",
                "-9999.00",
            ),
            (
                "disagreement_shared_interval_probe.csv",
                "R24-053075",
                "probe_type",
                "[Outrigger probe (Ewing) with corer]",
                "[Free fall probe (Lister-type)]",
            ),
        ],
    )
    def test_single_row_variant_changes_exactly_one_cell(
        self, filename, row_id, column, old_value, new_value
    ):
        base_rows = {row["ID"]: row for row in read_csv_rows(BASE_FIXTURE)}
        variant_rows = {row["ID"]: row for row in read_csv_rows(FIXTURES_DIR / filename)}

        assert set(base_rows) == set(variant_rows)
        assert base_rows[row_id][column] == old_value
        assert variant_rows[row_id][column] == new_value

        for row_key, base_row in base_rows.items():
            variant_row = variant_rows[row_key]
            differing = {
                key for key in base_row if base_row[key] != variant_row.get(key)
            }
            expected = {column} if row_key == row_id else set()
            assert differing == expected

    def test_disagreement_variants_disagree_about_a_row_the_base_agreed_on(self):
        """The base fixture's two rows sharing an interval agree about the
        probe and every row sharing site R24-P003477 agrees about
        elevation - each variant breaks exactly one of those agreements."""
        base_rows = {row["ID"]: row for row in read_csv_rows(BASE_FIXTURE)}
        assert base_rows["R24-033563"]["probe_type"] == base_rows["R24-053075"]["probe_type"]
        site_elevations = {
            row["elevation"] for row in base_rows.values() if row["ID_parent"] == "R24-P003477"
        }
        assert len(site_elevations) == 1


class TestBibliographicFixtures:
    """T007: the portal's bibliographic citation keys are not unique (D5,
    FR-020), so a release row's publication reference can match more than
    one record. ``LiteratureItem.citation_key`` is unique at the database
    level, so the two records here differ literally - by case and a
    trailing space - the same difference FR-017 requires the import to
    ignore when comparing publication references."""

    def test_known_citation_key_yields_one_record(
        self, literature_with_known_citation_key
    ):
        matches = LiteratureItem.objects.filter(
            citation_key=literature_with_known_citation_key.citation_key
        )
        assert matches.count() == 1

    def test_ambiguous_citation_key_yields_two_records_on_a_normalised_lookup(
        self, literature_with_ambiguous_citation_key
    ):
        first, second = literature_with_ambiguous_citation_key
        normalised = first.citation_key.strip().lower()
        assert second.citation_key.strip().lower() == normalised
        assert first.citation_key != second.citation_key

        matches = [
            item
            for item in LiteratureItem.objects.all()
            if item.citation_key.strip().lower() == normalised
        ]
        assert {item.pk for item in matches} == {first.pk, second.pk}
