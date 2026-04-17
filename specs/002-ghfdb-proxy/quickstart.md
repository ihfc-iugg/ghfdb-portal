# Quickstart: GHFDB Flat Data Interface

**Feature**: 002-ghfdb-proxy

## What This Feature Adds

1. **GHFDBChild proxy model** � query child heat flow data in the flat GHFDB spreadsheet structure with no N+1 queries
2. **GHFDBParent proxy model** � query parent-level heat flow data with annotated child counts and prefetched children
3. **GHFDB admin changelists** � read-only "GHFDB Entries" and "GHFDB Parent Entries" views with exact GHFDB column order and vocabulary-scoped filters
4. **Explore map page** � full-screen IHFC web-map viewer with `onerror` iframe fallback

For import/export quickstart, see [003-ghfdb-import-export/quickstart.md](../003-ghfdb-import-export/quickstart.md).

## Prerequisites

```bash
poetry install
poetry run python manage.py migrate
```

## Using the Proxy Model

```python
from ghfdb.models import GHFDBChild, GHFDBParent

# Get all records as flat GHFDB rows (optimised, no N+1)
flat_qs = GHFDBChild.objects.as_ghfdb_flat()

# Filter by country
german_hf = flat_qs.filter(site_country="Germany")

# Access annotated fields directly
for entry in german_hf[:5]:
    print(f"Parent: {entry.p_q} mW/m�  �{entry.p_q_uncertainty}")
    print(f"  Child: {entry.value}  Site: {entry.site_name}")
    print(f"  Lat: {entry.lat_ns}, Lon: {entry.long_ew}")
    print(f"  T gradient: {entry.tgrad_value}")
    print(f"  Correction IS: {entry.corr_IS_flag}")

# For export (includes prefetched M2M data � consumed by 003-ghfdb-import-export)
export_qs = GHFDBChild.objects.for_export()

# Parent-level summary queries
parent_qs = GHFDBParent.objects.with_child_counts()
for parent in parent_qs[:5]:
    print(parent.local_id, parent.total_children, parent.relevant_children)
```

Annotation names are defined in `data-model.md` under "Annotation Name Mapping".

## Running Tests

```bash
# Proxy model + admin + views tests only
poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py tests/test_ghfdb/test_views.py -v
```
