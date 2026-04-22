# Implementation Plan: GHFDB Flat Data Interface

**Branch**: `002-ghfdb-proxy` | **Date**: 2026-04-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-ghfdb-proxy/spec.md`
**Propagated**: 2026-04-14 -- Updated from spec.md refinement (admin column order + filter constraints)
**Propagated**: 2026-04-17 -- Updated from spec.md refinement (two proxy models: GHFDBChild + GHFDBParent; split admin registrations; resource-to-admin assignment)
**Propagated**: 2026-04-22 -- Updated from spec.md refinement: `ghfdb_id`/`quality` added to both models; `local_id`/`is_ghfdb` removed; FR-001b (manager default queryset scoping); child and parent admin column orders updated to match child.json/parent.json API schema
**Bugfix**: 2026-04-14 -- [BUG-001] Added constrained-option behavior for concept-backed admin filters (`explo_purpose`).
**Bugfix**: 2026-04-17 -- [BUG-002] Corrected the `GHFDBChild` admin contract to use child-level changelist columns with parent/site identifiers retained only as contextual fields.
**Bugfix**: 2026-04-17 -- [BUG-003] Added guardrails for child-admin queryset optimization so only valid ORM relation paths are used in changelist prefetches.
**Bugfix**: 2026-04-20 -- [BUG-004] Extended vocabulary-scoped filters to `environment` and `explo_method` on both admins; fixed `_interval()` fallback to return `None`.
**Downstream**: Import/export pipeline is planned and implemented in `003-ghfdb-import-export`.

## Summary

This plan covers:

1. **Two GHFDB proxy models** -- `GHFDBChild` extends `HeatFlow` (proxy, no new table), `objects = GHFDBChildManager()`; `GHFDBParent` extends `ParentHeatFlow` (proxy, no new table), `objects = GHFDBParentManager()`. Both admin-only (not registered with FairDM registry).
2. **`GHFDBChildQuerySet`** -- `as_ghfdb_flat()` (31 `F()`-annotated scalars + 9 correction-flag subqueries; <=2 DB queries, constant) and `for_export()` (`as_ghfdb_flat()` + 14 `prefetch_related` paths; ~16 queries, constant). `for_export()` is consumed by the downstream `003-ghfdb-import-export` spec.
3. **`GHFDBParentQuerySet`** -- `with_child_counts()` (annotates `total_children` and `relevant_children` counts), `with_children()` (prefetches linked child `HeatFlow` records). Constant query count.
4. **Two Django admin changelists** -- Read-only `GHFDBChildAdmin` (labelled "GHFDB Children") with 2026-04-22 child-level display order: `ghfdb_id`, `ID_parent`, `name`, `lat_NS`, `long_EW`, followed by child measurement, correction, probe, gradient, conductivity, and reference fields, with `quality` inserted before `Ref_ISGN` (~~`local_id`~~ removed); vocabulary-scoped custom `SimpleListFilter` classes for `environment` (`GeographicEnvironment`), `explo_method` (`ExplorationMethod`), and `explo_purpose` (`ExplorationPurpose`) on the child admin (BUG-001, BUG-004); analogous parent-path filter classes for the parent admin; search by `name`/`ID_parent`; `_interval()` helper returns `None` on missing MTI accessor (BUG-004); `GHFDBChildImportResource` + `GHFDBExportResource` attached. Read-only `GHFDBParentAdmin` (labelled "GHFDB Parents") with 2026-04-22 parent-level display order: `ghfdb_id`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `p_comment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `quality`, `country`, `region`, `continent`, `domain`, `total_children`, `relevant_children` (~~`ID_parent`~~ as lead removed; `p_comment` and `quality` added); same vocabulary-scoped filter/search set; `GHFDBParentImportResource` attached.
5. **Explore map page** -- `GHFDBExploreView` serving `explore.html`: full-viewport iframe embedding the IHFC web-map viewer, `onerror` fallback, no auth required, menu link active.
6. ~~**`HeatFlow.local_id` migration** -- Nullable `CharField` added to `HeatFlow` (also `HeatFlowSite.local_id` and `ParentHeatFlow.local_id`) as stable import upsert keys for the downstream import spec.~~ (superseded by 2026-04-22) **`ghfdb_id` + `quality` fields** -- `ghfdb_id` (PositiveIntegerField, nullable, db_index) and `quality` (CharField, nullable) have been added to both `HeatFlow` and `ParentHeatFlow` via the `001-heat-flow-data-model` branch migration. `local_id` and `is_ghfdb` have been removed. No further migration is required within this feature. **FR-001b**: Both `GHFDBChildManager` and `GHFDBParentManager` MUST scope their default querysets to `ghfdb_id__isnull=False` to exclude unassigned records automatically.

## Technical Context

- **Language**: Python >=3.13
- **Dependencies**: Django 5.0+, FairDM, django-pint-field
- **Performance**: `GHFDBChildQuerySet.as_ghfdb_flat()` <=2 queries (constant); `for_export()` ~16 queries (constant); `GHFDBParentQuerySet.with_child_counts()` 1 query (constant); `with_children()` ~2 queries (constant); no N+1 per row
- **Constraints**: Both proxies admin-only (no FairDM registry); all concept-backed list-filter choices vocabulary-scoped via custom `SimpleListFilter` classes — `environment` scoped to `GeographicEnvironment`, `explo_method` to `ExplorationMethod`, `explo_purpose` to `ExplorationPurpose` (BUG-001, BUG-004); `_interval()` returns `None` on missing MTI (BUG-004); ~~`local_id` fields nullable, indexed~~ (removed — superseded by `ghfdb_id` PositiveIntegerField on `HeatFlow` and `ParentHeatFlow`); both manager default querysets MUST scope to `ghfdb_id__isnull=False` (FR-001b); import/export resources attached to their respective admin only

## Constitution Check

| Principle | Status |
|-----------|--------|
| I. FAIR-First | **PASS** -- `ghfdb_id` (stable PositiveIntegerField GHFDB identifier, replaces former `local_id` CharField) preserved. Proxy models enable FAIR-compliant flat access without schema divergence. |}
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
