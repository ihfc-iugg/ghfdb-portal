# GHFDB Product Layer — Interface Contracts

**Feature**: 002-ghfdb-product-utilities
**Date**: 2026-04-10

This feature is an internal Django admin feature with no public-facing API endpoints. The interfaces are consumed by:

1. Django admin staff users (import/export via browser)
2. Internal Python code (proxy model queryset)

## Contract 1: GHFDB Proxy Model QuerySet API

### `GHFDB.objects.as_ghfdb_flat()`

**Consumer**: Admin list views, django-tables2, django-filter, internal queries
**Behaviour**: Returns a `QuerySet[GHFDB]` where each instance has annotated attributes for all GHFDB scalar columns plus correction flag subquery results.

```python
# Usage
qs = GHFDB.objects.as_ghfdb_flat()
qs = qs.filter(site_country="Germany").order_by("-p_q")

for entry in qs[:10]:
    print(entry.site_name, entry.lat_ns, entry.p_q, entry.corr_IS_flag)
```

**Guarantees**:

- No N+1 queries: O(1) query count regardless of result size
- All GHFDB scalar columns (non-M2M) available as attributes
- Standard queryset operations (filter, order_by, count, slicing) work normally
- Returns `GHFDB` model instances (not dicts)

### `GHFDB.objects.for_export()`

**Consumer**: `GHFDBExportResource`, export admin action
**Behaviour**: Extends `as_ghfdb_flat()` with `prefetch_related` for all M2M fields.

```python
# Usage (internal - called by export resource)
qs = GHFDB.objects.for_export()
for entry in qs:
    methods = ";".join(c.label for c in entry.method.all())  # no extra query
```

**Guarantees**:

- All guarantees of `as_ghfdb_flat()` plus:
- M2M fields accessible without additional queries (prefetched)
- Total query count: ~16 (constant)

## Contract 2: Admin Import Workflow

### Input Format

**Accepted**: GHFDB-template XLSX files only (`.xlsx` extension)
**Structure**: Headers at row 6, data starting at row 9 (as per `GHFDBImportFormat`)
**Sheet name**: `"data list"` (required by `GHFDBImportFormat.create_dataset()`)

### Import Behaviour

| Aspect | Contract |
|---|---|
| **Validation** | All rows validated before any persist. Errors collected, not raised individually. |
| **Atomicity** | Entire import is atomic — if any row fails, zero records are created/modified. |
| **Upsert** | Records matched by `local_id` (from spreadsheet `ID` column). Existing records updated; new records created. |
| **Error format** | Each error includes: row number, column name, invalid value, error message. |
| **Vocabulary mapping** | Semicolon-separated display labels → `Concept` objects. Case-insensitive. |
| **Staff only** | Accessible only via Django admin (requires `is_staff=True`). |

### Output on Success

Creates/updates records across:

- `HeatFlowSite` (get_or_create by location + name)
- `ParentHeatFlow` (get_or_create by site + value)
- `HeatFlowInterval` (get_or_create by site + top/bottom)
- `HeatFlow` (upsert by `local_id`)
- `ThermalGradient` (created per row)
- `IntervalConductivity` (created per row)

### Output on Failure

- HTTP 200 with error report page listing all row-level errors
- Zero database changes (transaction rolled back)

## Contract 3: Admin Export Workflow

### Trigger

Admin action on `GHFDB` change list. Staff user selects records (or all) and triggers export.

### Output Format

**Format**: XLSX
**Columns**: All ~65 GHFDB spreadsheet columns in the prescribed order per `ghfdb_colmeta.json`
**Column names**: Exact GHFDB spreadsheet header names (e.g., `q`, `q_uncertainty`, `lat_NS`, `T_grad_mean`)

### Data Formatting Rules

| Data Type | Format |
|---|---|
| Pint QuantityField | Plain numeric (SI unit magnitude, no unit symbol) |
| M2M ConceptField | Semicolon-separated display labels (e.g., `"Needle probe;Divided bar"`) |
| BooleanField (corr_HP_flag) | `"Yes"` / `"No"` |
| Correction flag (HeatFlowCorrection.status) | Status label string (e.g., `"present_corrected"`) |
| DateField | `YYYY-MM` format |
| Nullable fields | Empty cell (not `"None"` or `"null"`) |

## Contract 4: Map Viewer Page

### URL

`/explore/`

### Behaviour

- Renders full-screen iframe pointing to `https://ihfc-iugg.github.io/HeatFlowMapping/`
- No authentication required
- "Explore" menu item in main navigation marked as active
- Iframe fills available viewport height with no horizontal scrollbar
- Graceful degradation if iframe URL unreachable (informative fallback message)
