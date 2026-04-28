"""
Shared constants for the GHFDB app.

Defines the canonical GHFDB spreadsheet column structure as four lists:

- PARENT_COLUMNS: 15 parent-level column names (from PARENT level of GHFDB template row 6)
- CHILD_COLUMNS: 50 child-level column names (from CHILD level of GHFDB template row 6)
- META_FIELDS: 4 meta columns (quality codes / cross-level references)
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
# Maps the 9 GHFDB correction-flag spreadsheet column headers to the
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
# The 18 spreadsheet column names that belong to the parent level.
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
# The 44 spreadsheet column names that belong to the child level.
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
