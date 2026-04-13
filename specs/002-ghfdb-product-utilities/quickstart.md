# Quickstart: GHFDB Import / Export

**Feature**: 002-ghfdb-product-utilities

## What This Feature Adds

1. **GHFDB proxy model** — query heat flow data in the flat GHFDB spreadsheet structure with no N+1 queries
2. **GHFDB XLSX parent import** — ingest parent-level site records from official GHFDB spreadsheets (admin-only)
3. **GHFDB XLSX child import** — ingest child measurements and all related sub-records (admin-only)
4. **GHFDB XLSX export** — produce GHFDB-compliant spreadsheets from the normalised database (admin-only)
5. **Explore map page** — full-screen IHFC web-map viewer (exists, minor iframe fallback refinement)

## Prerequisites

```bash
poetry install            # Install all dependencies
poetry run python manage.py migrate   # Apply migrations
```

## Module Layout

After implementation, the import/export modules live under `project/ghfdb/resources/`:

```
project/ghfdb/resources/
├── __init__.py          # Public API: GHFDBParentImportResource, GHFDBChildImportResource, GHFDBExportResource
├── _base.py             # GHFDBImportFormat, BaseGHFDBResource, shared constants
├── _widgets.py          # ConceptWidget, MultiConceptWidget, QuantityWidget, YesNoWidget, RelatedModelWidget subclasses
├── parent.py            # GHFDBParentImportResource
├── child.py             # GHFDBChildImportResource
└── export.py            # GHFDBExportResource
```

## Using the Proxy Model

```python
from ghfdb.models import GHFDB

# Get all records as flat GHFDB rows (optimised, no N+1)
flat_qs = GHFDB.objects.as_ghfdb_flat()

# Filter by country
german_hf = flat_qs.filter(site_country="Germany")

# Access annotated fields directly
for entry in german_hf[:5]:
    print(f"Parent: {entry.p_q} mW/m\u00b2  \u00b1{entry.p_q_uncertainty}")
    print(f"  Child: {entry.value}  Site: {entry.site_name}")
    print(f"  Lat: {entry.lat_ns}, Lon: {entry.long_ew}")
    print(f"  T gradient: {entry.tgrad_value}")
    print(f"  Correction IS: {entry.corr_IS_flag}")

# For export (includes prefetched M2M data)
export_qs = GHFDB.objects.for_export()
```

Annotation names used above are defined in `data-model.md` under "Annotation Name Mapping".

## Admin Integration

The `GHFDBAdmin` in `project/ghfdb/admin.py` exposes:

- **Import**: Two import actions — "Import Parent Records" and "Import Child Measurements" (via `ImportExportMixin` with multiple resources)
- **Export**: One export action — "Export GHFDB Excel" producing the canonical GHFDB XLSX format

## Import Workflow

### 1. Import Parent Records

1. Navigate to **Admin → GHFDB → GHFDB entries**
2. Click **Import** and select the **"Parent Import"** resource
3. Upload the GHFDB XLSX file
4. The parent import processes the `"data list"` sheet, deduplicating rows by `ID_parent`
5. Preview shows one row per unique parent record with a diff of changed fields
6. Confirm to create/update parent records, or cancel to discard

### 2. Import Child Measurements

1. After sites are imported, click **Import** again and select the **"Child Import"** resource
2. Upload the **same** GHFDB XLSX file
3. The child import processes every row, linking each child measurement to its parent via `ID_parent` → `ParentHeatFlow.local_id`
4. For each row, the import creates/updates:
   - `HeatFlowInterval` (depth interval)
   - `HeatFlow` (the measurement itself)
   - `ThermalGradient` (if `T_grad_mean` is non-empty)
   - `IntervalConductivity` (if `tc_mean` is non-empty)
   - `ProbeMetadata` (if any probe column is non-empty)
   - `HeatFlowCorrection` records (for each `corr_*_flag` column)
5. Preview shows all rows with a diff of changed fields
6. Confirm to apply, or cancel to discard

### Order Matters

**Always import parent records first.** The child import requires parent records to already exist (it looks up `ParentHeatFlow` by `local_id`). If a child row references a non-existent `ID_parent`, it will produce an error.

## Export Workflow

1. Navigate to **Admin → GHFDB → GHFDB entries**
2. Optionally filter the queryset (search, list filters)
3. Select entries (or select all)
4. Choose **Export** from the action dropdown
5. The export produces a single XLSX file with one row per child measurement, site data denormalised

## Running Tests

```bash
# Run all import/export tests
poetry run pytest tests/test_ghfdb/test_resources/ -v

# Run specific test files
poetry run pytest tests/test_ghfdb/test_resources/test_widgets.py -v
poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py -v
poetry run pytest tests/test_ghfdb/test_resources/test_child_import.py -v
poetry run pytest tests/test_ghfdb/test_resources/test_export.py -v
```

### Test Data

Test fixtures use a minimal GHFDB XLSX file with:

- 3 unique parent records (3 distinct `ID_parent` values)
- 5 child measurements (2 sites with 2 children, 1 site with 1 child)
- Coverage of all widget types: concepts, quantities, yes/no, corrections, probe metadata

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Import split | Parent resource + Child resource | Independently testable; cleaner error boundaries |
| Related model creation | `RelatedModelWidget` subclasses | Leverages django-import-export's widget pipeline; errors flow naturally |
| Concept fields | `ConceptWidget` / `MultiConceptWidget` | Clean mapping from label → vocabularies via research-vocabs |
| Quantity fields | `QuantityWidget` | Strips/adds units transparently; stores magnitudes |
| XLSX format | `GHFDBImportFormat` | Handles row-6 headers, skips metadata rows 1–5 |
| Corrections | `after_save_instance()` | Structural limitation: corrections are a separate model, not FK/M2M on HeatFlow |
