# Export Contract: Normalised Heat Flow Models → GHFDB Spreadsheet

**Feature**: 002-ghfdb-proxy
**Date**: 2026-04-13
**Direction**: Export (relational database → flat spreadsheet)

## Overview

The `GHFDBExportResource` produces a single flat XLSX where each row represents one child heat flow measurement. Parent-level data is denormalised (repeated) across all child rows sharing the same `ID_parent`.

## Export Format

- **File type**: XLSX only (via `GHFDBImportFormat`)
- **Sheet name**: `"data list"`
- **Header row**: Row 1 (standard export; the custom GHFDB header block is for import only)
- **All columns**: Exported in the canonical GHFDB column order

## Data Source

Export uses the `GHFDB` proxy model with the `GHFDBManager.for_export()` queryset, which:

1. Calls `as_ghfdb_flat()` to produce scalar annotations for all parent-level and child-level fields
2. Adds `prefetch_related()` for all M2M paths (14 M2M relationships)

This means the queryset is already flat — the resource simply maps annotation names to column headers.

## Column Mapping

| # | Spreadsheet Column | Source Expression | Widget | Notes |
|---|---|---|---|---|
| 1 | `ID` | `local_id` | `CharWidget` | Child measurement ID |
| 2 | `ID_parent` | `parent__local_id` (annotated) | `CharWidget` | Site/parent ID |
| 3 | `q` | `parent__value` (annotated) | `QuantityWidget("mW/m²")` | Parent heat flow density |
| 4 | `q_uncertainty` | `parent__uncertainty` (annotated) | `QuantityWidget("mW/m²")` | |
| 5 | `qc` | `value` | `QuantityWidget("mW/m²")` | Child heat flow density |
| 6 | `qc_uncertainty` | `uncertainty` | `QuantityWidget("mW/m²")` | |
| 7 | `name` | `site__name` (annotated) | `CharWidget` | Site name |
| 8 | `lat_NS` | `site__latitude` (annotated) | `DecimalWidget` | Latitude |
| 9 | `long_EW` | `site__longitude` (annotated) | `DecimalWidget` | Longitude |
| 10 | `elevation` | `site__elevation` (annotated) | `QuantityWidget("m")` | |
| 11 | `environment` | `site__environment` (annotated) | `ConceptWidget` | Exports concept label |
| 12 | `Country` | `site__country` (annotated) | `CharWidget` | |
| 13 | `Region` | `site__region` (annotated) | `CharWidget` | |
| 14 | `Continent` | `site__continent` (annotated) | `CharWidget` | |
| 15 | `Domain` | `site__domain` (annotated) | `CharWidget` | |
| 16 | `explo_method` | `site__explo_method` (annotated) | `ConceptWidget` | |
| 17 | `explo_purpose` | `site__explo_purpose` (prefetched) | `MultiConceptWidget` | Semicolon-separated |
| 18 | `total_depth_MD` | `site__length` (annotated) | `QuantityWidget("m")` | |
| 19 | `total_depth_TVD` | `site__vertical_depth` (annotated) | `QuantityWidget("m")` | |
| 20 | `q_method` | `method` (prefetched) | `MultiConceptWidget` | Semicolon-separated |
| 21 | `q_date` | `date_acquired` | `CharWidget` | |
| 22 | `expedition` | `expedition` | `CharWidget` | |
| 23 | `water_temperature` | `water_temperature` | `QuantityWidget("°C")` | |
| 24 | `relevant_child` | `is_relevant` | `YesNoWidget` | Exports "Y"/"N" |
| 25 | `q_top` | `interval__top` (annotated) | `QuantityWidget("m")` | |
| 26 | `q_bottom` | `interval__bottom` (annotated) | `QuantityWidget("m")` | |
| 27 | `T_grad_mean` | `gradient__value` (annotated) | `QuantityWidget("K/km")` | |
| 28 | `T_grad_uncertainty` | `gradient__uncertainty` (annotated) | `QuantityWidget("K/km")` | |
| 29 | `T_grad_mean_cor` | `gradient__corrected_value` (annotated) | `QuantityWidget("K/km")` | |
| 30 | `T_grad_uncertainty_cor` | `gradient__corrected_uncertainty` (annotated) | `QuantityWidget("K/km")` | |
| 31 | `T_method_top` | `gradient__method_top` (prefetched) | `MultiConceptWidget` | |
| 32 | `T_method_bottom` | `gradient__method_bottom` (prefetched) | `MultiConceptWidget` | |
| 33 | `T_shutin_top` | `gradient__shutin_top` (annotated) | `QuantityWidget("hr")` | |
| 34 | `T_shutin_bottom` | `gradient__shutin_bottom` (annotated) | `QuantityWidget("hr")` | |
| 35 | `T_corr_top` | `gradient__correction_top` (prefetched) | `MultiConceptWidget` | |
| 36 | `T_corr_bottom` | `gradient__correction_bottom` (prefetched) | `MultiConceptWidget` | |
| 37 | `T_number` | `gradient__number` (annotated) | `IntegerWidget` | |
| 38 | `tc_mean` | `conductivity__value` (annotated) | `QuantityWidget("W/(m·K)")` | |
| 39 | `tc_uncertainty` | `conductivity__uncertainty` (annotated) | `QuantityWidget("W/(m·K)")` | |
| 40 | `tc_source` | `conductivity__source` (prefetched) | `MultiConceptWidget` | |
| 41 | `tc_location` | `conductivity__location` (prefetched) | `MultiConceptWidget` | |
| 42 | `tc_method` | `conductivity__method` (prefetched) | `MultiConceptWidget` | |
| 43 | `tc_saturation` | `conductivity__saturation` (prefetched) | `MultiConceptWidget` | |
| 44 | `tc_pT_conditions` | `conductivity__pT_conditions` (prefetched) | `MultiConceptWidget` | |
| 45 | `tc_pT_function` | `conductivity__pT_function` (prefetched) | `MultiConceptWidget` | |
| 46 | `tc_number` | `conductivity__number` (annotated) | `IntegerWidget` | |
| 47 | `tc_strategy` | `conductivity__strategy` (prefetched) | `MultiConceptWidget` | |
| 48 | `geo_lithology` | `interval__lithology` (prefetched) | `MultiConceptWidget` | |
| 49 | `geo_stratigraphy` | `interval__stratigraphy` (prefetched) | `MultiConceptWidget` | |
| 50 | `probe_penetration` | `probe__penetration` (annotated) | `DecimalWidget` | |
| 51 | `probe_type` | `probe__probe_type` (prefetched) | `MultiConceptWidget` | |
| 52 | `probe_length` | `probe__length` (annotated) | `DecimalWidget` | |
| 53 | `probe_tilt` | `probe__tilt` (annotated) | `DecimalWidget` | |
| 54 | `corr_IS_flag` | correction subquery (type=IS) | `CharWidget` | |
| 55 | `corr_T_flag` | correction subquery (type=T) | `CharWidget` | |
| 56 | `corr_S_flag` | correction subquery (type=S) | `CharWidget` | |
| 57 | `corr_E_flag` | correction subquery (type=E) | `CharWidget` | |
| 58 | `corr_TOPO_flag` | correction subquery (type=TOPO) | `CharWidget` | |
| 59 | `corr_PAL_flag` | correction subquery (type=PAL) | `CharWidget` | |
| 60 | `corr_SUR_flag` | correction subquery (type=SUR) | `CharWidget` | |
| 61 | `corr_CONV_flag` | correction subquery (type=CONV) | `CharWidget` | |
| 62 | `corr_HR_flag` | correction subquery (type=HR) | `CharWidget` | |
| 63 | `corr_HP_flag` | `parent__corr_HP_flag` (annotated) | `YesNoWidget` | Parent-level correction |
| 64 | `p_comment` | `parent__comment` (annotated) | `CharWidget` | |
| 65 | `c_comment` | `c_comment` | `CharWidget` | |

## Widget Behaviour on Export

| Widget | `render()` Behaviour |
|---|---|
| `CharWidget` | Return string as-is (empty string for None) |
| `QuantityWidget` | Strip unit, return magnitude as float |
| `DecimalWidget` | Return Decimal as-is |
| `IntegerWidget` | Return int as-is |
| `ConceptWidget` | Return `concept.label` (preferred label string) |
| `MultiConceptWidget` | Return `"; ".join(c.label for c in concepts)` — semicolon + space separated |
| `YesNoWidget` | Return `"Y"` for True, `"N"` for False, `""` for None |

## Ordering

Export rows are ordered by `parent__local_id` (ascending), then `local_id` (ascending), grouping children under their parent site for readability.

## Filtering

Export via the admin UI respects the current queryset filters (search, list filters). If no filters are applied, all GHFDB measurements are exported.
