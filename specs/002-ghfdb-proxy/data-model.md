# Data Model: GHFDB Flat Data Interface

**Feature**: 002-ghfdb-proxy
**Date**: 2026-04-13
**Prerequisites**: [research.md](research.md) complete

## Overview

This document defines the proxy model design, queryset API, annotation names, and field mappings for the GHFDB flat data interface. Import/export resource class design lives in [003-ghfdb-import-export/data-model.md](../003-ghfdb-import-export/data-model.md).

## Proxy Model & Queryset Design

### GHFDB Proxy Model

| Attribute | Value |
|---|---|
| **Extends** | `HeatFlow` (proxy, no new table) |
| **`verbose_name`** | `"GHFDB Entry"` |
| **`verbose_name_plural`** | `"GHFDB Entries"` |
| **`objects`** | `GHFDBManager` (provides `as_ghfdb_flat()` and `for_export()`) |

### HeatFlow — New Field: `local_id`

| Field | Type | Constraints | Purpose |
|---|---|---|---|
| `local_id` | `CharField(max_length=255)` | `null=True`, `blank=True`, `db_index=True` | Stores the GHFDB spreadsheet `ID` column; enables `import_id_fields = ("local_id",)` for upsert |

**Migration required**: Yes — adds a nullable varchar column to the `heat_flow_heatflow` table.

### GHFDBQuerySet Methods

| Method | DB Queries | Purpose |
|---|---|---|
| `as_ghfdb_flat()` | 1–2 (constant) | Annotated flat queryset for admin list, filtering, API |
| `for_export()` | ~16 (constant) | `as_ghfdb_flat()` + prefetch_related for all ~15 M2M relations |

### Annotation Name Mapping (used by `as_ghfdb_flat()`)

#### Scalar Annotations (folded into main SELECT with JOINs)

| Annotation Name | ORM Path | GHFDB Column |
|---|---|---|
| `site_name` | `sample__sample__name` | `name` |
| `lat_ns` | `sample__sample__location__y` | `lat_NS` |
| `long_ew` | `sample__sample__location__x` | `long_EW` |
| `site_elevation` | `sample__sample__elevation` | `elevation` |
| `site_environment` | `sample__sample__environment` | `environment` |
| `site_explo_method` | `sample__sample__explo_method` | `explo_method` |
| `site_country` | `sample__sample__country` | `Country` |
| `site_region` | `sample__sample__region` | `Region` |
| `site_continent` | `sample__sample__continent` | `Continent` |
| `site_domain` | `sample__sample__domain` | `Domain` |
| `total_depth_md` | `sample__sample__length` | `total_depth_MD` |
| `total_depth_tvd` | `sample__sample__vertical_depth` | `total_depth_TVD` |
| `p_q` | `parent__value` | `q` |
| `p_q_uncertainty` | `parent__uncertainty` | `q_uncertainty` |
| `p_corr_hp_flag` | `parent__corr_HP_flag` | `corr_HP_flag` |
| `p_comment` | `parent__comment` | `p_comment` |
| `interval_top` | `sample__top` | `q_top` |
| `interval_bottom` | `sample__bottom` | `q_bottom` |
| `tgrad_value` | `thermal_gradient__value` | `T_grad_mean` |
| `tgrad_uncertainty` | `thermal_gradient__uncertainty` | `T_grad_uncertainty` |
| `tgrad_corrected` | `thermal_gradient__corrected_value` | `T_grad_mean_cor` |
| `tgrad_corrected_unc` | `thermal_gradient__corrected_uncertainty` | `T_grad_uncertainty_cor` |
| `tgrad_shutin_top` | `thermal_gradient__shutin_top` | `T_shutin_top` |
| `tgrad_shutin_bottom` | `thermal_gradient__shutin_bottom` | `T_shutin_bottom` |
| `tgrad_number` | `thermal_gradient__number` | `T_number` |
| `tc_value` | `thermal_conductivity__value` | `tc_mean` |
| `tc_uncertainty` | `thermal_conductivity__uncertainty` | `tc_uncertainty` |
| `tc_number` | `thermal_conductivity__number` | `tc_number` |
| `probe_penetration` | `sample__probe_metadata__penetration` | `probe_penetration` |
| `probe_length` | `sample__probe_metadata__length` | `probe_length` |
| `probe_tilt` | `sample__probe_metadata__tilt` | `probe_tilt` |

#### Subquery Annotations (correction flags, one correlated subquery each)

| Annotation Name | Source | GHFDB Column |
|---|---|---|
| `corr_IS_flag` | `HeatFlowCorrection(type=IS).status` | `corr_IS_flag` |
| `corr_T_flag` | `HeatFlowCorrection(type=T).status` | `corr_T_flag` |
| `corr_S_flag` | `HeatFlowCorrection(type=S).status` | `corr_S_flag` |
| `corr_E_flag` | `HeatFlowCorrection(type=E).status` | `corr_E_flag` |
| `corr_TOPO_flag` | `HeatFlowCorrection(type=TOPO).status` | `corr_TOPO_flag` |
| `corr_PAL_flag` | `HeatFlowCorrection(type=PAL).status` | `corr_PAL_flag` |
| `corr_SUR_flag` | `HeatFlowCorrection(type=SUR).status` | `corr_SUR_flag` |
| `corr_CONV_flag` | `HeatFlowCorrection(type=CONV).status` | `corr_CONV_flag` |
| `corr_HR_flag` | `HeatFlowCorrection(type=HR).status` | `corr_HR_flag` |

#### Prefetch Paths (M2M fields, one query each for `for_export()`)

| Prefetch Path | GHFDB Column |
|---|---|
| `method` | `q_method` |
| `sample__sample__explo_purpose` | `explo_purpose` |
| `thermal_gradient__method_top` | `T_method_top` |
| `thermal_gradient__method_bottom` | `T_method_bottom` |
| `thermal_gradient__correction_top` | `T_corr_top` |
| `thermal_gradient__correction_bottom` | `T_corr_bottom` |
| `thermal_conductivity__source` | `tc_source` |
| `thermal_conductivity__location` | `tc_location` |
| `thermal_conductivity__method` | `tc_method` |
| `thermal_conductivity__saturation` | `tc_saturation` |
| `thermal_conductivity__pT_conditions` | `tc_pT_conditions` |
| `thermal_conductivity__pT_function` | `tc_pT_function` |
| `thermal_conductivity__strategy` | `tc_strategy` |
| `sample__probe_metadata__probe_type` | `probe_type` |
