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
