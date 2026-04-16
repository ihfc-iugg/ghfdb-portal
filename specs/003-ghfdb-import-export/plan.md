# Implementation Plan: GHFDB Import/Export Pipeline

**Branch**: `003-ghfdb-import-export` | **Date**: 2026-04-15 | **Spec**: [spec.md](spec.md)
**Split from**: `002-ghfdb-product-utilities` plan.md (import/export sections)
**Input**: Feature specification from `/specs/003-ghfdb-import-export/spec.md`
**Propagated**: 2026-04-15 — Added controlled-vocabulary import normalization (FR-016): strip square brackets and lowercase before vocabulary matching.
**Propagated**: 2026-04-14 — Updated from spec.md refinement
**Bugfix**: 2026-04-14 — [BUG-002] Added framework-hook compatibility requirement for admin import integration.
**Bugfix**: 2026-04-14 — [BUG-003] Added template-aware upsert constraints for standard uploads without `ID` / `ID_parent`.
**Bugfix**: 2026-04-15 — [BUG-003] Added header-validation-safe import constraint so standard uploads without `ID` / `ID_parent` do not fail `import_id_fields` checks.
**Bugfix**: 2026-04-15 — [BUG-004] Corrected GHFDB template row layout: unit labels at row 7 and "Allowed range of values" at row 8 are both skipped; `GHFDBImportFormat.create_dataset()` must use `min_row=9`.
**Bugfix**: 2026-04-15 — [BUG-005] Clarified that `AUTO_PARENT:` / `AUTO_CHILD:` synthetic upsert keys must be removed entirely; parent deduplication and lookup must use lat/lon location directly, and `ID_parent` on the confirm page must show `local_id` (or empty), never a synthetic key.
**Bugfix**: 2026-04-15 — [BUG-006] Added `get_user_visible_fields()` override constraint: both import resources must override this method (or an equivalent hook) to return fields sorted by their `column_name` position in `PARENT_COLUMNS` (parent resource) or `GHFDB_COLUMN_ORDER` (child resource), so the confirm-page diff presents columns in spreadsheet template order.
**Bugfix**: 2026-04-16 — [BUG-007] Added widget type-guard constraint: any widget `clean()` code path that calls `.strip()` — including via `CharWidget.super().clean()` — MUST guard with `try/except AttributeError` and re-raise a `ValueError` that names the column and the actual value received. This prevents the XLSX loader's numeric cell interpretation from surfacing as an unintelligible `AttributeError` to the end user.

**Dependency**: This plan depends on `002-ghfdb-product-utilities` being complete. The `GHFDB` proxy model, `GHFDBManager.for_export()` queryset, and `local_id` fields on `HeatFlow`, `HeatFlowSite`, and `ParentHeatFlow` must exist before any task in this plan is started.

## Summary

This plan implements the GHFDB round-trip import/export pipeline as a `resources/` package within `project/ghfdb/`. It uses a **two-resource import architecture**: a parent resource that creates/updates `HeatFlowSite` + `ParentHeatFlow` records (deduplicated by `ID_parent` or natural key), and a child resource that creates/updates `HeatFlow` + all sub-records. Both resources share a custom `GHFDBImportFormat` XLSX reader (header row 6, data from row 9) and a widget hierarchy (`ConceptWidget`, `MultiConceptWidget`, `QuantityWidget`, `YesNoWidget`, `RelatedModelWidget` subclasses) for creating related model instances from flat row data with field-level error reporting.

Upsert identifiers are template-aware: use `ID` / `ID_parent` when present in official-release sheets, but fall back to natural keys for standard uploads (`lat_NS` + `long_EW` for parent rows; `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference` for child rows). This fallback must remain compatible with django-import-export header validation — optional ID headers cannot be required by `import_id_fields` for standard template uploads.

All controlled-vocabulary tokens parsed from spreadsheet cells must be normalised — square brackets stripped and the result lowercased — before vocabulary validation and `Concept` lookup (FR-016).

The export uses the `GHFDB` proxy model's `for_export()` queryset (from `002-ghfdb-product-utilities`) to produce a GHFDB-compliant XLSX with all 62 columns in canonical order, semicolons for M2M fields, and plain SI numeric values for Pint quantity fields.

## Technical Context

**Language/Version**: Python ≥3.13
**Primary Dependencies**: Django 5.0+, FairDM framework, django-import-export ≥4.0.3 <5.0.0, research-vocabs, django-pint-field, openpyxl, tablib
**Storage**: PostgreSQL (reference); SQLite for local dev
**Testing**: pytest + pytest-django, factory-boy
**Target Platform**: Linux server (Docker), Windows dev
**Performance Goals**: Import 10,000-row GHFDB spreadsheet with full validation in <60 seconds
**Constraints**: Synchronous processing acceptable for files ≤50,000 rows / 20 MB; staff-only admin access for import/export; custom admin import/export hook overrides must remain signature-compatible with the installed django-import-export version; import upsert logic must support both ID-based (official release) and natural-key-based (standard upload template) matching; standard-template imports must not fail when `ID` / `ID_parent` headers are absent; controlled-vocabulary tokens must be normalised (bracket-stripped and lowercased) before vocabulary validation (FR-016); and `GHFDBImportFormat` must read column headers from row 6 and start data rows at row 9 (`min_row=9`) — rows 7 (unit labels) and 8 ("Allowed range of values") are metadata rows that must be skipped (BUG-004).
**Scale/Scope**: ~62 GHFDB spreadsheet columns, 6 relational models in the import graph, 14 M2M relations for export

## Constitution Check

| Principle | Status |
|-----------|--------|
| I. FAIR-First | **PASS** — Import preserves `local_id` (GHFDB identifier) for both parent and child. Export produces the IHFC-canonical flat format. No identifier degradation. |
| II. GHFDB Schema Fidelity | **PASS** — All 62 GHFDB columns mapped in contracts. Field mapping tables in contracts reference `docs/ghfdb_fields.md`. No schema divergence; all data stored at correct hierarchy level. Fuchs et al. citations in all resource docstrings. |
| III. FairDM-First | **PASS** — Resources use existing FairDM-derived models without modification. Custom resources justified: FairDM provides no GHFDB-specific import/export. |
| IV. Open Science & Provenance | **PASS** — Import/export is staff-only admin action. Imported data enters as unpublished; review workflow is not bypassed. Contributor fields preserved in round-trip. |
| V. Internationalisation | **PASS** — All user-facing error messages, admin labels, and widget error strings use `gettext_lazy()`. |
| VI. Test-First Quality | **PASS** — Tests written first (TDD). Round-trip import/export tests with known GHFDB sample data are pinned regression tests. Each resource tested independently. |
| VII. Documentation | **PASS** — Import/export column mapping documented via contracts and `docs/ghfdb_fields.md`. Large-export row limit documented in `GHFDBExportResource` docstring. |
| VIII. Spec-Driven Workflow | **PASS** — Following spec.md → plan.md → tasks.md. User stories ordered P2 (import) → P2 (export). |

## Project Structure

### Source Code (repository root)

```text
project/ghfdb/resources/
├── __init__.py          # Public re-exports: GHFDBParentImportResource, GHFDBChildImportResource, GHFDBExportResource, GHFDBImportFormat
├── _base.py             # GHFDBImportFormat, GHFDB_COLUMN_ORDER, PARENT_COLUMNS, CORRECTION_COL_MAP
├── _widgets.py          # ConceptWidget, MultiConceptWidget, QuantityWidget, YesNoWidget, RelatedModelWidget subclasses
├── parent.py            # GHFDBParentImportResource
├── child.py             # GHFDBChildImportResource
└── export.py            # GHFDBExportResource

tests/test_ghfdb/test_resources/
├── __init__.py
├── test_widgets.py           # Unit tests for custom widgets
├── test_parent_import.py     # GHFDBParentImportResource tests
├── test_child_import.py      # GHFDBChildImportResource tests
├── test_export.py            # GHFDBExportResource tests
├── test_schema_coverage.py   # Column-order / schema-coverage assertions
└── test_roundtrip.py         # End-to-end round-trip regression tests

tests/test_ghfdb/fixtures/
└── sample_ghfdb.xlsx         # 3–5 row fixture for round-trip regression
```

## Key Design Decisions

See [research.md](research.md) for full rationale. Summary:

- **Two-resource split** (parent + child) preferred over monolithic resource for testability, error isolation, and ability to update parent metadata independently.
- **`RelatedModelWidget`** creates/updates related model instances from multiple spreadsheet columns in a single `clean()` call, surfacing field-level `ValidationError` as prefixed `ValueError` for django-import-export's error pipeline.
- **`GHFDBImportFormat`** subclasses XLSX with sheet `"data list"`, headers at row 6, `min_row=9` for data.
- **Template-aware upsert**: `import_id_fields` uses always-present natural keys; `ID`/`ID_parent` are stored as `local_id` when present but never used as the sole upsert discriminator for standard uploads. ~~For standard uploads a synthetic `AUTO_PARENT:<lat>:<lon>` / `AUTO_CHILD:<lat>:<lon>:<q_top>:<q_bottom>:<ref>` key is generated internally. This key is **internal-only**: it MUST be stored in a hidden `_upsert_key` field (not the `ID_parent` / `ID` display fields) and MUST NOT appear on the confirm-page diff view.~~ (Superseded by BUG-005 fix: synthetic keys removed entirely.) For standard uploads without explicit IDs, parent deduplication uses `(lat_NS, long_EW)` tuples directly in `before_import()`, and site lookup in `_get_or_create_site()` queries `HeatFlowSite` by `location__x` / `location__y`. Child-to-parent resolution uses `_resolve_parent_by_location()` when `ForeignKeyWidget` returns no match. The `ID_parent` field on the confirm page MUST reflect `ParentHeatFlow.local_id` (or be empty when no explicit ID is present in the source file).
- **FR-016 normalisation**: `normalize_vocab_token(raw)` strips `[]` and lowercases before any concept lookup; error messages preserve original pre-normalisation text for user traceability.
- **Confirm-page column order**: Both `GHFDBParentImportResource` and `GHFDBChildImportResource` MUST override `get_user_visible_fields()` (or equivalent django-import-export hook) to sort the returned field list by each field's `column_name` position in `PARENT_COLUMNS` (parent) or `GHFDB_COLUMN_ORDER` (child). Fields whose `column_name` does not appear in the canonical list (e.g. internal `_upsert_key`) are sorted to the end. This ensures the confirm-page diff table column order matches the source spreadsheet, allowing staff to verify row values column-by-column against the uploaded file.
- **Widget type-guard contract** (BUG-007): Every widget `clean()` method that calls `.strip()` directly or indirectly (via `CharWidget.clean()`) MUST wrap that call in `try/except AttributeError` and re-raise as a `ValueError` with a message of the form: `"Column '<col>' received a non-text value <val!r>; expected a text string."` The three affected sites in `_widgets.py` are: (1) `ConceptWidget.clean()` — wraps `super().clean()`; (2) `RelatedModelWidget.clean()` — sentinel column guard; (3) `ParentWidget.clean()` — `name` sentinel guard. All re-raised `ValueError` messages MUST use `gettext_lazy()` (constitution §V).
