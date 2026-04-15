# Quickstart: GHFDB Flat Data Interface

**Feature**: 002-ghfdb-product-utilities

## What This Feature Adds

1. **GHFDB proxy model** — query heat flow data in the flat GHFDB spreadsheet structure with no N+1 queries
2. **GHFDB admin changelist** — read-only "GHFDB Entries" view with exact GHFDB column order, vocabulary-scoped filters, and `local_id` stable import key
3. **Explore map page** — full-screen IHFC web-map viewer with `onerror` iframe fallback

For import/export quickstart, see [003-ghfdb-import-export/quickstart.md](../003-ghfdb-import-export/quickstart.md).

## Prerequisites

```bash
poetry install
poetry run python manage.py migrate
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
    print(f"Parent: {entry.p_q} mW/m²  ±{entry.p_q_uncertainty}")
    print(f"  Child: {entry.value}  Site: {entry.site_name}")
    print(f"  Lat: {entry.lat_ns}, Lon: {entry.long_ew}")
    print(f"  T gradient: {entry.tgrad_value}")
    print(f"  Correction IS: {entry.corr_IS_flag}")

# For export (includes prefetched M2M data — consumed by 003-ghfdb-import-export)
export_qs = GHFDB.objects.for_export()
```

Annotation names are defined in `data-model.md` under "Annotation Name Mapping".

## Running Tests

```bash
# Proxy model + admin + views tests only
poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py tests/test_ghfdb/test_views.py -v
```
