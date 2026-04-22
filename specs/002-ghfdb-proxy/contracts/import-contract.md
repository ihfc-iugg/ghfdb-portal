# Import Contract: GHFDB Spreadsheet → Normalised Heat Flow Models

**Feature**: 002-ghfdb-proxy
**Date**: 2026-04-22
**Direction**: Import (flat spreadsheet → relational database)

## Overview

This contract defines the exact mapping between GHFDB spreadsheet columns and Django model fields for the import process. The import is split across two resources:

1. **Parent Import** (`GHFDBParentImportResource`) — processes parent-level columns
2. **Child Import** (`GHFDBChildImportResource`) — processes child-level columns

Both resources read the same XLSX file. The parent import deduplicates by `ID_parent`; the child import processes all rows.

## Spreadsheet Format

- **File type**: XLSX only
- **Sheet name**: `"data list"`
- **Header row**: Row 6 (1-based)
- **Unit row**: Row 7 (skipped)
- **Allowed-range row**: Row 8 (skipped)
- **Data rows**: Row 9+
- **Rows 1–5**: Metadata (skipped)

## Parent Import Contract

### Input → Output Mapping

| # | Spreadsheet Column | Type | Required | Target Model | Target Field | Widget | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `ID_parent` | integer | **M** | `ParentHeatFlow` | `ghfdb_id` | `IntegerWidget` | Upsert key. Empty string converts to `None`. |
| 2 | `q` | numeric | **M** | `ParentHeatFlow` | `value` | `QuantityWidget("mW/m²")` | Parent heat flow density. Validated ±10⁶. |
| 3 | `q_uncertainty` | numeric | O | `ParentHeatFlow` | `uncertainty` | `QuantityWidget("mW/m²")` | 1σ uncertainty. |
| 4 | `name` | string | **M** | `HeatFlowSite` | `name` | `CharWidget` | Site name. Via `ParentWidget`. |
| 5 | `lat_NS` | numeric | **M** | `Point` | `y` | `DecimalWidget` | Latitude. Via `ParentWidget` → Point. |
| 6 | `long_EW` | numeric | **M** | `Point` | `x` | `DecimalWidget` | Longitude. Via `ParentWidget` → Point. |
| 7 | `elevation` | numeric | O | `HeatFlowSite` | `elevation` | `QuantityWidget("m")` | Elevation above datum. |
| 8 | `environment` | concept | **M** | `HeatFlowSite` | `environment` | `ConceptWidget(GeographicEnvironment)` | Required in model. |
| 9 | `p_comment` | string | O | `ParentHeatFlow` | `comment` | `CharWidget` | Parent-level comments. |
| 10 | `corr_HP_flag` | yes/no | O | `ParentHeatFlow` | `corr_HP_flag` | `YesNoWidget` | Heat production correction flag. |
| 11 | `total_depth_MD` | numeric | O | `HeatFlowSite` | `length` | `QuantityWidget("m")` | Measured depth. |
| 12 | `total_depth_TVD` | numeric | O | `HeatFlowSite` | `vertical_depth` | `QuantityWidget("m")` | True vertical depth. |
| 13 | `explo_method` | concept | O | `HeatFlowSite` | `explo_method` | `ConceptWidget(ExplorationMethod)` | Access method. |
| 14 | `explo_purpose` | concepts | O | `HeatFlowSite` | `explo_purpose` | `MultiConceptWidget(ExplorationPurpose)` | Semicolon-separated. M2M. |
| 15 | `Country` | string | O | `HeatFlowSite` | `country` | `CharWidget` | Geographic classification. |
| 16 | `Region` | string | O | `HeatFlowSite` | `region` | `CharWidget` | |
| 17 | `Continent` | string | O | `HeatFlowSite` | `continent` | `CharWidget` | |
| 18 | `Domain` | string | O | `HeatFlowSite` | `domain` | `CharWidget` | |

**Legend**: **M** = Mandatory, O = Optional

### Deduplication Rule

When the spreadsheet contains multiple rows with the same `ID_parent` value, only the **first occurrence** is processed. Parent-level data for that `ID_parent` is taken from the first row; subsequent rows with the same `ID_parent` are skipped.

### Upsert Behaviour

- **Lookup**: `ParentHeatFlow.objects.filter(ghfdb_id=row["ID_parent"])`
- **If found**: Update all mapped fields
- **If not found**: Create new `ParentHeatFlow` + `HeatFlowSite` + `Point`

---

## Child Import Contract

### Input → Output Mapping — Direct Child Fields

| # | Spreadsheet Column | Type | Required | Target Model | Target Field | Widget | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `ID` | integer | **M** | `HeatFlow` | `ghfdb_id` | `IntegerWidget` | Upsert key. Empty string converts to `None`. Rows with no ID use `name` as natural key. |
| 2 | `qc` | numeric | **M** | `HeatFlow` | `value` | `QuantityWidget("mW/m²")` | Child heat flow density. |
| 3 | `qc_uncertainty` | numeric | O | `HeatFlow` | `uncertainty` | `QuantityWidget("mW/m²")` | 1σ uncertainty. |
| 4 | `q_method` | concepts | O | `HeatFlow` | `method` | `MultiConceptWidget(HeatFlowMethod)` | Semicolon-separated. M2M. |
| 5 | `q_date` | string | O | `HeatFlow` | `date_acquired` | `CharWidget` | Partial date (YYYY-MM-DD). |
| 6 | `expedition` | string | O | `HeatFlow` | `expedition` | `CharWidget` | Marine expedition name. |
| 7 | `water_temperature` | numeric | O | `HeatFlow` | `water_temperature` | `QuantityWidget("°C")` | Seafloor temperature. |
| 8 | `c_comment` | string | O | `HeatFlow` | `c_comment` | `CharWidget` | Child-level comments. |
| 9 | `relevant_child` | yes/no | O | `HeatFlow` | `is_relevant` | `YesNoWidget` | Used in parent calculation? |
| 10 | `ID_parent` | integer | **M** | `HeatFlow` | `parent` | `ForeignKeyWidget(ParentHeatFlow, "ghfdb_id")` | FK lookup by `ghfdb_id`. Parent must exist. |

### Input → Output Mapping — HeatFlowInterval (via IntervalWidget)

| # | Spreadsheet Column | Type | Required | Target Model | Target Field | Widget | Notes |
|---|---|---|---|---|---|---|---|
| 11 | `q_top` | numeric | O | `HeatFlowInterval` | `top` | `QuantityWidget("m")` | Interval top depth. |
| 12 | `q_bottom` | numeric | O | `HeatFlowInterval` | `bottom` | `QuantityWidget("m")` | Interval bottom depth. Must be > top. |
| 13 | `geo_lithology` | concepts | O | `HeatFlowInterval` | `lithology` | `MultiConceptWidget(...)` | M2M. |
| 14 | `geo_stratigraphy` | concepts | O | `HeatFlowInterval` | `stratigraphy` | `MultiConceptWidget(...)` | M2M. |

### Input → Output Mapping — ThermalGradient (via GradientWidget)

Created **only if** `T_grad_mean` is non-empty.

| # | Spreadsheet Column | Type | Required | Target Model | Target Field | Widget | Notes |
|---|---|---|---|---|---|---|---|
| 15 | `T_grad_mean` | numeric | sentinel | `ThermalGradient` | `value` | `QuantityWidget("K/km")` | Mean gradient. Sentinel: if empty, skip all T_grad fields. |
| 16 | `T_grad_uncertainty` | numeric | O | `ThermalGradient` | `uncertainty` | `QuantityWidget("K/km")` | |
| 17 | `T_grad_mean_cor` | numeric | O | `ThermalGradient` | `corrected_value` | `QuantityWidget("K/km")` | Corrected gradient. |
| 18 | `T_grad_uncertainty_cor` | numeric | O | `ThermalGradient` | `corrected_uncertainty` | `QuantityWidget("K/km")` | |
| 19 | `T_method_top` | concepts | O | `ThermalGradient` | `method_top` | `MultiConceptWidget(TemperatureMethod)` | M2M. |
| 20 | `T_method_bottom` | concepts | O | `ThermalGradient` | `method_bottom` | `MultiConceptWidget(TemperatureMethod)` | M2M. |
| 21 | `T_shutin_top` | numeric | O | `ThermalGradient` | `shutin_top` | `QuantityWidget("hr")` | Shut-in time. |
| 22 | `T_shutin_bottom` | numeric | O | `ThermalGradient` | `shutin_bottom` | `QuantityWidget("hr")` | |
| 23 | `T_corr_top` | concepts | O | `ThermalGradient` | `correction_top` | `MultiConceptWidget(TemperatureCorrection)` | M2M. |
| 24 | `T_corr_bottom` | concepts | O | `ThermalGradient` | `correction_bottom` | `MultiConceptWidget(TemperatureCorrection)` | M2M. |
| 25 | `T_number` | integer | O | `ThermalGradient` | `number` | `IntegerWidget` | Number of temperature points. |

### Input → Output Mapping — IntervalConductivity (via ConductivityWidget)

Created **only if** `tc_mean` is non-empty.

| # | Spreadsheet Column | Type | Required | Target Model | Target Field | Widget | Notes |
|---|---|---|---|---|---|---|---|
| 26 | `tc_mean` | numeric | sentinel | `IntervalConductivity` | `value` | `QuantityWidget("W/(m·K)")` | Mean conductivity. Sentinel: if empty, skip all tc fields. |
| 27 | `tc_uncertainty` | numeric | O | `IntervalConductivity` | `uncertainty` | `QuantityWidget("W/(m·K)")` | |
| 28 | `tc_source` | concepts | O | `IntervalConductivity` | `source` | `MultiConceptWidget(ConductivitySource)` | M2M. |
| 29 | `tc_location` | concepts | O | `IntervalConductivity` | `location` | `MultiConceptWidget(ConductivityLocation)` | M2M. |
| 30 | `tc_method` | concepts | O | `IntervalConductivity` | `method` | `MultiConceptWidget(ConductivityMethod)` | M2M. |
| 31 | `tc_saturation` | concepts | O | `IntervalConductivity` | `saturation` | `MultiConceptWidget(ConductivitySaturation)` | M2M. |
| 32 | `tc_pT_conditions` | concepts | O | `IntervalConductivity` | `pT_conditions` | `MultiConceptWidget(ConductivityPTConditions)` | M2M. |
| 33 | `tc_pT_function` | concepts | O | `IntervalConductivity` | `pT_function` | `MultiConceptWidget(ConductivityPTFunction)` | M2M. |
| 34 | `tc_number` | integer | O | `IntervalConductivity` | `number` | `IntegerWidget` | Number of samples. |
| 35 | `tc_strategy` | concepts | O | `IntervalConductivity` | `strategy` | `MultiConceptWidget(ConductivityStrategy)` | M2M. |

### Input → Output Mapping — Corrections (via `after_save_instance`)

| # | Spreadsheet Column | Type | Required | Target Model | Target Field | Notes |
|---|---|---|---|---|---|---|
| 36 | `corr_IS_flag` | status | O | `HeatFlowCorrection` | `status` (type=IS) | In-situ stress correction |
| 37 | `corr_T_flag` | status | O | `HeatFlowCorrection` | `status` (type=T) | Temperature correction |
| 38 | `corr_S_flag` | status | O | `HeatFlowCorrection` | `status` (type=S) | Sedimentation correction |
| 39 | `corr_E_flag` | status | O | `HeatFlowCorrection` | `status` (type=E) | Erosion correction |
| 40 | `corr_TOPO_flag` | status | O | `HeatFlowCorrection` | `status` (type=TOPO) | Topographic correction |
| 41 | `corr_PAL_flag` | status | O | `HeatFlowCorrection` | `status` (type=PAL) | Paleoclimatic correction |
| 42 | `corr_SUR_flag` | status | O | `HeatFlowCorrection` | `status` (type=SUR) | Surface temperature correction |
| 43 | `corr_CONV_flag` | status | O | `HeatFlowCorrection` | `status` (type=CONV) | Convection correction |
| 44 | `corr_HR_flag` | status | O | `HeatFlowCorrection` | `status` (type=HR) | Heat refraction correction |

### Input → Output Mapping — Probe Metadata (via `after_save_instance`)

| # | Spreadsheet Column | Type | Required | Target Model | Target Field | Notes |
|---|---|---|---|---|---|---|
| 45 | `probe_penetration` | numeric | O | `ProbeMetadata` | `penetration` | Only created if any probe column is non-empty |
| 46 | `probe_type` | concepts | O | `ProbeMetadata` | `probe_type` | M2M. |
| 47 | `probe_length` | numeric | O | `ProbeMetadata` | `length` | |
| 48 | `probe_tilt` | numeric | O | `ProbeMetadata` | `tilt` | |

---

## Validation Rules

### Field-Level Validation

| Rule | Source | Enforcement |
|---|---|---|
| Concept label must exist in vocabulary | `ConceptWidget` / `MultiConceptWidget` | `ValueError` with valid values list |
| Numeric quantity must be within model field bounds | `QuantityWidget` + `model.full_clean()` | `ValueError` or `ValidationError` |
| `q_bottom > q_top` when both present | `HeatFlowInterval.clean()` | `ValidationError` via `clean_model_instances` |
| `ID_parent` must exist for child import | `ForeignKeyWidget.clean()` | `DoesNotExist` error |
| Correction status must be valid for its type | `after_save_instance()` | `ValidationError` with column name |

### Transaction Semantics

- **Atomic**: Both resources use `use_transactions=True` + `rollback_on_validation_errors=True`
- If **any** row fails validation, the **entire import is rolled back**
- All row-level errors are collected and reported together (not just the first)

---

## Error Contract

### Error Format

Errors appear in the django-import-export admin UI per-row with the following format:

```
Row <N>:
  <field_name>: <error_message>
```

### Error Types

| Error Source | Example Message | Admin Display |
|---|---|---|
| Widget `ValueError` | `Invalid value 'xyz' for vocabulary 'HeatFlowMethod'. Valid values: BSR, BHT, ...` | Under the field column |
| Related model `full_clean()` | `ThermalGradient.value: Ensure this value is between -999999 and 999999` | Under the widget's field column, prefixed with model name |
| Main model `full_clean()` | `This field is required.` | Under the field column |
| FK lookup failure | `ParentHeatFlow matching query does not exist.` | Under the `parent` field column |
| Correction status | `Invalid correction status 'maybe' for corr_IS_flag` | Under the correction column |
