# Quickstart: GHFDB Product Layer

**Feature**: 002-ghfdb-product-utilities
**Date**: 2026-04-10

## What This Feature Adds

1. **GHFDB proxy model** — query heat flow data in the flat GHFDB spreadsheet structure
2. **GHFDB XLSX import** — ingest official GHFDB spreadsheets into the normalised data model (admin-only)
3. **GHFDB XLSX export** — produce GHFDB-compliant spreadsheets from the database (admin-only)
4. **Explore map page** — full-screen IHFC web-map viewer (already exists, minor refinements)

## Using the Proxy Model

```python
from ghfdb.models import GHFDB

# Get all records as flat GHFDB rows (optimised, no N+1)
flat_qs = GHFDB.objects.as_ghfdb_flat()

# Filter by country
german_hf = flat_qs.filter(site_country="Germany")

# Access annotated fields directly
for entry in german_hf[:5]:
    print(f"Site: {entry.site_name}")
    print(f"  Lat: {entry.lat_ns}, Lon: {entry.long_ew}")
    print(f"  Parent HF: {entry.p_q} mW/m²")
    print(f"  Child HF: {entry.value}")
    print(f"  T gradient: {entry.tgrad_value}")
    print(f"  Correction IS: {entry.corr_IS_flag}")

# For export (includes prefetched M2M data)
export_qs = GHFDB.objects.for_export()
```

## Importing Data via Django Admin

1. Log in as a staff user → navigate to **GHFDB Entries** in the admin
2. Click **Import** button
3. Select the target Dataset from the dropdown
4. Upload the GHFDB XLSX file (must follow the IHFC template: headers at row 6, data from row 9, sheet named "data list")
5. Review the preview — all rows are validated; any errors are listed with row number, column, and value
6. If no errors: click **Confirm Import** to persist all records
7. If errors: fix the spreadsheet and re-upload (no partial data is saved)

### Upsert Behaviour

If a record with the same `ID` (mapped to `local_id`) already exists, it is updated. Otherwise, a new record is created. Parent-level records (`HeatFlowSite`, `ParentHeatFlow`) are matched by their existing `local_id` fields.

## Exporting Data via Django Admin

1. Log in as a staff user → navigate to **GHFDB Entries** in the admin
2. Select records (or use "Select all") → choose **Export** from the action dropdown
3. Select XLSX format → click **Submit**
4. Download the generated XLSX file

The output file:

- Contains all ~65 GHFDB columns in the correct order
- Uses semicolons to separate multi-value fields
- Strips unit symbols from quantity fields (plain SI numerics)
- Writes dates in `YYYY-MM` format

## Map Viewer

Navigate to `/explore/` or click **Explore** in the main navigation. The IHFC web-map viewer loads in a full-screen iframe.

## Key Files

| File | Purpose |
|---|---|
| `project/ghfdb/models.py` | `GHFDB` proxy model, `GHFDBRelease` |
| `project/ghfdb/managers.py` | `GHFDBQuerySet`, `GHFDBManager` |
| `project/ghfdb/resources.py` | `GHFDBImportResource`, `GHFDBExportResource`, widgets |
| `project/ghfdb/admin.py` | Admin configuration with import/export actions |
| `project/ghfdb/views.py` | `GHFDBExploreView` |
| `project/heat_flow/models/child.py` | `HeatFlow.local_id` field (new) |
| `docs/ghfdb_fields.md` | Field mapping documentation |

## Running Tests

```bash
# All GHFDB product layer tests
poetry run pytest tests/test_ghfdb/ -v

# Only proxy model tests
poetry run pytest tests/test_ghfdb/test_models.py -v

# Only import round-trip tests
poetry run pytest tests/test_ghfdb/test_import.py -v

# Only export tests
poetry run pytest tests/test_ghfdb/test_export.py -v

# Query count guard tests
poetry run pytest tests/test_ghfdb/test_managers.py -v
```
