"""Reconciles the official upload template's header against the canonical
column constants (US-1, T001-T006).

``tests/fixtures/official_upload_template.xlsx`` is an unmodified copy of
``docs/constitution/references/data_upload_template.xlsx`` — the file the
assessment team actually fills in, not a hand-built approximation of it
(D3, ``specs/004-import-upload-template/decisions.md``).
"""

import filecmp
from pathlib import Path

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
