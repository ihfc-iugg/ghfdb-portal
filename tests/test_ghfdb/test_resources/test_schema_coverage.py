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

    def test_column_order_has_exactly_62_entries(self):
        """GHFDB_COLUMN_ORDER must contain exactly 62 columns."""
        from project.ghfdb.resources._base import GHFDB_COLUMN_ORDER

        assert len(GHFDB_COLUMN_ORDER) == 62, (
            f"Expected 62 columns in GHFDB_COLUMN_ORDER, got {len(GHFDB_COLUMN_ORDER)}"
        )

    def test_column_order_no_duplicates(self):
        """GHFDB_COLUMN_ORDER must not contain duplicate column names."""
        from project.ghfdb.resources._base import GHFDB_COLUMN_ORDER

        seen = set()
        duplicates = []
        for col in GHFDB_COLUMN_ORDER:
            if col in seen:
                duplicates.append(col)
            seen.add(col)
        assert not duplicates, f"Duplicate columns in GHFDB_COLUMN_ORDER: {duplicates}"

    def test_every_column_in_colmeta_json(self, colmeta):
        """Every column in GHFDB_COLUMN_ORDER must appear in ghfdb_colmeta.json."""
        from project.ghfdb.resources._base import GHFDB_COLUMN_ORDER

        missing = [col for col in GHFDB_COLUMN_ORDER if col not in colmeta]
        assert not missing, f"Columns in GHFDB_COLUMN_ORDER missing from ghfdb_colmeta.json: {missing}"


class TestParentResourceFieldCoverage:
    """T030a — GHFDBParentImportResource declares all parent columns."""

    def test_parent_resource_declares_all_parent_columns(self):
        """GHFDBParentImportResource must declare a Field for each PARENT_COLUMN."""
        from project.ghfdb.resources import GHFDBParentImportResource
        from project.ghfdb.resources._base import PARENT_COLUMNS

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
        from project.ghfdb.resources import GHFDBChildImportResource
        from project.ghfdb.resources._base import GHFDB_COLUMN_ORDER, PARENT_COLUMNS

        resource = GHFDBChildImportResource()
        declared_fields = set(resource.fields.keys())

        # Child columns = all columns minus those that are parent-only
        parent_only = set(PARENT_COLUMNS) - {"ID_parent"}  # ID_parent maps to parent FK
        child_columns = [col for col in GHFDB_COLUMN_ORDER if col not in parent_only]

        missing = set(child_columns) - declared_fields
        assert not missing, f"GHFDBChildImportResource missing fields for columns: {missing}"


class TestCombinedColumnCoverage:
    """T030a — Together, parent + child resources cover all 62 GHFDB columns."""

    def test_all_columns_covered_by_parent_or_child(self):
        """Every column in GHFDB_COLUMN_ORDER is a field in parent or child resource."""
        from project.ghfdb.resources import GHFDBChildImportResource, GHFDBParentImportResource
        from project.ghfdb.resources._base import GHFDB_COLUMN_ORDER

        parent_fields = set(GHFDBParentImportResource().fields.keys())
        child_fields = set(GHFDBChildImportResource().fields.keys())
        all_covered = parent_fields | child_fields

        missing = [col for col in GHFDB_COLUMN_ORDER if col not in all_covered]
        assert not missing, f"Columns in GHFDB_COLUMN_ORDER not covered by any resource: {missing}"
