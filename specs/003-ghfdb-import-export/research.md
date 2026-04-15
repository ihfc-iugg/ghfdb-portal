# Research: GHFDB Import/Export Architecture

**Feature**: 003-ghfdb-import-export
**Date**: 2026-04-13 (split from `002-ghfdb-product-utilities` research.md — 2026-04-15)
**Status**: Complete

## R01: Separate vs. Combined Import Resources

### Decision: **Separate resources** (parent-level + child-level)

The GHFDB spreadsheet is flat: one row per child heat-flow measurement with parent data denormalised across rows. Multiple child rows share the same `ID_parent`. This creates a fundamental tension: the spreadsheet structure doesn't match the relational model hierarchy.

**Two-resource architecture:**

1. **`GHFDBParentImportResource`** — Imports parent-level data: `HeatFlowSite`, `ParentHeatFlow`, and the `Point` (location). Deduplicates automatically — the spreadsheet may have 50 rows with the same `ID_parent` but only one parent record needs to be created/updated.

2. **`GHFDBChildImportResource`** — Imports child-level data: `HeatFlowInterval`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`, `ProbeMetadata`, and `HeatFlowCorrection`.

### Advantages over a single combined resource

| Criterion | Combined (monolithic) | Separate (chosen) |
|---|---|---|
| **Testability** | One massive test suite; hard to isolate failures | Each resource has focused, independent tests |
| **Admin workflow** | One import action — simpler UI but no granularity | Two admin import actions; admin can update parent records without touching child measurements |
| **Error isolation** | A parent-level error blocks all child imports | Parent errors are caught and fixed before child import |
| **Performance** | Processes all columns every row even when only updating parent records | Parent import skips child columns entirely |
| **Deduplication** | Must manually deduplicate `ID_parent` in `before_import` | Parent resource naturally deduplicates in `before_import()` |

### Alternatives considered

- **Single combined resource**: This is the approach in the legacy `resources.py`. Creates a 1,400+ line file with deeply nested logic, fragile and hard to test. Rejected.
- **Three resources (site, interval, child)**: Over-splits. Intervals are tightly coupled to child measurements. Rejected.

---

## R02: Custom Widget for Creating/Updating Related Models

### Decision: **`RelatedModelWidget`** — a custom widget that creates/updates related model instances from multiple spreadsheet columns

`ForeignKeyWidget` looks up a related model by a single field. The GHFDB spreadsheet encodes related model data across multiple columns. `RelatedModelWidget` handles this by:

1. Receiving the full row in `clean(value, row=None, **kwargs)`
2. Extracting all mapped columns and validating via `model.full_clean()`
3. Using a `sentinel_column` to skip creation when optional sub-records are absent (e.g., skip `ThermalGradient` when `T_grad_mean` is empty)
4. Storing pending M2M assignments and exposing `set_m2m_relations(instance)` for post-save M2M setting
5. Re-raising `ValidationError` as `ValueError` prefixed with the related model name for django-import-export's error pipeline

---

## R03: Error Reporting

### Decision: **Prefixed `ValueError` in widget `clean()` method**

Error format: `"{RelatedModel}.{field}: {message}"` — e.g., `"ThermalGradient.value: Ensure this value is between -999999 and 999999"`. This surfaces field-level errors from all related models through django-import-export's standard per-row error pipeline without a custom `RowResult` subclass.

---

## R04: GHFDB Spreadsheet Format Handling

### Decision: **Custom `GHFDBImportFormat`** extending `XLSX` with header row 6 and data starting at row 9

The official GHFDB XLSX template (BUG-004 confirmed):

| Row | Content |
|-----|---------|
| 1 | ID |
| 2 | Obligation |
| 3 | Domain |
| 4 | Quality Relevance |
| 5 | Name (human-readable column name) |
| 6 | **Short Name** ← column headers used by import |
| 7 | Unit labels (skipped) |
| 8 | Allowed range of values (skipped) |
| 9+ | **Data rows** |

Implementation uses `ws.iter_rows(min_row=9)` — any value below 9 reads metadata rows as data.

---

## R05: Upsert Strategy

### Decision: **Template-aware upsert** — ID-based for official releases, natural-key-based for standard uploads

The standard individual-dataset upload template omits `ID` and `ID_parent` (these are database-level IDs assigned by IHFC maintainers, not provided by individual contributors).

- **When `ID_parent` / `ID` are present**: map to `ParentHeatFlow.local_id` / `HeatFlow.local_id` and use as upsert key
- **When absent (standard template)**: parent upsert uses `lat_NS` + `long_EW`; child upsert uses `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`

`import_id_fields` must reference **always-present** columns (natural keys) — never the optional `ID`/`ID_parent` headers — to avoid django-import-export header-validation failures on standard uploads.

---

## R06: Export Resource Architecture

### Decision: **Single `GHFDBExportResource`** using `dehydrate_*` methods and the `for_export()` queryset

Export is simpler than import. The `GHFDBQuerySet.for_export()` method (from `002-ghfdb-product-utilities`) already provides all annotations and prefetches. The export resource:

1. Declares one `Field` per GHFDB column with attribute pointing to annotation name
2. Uses `dehydrate_<field>()` for M2M fields (render labels joined with `"; "`)
3. Uses `dehydrate_<field>()` for Pint fields (strip unit, return plain magnitude)
4. Enforces canonical column order via `export_order = GHFDB_COLUMN_ORDER`
5. Uses `get_queryset()` returning `GHFDB.objects.for_export()`

---

## R07: Vocabulary Widget Design

### Decision: **`ConceptWidget`** and **`MultiConceptWidget`** with FR-016 normalisation

Spreadsheet values use human-readable concept labels (e.g., `"Borehole"`, `"BSR;BHT"`) in potentially bracketed, mixed-case form (e.g., `"[Onshore (continental)]"`). These must be normalised before vocabulary lookup:

```python
def normalize_vocab_token(raw: str) -> str:
    return raw.strip("[]").lower()
```

Normalisation is applied before cache lookup. Error messages preserve the **original** pre-normalisation token text so the user can locate the source of invalid values in the file. Labels in the database are stored in the vocabulary's canonical case.
