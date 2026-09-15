"""Reconciles the official upload template's header against the canonical
column constants (US-1, T001-T006).

``tests/fixtures/official_upload_template.xlsx`` is the published template
(``docs/constitution/references/data_upload_template.xlsx``, the file the
assessment team actually fills in) with exactly the two ADR 0003
misspellings corrected — ``tc_pT_fuction`` to ``tc_pT_function`` and
``Ref_ISGN`` to ``Ref_IGSN`` — and nothing else different (D3,
``specs/004-import-upload-template/decisions.md``).
"""

from pathlib import Path

import openpyxl
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
    TEMPLATE_ONLY_COLUMNS,
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
    """T001: the fixture differs from the published template in exactly the
    two ADR 0003 misspellings, and nowhere else."""

    def test_fixture_differs_from_the_published_template_in_exactly_the_two_corrected_cells(
        self, official_upload_template_workbook
    ):
        published_workbook = openpyxl.load_workbook(
            PUBLISHED_TEMPLATE_PATH, data_only=True
        )
        fixture_header = _read_header_row(official_upload_template_workbook)
        published_header = _read_header_row(published_workbook)

        assert len(fixture_header) == len(published_header), (
            "the fixture and the published template no longer carry the same "
            "number of header cells"
        )
        differences = {
            published_name: fixture_name
            for published_name, fixture_name in zip(
                published_header, fixture_header, strict=True
            )
            if published_name != fixture_name
        }
        assert differences == {
            "tc_pT_fuction": "tc_pT_function",
            "Ref_ISGN": "Ref_IGSN",
        }

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
    or by one of the documented exceptions in ``constants.py`` (US-1 D7):
    the two ADR 0003 misspellings the portal rejects rather than maps, the
    four D8 portal-addition geography columns, and the template-only columns
    the 2026.03 revision added, which feed the relational model directly
    without a published-column name of their own. A column the template
    carries that resolves through neither is exactly the disagreement FR-004
    exists to catch."""

    def test_every_template_column_resolves_to_a_canonical_constant(
        self, official_upload_template_workbook
    ):
        header = _read_header_row(official_upload_template_workbook)
        known = set(PARENT_COLUMNS) | set(CHILD_COLUMNS) | set(META_FIELDS)
        excepted = (
            set(REJECTED_MISSPELLED_COLUMNS)
            | set(PORTAL_ADDITION_COLUMNS)
            | set(TEMPLATE_ONLY_COLUMNS)
        )
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

    def test_the_new_2026_03_temperature_columns_are_required(self):
        """The four columns the 2026.03 template adds carry the absolute
        temperatures a determination's gradient is calculated from, not an
        identifier or an assessment field, so they are not optional."""
        for column in (
            "T_top_mean",
            "T_top_uncertainty",
            "T_bot_mean",
            "T_bot_uncertainty",
        ):
            assert column in REQUIRED_TEMPLATE_COLUMNS


class TestOfficialHeaderRefusal:
    """T006 (FR-003): a spreadsheet whose header row is not the official
    template's is refused whole, naming the header, rather than partially
    read. ``validate_official_header`` is pure — it inspects only the header
    it is given — so a refusal here happens before any row is read and
    before anything could be written."""

    def test_a_header_with_the_corrected_spellings_validates(self):
        validate_official_header(list(OFFICIAL_TEMPLATE_HEADER))  # must not raise

    def test_the_currently_distributed_template_is_refused_and_named(self):
        """ADR 0003: the currently distributed template itself carries the
        two misspellings (``tc_pT_fuction``, ``Ref_ISGN``) and is refused,
        naming them, rather than silently mapped. Read from the published
        file directly, since the fixture used elsewhere in this module has
        those two cells corrected."""
        published_workbook = openpyxl.load_workbook(
            PUBLISHED_TEMPLATE_PATH, data_only=True
        )
        header = _read_header_row(published_workbook)

        with pytest.raises(ValueError) as excinfo:
            validate_official_header(header)

        assert "tc_pT_fuction" in str(excinfo.value)
        assert "Ref_ISGN" in str(excinfo.value)

    def test_a_foreign_header_is_refused_and_named(self):
        foreign_header = ["not", "the", "official", "template"]

        with pytest.raises(ValueError) as excinfo:
            validate_official_header(foreign_header)

        assert repr(foreign_header) in str(excinfo.value)
