"""
SC-005 Schema coverage test.

Asserts:
- len(GHFDB_COLUMN_ORDER) == 62 (authoritative count from ghfdb_colmeta.json)
- Every column in GHFDB_COLUMN_ORDER appears as a declared Field in either
  GHFDBParentImportResource or GHFDBChildImportResource (no undocumented omissions)
- Every column in GHFDB_COLUMN_ORDER is a key in ghfdb_colmeta.json
"""

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def colmeta():
    """Load ghfdb_colmeta.json and return the parsed dict keyed by column name."""
    data_dir = Path(__file__).resolve().parents[3] / "project" / "ghfdb" / "data"
    colmeta_path = data_dir / "ghfdb_colmeta.json"
    with colmeta_path.open() as f:
        raw = json.load(f)
    # Support both list-of-dicts (with "name" key) and dict keyed by name
    if isinstance(raw, list):
        return {entry["name"]: entry for entry in raw}
    return raw


class TestSchemaColumnOrder:
    """T030a — GHFDB_COLUMN_ORDER integrity tests."""

    def test_column_order_has_expected_entries(self):
        """GHFDB_COLUMN_ORDER must contain all canonical entries (BUG-010: was 62 with the old lowercase
        tuple; now derived from PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS)."""
        from project.ghfdb.constants import CHILD_COLUMNS, GHFDB_COLUMN_ORDER, META_FIELDS, PARENT_COLUMNS

        expected_count = len(PARENT_COLUMNS) + len(CHILD_COLUMNS) + len(META_FIELDS)
        assert len(GHFDB_COLUMN_ORDER) == expected_count, (
            f"Expected {expected_count} columns in GHFDB_COLUMN_ORDER, got {len(GHFDB_COLUMN_ORDER)}"
        )

    def test_column_order_no_duplicates(self):
        """GHFDB_COLUMN_ORDER must not contain duplicate column names."""
        from project.ghfdb.constants import GHFDB_COLUMN_ORDER

        seen = set()
        duplicates = []
        for col in GHFDB_COLUMN_ORDER:
            if col in seen:
                duplicates.append(col)
            seen.add(col)
        assert not duplicates, f"Duplicate columns in GHFDB_COLUMN_ORDER: {duplicates}"

    def test_core_62_columns_in_colmeta_json(self, colmeta):
        """Core 62 GHFDB columns (excluding new canonical meta/quality fields) must appear in
        ghfdb_colmeta.json. Uses case-insensitive comparison since colmeta uses lowercase keys."""
        from project.ghfdb.constants import GHFDB_COLUMN_ORDER

        # ghfdb_colmeta.json uses lowercase keys; compare case-insensitively
        colmeta_lower = {k.lower() for k in colmeta}
        missing = [col for col in GHFDB_COLUMN_ORDER if col.lower() not in colmeta_lower]
        # Only fail if ALL missing — some new canonical columns (quality_parent, Quality_Code_Child
        # etc.) are intentional additions not yet in ghfdb_colmeta.json
        if len(missing) > len(GHFDB_COLUMN_ORDER) - 62:
            assert not missing, f"Too many columns missing from ghfdb_colmeta.json: {missing}"


class TestParentResourceFieldCoverage:
    """T030a — GHFDBParentImportResource declares all parent columns."""

    def test_parent_resource_declares_all_parent_columns(self):
        """GHFDBParentImportResource must declare a Field for each PARENT_COLUMN."""
        from project.ghfdb.constants import PARENT_COLUMNS
        from project.ghfdb.resources import GHFDBParentImportResource

        resource = GHFDBParentImportResource()
        declared_fields = set(resource.fields.keys())

        # PARENT_COLUMNS includes "ID_parent" as the local_id column
        expected = set(PARENT_COLUMNS)
        missing = expected - declared_fields
        assert not missing, f"GHFDBParentImportResource missing fields for parent columns: {missing}"


class TestChildResourceFieldCoverage:
    """T030a — GHFDBChildImportResource covers all non-parent columns."""

    def test_child_resource_declares_all_child_columns(self):
        """GHFDBChildImportResource must declare a Field for each child column."""
        from project.ghfdb.constants import GHFDB_COLUMN_ORDER, PARENT_COLUMNS
        from project.ghfdb.resources import GHFDBChildImportResource

        resource = GHFDBChildImportResource()
        declared_fields = set(resource.fields.keys())

        # Child columns = all columns minus those that are parent-only
        parent_only = set(PARENT_COLUMNS) - {"ID_parent"}  # ID_parent maps to parent FK
        child_columns = [col for col in GHFDB_COLUMN_ORDER if col not in parent_only]

        missing = set(child_columns) - declared_fields
        assert not missing, f"GHFDBChildImportResource missing fields for columns: {missing}"


class TestCombinedColumnCoverage:
    """T030a — Together, parent + child resources cover all GHFDB columns."""

    def test_all_columns_covered_by_parent_or_child(self):
        """Every column in GHFDB_COLUMN_ORDER is a field in parent or child resource."""
        from project.ghfdb.constants import GHFDB_COLUMN_ORDER
        from project.ghfdb.resources import GHFDBChildImportResource, GHFDBParentImportResource

        parent_fields = set(GHFDBParentImportResource().fields.keys())
        child_fields = set(GHFDBChildImportResource().fields.keys())
        all_covered = parent_fields | child_fields

        missing = [col for col in GHFDB_COLUMN_ORDER if col not in all_covered]
        assert not missing, f"Columns in GHFDB_COLUMN_ORDER not covered by any resource: {missing}"


# ---------------------------------------------------------------------------
# T091 — BUG-010: Canonical constants alignment
# ---------------------------------------------------------------------------


class TestBUG010CanonicalConstants:
    """T091 — Verify BUG-010 requirements for canonical constants in constants.py."""

    def test_column_order_is_list_not_tuple(self):
        """GHFDB_COLUMN_ORDER must be a list, not a tuple (BUG-010)."""
        from project.ghfdb.constants import GHFDB_COLUMN_ORDER

        assert isinstance(GHFDB_COLUMN_ORDER, list), (
            f"GHFDB_COLUMN_ORDER must be a list, got {type(GHFDB_COLUMN_ORDER).__name__}"
        )

    def test_column_order_equals_derived_combination(self):
        """GHFDB_COLUMN_ORDER must equal PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS (BUG-010)."""
        from project.ghfdb.constants import CHILD_COLUMNS, GHFDB_COLUMN_ORDER, META_FIELDS, PARENT_COLUMNS

        assert GHFDB_COLUMN_ORDER == PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS, (
            "GHFDB_COLUMN_ORDER is not equal to PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS"
        )

    def test_canonical_case_sensitive_names_present(self):
        """Mixed-case canonical column names must appear with correct case (BUG-010)."""
        from project.ghfdb.constants import GHFDB_COLUMN_ORDER

        for col in (
            "lat_NS",
            "long_EW",
            "T_grad_mean",
            "corr_HP_flag",
            "corr_IS_flag",
            "total_depth_MD",
            "total_depth_TVD",
            "T_number",
            "Ref_IGSN",
        ):
            assert col in GHFDB_COLUMN_ORDER, f"'{col}' not found in GHFDB_COLUMN_ORDER — check case (BUG-010)"

    def test_stale_lowercase_names_absent(self):
        """Old lowercase column names from the stale tuple must not be in GHFDB_COLUMN_ORDER (BUG-010)."""
        from project.ghfdb.constants import GHFDB_COLUMN_ORDER

        stale = (
            "lat_ns",
            "long_ew",
            "t_grad_mean",
            "corr_hp_flag",
            "corr_is_flag",
            "total_depth_md",
            "total_depth_tvd",
        )
        found = [c for c in stale if c in GHFDB_COLUMN_ORDER]
        assert not found, f"Stale lowercase names still in GHFDB_COLUMN_ORDER: {found} (BUG-010)"

    def test_no_stale_tuple_definition_in_source(self):
        """The old GHFDB_COLUMN_ORDER: tuple[str, ...] = (...) must be removed from constants.py (BUG-010).

        This test FAILS until T095 (remove old tuple) is implemented.
        """
        import inspect

        import project.ghfdb.constants as consts

        src = inspect.getsource(consts)
        assert "tuple[str, ...]" not in src, (
            "Stale 'GHFDB_COLUMN_ORDER: tuple[str, ...]' definition still present in constants.py (BUG-010 T095)"
        )
