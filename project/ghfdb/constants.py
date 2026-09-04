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
META_FIELDS: list[str] = [
    "Quality_Code_Child",
    "Quality_Score_Parent",
]


GHFDB_COLUMN_ORDER: list[str] = PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS


# ---------------------------------------------------------------------------
# RELEASE_COLUMNS (003, specs/003-ghfdb-release-import)
#
# A published release carries every published parent and determination
# column, plus columns of its own: two identifiers, the publication year, a
# computed quality code, four geography columns and four columns the
# assessment team fills in (D13) - RELEASE_ONLY_COLUMNS below. It is derived
# from PARENT_COLUMNS and CHILD_COLUMNS rather than restating them, per
# FR-007: this module is the one place both the header check and the row
# reading consult, so the two cannot disagree.
#
# The release the portal actually reads today carries two misspelled
# published names rather than their correct forms (R1); MISSPELLED_COLUMNS
# holds that mapping, and D7 requires the import to refuse a file carrying
# either without exception. Appending its keys is what lets RELEASE_COLUMNS
# also be the set REFUSED_COLUMNS, DISCARDED_COLUMNS and READ_COLUMNS
# partition below (T003) - one release-column list, not two.
# ---------------------------------------------------------------------------
RELEASE_ONLY_COLUMNS: list[str] = [
    "Reviewer_name",
    "Reviewer_comment",
    "Review_date",
    "Review_status",
    "Country",
    "Region",
    "Continent",
    "Domain",
    "Year",
    "Quality_Code",
    "ID_parent",
    "ID",
]

# FR-004, D7: the two published names the 2024 release is actually
# distributed with, mapped to the correct spelling the portal accepts.
# Neither correct spelling appears in the archive as downloaded (R1) -
# correcting them is the operator's preparation step, not the portal's.
MISSPELLED_COLUMNS: dict[str, str] = {
    "tc_pT_fuction": "tc_pT_function",
    "Ref_ISGN": "Ref_IGSN",
}

RELEASE_COLUMNS: list[str] = (
    PARENT_COLUMNS + CHILD_COLUMNS + RELEASE_ONLY_COLUMNS + list(MISSPELLED_COLUMNS)
)


# ---------------------------------------------------------------------------
# The read / recognised-and-discarded / refused split (T003)
#
# Three disjoint sets whose union is RELEASE_COLUMNS, expressed as data
# rather than as behaviour scattered through the reader (FR-007).
# ---------------------------------------------------------------------------

# Standing constraint 3 / FR-033: quality is computed here, never ingested -
# covers both the single release-wide code and the two legacy per-row
# fields, which R1 found are never present in a real release for the same
# reason. FR-034: the assessment team's own columns are recognised and not
# stored. Neither may cause a file to be refused (D13) - both are part of
# the format.
#
# D25: ``Year``, ``Ref_IGSN`` and ``data_reference`` join them for a
# different reason - not a standing constraint against ingesting them, but
# because no field anywhere in the portal's schema holds any of the three
# (confirmed directly against every model this feature writes, not
# assumed). D13's own framing is binary - a release column "is either read,
# or recognised and not stored" - so a column with no field to be read into
# belongs here, not among the required columns a curator's file would be
# refused for omitting. ``Ref_IGSN``/``data_reference`` already carry this
# same "resolves to nothing" status in the unrelated 002 proxy feature's own
# column mapping (``columns.py``); ``Year`` is the one piece of the release
# format US-4 will read at import time to decide which publication a site's
# determinations belong to (research.md, spec.md Clarifications), but that
# is a runtime comparison, not a stored field, so it is discarded here too.
DISCARDED_COLUMNS: frozenset[str] = frozenset(
    {
        "quality_parent",
        "quality_child",
        "Quality_Code",
        "Reviewer_name",
        "Reviewer_comment",
        "Review_date",
        "Review_status",
        "Year",
        "Ref_IGSN",
        "data_reference",
    }
)

# FR-004, D7: the two misspelled forms are recognised by name and refused
# without exception - the only members of RELEASE_COLUMNS a valid, corrected
# release never carries.
REFUSED_COLUMNS: frozenset[str] = frozenset(MISSPELLED_COLUMNS)

# Every other released column: consulted for a value and stored somewhere.
READ_COLUMNS: frozenset[str] = (
    frozenset(RELEASE_COLUMNS) - DISCARDED_COLUMNS - REFUSED_COLUMNS
)
