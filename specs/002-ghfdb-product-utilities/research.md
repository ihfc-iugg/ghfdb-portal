# Research: GHFDB Product Layer

**Feature**: 002-ghfdb-product-utilities
**Date**: 2026-04-10

## R1: Proxy Model + Flat Queryset Design

### Decision: Proxy model with custom QuerySet, `select_related` + `annotate` (F/Subquery)

### Rationale

| Approach | Pros | Cons | Verdict |
|---|---|---|---|
| `select_related` + `.values()` | Simple, one query | Loses model instances; can't handle M2M or reverse FK | ❌ Rejected |
| `select_related` + `annotate` | Keeps model instances; composable; works with admin/tables/filters | Verbose for many annotations | ✅ **Chosen** |
| Database VIEW | Great read performance | Requires DDL migration; breaks SQLite dev; harder to test | ❌ Rejected |
| Materialized VIEW | Best read perf | Staleness + all VIEW drawbacks; premature optimisation | ❌ Rejected |

The annotate approach keeps `GHFDB` as a real `Model` subclass, working seamlessly with Django admin, django-tables2, django-filter, django-import-export, and standard queryset chaining.

### Architecture

```
GHFDB (proxy of HeatFlow)
     ├── GHFDBManager
     │       └── get_queryset() → GHFDBQuerySet
     │
     └── GHFDBQuerySet
             ├── as_ghfdb_flat()     → annotated flat queryset (scalar + correction subqueries)
             ├── for_export()        → as_ghfdb_flat() + prefetch_related for M2M
             └── (inherits filter/order_by/count from QuerySet)
```

---

## R2: Many-to-Many Fields as Semicolon-Separated Strings

### Decision: Prefetch + Python-level joining for export; leave M2M as relations for admin/display

### Rationale

- `StringAgg` (PostgreSQL) would work at the DB level but breaks SQLite dev fallback
- ~15 M2M fields make annotation-based joining very verbose for minimal gain
- `prefetch_related` executes one query per M2M relation (not per row) — O(1) query count
- Existing `MultiConceptWidget.render()` already implements the `";".join()` pattern

### Query Impact

- `as_ghfdb_flat()`: 1–2 queries (main + content-type cache), M2M left as relations
- `for_export()`: ~16 queries (1 main + ~15 prefetches), all constant regardless of row count

---

## R3: HeatFlowCorrection Row-to-Column Pivot

### Decision: 9 correlated `Subquery` annotations, one per correction type

### Rationale

| Approach | Verdict |
|---|---|
| `prefetch_related` + Python pivot | Can't filter/sort by correction columns at DB level | ❌ |
| Conditional aggregation (`Case`/`When` + `Max`) | Causes `GROUP BY` on entire row; worse performance | ❌ |
| 9 `Subquery` annotations | Clean, indexed, composable, filterable | ✅ **Chosen** |
| JSON pivot via `JSONObject` | Single subquery but blocks individual column filtering | ❌ |

With `unique_together = [("heat_flow", "correction_type")]`, each subquery is satisfied by an index-only scan.

### Implementation

```python
def _correction_subqueries() -> dict[str, Subquery]:
    annotations = {}
    for choice_value, _label in HeatFlowCorrection.CorrectionTypeChoices.choices:
        col_name = f"corr_{choice_value}_flag"
        annotations[col_name] = Subquery(
            HeatFlowCorrection.objects
            .filter(heat_flow=OuterRef("pk"), correction_type=choice_value)
            .values("status")[:1],
            output_field=CharField(),
        )
    return annotations
```

---

## R4: Pint QuantityField Handling in Export

### Decision: No special treatment for `F()` annotations; strip to `.magnitude` for export dehydrate methods

### Rationale

- `django-pint-field` stores quantities as plain `float`/`decimal` in the DB
- `F()` annotations return the raw numeric (no Pint object) — naturally export-friendly
- For direct attribute access via `select_related`, values are Pint `Quantity` objects — use `getattr(val, "magnitude", val)` to strip

### Utility Widget

```python
class QuantityWidget(CharWidget):
    """Strips Pint Quantity to plain numeric magnitude for export."""
    def render(self, value, obj=None):
        if value is None:
            return ""
        return str(getattr(value, "magnitude", value))
```

---

## R5: Query Count Guarantees

### Decision: 2 queries for admin/display; ~16 queries for full export. All O(1) — no N+1

| Method | Queries | Details |
|---|---|---|
| `as_ghfdb_flat()` | 1–2 | Main SELECT with JOINs + 9 correlated subqueries (folded into main query) + content-type cache |
| `for_export()` | ~16 | Main query + ~15 prefetch queries for M2M relations |

Both satisfy SC-002: "constant number of database queries regardless of the number of records returned."

Validated with `django_assert_max_num_queries` in tests.

---

## R6: Import/Export Admin Integration

### Decision: `ImportExportMixin` on `GHFDBAdmin`; separate `GHFDBImportResource` and `GHFDBExportResource`

### Rationale

- Import and export are fundamentally asymmetric (multi-model creation vs. flat serialisation)
- django-import-export docs recommend separate resource classes for asymmetric operations
- Admin supports this natively via `get_import_resource_classes()` / `get_export_resource_classes()`
- A shared base class holds common column name constants and vocabulary widget definitions

### Admin Configuration

```python
@admin.register(GHFDB)
class GHFDBAdmin(ImportExportMixin, admin.ModelAdmin):
    def get_import_resource_classes(self, request, *args, **kw):
        return [GHFDBImportResource]
    def get_export_resource_classes(self, request, *args, **kw):
        return [GHFDBExportResource]
    def get_import_formats(self):
        return [GHFDBImportFormat]       # GHFDB-template XLSX only
    def get_export_formats(self):
        return [XLSX]                     # Standard XLSX
```

---

## R7: Export Resource Design

### Decision: New `GHFDBExportResource` with explicit fields, `dehydrate_*` methods, and `export_order` in Meta

### Key patterns

- `export_order` tuple in `Meta` controls column order (must match GHFDB spreadsheet schema)
- Each field declared explicitly with `column_name` matching GHFDB spreadsheet headers
- `dehydrate_*` methods handle: Pint magnitude stripping, M2M semicolon joining, FK traversal for location coordinates
- `get_queryset()` returns `GHFDB.objects.for_export()` for optimised prefetching

---

## R8: Atomic Import with Full Validation

### Decision: `use_transactions=True` + `rollback_on_validation_errors=True` + `raise_errors=False`

### Rationale

| Config | Value | Effect |
|---|---|---|
| `use_transactions` | `True` | Entire import wrapped in a DB transaction |
| `rollback_on_validation_errors` | `True` | Rolls back if ANY row fails validation |
| `raise_errors` | `False` | Collects ALL errors (doesn't stop at first) |
| `clean_model_instances` | `True` | Runs `full_clean()` per row for model-level validation |

The existing `before_import_row()` creates related objects inside the same transaction, so rollback catches everything. All row-level errors are collected and returned to the admin user.

---

## R9: Upsert Strategy by GHFDB ID

### Decision: Add `local_id` field to `HeatFlow` model; use `import_id_fields = ("local_id",)` in import resource

### Rationale

- `HeatFlow` currently inherits from `Measurement` which has no `local_id` field (only `Sample` does)
- The GHFDB `ID` column identifies the **child measurement**, not the sample — it belongs on `HeatFlow`
- Adding `local_id` enables: `import_id_fields = ("local_id",)` → automatic upsert by django-import-export
- Parallels the existing `Sample.local_id` pattern in FairDM

### Parent-level upsert

`ID_parent` maps to `ParentHeatFlow`/`HeatFlowSite`. Parent-level upsert handled manually in `before_import_row()` via `get_or_create(local_id=..., dataset=...)` in the existing `get_heat_flow_site()` and `get_parent_heat_flow()` methods.

### Alternatives rejected

- Custom `get_instance()` override: Works but more fragile than `import_id_fields`; requires maintaining custom lookup logic
- Composite key with dataset: Over-complicates for current use case; `local_id` uniqueness within a dataset is enforced by the GHFDB schema

---

## R10: GHFDBImportFormat (Custom XLSX Reader)

### Decision: Keep existing `GHFDBImportFormat`; register via `get_import_formats()` on admin class

The existing `GHFDBImportFormat` correctly handles the GHFDB XLSX template (headers at row 6, data from row 8). It is registered as the sole import format on the admin class, not globally.

---

## R11: Existing `resources.py` Refactoring Strategy

### Decision: Rename `GHFDBResource` → `GHFDBImportResource`; extract shared constants to `GHFDBBaseResource`

### What to keep

- All of `before_import_row()` logic (vocabulary cleaning, related object creation)
- `ForeignObjectWidget` and its field_map patterns
- `GHFDBImportFormat` (XLSX reader with custom header/skip rows)
- `ConceptWidget`, `MultiConceptWidget`, `YesNoWidget` — shared between import and export

### What to refactor

- Split `GHFDBResource` into `GHFDBImportResource` (inherits current logic) and `GHFDBExportResource` (new)
- Extract column name constants (GHFDB_COLUMNS, CHOICE_FIELDS, MULTI_CHOICE_FIELDS) to module-level or a base class
- Remove the `dataset` constructor requirement from the base class (pass via admin kwargs)
- Add `import_id_fields = ("local_id",)` for upsert support

---

## R12: Map Viewer (Existing — No Research Needed)

The `GHFDBExploreView` and explore template already exist and meet all spec requirements:

- Full-screen iframe embedding `https://ihfc-iugg.github.io/HeatFlowMapping/`
- URL at `explore/`
- Menu item registered via `flex_menu` in `heat_flow/menus.py`

Only minor refinement needed: graceful degradation when iframe URL is unreachable (add `onerror` handling).
