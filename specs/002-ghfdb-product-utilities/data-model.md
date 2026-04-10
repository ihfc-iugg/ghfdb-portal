# Data Model: GHFDB Product Layer

**Feature**: 002-ghfdb-product-utilities
**Date**: 2026-04-10

## Entity Overview

This feature introduces **no new database tables**. The proxy model adds only Python-level abstractions over the existing normalised schema. The one model field addition is `HeatFlow.local_id` for upsert support.

```
┌─────────────────────────────────────────────────────────────┐
│                        GHFDB Flat Row                       │
│  (one row per child HeatFlow measurement, ~65 columns)      │
└──────────────┬──────────────────────────────────────────────┘
               │ mapped to/from
               ▼
┌──────────────────────┐      ┌──────────────────────┐
│    HeatFlowSite      │◄─FK─│   ParentHeatFlow     │
│  (GenericHole +      │      │   (Measurement)      │
│   GeoDepthInterval + │      │  q, uncertainty,     │
│   GenericEarthSample)│      │  corr_HP_flag,       │
│  environment,        │      │  comment, is_ghfdb   │
│  explo_method/purpose│      └──────────┬───────────┘
│  country/region/etc. │                 │ children (reverse FK)
└──────────┬───────────┘                 │
           │ intervals (reverse FK)      │
           ▼                             ▼
┌──────────────────────┐      ┌──────────────────────┐
│  HeatFlowInterval    │◄─FK─│     HeatFlow         │
│  (Interval +         │      │   (Measurement)      │
│   GeoDepthInterval)  │      │  value, uncertainty, │
│  top, bottom,        │      │  U_score, M_score,   │
│  lithology, age      │      │  parent FK,          │
└──────────────────────┘      │  thermal_gradient FK,│
           │                  │  thermal_cond FK,    │
           ▼                  │  local_id (NEW),     │
┌──────────────────────┐      │  method M2M,         │
│   ProbeMetadata      │      │  expedition, etc.    │
│  penetration, type,  │      └──────┬──────┬────────┘
│  length, tilt        │             │      │
└──────────────────────┘             │      │
                                     │      │ corrections (reverse FK)
           ┌─────────────────────────┘      ▼
           ▼                      ┌──────────────────────┐
┌──────────────────────┐          │ HeatFlowCorrection   │
│  ThermalGradient     │          │  correction_type,    │
│  value, uncertainty, │          │  status              │
│  corrected_value,    │          │  (9 types per child) │
│  method_top/bottom,  │          └──────────────────────┘
│  shutin_top/bottom,  │
│  correction_top/bot, │
│  number              │
└──────────────────────┘
           ▲
           │
┌──────────────────────┐
│IntervalConductivity  │
│  value, uncertainty, │
│  source, location,   │
│  method, saturation, │
│  pT_conditions,      │
│  pT_function,        │
│  number, strategy    │
└──────────────────────┘
```

## New Entities

### GHFDB (Proxy Model)

**Type**: Django proxy model over `HeatFlow`
**Database impact**: None (no new table, no migrations for the proxy itself)
**Purpose**: Read-oriented flat view of the normalised heat flow data
**`verbose_name`**: `"GHFDB Entry"`
**`verbose_name_plural`**: `"GHFDB Entries"`

| Attribute | Type | Source | Notes |
|---|---|---|---|
| All `HeatFlow` fields | (inherited) | `HeatFlow` model | Direct access |
| `objects` | `GHFDBManager` | Custom manager | Provides `as_ghfdb_flat()` and `for_export()` |

### GHFDBQuerySet

| Method | Returns | DB Queries | Purpose |
|---|---|---|---|
| `as_ghfdb_flat()` | QuerySet with annotated flat columns | 1–2 (constant) | Admin list, filtering, API |
| `for_export()` | QuerySet with flat columns + prefetched M2M | ~16 (constant) | XLSX export |

### GHFDBManager

| Method | Delegates to |
|---|---|
| `as_ghfdb_flat()` | `GHFDBQuerySet.as_ghfdb_flat()` |
| `for_export()` | `GHFDBQuerySet.for_export()` |

## Modified Entities

### HeatFlow — New Field: `local_id`

| Field | Type | Constraints | Purpose |
|---|---|---|---|
| `local_id` | `CharField(max_length=255)` | `null=True`, `blank=True`, `db_index=True` | Stores the GHFDB spreadsheet `ID` column for upsert identification during import |

**Migration required**: Yes — adds a nullable varchar column to `heat_flow_heatflow` table.

**Rationale**: The GHFDB `ID` column identifies the child measurement (not the sample). Adding this field to `HeatFlow` enables `import_id_fields = ("local_id",)` in django-import-export for automatic upsert detection.

## Resource Classes

### GHFDBImportResource (refactored from existing `GHFDBResource`)

| Config | Value |
|---|---|
| `Meta.model` | `HeatFlow` |
| `Meta.import_id_fields` | `("local_id",)` |
| `Meta.use_transactions` | `True` |
| `Meta.clean_model_instances` | `True` |

**Behaviour**:

- Reads flat GHFDB XLSX rows
- Creates/updates across 6+ models in `before_import_row()`
- Validates all rows; rolls back entirely on any failure
- Upserts by `local_id` (mapped from spreadsheet `ID` column)

### GHFDBExportResource (new)

| Config | Value |
|---|---|
| `Meta.model` | `GHFDB` (proxy) |
| `Meta.export_order` | Full GHFDB column order (~65 fields) |
| `Meta.fields` | All GHFDB columns declared explicitly |

**Behaviour**:

- Uses `GHFDB.objects.for_export()` queryset
- Dehydrate methods handle: Pint magnitude stripping, M2M semicolon joining, FK traversal
- Produces XLSX matching the official GHFDB spreadsheet schema

## GHFDB Column Mapping (Flat → Relational)

The complete mapping is documented in `docs/ghfdb_fields.md`. The proxy model annotations mirror these paths:

### Select-Related Paths (scalar fields, single main query)

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

### Subquery Annotations (correction flags, folded into main query)

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

### Prefetch-Related Paths (M2M fields, one query each for export)

| Prefetch Path | GHFDB Column | Export Format |
|---|---|---|
| `method` | `q_method` | Semicolon-separated labels |
| `sample__sample__explo_purpose` | `explo_purpose` | Semicolon-separated labels |
| `thermal_gradient__method_top` | `T_method_top` | Semicolon-separated labels |
| `thermal_gradient__method_bottom` | `T_method_bottom` | Semicolon-separated labels |
| `thermal_gradient__correction_top` | `T_corr_top` | Semicolon-separated labels |
| `thermal_gradient__correction_bottom` | `T_corr_bottom` | Semicolon-separated labels |
| `thermal_conductivity__source` | `tc_source` | Semicolon-separated labels |
| `thermal_conductivity__location` | `tc_location` | Semicolon-separated labels |
| `thermal_conductivity__method` | `tc_method` | Semicolon-separated labels |
| `thermal_conductivity__saturation` | `tc_saturation` | Semicolon-separated labels |
| `thermal_conductivity__pT_conditions` | `tc_pT_conditions` | Semicolon-separated labels |
| `thermal_conductivity__pT_function` | `tc_pT_function` | Semicolon-separated labels |
| `thermal_conductivity__strategy` | `tc_strategy` | Semicolon-separated labels |
| `sample__probe_metadata__probe_type` | `probe_type` | Semicolon-separated labels |

## Validation Rules

### Import Validation

| Rule | Scope | Enforcement |
|---|---|---|
| Mandatory GHFDB fields (obligation=M) present | Per row | `clean_model_instances=True` + model validators |
| Controlled vocabulary values are valid | Per field | `ConceptWidget.clean()` / `MultiConceptWidget.clean()` raises `ValidationError` |
| Numeric ranges within GHFDB min/max | Per field | Model field validators (MinVal/MaxVal) |
| Coordinates valid (-90≤lat≤90, -180≤lon≤180) | Per row | `normalize_coordinate()` + model validation |
| All rows validated before any persist | Whole file | `rollback_on_validation_errors=True` |
| Errors include row number, column, value | Per error | django-import-export error collection |

### Export Validation

| Rule | Scope | Enforcement |
|---|---|---|
| All ~65 GHFDB columns present in output | File | `export_order` tuple completeness test |
| Column order matches GHFDB spec | File | Regression test comparing headers |
| Numeric values in correct SI units | Per cell | `dehydrate_*` methods strip Pint magnitude |
| M2M fields as semicolon-separated strings | Per cell | `dehydrate_*` methods join with ";" |

## State Transitions

### Import Flow

```
XLSX File Upload → GHFDBImportFormat.create_dataset()
  → Admin preview (dry_run=True, collects errors)
  → User confirms
  → import_data(dry_run=False, use_transactions=True)
    → for each row:
        → clean_choices() (vocabulary normalisation)
        → get_location() → Point
        → get_heat_flow_site() → HeatFlowSite (get_or_create)
        → get_parent_heat_flow() → ParentHeatFlow (get_or_create)
        → get_heat_flow_interval() → HeatFlowInterval (get_or_create)
        → HeatFlow created/updated (by local_id)
        → ThermalGradient created (ForeignObjectWidget)
        → IntervalConductivity created (ForeignObjectWidget)
    → if ANY error: ROLLBACK entire transaction
    → if success: COMMIT
```

### Export Flow

```
Admin "Export" action → GHFDBExportResource.export()
  → get_queryset() → GHFDB.objects.for_export()
  → for each row:
    → dehydrate_* methods produce flat values
    → QuantityWidget strips Pint magnitudes
    → MultiConceptWidget joins M2M with ";"
  → tablib.Dataset assembled
  → XLSX rendered and streamed to browser
```
