# Data Model: GHFDB Import/Export Resource Classes

**Feature**: 003-ghfdb-import-export
**Date**: 2026-04-13 (split from `002-ghfdb-product-utilities` data-model.md — 2026-04-15)
**Prerequisites**: [research.md](research.md) complete; `002-ghfdb-product-utilities` proxy model complete

## Overview

This document defines the class hierarchy, field mappings, and data flow for the GHFDB import/export `resources/` package. The proxy model and queryset design lives in `002-ghfdb-product-utilities/data-model.md`. This document covers only the import/export layer.

## Entity Relationship Summary

```
GHFDB Spreadsheet (flat, ~62 columns per row)
    │
    ├── Parent Import Resource ──► ParentHeatFlow ──► HeatFlowSite ──► Point (location)
    │                                                    │
    │                                                    ├── explo_purpose (M2M)
    │                                                    └── geographic fields
    │
    └── Child Import Resource  ──► HeatFlow ──► HeatFlowInterval
                                     │              │
                                     ├── parent (FK to ParentHeatFlow)
                                     ├── thermal_gradient (FK) ──► ThermalGradient
                                     │                                  ├── method_top (M2M)
                                     │                                  ├── method_bottom (M2M)
                                     │                                  ├── correction_top (M2M)
                                     │                                  └── correction_bottom (M2M)
                                     ├── thermal_conductivity (FK) ──► IntervalConductivity
                                     │                                      ├── source (M2M)
                                     │                                      ├── location (M2M)
                                     │                                      ├── method (M2M)
                                     │                                      ├── saturation (M2M)
                                     │                                      ├── pT_conditions (M2M)
                                     │                                      ├── pT_function (M2M)
                                     │                                      └── strategy (M2M)
                                     ├── method (M2M)
                                     └── corrections ──► HeatFlowCorrection (9 types)
                                                              └── ProbeMetadata (1:1 on interval)
```

## Module: `_base.py` — Shared Constants & Format

### `GHFDBImportFormat`

Custom XLSX reader for the GHFDB spreadsheet template:

| Row | Content | Treatment |
|-----|---------|-----------|
| 1–5 | Metadata (ID, Obligation, Domain, Quality Relevance, Name) | Skipped |
| 6 | Short Name (technical column headers) | Read as headers |
| 7 | Unit labels | Skipped |
| 8 | Allowed range of values | Skipped |
| 9+ | Data rows | Read as data (`min_row=9`) |

Sheet name: `"data list"`

### Column Order Constants

- **`GHFDB_COLUMN_ORDER`**: Ordered list of all 62 GHFDB spreadsheet column names in canonical order (Fuchs et al. 2023), sourced from `ghfdb_colmeta.json`
- **`PARENT_COLUMNS`**: 18 parent-level column names processed by `GHFDBParentImportResource`
- **`CORRECTION_COL_MAP`**: `{"corr_IS_flag": "IS", "corr_T_flag": "T", ...}` — 9-entry dict mapping correction-flag column names to `HeatFlowCorrection.correction_type` values

## Module: `_widgets.py` — Widget Hierarchy

### Leaf Widgets

| Widget | Purpose | Notes |
|--------|---------|-------|
| `ConceptWidget` | Maps spreadsheet label → `Concept` instance | Case-insensitive; FR-016 normalisation applied |
| `MultiConceptWidget` | Semicolon-split + batched `ConceptWidget` | Returns list of `Concept` instances |
| `QuantityWidget` | Converts numeric string → `Pint Quantity`; renders as plain magnitude | Unit specified at init |
| `YesNoWidget` | `"Yes"` → `True`, `"No"` → `False`, empty → `None` | |

### FR-016 Normalisation

All concept token inputs are processed by `normalize_vocab_token(raw)` before cache lookup:

```python
def normalize_vocab_token(raw: str) -> str:
    """Strip square brackets and lowercase for vocabulary matching."""
    return raw.strip("[]").lower()
```

Error messages include the **original** pre-normalisation token text for user traceability.

### `RelatedModelWidget` and Subclasses

| Widget | Sentinel Column | Target Models | M2M Fields |
|--------|----------------|---------------|-----------|
| `ParentWidget` | `"name"` | `HeatFlowSite` + `Point` | `explo_purpose` |
| `IntervalWidget` | None (always creates) | `HeatFlowInterval` | `geo_lithology` → `lithology`; `geo_stratigraphy` → `age` (⚠️ NOT `stratigraphy` — see BUG-009) |
| `GradientWidget` | `"T_grad_mean"` | `ThermalGradient` | `method_top`, `method_bottom`, `correction_top`, `correction_bottom` |
| `ConductivityWidget` | `"tc_mean"` | `IntervalConductivity` | `source`, `location`, `method`, `saturation`, `pT_conditions`, `pT_function`, `strategy` |

## Module: `parent.py` — `GHFDBParentImportResource`

**Target model**: `ParentHeatFlow`

| Field Declaration | Spreadsheet Column | Widget | Notes |
|---|---|---|---|
| `local_id` | `ID_parent` | `CharWidget` | Stored but not in `import_id_fields`; used via `before_import_row` |
| `value` | `q` | `QuantityWidget("mW/m²")` | Parent heat flow density |
| `uncertainty` | `q_uncertainty` | `QuantityWidget("mW/m²")` | |
| `comment` | `p_comment` | `CharWidget` | |
| `corr_HP_flag` | `corr_HP_flag` | `YesNoWidget` | |
| `sample` | `name` (sentinel) | `ParentWidget` | Creates/updates `HeatFlowSite` + `Point` |

**Upsert strategy**: Template-aware. `import_id_fields` uses natural keys (`lat_NS` + `long_EW`) present in all templates. When `ID_parent` is present, it is stored in `local_id` for round-trip traceability.

**`before_import()` deduplication**: Preprocesses the dataset to keep only the first row per unique `ID_parent` (or per unique lat/lon when ID is absent).

## Module: `child.py` — `GHFDBChildImportResource`

**Target model**: `HeatFlow`

Direct field mappings (14 fields):

| Field | Spreadsheet Column | Widget |
|---|---|---|
| `local_id` | `ID` | `CharWidget` |
| `value` | `qc` | `QuantityWidget("mW/m²")` |
| `uncertainty` | `qc_uncertainty` | `QuantityWidget("mW/m²")` |
| `method` (M2M) | `q_method` | `MultiConceptWidget(HeatFlowMethod)` |
| `date_acquired` | `q_date` | `CharWidget` |
| `expedition` | `expedition` | `CharWidget` |
| `water_temperature` | `water_temperature` | `QuantityWidget("°C")` |
| `is_relevant` | `relevant_child` | `YesNoWidget` |
| `c_comment` | `c_comment` | `CharWidget` |
| `parent` | `ID_parent` | `ForeignKeyWidget(ParentHeatFlow, "local_id")` |
| `sample` (FK to interval) | `q_top` (sentinel) | `IntervalWidget` |
| `thermal_gradient` | `T_grad_mean` (sentinel) | `GradientWidget` |
| `thermal_conductivity` | `tc_mean` (sentinel) | `ConductivityWidget` |

**`after_save_instance()` creates**:

- 9 `HeatFlowCorrection.objects.update_or_create()` calls via `CORRECTION_COL_MAP`
- `ProbeMetadata.objects.update_or_create()` when any probe column is non-empty
- `widget.set_m2m_relations()` for each `RelatedModelWidget` field

**Upsert strategy**: Template-aware. `import_id_fields` uses `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference` (always-present natural key). `ID` is stored in `local_id` when present.

## Module: `export.py` — `GHFDBExportResource`

**Target model**: `GHFDB` (proxy, via `002-ghfdb-product-utilities`)
**`get_queryset()`**: Returns `GHFDB.objects.for_export()` (annotations + 14 prefetches)
**`export_order`**: `GHFDB_COLUMN_ORDER` (62 columns, canonical order)

All 62 fields are declared explicitly. Specialised `dehydrate_*` methods:

| Method group | Treatment |
|---|---|
| Pint quantity fields | Return `.magnitude` (plain numeric) or `""` if null |
| M2M fields | Return `"; ".join(c.label for c in obj.<prefetch>.all())` or `""` |
| Correction flag fields | Return annotated status string or `""` |
| Scalar string/numeric fields | Direct attribute access via annotation name |
