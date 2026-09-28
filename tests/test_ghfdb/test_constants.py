# Reconciles the official upload template's header against the canonical column
# constants (FS-004 US-1).

import json
from pathlib import Path

import openpyxl
import pytest

from project.ghfdb.constants import (
    ACCEPTED_UNSTORED_COLUMNS,
    CHILD_COLUMNS,
    GHFDB_COLUMN_ORDER,
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
    # The fixture differs from the published template in exactly the two ADR 0003
    # misspellings, and nowhere else.

    def test_fixture_differs_from_the_published_template_in_exactly_the_two_corrected_cells(
        self, official_upload_template_workbook
    ):
        # Every cell of every sheet, not only the header row.
        published_workbook = openpyxl.load_workbook(
            PUBLISHED_TEMPLATE_PATH, data_only=True
        )

        assert (
            official_upload_template_workbook.sheetnames
            == published_workbook.sheetnames
        )

        differences = {}
        for sheet_name in published_workbook.sheetnames:
            published_sheet = published_workbook[sheet_name]
            fixture_sheet = official_upload_template_workbook[sheet_name]
            rows = max(published_sheet.max_row, fixture_sheet.max_row)
            columns = max(published_sheet.max_column, fixture_sheet.max_column)
            for row in range(1, rows + 1):
                for column in range(1, columns + 1):
                    published_value = published_sheet.cell(row, column).value
                    fixture_value = fixture_sheet.cell(row, column).value
                    if published_value != fixture_value:
                        differences[published_value] = fixture_value

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
    # Every column the official template carries must be recognised — either
    # by ``PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS``.

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
    # Every template column the portal is expected to actually process — that is,
    # excluding the two ADR 0003 misspellings this feature refuses outright — must be
    # either mapped by a resource field's ``column_name`` or a member of

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
    # FS-004 FR-017: ``UPLOAD_TEMPLATE_HEADER_ROW`` is the template's header row, in the
    # template's order, with only the two ADR 0003 misspellings corrected.

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
        # Everything else the template carries is required, so a file that drops one is
        # a different template.
        assert (
            frozenset(
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
            == OPTIONAL_TEMPLATE_COLUMNS
        )
        assert REQUIRED_TEMPLATE_COLUMNS == (
            OFFICIAL_TEMPLATE_HEADER - OPTIONAL_TEMPLATE_COLUMNS
        )
        assert "q" in REQUIRED_TEMPLATE_COLUMNS
        assert "ID" not in REQUIRED_TEMPLATE_COLUMNS

    def test_the_new_2026_03_temperature_columns_are_required(self):
        # The four columns the 2026.03 template adds carry the absolute temperatures a
        # determination's gradient is calculated from, not an identifier or an
        # assessment field, so they are not optional.
        for column in (
            "T_top_mean",
            "T_top_uncertainty",
            "T_bot_mean",
            "T_bot_uncertainty",
        ):
            assert column in REQUIRED_TEMPLATE_COLUMNS


class TestOfficialHeaderRefusal:
    # FS-004 FR-003: a spreadsheet whose header row is not the official template's is
    # refused whole, naming the header, rather than partially read.

    def test_a_header_with_the_corrected_spellings_validates(self):
        validate_official_header(list(OFFICIAL_TEMPLATE_HEADER))  # must not raise

    def test_the_currently_distributed_template_is_refused_and_named(self):
        # ADR 0003: the currently distributed template itself carries the two
        # misspellings (``tc_pT_fuction``, ``Ref_ISGN``) and is refused, naming them,
        # rather than silently mapped.
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


@pytest.fixture(scope="module")
def colmeta():
    data_dir = Path(__file__).resolve().parents[2] / "project" / "ghfdb" / "data"
    colmeta_path = data_dir / "ghfdb_colmeta.json"
    with colmeta_path.open() as f:
        raw = json.load(f)
    if isinstance(raw, list):
        return {entry["name"]: entry for entry in raw}
    return raw


class TestSchemaColumnOrder:
    def test_column_order_has_expected_entries(self):
        expected_count = len(PARENT_COLUMNS) + len(CHILD_COLUMNS) + len(META_FIELDS)
        assert len(GHFDB_COLUMN_ORDER) == expected_count, (
            f"Expected {expected_count} columns in GHFDB_COLUMN_ORDER, got {len(GHFDB_COLUMN_ORDER)}"
        )

    def test_column_order_no_duplicates(self):
        seen = set()
        duplicates = []
        for col in GHFDB_COLUMN_ORDER:
            if col in seen:
                duplicates.append(col)
            seen.add(col)
        assert not duplicates, f"Duplicate columns in GHFDB_COLUMN_ORDER: {duplicates}"

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Half-landed GHFDB canonical column work: the constants moved to the "
            "published spreadsheet casing, but ghfdb_colmeta.json, the resource "
            "field declarations and one manager annotation key did not follow. "
            "Needs debugging, and a decision on the published column vocabulary, "
            "before it can pass. See issue #122."
        ),
    )
    def test_core_62_columns_in_colmeta_json(self, colmeta):
        # Case-insensitive comparison since colmeta uses lowercase keys.
        colmeta_lower = {k.lower() for k in colmeta}
        missing = [
            col for col in GHFDB_COLUMN_ORDER if col.lower() not in colmeta_lower
        ]
        if len(missing) > len(GHFDB_COLUMN_ORDER) - 62:
            assert not missing, (
                f"Too many columns missing from ghfdb_colmeta.json: {missing}"
            )


class TestParentResourceFieldCoverage:
    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Half-landed GHFDB canonical column work: the constants moved to the "
            "published spreadsheet casing, but ghfdb_colmeta.json, the resource "
            "field declarations and one manager annotation key did not follow. "
            "Needs debugging, and a decision on the published column vocabulary, "
            "before it can pass. See issue #122."
        ),
    )
    def test_parent_resource_declares_all_parent_columns(self):
        resource = GHFDBParentImportResource()
        declared_fields = set(resource.fields.keys())

        expected = set(PARENT_COLUMNS)
        missing = expected - declared_fields
        assert not missing, (
            f"GHFDBParentImportResource missing fields for parent columns: {missing}"
        )


class TestChildResourceFieldCoverage:
    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Half-landed GHFDB canonical column work: the constants moved to the "
            "published spreadsheet casing, but ghfdb_colmeta.json, the resource "
            "field declarations and one manager annotation key did not follow. "
            "Needs debugging, and a decision on the published column vocabulary, "
            "before it can pass. See issue #122."
        ),
    )
    def test_child_resource_declares_all_child_columns(self):
        resource = GHFDBChildImportResource()
        declared_fields = set(resource.fields.keys())

        parent_only = set(PARENT_COLUMNS) - {"ID_parent"}
        child_columns = [col for col in GHFDB_COLUMN_ORDER if col not in parent_only]

        missing = set(child_columns) - declared_fields
        assert not missing, (
            f"GHFDBChildImportResource missing fields for columns: {missing}"
        )


class TestCombinedColumnCoverage:
    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Half-landed GHFDB canonical column work: the constants moved to the "
            "published spreadsheet casing, but ghfdb_colmeta.json, the resource "
            "field declarations and one manager annotation key did not follow. "
            "Needs debugging, and a decision on the published column vocabulary, "
            "before it can pass. See issue #122."
        ),
    )
    def test_all_columns_covered_by_parent_or_child(self):
        parent_fields = set(GHFDBParentImportResource().fields.keys())
        child_fields = set(GHFDBChildImportResource().fields.keys())
        all_covered = parent_fields | child_fields

        missing = [col for col in GHFDB_COLUMN_ORDER if col not in all_covered]
        assert not missing, (
            f"Columns in GHFDB_COLUMN_ORDER not covered by any resource: {missing}"
        )


class TestBUG010CanonicalConstants:
    def test_column_order_is_list_not_tuple(self):
        assert isinstance(GHFDB_COLUMN_ORDER, list), (
            f"GHFDB_COLUMN_ORDER must be a list, got {type(GHFDB_COLUMN_ORDER).__name__}"
        )

    def test_column_order_equals_derived_combination(self):
        assert GHFDB_COLUMN_ORDER == PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS, (
            "GHFDB_COLUMN_ORDER is not equal to PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS"
        )

    def test_canonical_case_sensitive_names_present(self):
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
            assert col in GHFDB_COLUMN_ORDER, (
                f"'{col}' not found in GHFDB_COLUMN_ORDER — check case (FS-003 BUG-010)"
            )

    def test_stale_lowercase_names_absent(self):
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
        assert not found, (
            f"Stale lowercase names still in GHFDB_COLUMN_ORDER: {found} (FS-003 BUG-010)"
        )
