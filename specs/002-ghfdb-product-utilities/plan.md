# Implementation Plan: GHFDB Flat Data Interface

**Branch**: `002-ghfdb-product-utilities` | **Date**: 2026-04-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-ghfdb-product-utilities/spec.md`
**Propagated**: 2026-04-14 -- Updated from spec.md refinement (admin column order + filter constraints)
**Bugfix**: 2026-04-14 -- [BUG-001] Added constrained-option behavior for concept-backed admin filters (`explo_purpose`).
**Downstream**: Import/export pipeline is planned and implemented in `003-ghfdb-import-export`.

## Summary

This plan covers:

1. **GHFDB proxy model** -- `GHFDB` extends `HeatFlow` (proxy, no new table), `objects = GHFDBManager()`, admin-only (not registered with FairDM registry).
2. **`GHFDBQuerySet`** -- `as_ghfdb_flat()` (31 `F()`-annotated scalars + 9 correction-flag subqueries; <=2 DB queries, constant) and `for_export()` (`as_ghfdb_flat()` + 14 `prefetch_related` paths; ~16 queries, constant). `for_export()` is consumed by the downstream `003-ghfdb-import-export` spec.
3. **Django admin changelist** -- Read-only `GHFDBAdmin` with exact parent-field display order, vocabulary-scoped `explo_purpose` list filter (BUG-001), and search by `name`/`ID_parent`.
4. **Explore map page** -- `GHFDBExploreView` serving `explore.html`: full-viewport iframe embedding the IHFC web-map viewer, `onerror` fallback, no auth required, menu link active.
5. **`HeatFlow.local_id` migration** -- Nullable `CharField` added to `HeatFlow` (also `HeatFlowSite.local_id` and `ParentHeatFlow.local_id`) as stable import upsert keys for the downstream import spec.

## Technical Context

- **Language**: Python >=3.13
- **Dependencies**: Django 5.0+, FairDM, django-pint-field
- **Performance**: `as_ghfdb_flat()` <=2 queries (constant); `for_export()` ~16 queries (constant); no N+1 per row
- **Constraints**: `GHFDB` admin-only (no FairDM registry); `explo_purpose` list-filter choices vocabulary-scoped (not generic); `local_id` fields nullable, indexed

## Constitution Check

| Principle | Status |
|-----------|--------|
| I. FAIR-First | **PASS** -- `local_id` (GHFDB identifier) preserved. Proxy model enables FAIR-compliant flat access without schema divergence. |
| II. GHFDB Schema Fidelity | **PASS** -- All GHFDB column names preserved as annotation names. Mapping in `data-model.md`. Fuchs et al. proxy model docstring citations. |
| III. FairDM-First | **PASS** -- `GHFDB` extends `HeatFlow` (FairDM `Measurement`). Not registered (admin-only; no auto-generated views needed). |
| V. Internationalisation | **PASS** -- Admin verbose names and labels use `gettext_lazy()`. |
| VI. Test-First Quality | **PASS** -- Query-count tests and admin tests written first (TDD). Correction-flag annotations have pinned regression tests. |

## Project Structure

### Source Code

```
project/ghfdb/
+-- models.py            # GHFDB proxy model (GHFDBManager assigned)
+-- managers.py          # GHFDBQuerySet: as_ghfdb_flat(), for_export()
+-- admin.py             # GHFDBAdmin (read-only changelist; import/export hooks in 003)
+-- views.py             # GHFDBExploreView
+-- urls.py              # explore/ URL routing
+-- templates/ghfdb/
    +-- explore.html     # Full-viewport iframe + onerror fallback

tests/test_ghfdb/
+-- conftest.py          # heat_flow_chain fixture, sample_ghfdb_row fixture
+-- test_models.py       # Proxy model smoke tests
+-- test_managers.py     # Query-count tests, annotation completeness, correction flags
+-- test_admin.py        # Changelist HTTP 200, column order, filters, search
+-- test_views.py        # Map page: HTTP 200, iframe, no auth required
```
