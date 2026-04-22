# Tasks: GHFDB Flat Data Interface

**Feature**: 002-ghfdb-proxy
**Branch**: `002-ghfdb-proxy`
**Input**: plan.md, spec.md, data-model.md, quickstart.md
**Generated**: 2026-04-13
**Propagated**: 2026-04-14 — Updated from spec.md refinement (admin column order + filter constraints)
**Propagated**: 2026-04-17 — Updated from spec.md refinement (two proxy models: GHFDBChild + GHFDBParent; split admin registrations; resource-to-admin assignment)
**Propagated**: 2026-04-22 — Updated from spec.md refinement: `ghfdb_id`/`quality` added; `local_id`/`is_ghfdb` removed; FR-001b manager default queryset scoping; child and parent admin column orders updated; Phase 2 local_id tasks superseded; Phase 8 added.
**Bugfix**: 2026-04-14 � [BUG-001] Reopened admin filter tasks and added vocabulary-scoping tasks for `explo_purpose` list-filter choices.
**Bugfix**: 2026-04-17 — [BUG-002] Reopened child-admin tasks and added child-field coverage work so `GHFDBChild` no longer uses the parent changelist contract.
**Bugfix**: 2026-04-17 — [BUG-003] Reopened child-admin validation tasks after invalid `prefetch_related()` relation paths caused changelist runtime errors.
**Bugfix**: 2026-04-20 — [BUG-004] Reopened vocabulary-scoping tasks; added filter classes for `environment`/`explo_method` on both admins; fixed `_interval()` fallback; added regression tests.
**Downstream**: Import/export pipeline tasks (T022-T071) have been moved to `003-ghfdb-import-export/tasks.md`.

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

## Phase 2: ~~Foundational (Blocking Prerequisite — `HeatFlow.local_id`)~~ [SUPERSEDED by 2026-04-22]

**Purpose**: ~~Add the `local_id` field to `HeatFlow` and generate its migration.~~ (superseded) This phase is now complete via a different migration in the `001-heat-flow-data-model` branch: `ghfdb_id` (PositiveIntegerField, nullable) and `quality` (CharField, nullable) were added to both `HeatFlow` and `ParentHeatFlow`; `local_id` and `is_ghfdb` were removed. The database is already migrated. Phase 2 tasks below are struck through; the new work is in Phase 8.

**⚠️ CRITICAL**: ~~No user story work can begin until this phase is complete and the migration is verified.~~ (done)

- ~~[X] T004 Add `local_id = models.CharField(max_length=255, null=True, blank=True, db_index=True, help_text=_("GHFDB spreadsheet ID column — used as the stable key for import upsert"))` to the `HeatFlow` model~~ **[SUPERSEDED]** — `ghfdb_id` (PositiveIntegerField) now serves this role. Added in `001-heat-flow-data-model` branch.
- ~~[X] T005 Generate migration: run `poetry run python manage.py makemigrations heat_flow` and verify the resulting file in `project/heat_flow/migrations/` adds only a nullable `local_id` varchar column with a `db_index`~~ **[SUPERSEDED]** — Migration generated and applied via `001-heat-flow-data-model` branch for `ghfdb_id`/`quality`.

### System Validation � Phase 2

- [X] T006 ?? CRITICAL: Run Django system checks: `poetry run python manage.py check` � MUST pass before proceeding
- [X] T007 ?? CRITICAL: Apply migration and verify: `poetry run python manage.py migrate` � MUST succeed cleanly before proceeding to any user story

**Checkpoint — ~~Foundation Ready: `HeatFlow.local_id` exists in the database~~** [SUPERSEDED] — `ghfdb_id` and `quality` already exist on both `HeatFlow` and `ParentHeatFlow` following merge of `001-heat-flow-data-model`.

---

## Phase 3: User Story 1 — GHFDBChild Proxy Model (Priority: P1) ⚠️ MVP

**Goal**: A `GHFDBChild` proxy model over `HeatFlow` with a `GHFDBChildQuerySet` returning all **40 scalar + correction-flag columns** via `as_ghfdb_flat()` (31 `F()`-annotated scalars + 9 correction-flag subqueries; <=2 DB queries, constant) and the full **65 GHFDB columns** via `for_export()` (~16 queries, constant), registered as a read-only Django admin view labelled "GHFDB Children" with the 2026-04-22 child-level changelist order: `ghfdb_id`, `ID_parent`, `name`, `lat_NS`, `long_EW`, then the required child measurement, correction, probe, gradient, conductivity, and reference fields, with `quality` before `Ref_ISGN` (~~`local_id`~~ removed). `GHFDBChildImportResource` and `GHFDBExportResource` attached to this admin only.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v`

### Tests for User Story 1 ?? Write FIRST � verify they FAIL before implementing

- [X] T008 [P] [US1] Write query-count test: assert `GHFDBChild.objects.as_ghfdb_flat()` executes =2 DB queries using `django_assert_max_num_queries(2)` with the `heat_flow_chain` fixture in `tests/test_ghfdb/test_managers.py`
- [X] T009 [P] [US1] Write scalar-column completeness test: assert all 31 select_related annotations (`site_name`, `lat_ns`, `long_ew`, `p_q`, `p_q_uncertainty`, `interval_top`, `interval_bottom`, `tgrad_value`, `tc_value`, `probe_penetration`, etc.) are accessible as attributes on records from `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [X] T010 [P] [US1] Write correction-flags test: assert all 9 `corr_*_flag` annotations (`corr_IS_flag`, `corr_T_flag`, `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag`) are accessible as attributes on records from `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [X] T011 [P] [US1] Write `for_export()` query-count test: assert `GHFDBChild.objects.for_export()` executes =16 DB queries using `django_assert_max_num_queries(16)` in `tests/test_ghfdb/test_managers.py`
- [X] T012 [P] [US1] Write standard queryset operability test: assert `filter()`, `order_by()`, and `count()` work without error on the queryset returned by `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [X] T013 ⚠️ Reopened [P] [US1] Refine admin registration tests in `tests/test_ghfdb/test_admin.py`: assert changelist HTTP 200, title "GHFDB Children", exact ordered child-level columns (~~`local_id`~~ [superseded 2026-04-22] `ghfdb_id`, `ID_parent`, `name`, `lat_NS`, `long_EW`, `qc`, `qc_uncertainty`, `q_method`, `q_top`, `q_bottom`, `probe_penetration`, `publication_reference`, `data_reference`, `relevant_child`, `c_comment`, `corr_IS_flag`, `corr_T_flag`, `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag`, `expedition`, `probe_type`, `probe_length`, `probe_tilt`, `water_temperature`, `geo_lithology`, `geo_stratigraphy`, `T_grad_mean`, `T_grad_uncertainty`, `T_grad_mean_cor`, `T_grad_uncertainty_cor`, `T_method_top`, `T_method_bottom`, `T_shutin_top`, `T_shutin_bottom`, `T_corr_top`, `T_corr_bottom`, `T_number`, `q_date`, `tc_mean`, `tc_uncertainty`, `tc_source`, `tc_location`, `tc_method`, `tc_saturation`, `tc_pT_conditions`, `tc_pT_fuction`, `tc_number`, `tc_strategy`, `quality`, `Ref_ISGN`), search fields for `name` and `ID_parent`, and list filters for `environment`, `corr_HP_flag`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, and `domain` (reopened — BUG-002; column list updated 2026-04-22)
- [X] T063 [P] [US1] Add a failing regression test in `tests/test_ghfdb/test_admin.py` verifying that `explo_purpose` list-filter choices are restricted to values accepted by `HeatFlowSite.explo_purpose` and exclude unrelated generic `Concept` values

### Implementation for User Story 1

- [X] T014 [US1] Extend existing `project/ghfdb/managers.py` and implement `_correction_subqueries()` helper: iterates `HeatFlowCorrection.CorrectionTypeChoices.choices`, returns a dict of 9 correlated `Subquery` annotations keyed as `corr_{type}_flag`, each selecting `HeatFlowCorrection.status` filtered by `heat_flow=OuterRef("pk")` and `correction_type=choice_value`
- [X] T015 [US1] Implement `GHFDBChildQuerySet.as_ghfdb_flat()` in `project/ghfdb/managers.py`: chain `select_related(...)` for paths `sample__sample`, `sample__sample__location`, `parent`, `thermal_gradient`, `thermal_conductivity`, `sample__probe_metadata`; then `annotate(...)` with `F()` expressions for all 31 scalar columns per the data-model.md mapping table; then merge the 9 `_correction_subqueries()` annotations
- [X] T016 [US1] Implement `GHFDBChildQuerySet.for_export()` in `project/ghfdb/managers.py`: call `self.as_ghfdb_flat()` and chain `prefetch_related(...)` for all 14 M2M paths: `method`, `sample__sample__explo_purpose`, `thermal_gradient__method_top`, `thermal_gradient__method_bottom`, `thermal_gradient__correction_top`, `thermal_gradient__correction_bottom`, `thermal_conductivity__source`, `thermal_conductivity__location`, `thermal_conductivity__method`, `thermal_conductivity__saturation`, `thermal_conductivity__pT_conditions`, `thermal_conductivity__pT_function`, `thermal_conductivity__strategy`, `sample__probe_metadata__probe_type`
- [X] T017 [US1] Implement `GHFDBChildManager(models.Manager)` in `project/ghfdb/managers.py`: override `get_queryset()` to return `GHFDBChildQuerySet(self.model, using=self._db)`, and add `as_ghfdb_flat()` and `for_export()` delegation methods
- [X] T018 [US1] Implement `GHFDBChild` proxy model in `project/ghfdb/models.py`: inherits `HeatFlow`, `objects = GHFDBChildManager()`, `class Meta: proxy = True; verbose_name = _("GHFDB Child"); verbose_name_plural = _("GHFDB Children")`; add class docstring citing Fuchs et al. (2021, 2023). **Note � registry exemption**: `GHFDBChild` is a proxy over `HeatFlow`, not a direct `Sample` or `Measurement` subclass. FairDM registry (`@fairdm.register`) applies only to direct `Sample`/`Measurement` subtypes that need auto-generated views/tables/filters; this proxy is intentionally admin-only and does not require registry registration. **Also**: add a minimal smoke test to `tests/test_ghfdb/test_models.py`: `from project.ghfdb.models import GHFDBChild` / `assert GHFDBChild._meta.proxy is True` / `assert GHFDBChild._meta.verbose_name == "GHFDB Child"`.
- [X] T019 ⚠️ Reopened [US1] Update `project/ghfdb/admin.py` `GHFDBChildAdmin(ImportExportMixin, admin.ModelAdmin)`: keep `get_queryset()` returning `GHFDBChild.objects.as_ghfdb_flat()`. Attach `GHFDBChildImportResource` and `GHFDBExportResource` exclusively to this admin (FR-011b), set `list_display` to the 2026-04-22 updated child-level order (~~`local_id`~~ [removed] `ghfdb_id`, `ID_parent`, `name`, `lat_NS`, `long_EW`, `qc`, `qc_uncertainty`, `q_method`, `q_top`, `q_bottom`, `probe_penetration`, `publication_reference`, `data_reference`, `relevant_child`, `c_comment`, `corr_IS_flag`, `corr_T_flag`, `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag`, `expedition`, `probe_type`, `probe_length`, `probe_tilt`, `water_temperature`, `geo_lithology`, `geo_stratigraphy`, `T_grad_mean`, `T_grad_uncertainty`, `T_grad_mean_cor`, `T_grad_uncertainty_cor`, `T_method_top`, `T_method_bottom`, `T_shutin_top`, `T_shutin_bottom`, `T_corr_top`, `T_corr_bottom`, `T_number`, `q_date`, `tc_mean`, `tc_uncertainty`, `tc_source`, `tc_location`, `tc_method`, `tc_saturation`, `tc_pT_conditions`, `tc_pT_fuction`, `tc_number`, `tc_strategy`, `quality`, `Ref_ISGN`), use vocabulary-scoped custom `SimpleListFilter` classes for `environment`, `explo_method`, and `explo_purpose` in `list_filter` (BUG-004), keep `list_display_links = None` for read-only, and wrap user-facing strings in `_()` (reopened — BUG-003, reopened — BUG-004; `list_display` updated 2026-04-22)
- [X] T064 ⚠️ Reopened [US1] Implement constrained admin list filter classes (`SimpleListFilter`) for all concept-backed fields in `project/ghfdb/admin.py`: `ExplorePurposeListFilter` scoped to `ExplorationPurpose` (BUG-001), plus `EnvironmentListFilter` scoped to `GeographicEnvironment` and `ChildExplorationMethodListFilter` scoped to `ExplorationMethod` for the child admin (reopened — BUG-004)
- [X] T079 [US1] Extend `project/ghfdb/managers.py` `GHFDBChildQuerySet.as_ghfdb_flat()` (and any supporting admin helpers) so the BUG-002 child-admin columns are available efficiently for changelist rendering, including child identifiers, child heat-flow values, references, probe metadata, gradient fields, conductivity fields, and `Ref_ISGN`

### System Validation � Phase 3

- [X] T020 ?? CRITICAL: Run Django system checks: `poetry run python manage.py check` � MUST pass before proceeding
- [X] T021 ⚠️ Reopened CRITICAL: Re-run User Story 1 tests after admin refinement: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v` — ALL tests MUST pass including the BUG-002 child-admin column-order assertions and BUG-003 changelist queryset evaluation checks (reopened — BUG-003)

- [X] T080 [P] [US1] Add regression test in `tests/test_ghfdb/test_admin.py` that forces `GHFDBChildAdmin.get_queryset()` evaluation and asserts no invalid `prefetch_related()` relation-path error is raised (BUG-003)
- [X] T081 [US1] Remove invalid child-admin queryset optimization paths in `project/ghfdb/admin.py` (notably `publication_references`/`data_references` when absent on `HeatFlow`) and keep only valid ORM relations (BUG-003)
- [X] T082 ⚠️ CRITICAL [US1] Re-run `poetry run pytest tests/test_ghfdb/test_admin.py -v` after BUG-003 fix and confirm child changelist responds HTTP 200 without queryset relation-path failures
- [X] T065 ⚠️ Reopened CRITICAL [US1] Re-run `poetry run pytest tests/test_ghfdb/test_admin.py -v` and confirm all concept-backed filter choices (`environment`, `explo_method`, `explo_purpose`) are vocabulary-scoped before closing BUG-001 and BUG-004 (reopened — BUG-004)

- [X] T083 [US1] Add `EnvironmentListFilter(SimpleListFilter)` in `project/ghfdb/admin.py` scoped to `GeographicEnvironment` vocabulary, filtering via `sample__heatflowinterval__sample__heatflowsite__environment` (BUG-004)
- [X] T084 [US1] Add `ChildExplorationMethodListFilter(SimpleListFilter)` in `project/ghfdb/admin.py` scoped to `ExplorationMethod` vocabulary, filtering via `sample__heatflowinterval__sample__heatflowsite__explo_method` (BUG-004)
- [X] T085 [US1] Replace raw `environment` and `explo_method` string paths in `GHFDBChildAdmin.list_filter` with `EnvironmentListFilter` and `ChildExplorationMethodListFilter` (BUG-004)
- [X] T086 [US1] Fix `GHFDBChildAdmin._interval()` fallback: change `getattr(sample, "heatflowinterval", sample)` to `getattr(sample, "heatflowinterval", None)` so callers receive `None` instead of a wrong-type `Sample` object (BUG-004, FR-015b)
- [X] T087 [US1] Add `ParentEnvironmentListFilter(SimpleListFilter)` in `project/ghfdb/admin.py` scoped to `GeographicEnvironment` vocabulary, filtering via `sample__heatflowsite__environment` (BUG-004)
- [X] T088 [US1] Add `ParentExplorationMethodListFilter(SimpleListFilter)` in `project/ghfdb/admin.py` scoped to `ExplorationMethod` vocabulary, filtering via `sample__heatflowsite__explo_method` (BUG-004)
- [X] T089 [US1] Replace raw `environment` and `explo_method` string paths in `GHFDBParentAdmin.list_filter` with `ParentEnvironmentListFilter` and `ParentExplorationMethodListFilter` (BUG-004)
- [X] T090 [P] [US1] Add regression tests in `tests/test_ghfdb/test_admin.py`: `test_environment_filter_choices_are_vocabulary_scoped`, `test_explo_method_filter_choices_are_vocabulary_scoped`, `test_parent_environment_filter_choices_are_vocabulary_scoped`, `test_parent_explo_method_filter_choices_are_vocabulary_scoped` — each asserts filter `lookups()` returns exactly the vocabulary-defined choices (BUG-004)
- [X] T091 ⚠️ CRITICAL [US1] Re-run `poetry run pytest tests/test_ghfdb/test_admin.py -v` after BUG-004 fixes and confirm all 11 tests pass including the 4 new vocabulary-scope tests

**Checkpoint — US1 Complete**: Child proxy model queryable, all scalar annotations verified, correction flags present, child-admin list view renders with the BUG-002 child-oriented column order, search/filter controls, all concept-backed filters vocabulary-scoped (BUG-001, BUG-004), `_interval()` returns `None` on missing MTI (BUG-004), query counts confirmed constant. `GHFDBChildImportResource` + `GHFDBExportResource` attached to this admin only.

---

## Phase 3b: User Story 1b — GHFDBParent Proxy Model (Priority: P1) ✨ NEW

**Goal**: A `GHFDBParent` proxy model over `ParentHeatFlow` with a `GHFDBParentQuerySet` that supports parent-level queries with `with_child_counts()` (annotates `total_children` and `relevant_children`) and `with_children()` (prefetches linked child records). Registered as a read-only Django admin view labelled "GHFDB Parents" with parent-level spreadsheet column order plus computed child-count columns. `GHFDBParentImportResource` attached to this admin only.

**Depends on**: Phase 2 (HeatFlow.local_id)
**Independent Test**: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v`

### Tests for User Story 1b ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T066 [P] [US1b] Write query-count test: assert `GHFDBParent.objects.with_child_counts()` executes in a constant number of DB queries (no N+1) in `tests/test_ghfdb/test_managers.py`
- [X] T067 [P] [US1b] Write count-correctness test: given a `ParentHeatFlow` with N children, assert `total_children == N` and `relevant_children` matches expected threshold-filtered count in `tests/test_ghfdb/test_managers.py`
- [X] T068 [P] [US1b] Write `with_children()` test: assert parent records include prefetched child `HeatFlow` objects accessible without extra queries in `tests/test_ghfdb/test_managers.py`
- [X] T069 [P] [US1b] Write standard queryset operability test: assert `filter()`, `order_by()`, and `count()` work on `GHFDBParent.objects.all()` in `tests/test_ghfdb/test_managers.py`
- [X] T070 [P] [US1b] Write admin registration tests in `tests/test_ghfdb/test_admin.py`: assert `GHFDBParentAdmin` changelist HTTP 200, title "GHFDB Parents", exact ordered columns (~~`ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`, `total_children`, `relevant_children`~~ [superseded 2026-04-22] `ghfdb_id`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `p_comment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `quality`, `country`, `region`, `continent`, `domain`, `total_children`, `relevant_children`), search fields for `name` and `ID_parent`, same list filters as `GHFDBChildAdmin` including vocabulary-scoped `explo_purpose`
- [X] T071 [P] [US1b] Write admin import resource test: assert `GHFDBParentAdmin.get_import_resource_classes()` returns `[GHFDBParentImportResource]` only (not `GHFDBChildImportResource` or `GHFDBExportResource`) in `tests/test_ghfdb/test_admin.py`

### Implementation for User Story 1b

- [X] T072 [US1b] Implement `GHFDBParentQuerySet` in `project/ghfdb/managers.py`: add `with_child_counts()` method that annotates `total_children = Count("children")` (or equivalent FK reverse name) and `relevant_children = Count("children", filter=Q(...))` with an appropriate quality/relevance threshold; add `with_children()` method that calls `prefetch_related("children")` (or equivalent) to attach child `HeatFlow` records
- [X] T073 [US1b] Implement `GHFDBParentManager` in `project/ghfdb/managers.py`: override `get_queryset()` to return `GHFDBParentQuerySet(self.model, using=self._db)`, add `with_child_counts()` and `with_children()` delegation methods
- [X] T074 [US1b] Implement `GHFDBParent` proxy model in `project/ghfdb/models.py`: inherits `ParentHeatFlow`, `objects = GHFDBParentManager()`, `class Meta: proxy = True; verbose_name = _("GHFDB Parent"); verbose_name_plural = _("GHFDB Parents")`; add class docstring. Add smoke test to `tests/test_ghfdb/test_models.py`: `assert GHFDBParent._meta.proxy is True` / `assert GHFDBParent._meta.verbose_name == "GHFDB Parent"`
- [X] T075 [US1b] Implement `GHFDBParentAdmin(ImportExportMixin, admin.ModelAdmin)` in `project/ghfdb/admin.py`: register for `GHFDBParent`, `get_queryset()` returns `GHFDBParent.objects.with_child_counts()`, `list_display` = 2026-04-22 parent-level GHFDB column order (`ghfdb_id`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `p_comment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `quality`, `country`, `region`, `continent`, `domain`) + `total_children` + `relevant_children` as computed columns (~~`search_fields` for `name` and `local_id`~~ [superseded] `search_fields` for `name` and `ghfdb_id`), `list_filter` same set as `GHFDBChildAdmin` (including `ExplorePurposeListFilter`), `list_display_links = None`, read-only permissions. Attach `GHFDBParentImportResource` exclusively (FR-011b) — no export resource or child import resource.

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

- [X] T059 [P] Update `docs/ghfdb_fields.md` to ~~document `HeatFlow.local_id` (type, constraints, purpose, GHFDB spreadsheet `ID` column)~~ [superseded 2026-04-22 — `local_id` removed; document `HeatFlow.ghfdb_id` (PositiveIntegerField, nullable, indexed, stable GHFDB row identifier) and `HeatFlow.quality` (CharField, nullable, composite quality string per Fuchs et al. 2023) instead] and add a "Proxy Model Access Patterns" section citing key annotation names from the `data-model.md` mapping table
- [X] T078 [P] Update `docs/ghfdb_fields.md` to document the `GHFDBParent` proxy model, its queryset methods (`with_child_counts()`, `with_children()`), admin registration, and the ~~`ParentHeatFlow.local_id`~~ [superseded 2026-04-22] `ParentHeatFlow.ghfdb_id` and `ParentHeatFlow.quality` fields

### System Validation — Final

- [X] T061 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass
- [x] T061a ⚠️ CRITICAL: Run final type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors
- [X] T061b ⚠️ CRITICAL: Run final linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations
- [X] T062 ⚠️ Reopened CRITICAL: Run full GHFDB proxy model test suite: `poetry run pytest tests/test_ghfdb/ -v` — ALL test modules MUST pass (including new GHFDBParent tests) (reopened — BUG-002)

**Checkpoint — Feature Complete**: System checks pass, all GHFDB proxy model + admin + views tests green (both GHFDBChild and GHFDBParent), `ghfdb_fields.md` updated.

---

## Phase 8: Data Model Update — `ghfdb_id` / `quality` Alignment (2026-04-22)

**Purpose**: Apply spec.md 2026-04-22 refinement in code. The underlying models already have `ghfdb_id` and `quality` (from `001-heat-flow-data-model` branch); this phase updates managers, admin column lists, tests, and documentation to match.

**Depends on**: All previous phases (code already exists)
**Independent Test**: `poetry run pytest tests/test_ghfdb/ -v`

### FR-001b — Manager Default Queryset Scoping

- [X] T092 [US1] Update `GHFDBChildManager.get_queryset()` in `project/ghfdb/managers.py` to filter `ghfdb_id__isnull=False` so only published GHFDB child records are returned by default (FR-001b)
- [X] T093 [US1b] Update `GHFDBParentManager.get_queryset()` in `project/ghfdb/managers.py` to filter `ghfdb_id__isnull=False` so only published GHFDB parent records are returned by default (FR-001b)
- [X] T094 [P] Add tests in `tests/test_ghfdb/test_managers.py`: assert `GHFDBChild.objects.count()` excludes records where `ghfdb_id` is null; assert `GHFDBParent.objects.count()` excludes records where `ghfdb_id` is null

### Child Admin Column Update

- [X] T095 [US1] Update `GHFDBChildAdmin.list_display` in `project/ghfdb/admin.py`: replace leading ~~`local_id`~~ with `ghfdb_id`; append `quality` before `Ref_ISGN` (FR-012, 2026-04-22 order)
- [X] T096 [P] Update test T013 assertion in `tests/test_ghfdb/test_admin.py`: replace `local_id` with `ghfdb_id` as first display column and add `quality` before `Ref_ISGN` in the expected `list_display` tuple

### Parent Admin Column Update

- [X] T097 [US1b] Update `GHFDBParentAdmin.list_display` in `project/ghfdb/admin.py` to the 2026-04-22 column order: `ghfdb_id`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `p_comment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `quality`, `country`, `region`, `continent`, `domain`, `total_children`, `relevant_children`; update `search_fields` from ~~`local_id`~~ to `ghfdb_id` (FR-012b, 2026-04-22)
- [X] T098 [P] Update test T070 assertion in `tests/test_ghfdb/test_admin.py`: replace old parent column order with new 2026-04-22 order (see FR-012b in spec.md)
- [X] T099 [P] Add display method `ghfdb_id` (and `p_comment`, `quality` if not already present) to `GHFDBParentAdmin` in `project/ghfdb/admin.py` so they resolve from `ParentHeatFlow` fields correctly

### System Validation — Phase 8

- [X] T100 ⚠️ CRITICAL: Run `poetry run python manage.py check` — MUST pass
- [X] T101 ⚠️ CRITICAL: Run full test suite: `poetry run pytest tests/test_ghfdb/ -v` — ALL tests MUST pass with updated column assertions
- [X] T102 [P] Update `docs/ghfdb_fields.md` to replace ~~`local_id` / `is_ghfdb`~~ references with `ghfdb_id` and `quality` for both `HeatFlow` and `ParentHeatFlow`

**Checkpoint — Phase 8 Complete**: Both manager default querysets scope to `ghfdb_id__isnull=False`; child and parent admin `list_display` match spec FR-012/FR-012b 2026-04-22 column order; all existing tests updated and passing; docs reflect model changes.

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends on | Blocks |
|---|---|---|
| Phase 1 � Setup | Nothing | Nothing |
| ~~Phase 2 — Foundational (`HeatFlow.local_id`)~~ [SUPERSEDED] | Phase 1 | ~~Phase 3, Phase 3b, Phase 6~~ (unblocked; migration done via `001` branch) |
| Phase 3 — US1 GHFDBChild Proxy (P1) | Phase 1 | `003-ghfdb-import-export` Phase 5 (US3 export needs `for_export()`) |
| Phase 3b — US1b GHFDBParent Proxy (P1) | Phase 1 | `003-ghfdb-import-export` (parent import resource needs `GHFDBParent` admin) |
| Phase 6 — US4 Map Viewer (P3) | Phase 1 | Nothing (independent) |
| Phase 7 — Polish | Phase 3 + Phase 3b + Phase 6 | Nothing |
| Phase 8 — `ghfdb_id`/`quality` Alignment (2026-04-22) | Phase 3 + Phase 3b | `003-ghfdb-import-export` (upsert key change to `ghfdb_id`) |
