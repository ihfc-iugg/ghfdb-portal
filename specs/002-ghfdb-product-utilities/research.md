# Research: GHFDB Product Layer — Import/Export Architecture

**Feature**: 002-ghfdb-product-utilities
**Date**: 2026-04-13
**Status**: Complete

## R01: Separate vs. Combined Import Resources

### Decision: **Separate resources** (parent-level + child-level)

### Rationale

The GHFDB spreadsheet is flat: one row per child heat-flow measurement with parent data denormalised across rows. Multiple child rows share the same `ID_parent`. This creates a fundamental tension: the spreadsheet structure doesn't match the relational model hierarchy.

**Two-resource architecture:**

1. **`GHFDBParentImportResource`** — Imports parent-level data: `HeatFlowSite`, `ParentHeatFlow`, and the `Point` (location). Keyed on `ID_parent` as the upsert identifier. Deduplicates automatically — the spreadsheet may have 50 rows with the same `ID_parent` but only one parent record needs to be created/updated.

2. **`GHFDBChildImportResource`** — Imports child-level data: `HeatFlowInterval`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`, `ProbeMetadata`, and `HeatFlowCorrection`. Keyed on `ID` (mapped to `HeatFlow.local_id`) as the upsert identifier. References the site via `ID_parent` lookup.

### Advantages over a single combined resource

| Criterion | Combined (monolithic) | Separate (chosen) |
|---|---|---|
| **Testability** | One massive test suite; hard to isolate failures | Each resource has focused, independent tests |
| **Admin workflow** | One import action — simpler UI but no granularity | Two admin import actions; admin can update parent records without touching child measurements |
| **Error isolation** | A parent-level error blocks all child imports | Parent errors are caught and fixed before child import |
| **Performance** | Processes all columns every row even when only updating parent records | Parent import skips child columns entirely; child import is faster because parent records already exist |
| **Deduplication** | Must manually deduplicate `ID_parent` in `before_import` | Parent resource naturally deduplicates (one row per unique `ID_parent` extracted in `before_import`) |
| **Reusability** | Locked to the combined workflow | Parent resource reusable for bulk parent metadata corrections |
| **Complexity** | All related-model creation in `before_import_row` — massive method | Each resource creates only its own related models |

### Alternatives considered

- **Single combined resource with `before_import_row` creating all related models**: This is the approach in the legacy `resources.py`. It works but creates a 1,400+ line file with deeply nested logic in `before_import_row`, making it fragile, hard to test, and impossible to update sites independently. Rejected.
- **Three resources (site, interval, child)**: Over-splits the import. Intervals are tightly coupled to child measurements (one interval per child in practice). The added admin complexity isn't justified. Rejected.

### Implementation approach

The admin will provide both import actions on the `GHFDBAdmin` class via `get_import_resource_classes()` returning `[GHFDBParentImportResource, GHFDBChildImportResource]`. django-import-export ≥4.0 supports multiple resource classes — the admin user selects which resource to use from a dropdown during import.

**Workflow for a full GHFDB spreadsheet import:**

1. Staff user uploads the XLSX file and selects "GHFDB Parent" resource → creates/updates all parent records
2. Staff user uploads the **same** XLSX file and selects "GHFDB Child" resource → creates/updates all child records, linking to existing parent records
3. Both steps use the same file; no pre-processing needed

**Parent deduplication in `before_import`:**
The `GHFDBParentImportResource.before_import()` method will preprocess the dataset to extract unique rows by `ID_parent`, discarding duplicate rows. This means the resource operates on a reduced dataset where each row represents one unique parent record.

---

## R02: Custom Widget for Creating/Updating Related Models from Flat Row Data

### Decision: **`RelatedModelWidget`** — a custom widget that creates/updates related model instances from multiple spreadsheet columns

### Rationale

django-import-export's built-in `ForeignKeyWidget` looks up a related model by a **single field** (e.g., `Author.name`). The GHFDB spreadsheet encodes related model data across **multiple columns** in the same row. For example, a `ThermalGradient` instance requires `T_grad_mean`, `T_grad_uncertainty`, `T_grad_mean_cor`, `T_grad_uncertainty_cor`, `T_number`, plus M2M fields `T_method_top`, `T_method_bottom`, `T_corr_top`, `T_corr_bottom`.

There is no built-in widget that:

1. Reads multiple columns from the row
2. Creates/updates a related model instance using those columns
3. Returns the instance as a FK value for the parent resource
4. Reports field-level validation errors on the related model back to the import pipeline

### Design

```python
class RelatedModelWidget(Widget):
    """Widget that creates/updates a related model instance from row data.

    Given a mapping of spreadsheet columns → model fields, this widget:
    1. Extracts field values from the import row
    2. Validates them via model full_clean()
    3. Creates or updates the related instance
    4. Returns the instance for FK assignment
    5. Reports field-level errors prefixed with the related model name
    """

    def __init__(self, model, field_map, lookup_fields=None, m2m_fields=None,
                 sentinel_column=None):
        """
        Args:
            model: The Django model class to create/update.
            field_map: Dict mapping spreadsheet column names to model field names.
                       e.g., {"T_grad_mean": "value", "T_grad_uncertainty": "uncertainty"}
            lookup_fields: List of (spreadsheet_col, model_field) tuples used for
                          get_or_create lookup. If None, always creates new instances.
            m2m_fields: Dict mapping spreadsheet column names to (model_m2m_field, widget)
                       tuples. These are set after instance creation.
            sentinel_column: The spreadsheet column that determines whether the
                            related model should be created. If this column is
                            empty, clean() returns None.
        """
```

**Key design properties:**

1. **Row-aware `clean()`**: The `clean(value, row=None, **kwargs)` method receives the full row. It extracts all mapped columns, validates them, and creates/updates the related instance. The `value` parameter is the sentinel column value — if empty, the related model is skipped entirely.

2. **Conditional creation**: If the sentinel column value is empty/null, `clean()` returns `None` (no related model needed for this row). This handles optional relations like `ThermalGradient` (only present when `T_grad_mean` has a value) and `IntervalConductivity` (only when `tc_mean` has a value).

3. **M2M handling**: M2M fields (e.g., `T_method_top`, `tc_source`) are set after `save()`. The widget stores pending M2M assignments internally and exposes a `set_m2m_relations(instance)` method called by the resource in `after_save_instance()`.

4. **Validation via `full_clean()`**: The widget calls `model.full_clean()` on the instance before saving. Django `ValidationError` exceptions are caught and re-raised as `ValueError` with **prefixed field names** (e.g., `"ThermalGradient.value: Ensure this value is ≤ 999999.9"`). This flows through django-import-export's standard error pipeline.

5. **`render()` for export**: Returns the primary value of the related instance (e.g., `instance.value.magnitude` for a QuantityField) for export use.

### Alternatives considered

- **`ForeignKeyWidget` with `before_import_row` side-effects**: The legacy approach. `before_import_row` creates related models imperatively and stuffs PKs into the row dict. This works but scatters related-model logic across the resource instead of encapsulating it in the widget. Validation errors from related models are not surfaced through the standard error pipeline. Rejected.
- **Separate import resources for every related model**: Would require 6+ import steps for a single spreadsheet. Impractical for admin workflow. Rejected.
- **Custom `Field` subclass instead of `Widget`**: Less composable — widgets can be reused across fields; custom fields are more tightly coupled to specific resources. Rejected.

---

## R03: Error Reporting for Related Model Fields

### Decision: **Prefixed `ValueError` in widget `clean()` method**

### Rationale

django-import-export's error reporting works at two levels:

1. **Widget-level `ValueError`** → stored in `InvalidRow.error` as a `ValidationError` dict keyed by field name
2. **Instance-level `ValidationError`** from `model.full_clean()` → stored in `InvalidRow.error` when `clean_model_instances=True`

For related models created in widgets, we need errors to appear in the admin UI with enough context for the user to identify which column and which related model caused the failure.

### Approach

1. **In `RelatedModelWidget.clean()`**:
   - Catch `ValidationError` from related model `full_clean()`
   - Re-raise as `ValueError` with a message format: `"{related_model}.{field}: {error_message}"`
   - Example: `ValueError("ThermalGradient.value: Ensure this value is between -999999 and 999999")`

2. **In the admin UI**: django-import-export displays `ValueError` messages per-row. The prefixed format tells the user exactly which related model field failed.

3. **Concept vocabulary errors**:
   - `ConceptWidget.clean()` validates that the provided label exists in the vocabulary
   - On failure: `ValueError("Invalid value 'xyz' for vocabulary 'HeatFlowMethod'. Valid values: ...")`
   - For `MultiConceptWidget` (semicolon-separated): each value is validated individually; the error identifies the specific invalid value

4. **Aggregated error collection**: The resource's `import_row()` collects all field errors (including those from `RelatedModelWidget` instances) into the standard `RowResult`. No custom `RowResult` subclass is needed — the prefixed `ValueError` messages are sufficient.

### Example error output in admin UI

```
Row 42:
  thermal_gradient: ThermalGradient.value: This field is required when T_grad_mean is provided.
  thermal_conductivity: IntervalConductivity.method: Invalid value 'laser flash' for vocabulary 'ConductivityMethod'.
  q_method: Invalid value 'BSR;xyz' — 'xyz' is not a valid HeatFlowMethod. Valid values: BSR, BHT, ...
```

---

## R04: GHFDB Spreadsheet Format Handling

### Decision: **Custom `GHFDBImportFormat`** extending `XLSX` with header row 6 and data starting at row 8

### Rationale

The official GHFDB XLSX template has a non-standard layout:

- Rows 1–5: Title, description, metadata
- Row 6: Column headers (technical names like `q`, `lat_NS`, `tc_mean`)
- Row 7: Column descriptions (human-readable labels)
- Row 8+: Data rows

The sheet is named "data list".

### Implementation

```python
class GHFDBImportFormat(XLSX):
    """Custom XLSX format for GHFDB spreadsheet with header at row 6."""

    def create_dataset(self, in_stream):
        """Read GHFDB XLSX with custom header/data row positions."""
        from openpyxl import load_workbook
        wb = load_workbook(BytesIO(in_stream), read_only=True, data_only=True)
        ws = wb["data list"]

        headers = [cell.value for cell in ws[6]]  # Row 6 = headers
        dataset = tablib.Dataset(headers=headers)

        for row in ws.iter_rows(min_row=8, values_only=True):  # Skip rows 1-7
            dataset.append(row)

        wb.close()
        return dataset
```

Both the site and child import resources share this format class.

---

## R05: Upsert Strategy

### Decision: `import_id_fields` using `local_id` for both site and child resources

### Rationale

- **Parent resource**: The `GHFDBParentImportResource` model target is `ParentHeatFlow`. The spreadsheet's `ID_parent` column maps to `ParentHeatFlow.local_id`. After `before_import()` deduplication, each row has a unique `ID_parent`. `import_id_fields = ("local_id",)`.
- **Child resource**: The `GHFDBChildImportResource` model target is `HeatFlow`. The spreadsheet's `ID` column maps to `HeatFlow.local_id`. `import_id_fields = ("local_id",)`.
- Both use django-import-export's built-in upsert: if a record with the same `local_id` exists, it's updated; otherwise created.

### Parent resource model target choice

The parent resource targets `ParentHeatFlow` (not `HeatFlowSite`) because:

1. `ParentHeatFlow` has a FK to `HeatFlowSite.sample` — creating a `ParentHeatFlow` can also create its `HeatFlowSite` via the `RelatedModelWidget`
2. `ParentHeatFlow` has `local_id` field for upsert
3. The GHFDB spreadsheet identifies sites by `ID_parent`, which semantically maps to `ParentHeatFlow`
4. Parent-level location fields (name, lat, lon, elevation, etc.) are created/updated via the `RelatedModelWidget` attached to the `sample` FK field

---

## R06: Export Resource Architecture

### Decision: **Single `GHFDBExportResource`** using `dehydrate_*` methods and the `for_export()` queryset

### Rationale

Export is simpler than import because we're reading from a well-structured relational model and flattening to a spreadsheet. The `GHFDBQuerySet.for_export()` method already provides all necessary annotations and prefetches.

### Implementation approach

1. The `GHFDBExportResource` declares one `Field` per GHFDB spreadsheet column
2. Scalar fields use the annotated flat names from `as_ghfdb_flat()` (e.g., `site_name`, `p_q`, `tgrad_value`)
3. M2M fields use `dehydrate_<field>()` methods that:
   - Access the prefetched M2M relation
   - Render concept labels joined with `"; "` (semicolon + space, matching GHFDB convention)
4. Quantity fields use `dehydrate_<field>()` methods that strip Pint units and return plain numeric values
5. Correction flags use `dehydrate_corr_<TYPE>_flag()` that render the annotated status string
6. Column order is enforced via `export_order` matching the official GHFDB schema sequence from `ghfdb_colmeta.json`

### Why not separate export resources?

Unlike import, there's no benefit to splitting export. The queryset already provides all data in one optimised query path. A single resource with `export_order` is simpler and produces a single sheet.

---

## R07: ConceptField / ConceptManyToManyField Widget Design

### Decision: **`ConceptWidget`** and **`MultiConceptWidget`** for research-vocabs integration

### Rationale

The GHFDB spreadsheet uses human-readable concept labels (e.g., "Borehole", "BSR;BHT") that must be mapped to `research_vocabs.Concept` instances stored in the database. This mapping is vocabulary-specific and case-insensitive.

### Design

```python
class ConceptWidget(Widget):
    """Widget for single ConceptField values.

    Maps human-readable concept labels from the spreadsheet to
    research_vocabs.Concept instances, with case-insensitive matching
    and 'unspecified' filtering.
    """

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary
        self._cache = None  # Lazy-loaded label → concept mapping

    def clean(self, value, row=None, **kwargs):
        if not value or str(value).strip().lower() in ("", "unspecified"):
            return None
        label = str(value).strip()
        concept = self._lookup(label)
        if concept is None:
            valid = self._get_valid_labels()
            raise ValueError(
                f"Invalid value '{label}' for vocabulary "
                f"'{self.vocabulary.__class__.__name__}'. "
                f"Valid values: {', '.join(sorted(valid))}"
            )
        return concept

    def render(self, value, obj=None, **kwargs):
        if value is None:
            return ""
        return str(value)  # Concept.__str__ returns the label

    def _lookup(self, label):
        """Case-insensitive concept lookup with caching."""
        if self._cache is None:
            self._cache = {
                str(c).lower(): c
                for c in self.vocabulary.get_queryset()
            }
        return self._cache.get(label.lower())

    def _get_valid_labels(self):
        if self._cache is None:
            self._lookup("")  # Force cache population
        return [str(c) for c in self._cache.values()]


class MultiConceptWidget(Widget):
    """Widget for semicolon-separated ConceptManyToManyField values.

    Parses 'BSR;BHT;Probe sensing' into a list of Concept instances
    from the specified vocabulary.
    """

    def __init__(self, vocabulary, separator=";"):
        self.vocabulary = vocabulary
        self.separator = separator
        self._concept_widget = ConceptWidget(vocabulary)

    def clean(self, value, row=None, **kwargs):
        if not value:
            return []
        labels = [v.strip() for v in str(value).split(self.separator)
                  if v.strip() and v.strip().lower() != "unspecified"]
        concepts = []
        invalid = []
        for label in labels:
            try:
                concept = self._concept_widget.clean(label, row=row, **kwargs)
                if concept is not None:
                    concepts.append(concept)
            except ValueError:
                invalid.append(label)
        if invalid:
            valid = self._concept_widget._get_valid_labels()
            raise ValueError(
                f"Invalid value(s) {invalid} for vocabulary "
                f"'{self.vocabulary.__class__.__name__}'. "
                f"Valid values: {', '.join(sorted(valid))}"
            )
        return concepts

    def render(self, value, obj=None, **kwargs):
        if not value:
            return ""
        items = value.all() if hasattr(value, 'all') else value
        return "; ".join(str(c) for c in items if str(c))
```

The `_cache` is populated once per import run and reused for all rows — vocabulary labels don't change during an import. This is critical for performance with 10,000+ row imports.

---

## R08: QuantityField Handling

### Decision: **`QuantityWidget`** that strips Pint units on export and accepts plain numerics on import

### Rationale

The GHFDB spreadsheet uses plain numeric values (e.g., `65.3` for heat flow in mW/m²). The Django model stores these as Pint `Quantity` objects. The widget bridges the gap.

### Design

```python
class QuantityWidget(DecimalWidget):
    """Widget for Pint QuantityField / DecimalQuantityField values.

    Import: plain numeric → Quantity(numeric, unit)
    Export: Quantity → plain numeric (magnitude only)
    """

    def __init__(self, unit, **kwargs):
        super().__init__(**kwargs)
        self.unit = unit  # e.g., "mW/m²", "K/km", "W/(m·K)"

    def clean(self, value, row=None, **kwargs):
        numeric = super().clean(value, row=row, **kwargs)
        if numeric is None:
            return None
        return Quantity(numeric, self.unit)

    def render(self, value, obj=None, **kwargs):
        if value is None:
            return ""
        if hasattr(value, 'magnitude'):
            return value.magnitude
        return value
```

---

## R09: HeatFlowCorrection Import/Export

### Decision: **Handled in `after_save_instance()` on the child import resource** and **`dehydrate_corr_*` on export**

### Rationale

`HeatFlowCorrection` records are not a standard FK/M2M relationship — they're a normalised set of correction flags stored as separate rows keyed by `(heat_flow, correction_type)`. There are 9 correction types (IS, T, S, E, TOPO, PAL, SUR, CONV, HR).

### Import approach

In `GHFDBChildImportResource.after_save_instance()`:

1. Map correction column → correction type:

   ```python
   _CORRECTION_COL_MAP = {
       "corr_IS_flag": "IS",
       "corr_T_flag": "T",
       "corr_S_flag": "S",
       "corr_E_flag": "E",
       "corr_TOPO_flag": "TOPO",
       "corr_PAL_flag": "PAL",
       "corr_SUR_flag": "SUR",
       "corr_CONV_flag": "CONV",
       "corr_HR_flag": "HR",
   }
   ```

2. For each correction column with a non-empty value:
   - Map the display label to a `HeatFlowCorrection.StatusChoices` value (case-insensitive)
   - Call `HeatFlowCorrection.objects.update_or_create(heat_flow=instance, correction_type=<TYPE>, defaults={"status": status})`
3. Invalid status values raise `ValidationError` with the column name and invalid value

### Export approach

The `as_ghfdb_flat()` queryset already annotates `corr_{TYPE}_flag` via Subquery. The export resource declares these as readonly fields and uses `dehydrate_corr_{TYPE}_flag()` to render the annotated value as the display label.

---

## R10: CSV vs XLSX for Import

### Decision: **XLSX only** — CSV is not supported for import

### Rationale (from spec clarification)

The official GHFDB template is distributed as XLSX with a multi-row header structure (rows 1–5 metadata, row 6 headers, row 7 descriptions). CSV cannot represent this structure. All IHFC submissions use XLSX. Supporting CSV adds complexity (header detection, encoding issues) with no real-world use case.

Export produces XLSX only (matching the official template format).

---

## R11: Proxy Model + Flat Queryset Design

### Decision: Proxy model with custom `QuerySet`, `select_related` + `annotate` (F/Subquery)

### Rationale

| Approach | Pros | Cons | Verdict |
|---|---|---|---|
| `select_related` + `.values()` | Simple, one query | Loses model instances; can’t handle M2M or reverse FK | ❌ Rejected |
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

## R12: Many-to-Many Fields in Export

### Decision: Prefetch + Python-level joining for export; leave M2M as relations for admin/display

### Rationale

- `StringAgg` (PostgreSQL) would work at the DB level but breaks SQLite dev fallback
- ~15 M2M fields make annotation-based joining very verbose for minimal gain
- `prefetch_related` executes one query per M2M relation (not per row) — O(1) query count
- Existing `MultiConceptWidget.render()` already implements the `";".join()` pattern

### Query Impact

- `as_ghfdb_flat()`: 1–2 queries (main + content-type cache); M2M left as live relations
- `for_export()`: ~16 queries (1 main + ~15 prefetches), all constant regardless of row count

---

## R13: HeatFlowCorrection Row-to-Column Pivot

### Decision: 9 correlated `Subquery` annotations, one per correction type

### Rationale

| Approach | Verdict |
|---|---|
| `prefetch_related` + Python pivot | Can’t filter/sort by correction columns at DB level | ❌ |
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

## R14: Query Count Guarantees

### Decision: 2 queries for admin/display; ~16 queries for full export. All O(1) — no N+1

| Method | Queries | Details |
|---|---|---|
| `as_ghfdb_flat()` | 1–2 | Main SELECT with JOINs + 9 correlated subqueries (folded into main query) + content-type cache |
| `for_export()` | ~16 | Main query + ~15 prefetch queries for M2M relations |

Both satisfy SC-002: “constant number of database queries regardless of the number of records returned.”

Validated with `django_assert_max_num_queries` in tests.

---

## R15: Map Viewer

### Decision: Minimal changes — `GHFDBExploreView` and the explore template already satisfy all spec requirements

### What already exists

- Full-screen iframe embedding `https://ihfc-iugg.github.io/HeatFlowMapping/`
- URL at `explore/`
- Menu item registered via `flex_menu` in `heat_flow/menus.py`

### Only change needed

Graceful degradation when the iframe URL is unreachable: add an `onerror` handler on the `<iframe>` element to show a user-friendly fallback message rather than a blank panel.
