# Implementation Plan: GHFDB Flat Data Interface

**Branch**: `002-ghfdb-proxy` | **Date**: 2026-04-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-ghfdb-proxy/spec.md`
**Propagated**: 2026-04-14 -- Updated from spec.md refinement (admin column order + filter constraints)
**Propagated**: 2026-04-17 -- Updated from spec.md refinement (two proxy models: GHFDBChild + GHFDBParent; split admin registrations; resource-to-admin assignment)
**Bugfix**: 2026-04-14 -- [BUG-001] Added constrained-option behavior for concept-backed admin filters (`explo_purpose`).
**Downstream**: Import/export pipeline is planned and implemented in `003-ghfdb-import-export`.

## Summary

This plan covers:

1. **Two GHFDB proxy models** -- `GHFDBChild` extends `HeatFlow` (proxy, no new table), `objects = GHFDBChildManager()`; `GHFDBParent` extends `ParentHeatFlow` (proxy, no new table), `objects = GHFDBParentManager()`. Both admin-only (not registered with FairDM registry).
2. **`GHFDBChildQuerySet`** -- `as_ghfdb_flat()` (31 `F()`-annotated scalars + 9 correction-flag subqueries; <=2 DB queries, constant) and `for_export()` (`as_ghfdb_flat()` + 14 `prefetch_related` paths; ~16 queries, constant). `for_export()` is consumed by the downstream `003-ghfdb-import-export` spec.
3. **`GHFDBParentQuerySet`** -- `with_child_counts()` (annotates `total_children` and `relevant_children` counts), `with_children()` (prefetches linked child `HeatFlow` records). Constant query count.
4. **Two Django admin changelists** -- Read-only `GHFDBChildAdmin` (labelled "GHFDB Entries") with exact child-level display order, vocabulary-scoped `explo_purpose` list filter (BUG-001), search by `name`/`ID_parent`, and `GHFDBChildImportResource` + `GHFDBExportResource` attached. Read-only `GHFDBParentAdmin` (labelled "GHFDB Parent Entries") with parent-level display order plus `total_children`/`relevant_children` computed columns, same filter/search set, and `GHFDBParentImportResource` attached.
5. **Explore map page** -- `GHFDBExploreView` serving `explore.html`: full-viewport iframe embedding the IHFC web-map viewer, `onerror` fallback, no auth required, menu link active.
6. **`HeatFlow.local_id` migration** -- Nullable `CharField` added to `HeatFlow` (also `HeatFlowSite.local_id` and `ParentHeatFlow.local_id`) as stable import upsert keys for the downstream import spec.

## Technical Context

- **Language**: Python >=3.13
- **Dependencies**: Django 5.0+, FairDM, django-pint-field
- **Performance**: `GHFDBChildQuerySet.as_ghfdb_flat()` <=2 queries (constant); `for_export()` ~16 queries (constant); `GHFDBParentQuerySet.with_child_counts()` 1 query (constant); `with_children()` ~2 queries (constant); no N+1 per row
- **Constraints**: Both proxies admin-only (no FairDM registry); `explo_purpose` list-filter choices vocabulary-scoped (not generic); `local_id` fields nullable, indexed; import/export resources attached to their respective admin only

## Constitution Check

| Principle | Status |
|-----------|--------|
| I. FAIR-First | **PASS** -- `local_id` (GHFDB identifier) preserved. Proxy models enable FAIR-compliant flat access without schema divergence. |
| II. GHFDB Schema Fidelity | **PASS** -- All GHFDB column names preserved as annotation names. Mapping in `data-model.md`. Fuchs et al. proxy model docstring citations. |
| III. FairDM-First | **PASS** -- `GHFDBChild` extends `HeatFlow` (FairDM `Measurement`); `GHFDBParent` extends `ParentHeatFlow` (FairDM `Measurement`). Neither registered (admin-only; no auto-generated views needed). |
| V. Internationalisation | **PASS** -- Admin verbose names and labels use `gettext_lazy()`. |
| VI. Test-First Quality | **PASS** -- Query-count tests and admin tests written first (TDD). Correction-flag annotations have pinned regression tests. Parent count annotation tests added. |

## Project Structure

### Source Code

```
project/ghfdb/
+-- models.py            # GHFDBChild proxy (GHFDBChildManager) + GHFDBParent proxy (GHFDBParentManager)
+-- managers.py          # GHFDBChildQuerySet: as_ghfdb_flat(), for_export(); GHFDBParentQuerySet: with_child_counts(), with_children()
+-- admin.py             # GHFDBChildAdmin (child import + export) + GHFDBParentAdmin (parent import) — both read-only
+-- views.py             # GHFDBExploreView
+-- urls.py              # explore/ URL routing
+-- templates/ghfdb/
    +-- explore.html     # Full-viewport iframe + onerror fallback

tests/test_ghfdb/
+-- conftest.py          # heat_flow_chain fixture, sample_ghfdb_row fixture
+-- test_models.py       # Proxy model smoke tests (both GHFDBChild and GHFDBParent)
+-- test_managers.py     # Query-count tests, annotation completeness, correction flags, parent count annotations
+-- test_admin.py        # Changelist HTTP 200, column order, filters, search (both admins)
+-- test_views.py        # Map page: HTTP 200, iframe, no auth required
```
