"""Reconciles the official upload template's header against the canonical
column constants (US-1, T001-T006).

``tests/fixtures/official_upload_template.xlsx`` is an unmodified copy of
``docs/constitution/references/data_upload_template.xlsx`` — the file the
assessment team actually fills in, not a hand-built approximation of it
(D3, ``specs/004-import-upload-template/decisions.md``).
"""

import filecmp
from pathlib import Path

from project.ghfdb.constants import CHILD_COLUMNS, META_FIELDS, PARENT_COLUMNS

OFFICIAL_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "official_upload_template.xlsx"
)
PUBLISHED_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "constitution"
    / "references"
    / "data_upload_template.xlsx"
)


class TestOfficialUploadTemplateFixture:
    """T001: the fixture is a byte-identical, openable copy of the published
    template."""

    def test_fixture_bytes_are_identical_to_the_published_template(self):
        assert filecmp.cmp(
            OFFICIAL_TEMPLATE_PATH, PUBLISHED_TEMPLATE_PATH, shallow=False
        ), (
            f"{OFFICIAL_TEMPLATE_PATH} must be byte-identical to "
            f"{PUBLISHED_TEMPLATE_PATH}"
        )

    def test_fixture_opens_as_a_workbook(self, official_upload_template_workbook):
        assert "data list" in official_upload_template_workbook.sheetnames


def _read_header_row(workbook):
    """The template's Short Name row (row 6 of the ``data list`` sheet).

    Column A carries the row's own label ("Short Name") rather than a
    published column, so the real header starts at column B.
    """
    worksheet = workbook["data list"]
    return [
        cell.value
        for cell in worksheet[6][1:]
        if cell.value is not None
    ]


class TestTemplateColumnsMatchTheCanonicalConstants:
    """T002: every column the official template carries must be recognised
    by ``PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS`` — a column the
    template carries that no constant covers is exactly the disagreement
    FR-004 exists to catch."""

    def test_every_template_column_resolves_to_a_canonical_constant(
        self, official_upload_template_workbook
    ):
        header = _read_header_row(official_upload_template_workbook)
        known = set(PARENT_COLUMNS) | set(CHILD_COLUMNS) | set(META_FIELDS)
        resolved = {name for name in header if name in known}

        assert resolved == set(header), (
            "template columns not covered by PARENT_COLUMNS + CHILD_COLUMNS + "
            f"META_FIELDS: {sorted(set(header) - resolved)}"
        )
