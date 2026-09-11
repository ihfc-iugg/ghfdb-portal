"""
Shared constants for the GHFDB app.

Defines the canonical GHFDB spreadsheet column structure as four lists:

- PARENT_COLUMNS: parent-level column names (from PARENT level of GHFDB template row 6)
- CHILD_COLUMNS: child-level column names (from CHILD level of GHFDB template row 6)
- META_FIELDS: meta columns (quality codes / cross-level references)
- GHFDB_COLUMN_ORDER: Canonical full-column order (= PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS)
- CORRECTION_COL_MAP: Mapping of correction-flag columns to CorrectionTypeChoices values

All column names use the exact case from the official IHFC GHFDB spreadsheet template
(Fuchs et al. 2021, 2023), e.g. 'lat_NS', 'T_grad_mean', 'corr_HP_flag'.

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

# ---------------------------------------------------------------------------
# CORRECTION_COL_MAP
# Maps the GHFDB correction-flag spreadsheet column headers to the
# corresponding HeatFlowCorrection.CorrectionTypeChoices value.
# Keys use actual spreadsheet header names; values are TextChoices values.
# ---------------------------------------------------------------------------
CORRECTION_COL_MAP: dict[str, str] = {
    "corr_IS_flag": "IS",
    "corr_T_flag": "T",
    "corr_S_flag": "S",
    "corr_E_flag": "E",
    "corr_TOPO_flag": "TOPO",
    "corr_PAL_flag": "PAL",
    "corr_SUR_flag": "SUR",
    "corr_CONV_flag": "CONV",
    "corr_HR_flag": "HR",
}


# ---------------------------------------------------------------------------
# PARENT_COLUMNS
# The spreadsheet column names that belong to the parent level.
# Used by GHFDBParentImportResource.before_import() to deduplicate rows and
# extract unique parent records from the flat GHFDB XLSX.
# Note: Uses actual spreadsheet header names (case-sensitive as in row 6 of
# the official GHFDB XLSX template).
# ---------------------------------------------------------------------------
PARENT_COLUMNS: list[str] = [
    "ID_parent",
    "q",
    "q_uncertainty",
    "name",
    "lat_NS",
    "long_EW",
    "elevation",
    "environment",
    "p_comment",
    "corr_HP_flag",
    "total_depth_MD",
    "total_depth_TVD",
    "explo_method",
    "explo_purpose",
    "quality_parent",
]

# ---------------------------------------------------------------------------
# CHILD_COLUMNS
# The spreadsheet column names that belong to the child level.
# Used by GHFDBChildImportResource to extract child records from the flat
# GHFDB XLSX.
# Note: Uses actual spreadsheet header names (case-sensitive as in row 6 of
# the official GHFDB XLSX template).
# ---------------------------------------------------------------------------
CHILD_COLUMNS: list[str] = [
    "qc",
    "qc_uncertainty",
    "q_method",
    "q_top",
    "q_bottom",
    "probe_penetration",
    "publication_reference",
    "data_reference",
    "relevant_child",
    "c_comment",
    "corr_IS_flag",
    "corr_T_flag",
    "corr_S_flag",
    "corr_E_flag",
    "corr_TOPO_flag",
    "corr_PAL_flag",
    "corr_SUR_flag",
    "corr_CONV_flag",
    "corr_HR_flag",
    "expedition",
    "probe_type",
    "probe_length",
    "probe_tilt",
    "water_temperature",
    "geo_lithology",
    "geo_stratigraphy",
    "T_grad_mean",
    "T_grad_uncertainty",
    "T_grad_mean_cor",
    "T_grad_uncertainty_cor",
    "T_method_top",
    "T_method_bottom",
    "T_shutin_top",
    "T_shutin_bottom",
    "T_corr_top",
    "T_corr_bottom",
    "T_number",
    "q_date",
    "tc_mean",
    "tc_uncertainty",
    "tc_source",
    "tc_location",
    "tc_method",
    "tc_saturation",
    "tc_pT_conditions",
    "tc_pT_function",
    "tc_number",
    "tc_strategy",
    "Ref_IGSN",  # Recommend removing field.
    "quality_child",
]

# Quality/meta columns appended after PARENT_COLUMNS + CHILD_COLUMNS.
# Do NOT include names already present in PARENT_COLUMNS or CHILD_COLUMNS.
# ID, Reviewer_name, Reviewer_comment and Review_date are published-template
# columns the portal accepts without storing (FR-009, US-1 D7). They belong
# here rather than in PARENT_COLUMNS/CHILD_COLUMNS because those two feed
# admin.py's ColumnDisplay.list_display_for(), which requires a matching
# entry in columns.py's PublishedColumns.ENTRIES for every member.
META_FIELDS: list[str] = [
    "Quality_Code_Child",
    "Quality_Score_Parent",
    "ID",
    "Reviewer_name",
    "Reviewer_comment",
    "Review_date",
]


GHFDB_COLUMN_ORDER: list[str] = PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS

# ---------------------------------------------------------------------------
# Documented exceptions to "the template's spelling wins" (US-1 D7,
# specs/004-import-upload-template/decisions.md).
# ---------------------------------------------------------------------------

# ADR 0003 (docs/adr/0003): the currently distributed template carries these
# two misspellings. The portal keeps the corrected spelling internally
# (Ref_IGSN, tc_pT_function, both already present above) and refuses a file
# whose header carries either misspelled form, rather than silently mapping
# it. They therefore never resolve against PARENT_COLUMNS/CHILD_COLUMNS/
# META_FIELDS, by design.
REJECTED_MISSPELLED_COLUMNS: list[str] = ["Ref_ISGN", "tc_pT_fuction"]

# D8 (specs/002-ghfdb-proxy/decisions.md): site geography columns are portal
# additions, not part of the published GHFDB structure. Stored on
# HeatFlowSite (FR-008) and rendered by GHFDBParentAdmin after the published
# block, but deliberately never a member of PARENT_COLUMNS — adding them
# there would route them through ColumnDisplay.list_display_for(PARENT_COLUMNS)
# ahead of that separate block.
PORTAL_ADDITION_COLUMNS: list[str] = ["Country", "Region", "Continent", "Domain"]

# ---------------------------------------------------------------------------
# T005: accepted-and-not-stored.
# ---------------------------------------------------------------------------

# FR-009: the reviewer columns and ID are accepted without being stored.
# Declared as their own collection, distinct from PARENT_COLUMNS/
# CHILD_COLUMNS/META_FIELDS membership, so a column the reader recognises
# but deliberately does not store cannot be confused with one nothing
# resolves at all.
ACCEPTED_UNSTORED_COLUMNS: list[str] = [
    "ID",
    "Reviewer_name",
    "Reviewer_comment",
    "Review_date",
]


# ---------------------------------------------------------------------------
# T006: refuse a header that is not the official template's (FR-003).
# ---------------------------------------------------------------------------

# The header row of the official upload template, in the order the template
# carries it — row 6 of its "data list" sheet — with the two ADR 0003
# misspellings written in their corrected form, which is the spelling the
# portal uses everywhere and the spelling a file has to carry to be read.
#
# Written out rather than assembled from the lists above, because the
# submission template is not the published database structure that
# GHFDB_COLUMN_ORDER describes: the template has no ID_parent and none of the
# quality columns the portal computes for itself, and it carries the four
# geography columns the portal adds. ``tests/test_ghfdb/test_constants.py``
# holds this list to an unmodified copy of the template (FR-017), so a
# revised template surfaces as a failing test here rather than as a refused
# submission in production.
UPLOAD_TEMPLATE_HEADER_ROW: list[str] = [
    "q",
    "q_uncertainty",
    "name",
    "lat_NS",
    "long_EW",
    "elevation",
    "environment",
    "p_comment",
    "corr_HP_flag",
    "total_depth_MD",
    "total_depth_TVD",
    "explo_method",
    "explo_purpose",
    "qc",
    "qc_uncertainty",
    "q_method",
    "q_top",
    "q_bottom",
    "probe_penetration",
    "publication_reference",
    "data_reference",
    "relevant_child",
    "c_comment",
    "corr_IS_flag",
    "corr_T_flag",
    "corr_S_flag",
    "corr_E_flag",
    "corr_TOPO_flag",
    "corr_PAL_flag",
    "corr_SUR_flag",
    "corr_CONV_flag",
    "corr_HR_flag",
    "expedition",
    "probe_type",
    "probe_length",
    "probe_tilt",
    "water_temperature",
    "geo_lithology",
    "geo_stratigraphy",
    "T_grad_mean",
    "T_grad_uncertainty",
    "T_grad_mean_cor",
    "T_grad_uncertainty_cor",
    "T_method_top",
    "T_method_bottom",
    "T_shutin_top",
    "T_shutin_bottom",
    "T_corr_top",
    "T_corr_bottom",
    "T_number",
    "q_date",
    "tc_mean",
    "tc_uncertainty",
    "tc_source",
    "tc_location",
    "tc_method",
    "tc_saturation",
    "tc_pT_conditions",
    "tc_pT_function",
    "tc_number",
    "tc_strategy",
    "Ref_IGSN",
    "Reviewer_name",
    "Reviewer_comment",
    "Review_date",
    "Country",
    "Region",
    "Continent",
    "Domain",
    "ID",
]

OFFICIAL_TEMPLATE_HEADER: frozenset[str] = frozenset(UPLOAD_TEMPLATE_HEADER_ROW)

# Column A of the template's header row carries the row's own label rather
# than a column name, and the reader takes row 6 whole, so the label arrives
# in the header list alongside the real columns.
TEMPLATE_ROW_LABEL_CELL = "Short Name"

# Columns a file may carry or leave out without being a different template.
# Two groups, and nothing else is optional:
#
#   - identifiers. ``ID`` and ``ID_parent`` name a determination and its
#     parent so a later file can correct them (FR-016). A first submission
#     has no identifiers to give, and both import resources inject the
#     columns when they are absent, so requiring them would refuse exactly
#     the files the portal most expects.
#   - the assessment columns. The reviewer fields and the IGSN reference
#     resolve to nothing the portal stores (FR-009), and they are filled in
#     during assessment — after the submission has been read.
#
# ``igsn`` is the spelling the 2024 release file uses for the same reference;
# the child resource reads either.
OPTIONAL_TEMPLATE_COLUMNS: frozenset[str] = frozenset(
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

REQUIRED_TEMPLATE_COLUMNS: frozenset[str] = (
    OFFICIAL_TEMPLATE_HEADER - OPTIONAL_TEMPLATE_COLUMNS
)

RECOGNISED_TEMPLATE_COLUMNS: frozenset[str] = (
    OFFICIAL_TEMPLATE_HEADER | OPTIONAL_TEMPLATE_COLUMNS
)


def validate_official_header(header: list[str]) -> None:
    """Raise ``ValueError`` unless *header* is the official upload template's
    header: every column the template asks for, and no column it does not.

    A file may leave out the identifier and assessment columns
    (``OPTIONAL_TEMPLATE_COLUMNS``) and still be the official template — a
    first submission has no identifiers to give and no assessment yet. Any
    other missing column, and any column the template does not carry,
    including either ADR 0003 misspelling, makes this a different template
    and refuses the file.

    Column order is not enforced: every reader here addresses columns by
    name, and a contributor who moved a column has still sent every value
    the template asks for.

    Pure: inspects only the header it is given, so a caller that validates
    before reading any row never writes anything for a refused file.
    """
    supplied = {
        str(column).strip()
        for column in header
        if column is not None and str(column).strip()
    } - {TEMPLATE_ROW_LABEL_CELL}

    missing = sorted(REQUIRED_TEMPLATE_COLUMNS - supplied)
    unrecognised = sorted(supplied - RECOGNISED_TEMPLATE_COLUMNS)
    if not missing and not unrecognised:
        return

    faults = []
    if missing:
        faults.append(f"columns the template asks for and this file has not: {missing}")
    if unrecognised:
        faults.append(f"columns the template does not carry: {unrecognised}")
    raise ValueError(
        "Not the official upload template header — an outdated or "
        f"unrecognised template ({'; '.join(faults)}). Header read: {header!r}"
    )
