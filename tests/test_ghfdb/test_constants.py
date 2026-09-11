"""Reconciles the official upload template's header against the canonical
column constants (US-1, T001-T006).

``tests/fixtures/official_upload_template.xlsx`` is an unmodified copy of
``docs/constitution/references/data_upload_template.xlsx`` — the file the
assessment team actually fills in, not a hand-built approximation of it
(D3, ``specs/004-import-upload-template/decisions.md``).
"""

import filecmp
from pathlib import Path

import pytest

from project.ghfdb.constants import (
    ACCEPTED_UNSTORED_COLUMNS,
    CHILD_COLUMNS,
    META_FIELDS,
    OFFICIAL_TEMPLATE_HEADER,
    OPTIONAL_TEMPLATE_COLUMNS,
    PARENT_COLUMNS,
    PORTAL_ADDITION_COLUMNS,
    REJECTED_MISSPELLED_COLUMNS,
    REQUIRED_TEMPLATE_COLUMNS,
    UPLOAD_TEMPLATE_HEADER_ROW,
    validate_official_header,
)
from project.ghfdb.resources import GHFDBChildImportResource, GHFDBParentImportResource

OFFICIAL_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "official_upload_template.xlsx"
)
PUBLISHED_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[2]
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
    return [cell.value for cell in worksheet[6][1:] if cell.value is not None]


class TestTemplateColumnsMatchTheCanonicalConstants:
    """T002/T004: every column the official template carries must be
    recognised — either by ``PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS``,
    or by one of the two documented exceptions in ``constants.py`` (US-1 D7):
    the two ADR 0003 misspellings the portal rejects rather than maps, and
    the four D8 portal-addition geography columns. A column the template
    carries that resolves through neither is exactly the disagreement FR-004
    exists to catch."""

    def test_every_template_column_resolves_to_a_canonical_constant(
        self, official_upload_template_workbook
    ):
        header = _read_header_row(official_upload_template_workbook)
        known = set(PARENT_COLUMNS) | set(CHILD_COLUMNS) | set(META_FIELDS)
        excepted = set(REJECTED_MISSPELLED_COLUMNS) | set(PORTAL_ADDITION_COLUMNS)
        resolved = {name for name in header if name in known or name in excepted}

        assert resolved == set(header), (
            "template columns not covered by PARENT_COLUMNS + CHILD_COLUMNS + "
            "META_FIELDS, nor a documented exception: "
            f"{sorted(set(header) - resolved)}"
        )


class TestEveryTemplateColumnIsMappedOrAccepted:
    """T005: every template column the portal is expected to actually
    process — that is, excluding the two ADR 0003 misspellings T006 refuses
    outright — must be either mapped by a resource field's ``column_name``
    or a member of ``ACCEPTED_UNSTORED_COLUMNS``. Without this, "unmatched"
    (a real defect) and "deliberately ignored" look the same."""

    def test_every_template_column_is_mapped_or_accepted(
        self, official_upload_template_workbook
    ):
        header = _read_header_row(official_upload_template_workbook)
        mapped = {
            field.column_name for field in GHFDBParentImportResource().fields.values()
        } | {field.column_name for field in GHFDBChildImportResource().fields.values()}
        handled = mapped | set(ACCEPTED_UNSTORED_COLUMNS)
        considered = set(header) - set(REJECTED_MISSPELLED_COLUMNS)

        assert considered <= handled, (
            "template columns neither mapped by a resource field nor in "
            f"ACCEPTED_UNSTORED_COLUMNS: {sorted(considered - handled)}"
        )


class TestTheHeaderConstantIsTheTemplatesOwnHeader:
    """FR-017: ``UPLOAD_TEMPLATE_HEADER_ROW`` is the template's header row,
    in the template's order, with only the two ADR 0003 misspellings
    corrected. Pinned to an unmodified copy of the template so a revised
    template shows up as a failure here rather than as a refused submission
    in production."""

    def test_it_matches_the_templates_header_row_corrected(
        self, official_upload_template_workbook
    ):
        corrections = {"tc_pT_fuction": "tc_pT_function", "Ref_ISGN": "Ref_IGSN"}
        header = [
            corrections.get(name, name)
            for name in _read_header_row(official_upload_template_workbook)
        ]

        assert header == UPLOAD_TEMPLATE_HEADER_ROW

    def test_the_optional_columns_are_the_identifiers_and_assessment_columns(self):
        """Everything else the template carries is required, so a file that
        drops one is a different template. The optional set is small and
        deliberate: identifiers a first submission cannot have, and the
        columns filled in after a submission is read."""
        assert OPTIONAL_TEMPLATE_COLUMNS == frozenset(
            {
                "ID",
                "ID_parent",
                "Ref_IGSN",
                "igsn",
                "Reviewer_name",
                "Reviewer_comment",
                "Review_date",
            }
        )
        assert REQUIRED_TEMPLATE_COLUMNS == (
            OFFICIAL_TEMPLATE_HEADER - OPTIONAL_TEMPLATE_COLUMNS
        )
        assert "q" in REQUIRED_TEMPLATE_COLUMNS
        assert "ID" not in REQUIRED_TEMPLATE_COLUMNS


class TestOfficialHeaderRefusal:
    """T006 (FR-003): a spreadsheet whose header row is not the official
    template's is refused whole, naming the header, rather than partially
    read. ``validate_official_header`` is pure — it inspects only the header
    it is given — so a refusal here happens before any row is read and
    before anything could be written."""

    def test_a_header_with_the_corrected_spellings_validates(self):
        validate_official_header(list(OFFICIAL_TEMPLATE_HEADER))  # must not raise

    def test_the_currently_distributed_template_is_refused_and_named(
        self, official_upload_template_workbook
    ):
        """ADR 0003: the currently distributed template itself carries the
        two misspellings (``tc_pT_fuction``, ``Ref_ISGN``) and is refused,
        naming them, rather than silently mapped."""
        header = _read_header_row(official_upload_template_workbook)

        with pytest.raises(ValueError) as excinfo:
            validate_official_header(header)

        assert "tc_pT_fuction" in str(excinfo.value)
        assert "Ref_ISGN" in str(excinfo.value)

    def test_a_foreign_header_is_refused_and_named(self):
        foreign_header = ["not", "the", "official", "template"]

        with pytest.raises(ValueError) as excinfo:
            validate_official_header(foreign_header)

        assert repr(foreign_header) in str(excinfo.value)
