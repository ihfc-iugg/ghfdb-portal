# Tasks: GHFDB Flat Data Interface

**Feature**: 002-ghfdb-proxy
**Branch**: `002-ghfdb-proxy`
**Input**: plan.md, spec.md, data-model.md, quickstart.md
**Generated**: 2026-04-13
**Propagated**: 2026-04-14 — Updated from spec.md refinement (admin column order + filter constraints)
**Propagated**: 2026-04-17 — Updated from spec.md refinement (two proxy models: GHFDBChild + GHFDBParent; split admin registrations; resource-to-admin assignment)
**Bugfix**: 2026-04-14 � [BUG-001] Reopened admin filter tasks and added vocabulary-scoping tasks for `explo_purpose` list-filter choices.
**Downstream**: Import/export pipeline tasks (T022�T074) have been moved to `003-ghfdb-import-export/tasks.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no dependency on an incomplete task)
- **[US1/4]**: Mapped user story
- All tasks include an exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the new test package and directory structure before all implementation begins.

- [X] T001 Create `tests/test_ghfdb/` package with `__init__.py` and empty placeholder files: `test_models.py`, `test_managers.py`, `test_admin.py`, `test_views.py` in `tests/test_ghfdb/`
- [X] T002 Create `tests/test_ghfdb/conftest.py` with a `heat_flow_chain` pytest fixture that builds a complete record chain: `HeatFlowSite` ? `HeatFlowInterval` (with `ProbeMetadata`) ? `ParentHeatFlow` ? `HeatFlow` (linked to `ThermalGradient`, `IntervalConductivity`, and `HeatFlowCorrection` instances for all 9 correction types); include a `sample_ghfdb_row` fixture with a minimal valid dict of GHFDB flat-column values

### System Validation � Phase 1

- [X] T003 ?? CRITICAL: Run Django system checks: `poetry run python manage.py check` � MUST pass before proceeding to Phase 2

**Checkpoint � Setup Complete**: Package structure exists and system checks pass.

---

## Phase 2: Foundational (Blocking Prerequisite � `HeatFlow.local_id`)

**Purpose**: Add the `local_id` field to `HeatFlow` and generate its migration. This field serves as the stable import upsert key consumed by the downstream `003-ghfdb-import-export` spec.

**?? CRITICAL**: No user story work can begin until this phase is complete and the migration is verified.

- [X] T004 Add `local_id = models.CharField(max_length=255, null=True, blank=True, db_index=True, help_text=_("GHFDB spreadsheet ID column � used as the stable key for import upsert"))` to the `HeatFlow` model
- [X] T005 Generate migration: run `poetry run python manage.py makemigrations heat_flow` and verify the resulting file in `project/heat_flow/migrations/` adds only a nullable `local_id` varchar column with a `db_index`

### System Validation � Phase 2

- [X] T006 ?? CRITICAL: Run Django system checks: `poetry run python manage.py check` � MUST pass before proceeding
- [X] T007 ?? CRITICAL: Apply migration and verify: `poetry run python manage.py migrate` � MUST succeed cleanly before proceeding to any user story

**Checkpoint � Foundation Ready**: `HeatFlow.local_id` exists in the database.

---

## Phase 3: User Story 1 — GHFDBChild Proxy Model (Priority: P1) ⚠️ MVP

**Goal**: A `GHFDBChild` proxy model over `HeatFlow` with a `GHFDBChildQuerySet` returning all **40 scalar + correction-flag columns** via `as_ghfdb_flat()` (31 `F()`-annotated scalars + 9 correction-flag subqueries; =2 DB queries, constant) and the full **65 GHFDB columns** via `for_export()` (~16 queries, constant), registered as a read-only Django admin view labelled "GHFDB Entries" with exact parent-level changelist column order plus required search and filter fields. `GHFDBChildImportResource` and `GHFDBExportResource` attached to this admin only.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v`

### Tests for User Story 1 ?? Write FIRST � verify they FAIL before implementing

- [X] T008 [P] [US1] Write query-count test: assert `GHFDBChild.objects.as_ghfdb_flat()` executes =2 DB queries using `django_assert_max_num_queries(2)` with the `heat_flow_chain` fixture in `tests/test_ghfdb/test_managers.py`
- [X] T009 [P] [US1] Write scalar-column completeness test: assert all 31 select_related annotations (`site_name`, `lat_ns`, `long_ew`, `p_q`, `p_q_uncertainty`, `interval_top`, `interval_bottom`, `tgrad_value`, `tc_value`, `probe_penetration`, etc.) are accessible as attributes on records from `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [X] T010 [P] [US1] Write correction-flags test: assert all 9 `corr_*_flag` annotations (`corr_IS_flag`, `corr_T_flag`, `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag`) are accessible as attributes on records from `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [X] T011 [P] [US1] Write `for_export()` query-count test: assert `GHFDBChild.objects.for_export()` executes =16 DB queries using `django_assert_max_num_queries(16)` in `tests/test_ghfdb/test_managers.py`
- [X] T012 [P] [US1] Write standard queryset operability test: assert `filter()`, `order_by()`, and `count()` work without error on the queryset returned by `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [X] T013 ?? Reopened [P] [US1] Refine admin registration tests in `tests/test_ghfdb/test_admin.py`: assert changelist HTTP 200, title "GHFDB Entries", exact ordered parent-level columns (`ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`), search fields for `name` and `ID_parent`, and list filters for `environment`, `corr_HP_flag`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain` (reopened � BUG-001)
- [X] T063 [P] [US1] Add a failing regression test in `tests/test_ghfdb/test_admin.py` verifying that `explo_purpose` list-filter choices are restricted to values accepted by `HeatFlowSite.explo_purpose` and exclude unrelated generic `Concept` values

### Implementation for User Story 1

- [X] T014 [US1] Extend existing `project/ghfdb/managers.py` and implement `_correction_subqueries()` helper: iterates `HeatFlowCorrection.CorrectionTypeChoices.choices`, returns a dict of 9 correlated `Subquery` annotations keyed as `corr_{type}_flag`, each selecting `HeatFlowCorrection.status` filtered by `heat_flow=OuterRef("pk")` and `correction_type=choice_value`
- [X] T015 [US1] Implement `GHFDBChildQuerySet.as_ghfdb_flat()` in `project/ghfdb/managers.py`: chain `select_related(...)` for paths `sample__sample`, `sample__sample__location`, `parent`, `thermal_gradient`, `thermal_conductivity`, `sample__probe_metadata`; then `annotate(...)` with `F()` expressions for all 31 scalar columns per the data-model.md mapping table; then merge the 9 `_correction_subqueries()` annotations
- [X] T016 [US1] Implement `GHFDBChildQuerySet.for_export()` in `project/ghfdb/managers.py`: call `self.as_ghfdb_flat()` and chain `prefetch_related(...)` for all 14 M2M paths: `method`, `sample__sample__explo_purpose`, `thermal_gradient__method_top`, `thermal_gradient__method_bottom`, `thermal_gradient__correction_top`, `thermal_gradient__correction_bottom`, `thermal_conductivity__source`, `thermal_conductivity__location`, `thermal_conductivity__method`, `thermal_conductivity__saturation`, `thermal_conductivity__pT_conditions`, `thermal_conductivity__pT_function`, `thermal_conductivity__strategy`, `sample__probe_metadata__probe_type`
- [X] T017 [US1] Implement `GHFDBChildManager(models.Manager)` in `project/ghfdb/managers.py`: override `get_queryset()` to return `GHFDBChildQuerySet(self.model, using=self._db)`, and add `as_ghfdb_flat()` and `for_export()` delegation methods
- [X] T018 [US1] Implement `GHFDBChild` proxy model in `project/ghfdb/models.py`: inherits `HeatFlow`, `objects = GHFDBChildManager()`, `class Meta: proxy = True; verbose_name = _("GHFDB Entry"); verbose_name_plural = _("GHFDB Entries")`; add class docstring citing Fuchs et al. (2021, 2023). **Note � registry exemption**: `GHFDBChild` is a proxy over `HeatFlow`, not a direct `Sample` or `Measurement` subclass. FairDM registry (`@fairdm.register`) applies only to direct `Sample`/`Measurement` subtypes that need auto-generated views/tables/filters; this proxy is intentionally admin-only and does not require registry registration. **Also**: add a minimal smoke test to `tests/test_ghfdb/test_models.py`: `from project.ghfdb.models import GHFDBChild` / `assert GHFDBChild._meta.proxy is True` / `assert GHFDBChild._meta.verbose_name == "GHFDB Entry"`.
- [X] T019 ?? Reopened [US1] Update `project/ghfdb/admin.py` `GHFDBChildAdmin(ImportExportMixin, admin.ModelAdmin)`: keep `get_queryset()` returning `GHFDBChild.objects.as_ghfdb_flat()`. Attach `GHFDBChildImportResource` and `GHFDBExportResource` exclusively to this admin (FR-011b), set `list_display` to exact parent-level order (`ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`), configure `search_fields` for `name` and `ID_parent`, configure `list_filter` for `environment`, `corr_HP_flag`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`, keep `list_display_links = None` for read-only, and wrap user-facing strings in `_()` (reopened � BUG-001)
- [X] T064 [US1] Implement a constrained admin list filter class (e.g., `SimpleListFilter`) for `explo_purpose` in `project/ghfdb/admin.py` so filter lookups are vocabulary-scoped to `HeatFlowSite.explo_purpose`

### System Validation � Phase 3

- [X] T020 ?? CRITICAL: Run Django system checks: `poetry run python manage.py check` � MUST pass before proceeding
- [X] T021 ?? Reopened CRITICAL: Re-run User Story 1 tests after admin refinement: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v` � ALL tests MUST pass including exact admin column-order/search/filter assertions (reopened � BUG-001)
- [X] T065 ?? CRITICAL [US1] Re-run `poetry run pytest tests/test_ghfdb/test_admin.py -v` and confirm `explo_purpose` filter choices are vocabulary-scoped before closing BUG-001

**Checkpoint — US1 Complete**: Child proxy model queryable, all scalar annotations verified, correction flags present, admin list view renders with exact column order, search/filter controls, `explo_purpose` filter vocabulary-scoped (BUG-001), query counts confirmed constant. `GHFDBChildImportResource` + `GHFDBExportResource` attached to this admin only.

---

## Phase 3b: User Story 1b — GHFDBParent Proxy Model (Priority: P1) ✨ NEW

**Goal**: A `GHFDBParent` proxy model over `ParentHeatFlow` with a `GHFDBParentQuerySet` that supports parent-level queries with `with_child_counts()` (annotates `total_children` and `relevant_children`) and `with_children()` (prefetches linked child records). Registered as a read-only Django admin view labelled "GHFDB Parent Entries" with parent-level spreadsheet column order plus computed child-count columns. `GHFDBParentImportResource` attached to this admin only.

**Depends on**: Phase 2 (HeatFlow.local_id)
**Independent Test**: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v`

### Tests for User Story 1b ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T066 [P] [US1b] Write query-count test: assert `GHFDBParent.objects.with_child_counts()` executes in a constant number of DB queries (no N+1) in `tests/test_ghfdb/test_managers.py`
- [X] T067 [P] [US1b] Write count-correctness test: given a `ParentHeatFlow` with N children, assert `total_children == N` and `relevant_children` matches expected threshold-filtered count in `tests/test_ghfdb/test_managers.py`
- [X] T068 [P] [US1b] Write `with_children()` test: assert parent records include prefetched child `HeatFlow` objects accessible without extra queries in `tests/test_ghfdb/test_managers.py`
- [X] T069 [P] [US1b] Write standard queryset operability test: assert `filter()`, `order_by()`, and `count()` work on `GHFDBParent.objects.all()` in `tests/test_ghfdb/test_managers.py`
- [X] T070 [P] [US1b] Write admin registration tests in `tests/test_ghfdb/test_admin.py`: assert `GHFDBParentAdmin` changelist HTTP 200, title "GHFDB Parent Entries", exact ordered columns (`ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`, `total_children`, `relevant_children`), search fields for `name` and `ID_parent`, same list filters as `GHFDBChildAdmin` including vocabulary-scoped `explo_purpose`
- [X] T071 [P] [US1b] Write admin import resource test: assert `GHFDBParentAdmin.get_import_resource_classes()` returns `[GHFDBParentImportResource]` only (not `GHFDBChildImportResource` or `GHFDBExportResource`) in `tests/test_ghfdb/test_admin.py`

### Implementation for User Story 1b

- [X] T072 [US1b] Implement `GHFDBParentQuerySet` in `project/ghfdb/managers.py`: add `with_child_counts()` method that annotates `total_children = Count("children")` (or equivalent FK reverse name) and `relevant_children = Count("children", filter=Q(...))` with an appropriate quality/relevance threshold; add `with_children()` method that calls `prefetch_related("children")` (or equivalent) to attach child `HeatFlow` records
- [X] T073 [US1b] Implement `GHFDBParentManager` in `project/ghfdb/managers.py`: override `get_queryset()` to return `GHFDBParentQuerySet(self.model, using=self._db)`, add `with_child_counts()` and `with_children()` delegation methods
- [X] T074 [US1b] Implement `GHFDBParent` proxy model in `project/ghfdb/models.py`: inherits `ParentHeatFlow`, `objects = GHFDBParentManager()`, `class Meta: proxy = True; verbose_name = _("GHFDB Parent Entry"); verbose_name_plural = _("GHFDB Parent Entries")`; add class docstring. Add smoke test to `tests/test_ghfdb/test_models.py`: `assert GHFDBParent._meta.proxy is True` / `assert GHFDBParent._meta.verbose_name == "GHFDB Parent Entry"`
- [X] T075 [US1b] Implement `GHFDBParentAdmin(ImportExportMixin, admin.ModelAdmin)` in `project/ghfdb/admin.py`: register for `GHFDBParent`, `get_queryset()` returns `GHFDBParent.objects.with_child_counts()`, `list_display` = parent-level GHFDB column order + `total_children` + `relevant_children` as computed columns, `search_fields` for `name` and `local_id`, `list_filter` same set as `GHFDBChildAdmin` (including `ExplorePurposeListFilter`), `list_display_links = None`, read-only permissions. Attach `GHFDBParentImportResource` exclusively (FR-011b) — no export resource or child import resource.

### System Validation — Phase 3b

- [X] T076 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [X] T077 ⚠️ CRITICAL: Run User Story 1b tests: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v` — ALL new parent-proxy tests MUST pass

**Checkpoint — US1b Complete**: Parent proxy model queryable with child count annotations and prefetchable children; admin list view renders with correct column order + computed columns; `GHFDBParentImportResource` attached exclusively to this admin.

---

## Phase 6: User Story 4 � Web Map Viewer Page (Priority: P3)

**Goal**: The existing `GHFDBExploreView` and `explore.html` are enhanced with a graceful `onerror` fallback for unreachable iframes; the "Explore" menu item and URL routing are verified correct.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_views.py -v`

### Tests for User Story 4 ?? Write FIRST � verify they FAIL before implementing

- [X] T048 [P] [US4] Write failing test: anonymous `GET /ghfdb/explore/` returns HTTP 200 and response body contains `<iframe>` with `src="https://ihfc-iugg.github.io/HeatFlowMapping/"` in `tests/test_ghfdb/test_views.py`
- [X] T049 [P] [US4] Write failing test: rendered `explore.html` template source contains a visible fallback element (e.g. `class="explore-fallback"` or `id="map-error"`) for the unreachable-URL case in `tests/test_ghfdb/test_views.py`
- [X] T050 [P] [US4] Write no-auth test: map page returns HTTP 200 for an unauthenticated request (no redirect to login) in `tests/test_ghfdb/test_views.py`

### Implementation for User Story 4

- [X] T051 [US4] Update `project/ghfdb/templates/ghfdb/explore.html`: full-viewport iframe (`width="100%"`, `height="100vh"`, `style="border:none"`) embedding `https://ihfc-iugg.github.io/HeatFlowMapping/`; add `onerror="this.style.display='none'; document.getElementById('map-error').style.display='block';"` attribute and a `<div id="map-error" class="explore-fallback" style="display:none">` fallback message explaining the map is temporarily unavailable
- [X] T052 [US4] Verify `GHFDBExploreView` in `project/ghfdb/views.py` has no `LoginRequiredMixin` and uses template `"ghfdb/explore.html"`; confirm URL pattern in `project/ghfdb/urls.py` resolves as `name="explore"` (or `ghfdb-explore`)
- [X] T053 [US4] Verify the "Explore" `MenuItem` (in `project/heat_flow/menus.py` or `project/ghfdb/apps.py` � check FairDM nav registration pattern) points to the correct URL name and is configured to mark itself active when on the map page

### System Validation � Phase 6

- [X] T054 ?? CRITICAL: Run Django system checks: `poetry run python manage.py check` � MUST pass before proceeding
- [x] T054a ?? CRITICAL: Run type checks: `poetry run mypy project/ghfdb/` � MUST pass with no new errors
- [X] T054b ?? CRITICAL: Run linting: `poetry run ruff check project/ghfdb/` � MUST pass with zero violations
- [X] T055 ?? CRITICAL: Run User Story 4 tests: `poetry run pytest tests/test_ghfdb/test_views.py -v` � ALL tests MUST pass

**Checkpoint � US4 Complete**: Map page accessible without auth, iframe present with `onerror` fallback, Explore menu item active.

---

## Phase 7: Polish & Final Validation

**Purpose**: Documentation update and full-suite validation.

- [X] T059 [P] Update `docs/ghfdb_fields.md` to document `HeatFlow.local_id` (type, constraints, purpose, GHFDB spreadsheet `ID` column) and add a "Proxy Model Access Patterns" section citing key annotation names from the `data-model.md` mapping table
- [X] T078 [P] Update `docs/ghfdb_fields.md` to document the `GHFDBParent` proxy model, its queryset methods (`with_child_counts()`, `with_children()`), and admin registration

### System Validation — Final

- [X] T061 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass
- [x] T061a ⚠️ CRITICAL: Run final type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors
- [X] T061b ⚠️ CRITICAL: Run final linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations
- [X] T062 ⚠️ CRITICAL: Run full GHFDB proxy model test suite: `poetry run pytest tests/test_ghfdb/ -v` — ALL test modules MUST pass (including new GHFDBParent tests)

**Checkpoint — Feature Complete**: System checks pass, all GHFDB proxy model + admin + views tests green (both GHFDBChild and GHFDBParent), `ghfdb_fields.md` updated.

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends on | Blocks |
|---|---|---|
| Phase 1 � Setup | Nothing | Nothing |
| Phase 2 — Foundational (`HeatFlow.local_id`) | Phase 1 | Phase 3 (US1), Phase 3b (US1b), Phase 6 (US4) |
| Phase 3 — US1 GHFDBChild Proxy (P1) | Phase 2 | `003-ghfdb-import-export` Phase 5 (US3 export needs `for_export()`) |
| Phase 3b — US1b GHFDBParent Proxy (P1) | Phase 2 | `003-ghfdb-import-export` (parent import resource needs `GHFDBParent` admin) |
| Phase 6 — US4 Map Viewer (P3) | Phase 2 | Nothing (independent) |
| Phase 7 — Polish | Phase 3 + Phase 3b + Phase 6 | Nothing |
