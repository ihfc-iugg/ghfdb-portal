# Tasks: GHFDB Product Layer

**Feature**: 002-ghfdb-product-utilities
**Branch**: `002-ghfdb-product-utilities`
**Input**: plan.md, spec.md, data-model.md, research.md, contracts/import-contract.md, contracts/export-contract.md, quickstart.md
**Generated**: 2026-04-13 (replanned — resources/ package architecture)
**Propagated**: 2026-04-14 — Updated from spec.md refinement
**Bugfix**: 2026-04-14 — [BUG-001] Reopened admin filter tasks and added vocabulary-scoping tasks for `explo_purpose` list-filter choices.
**Bugfix**: 2026-04-14 — [BUG-002] Reopened admin import integration tasks and added import-page regression coverage for django-import-export hook compatibility.
**Bugfix**: 2026-04-14 — [BUG-003] Reopened import upsert tasks and added template-aware natural-key coverage for standard uploads without `ID` / `ID_parent`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no dependency on an incomplete task)
- **[US1/2/3/4]**: Mapped user story
- All tasks include an exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the new test package and directory structure before all implementation begins.

- [X] T001 Create `tests/test_ghfdb/` package with `__init__.py` and empty placeholder files: `test_models.py`, `test_managers.py`, `test_import.py`, `test_export.py`, `test_admin.py`, `test_views.py` in `tests/test_ghfdb/`
- [X] T002 Create `tests/test_ghfdb/conftest.py` with a `heat_flow_chain` pytest fixture that builds a complete record chain: `HeatFlowSite` → `HeatFlowInterval` (with `ProbeMetadata`) → `ParentHeatFlow` → `HeatFlow` (linked to `ThermalGradient`, `IntervalConductivity`, and `HeatFlowCorrection` instances for all 9 correction types); include a `sample_ghfdb_row` fixture with a minimal valid dict of GHFDB flat-column values

### System Validation — Phase 1

- [X] T003 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding to Phase 2

**Checkpoint — Setup Complete**: Package structure exists and system checks pass.

---

## Phase 2: Foundational (Blocking Prerequisite — `HeatFlow.local_id`)

**Purpose**: Add the `local_id` field to `HeatFlow` and generate its migration. US2 import upsert and all import tests depend on this field; it must be migrated before any user story work begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete and the migration is verified.

- [X] T004 Add `local_id = models.CharField(max_length=255, null=True, blank=True, db_index=True, help_text=_("GHFDB spreadsheet ID column — used as the stable key for import upsert"))` to the `HeatFlow` model
- [X] T005 Generate migration: run `poetry run python manage.py makemigrations heat_flow` and verify the resulting file in `project/heat_flow/migrations/` adds only a nullable `local_id` varchar column with a `db_index`

### System Validation — Phase 2

- [X] T006 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [X] T007 ⚠️ CRITICAL: Apply migration and verify: `poetry run python manage.py migrate` — MUST succeed cleanly before proceeding to any user story

**Checkpoint — Foundation Ready**: `HeatFlow.local_id` exists in the database. All user story phases can now begin.

---

## Phase 3: User Story 1 — GHFDB Proxy Model (Priority: P1) 🎯 MVP

**Goal**: A `GHFDB` proxy model over `HeatFlow` with a `GHFDBQuerySet` returning all **40 scalar + correction-flag columns** via `as_ghfdb_flat()` (31 `F()`-annotated scalars + 9 correction-flag subqueries; ≤2 DB queries, constant) and the full **65 GHFDB columns** (the 40 above plus 14 M2M fields, plus remaining scalars) via `for_export()` (~16 queries, constant), registered as a read-only Django admin view labelled "GHFDB Entries" with exact parent-level changelist column order plus required search and filter fields.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v`

### Tests for User Story 1 ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T008 [P] [US1] Write query-count test: assert `GHFDB.objects.as_ghfdb_flat()` executes ≤2 DB queries using `django_assert_max_num_queries(2)` with the `heat_flow_chain` fixture in `tests/test_ghfdb/test_managers.py`
- [X] T009 [P] [US1] Write scalar-column completeness test: assert all 31 select_related annotations (`site_name`, `lat_ns`, `long_ew`, `p_q`, `p_q_uncertainty`, `interval_top`, `interval_bottom`, `tgrad_value`, `tc_value`, `probe_penetration`, etc.) are accessible as attributes on records from `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [X] T010 [P] [US1] Write correction-flags test: assert all 9 `corr_*_flag` annotations (`corr_IS_flag`, `corr_T_flag`, `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag`) are accessible as attributes on records from `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [X] T011 [P] [US1] Write `for_export()` query-count test: assert `GHFDB.objects.for_export()` executes ≤16 DB queries using `django_assert_max_num_queries(16)` in `tests/test_ghfdb/test_managers.py`
- [X] T012 [P] [US1] Write standard queryset operability test: assert `filter()`, `order_by()`, and `count()` work without error on the queryset returned by `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [X] T013 ⚠️ Reopened [P] [US1] Refine admin registration tests in `tests/test_ghfdb/test_admin.py`: assert changelist HTTP 200, title "GHFDB Entries", exact ordered parent-level columns (`ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`), search fields for `name` and `ID_parent`, and list filters for `environment`, `corr_HP_flag`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain` (reopened — BUG-001)
- [X] T063 [P] [US1] Add a failing regression test in `tests/test_ghfdb/test_admin.py` verifying that `explo_purpose` list-filter choices are restricted to values accepted by `HeatFlowSite.explo_purpose` and exclude unrelated generic `Concept` values

### Implementation for User Story 1

- [X] T014 [US1] Extend existing `project/ghfdb/managers.py` and implement `_correction_subqueries()` helper: iterates `HeatFlowCorrection.CorrectionTypeChoices.choices`, returns a dict of 9 correlated `Subquery` annotations keyed as `corr_{type}_flag`, each selecting `HeatFlowCorrection.status` filtered by `heat_flow=OuterRef("pk")` and `correction_type=choice_value`
- [X] T015 [US1] Implement `GHFDBQuerySet.as_ghfdb_flat()` in `project/ghfdb/managers.py`: chain `select_related(...)` for paths `sample__sample`, `sample__sample__location`, `parent`, `thermal_gradient`, `thermal_conductivity`, `sample__probe_metadata`; then `annotate(...)` with `F()` expressions for all 31 scalar columns per the data-model.md mapping table; then merge the 9 `_correction_subqueries()` annotations
- [X] T016 [US1] Implement `GHFDBQuerySet.for_export()` in `project/ghfdb/managers.py`: call `self.as_ghfdb_flat()` and chain `prefetch_related(...)` for all 14 M2M paths: `method`, `sample__sample__explo_purpose`, `thermal_gradient__method_top`, `thermal_gradient__method_bottom`, `thermal_gradient__correction_top`, `thermal_gradient__correction_bottom`, `thermal_conductivity__source`, `thermal_conductivity__location`, `thermal_conductivity__method`, `thermal_conductivity__saturation`, `thermal_conductivity__pT_conditions`, `thermal_conductivity__pT_function`, `thermal_conductivity__strategy`, `sample__probe_metadata__probe_type`
- [X] T017 [US1] Implement `GHFDBManager(models.Manager)` in `project/ghfdb/managers.py`: override `get_queryset()` to return `GHFDBQuerySet(self.model, using=self._db)`, and add `as_ghfdb_flat()` and `for_export()` delegation methods
- [X] T018 [US1] Implement `GHFDB` proxy model in `project/ghfdb/models.py`: inherits `HeatFlow`, `objects = GHFDBManager()`, `class Meta: proxy = True; verbose_name = _("GHFDB Entry"); verbose_name_plural = _("GHFDB Entries")`; add class docstring citing Fuchs et al. (2021, 2023). **Note — registry exemption**: `GHFDB` is a proxy over `HeatFlow`, not a direct `Sample` or `Measurement` subclass. FairDM registry (`@fairdm.register`) applies only to direct `Sample`/`Measurement` subtypes that need auto-generated views/tables/filters; this proxy is intentionally admin-only and does not require registry registration. **Also**: add a minimal smoke test to `tests/test_ghfdb/test_models.py`: `from project.ghfdb.models import GHFDB` / `assert GHFDB._meta.proxy is True` / `assert GHFDB._meta.verbose_name == "GHFDB Entry"`.
- [X] T019 ⚠️ Reopened [US1] Update `project/ghfdb/admin.py` `GHFDBAdmin(admin.ModelAdmin)` for refined admin requirements: keep `get_queryset()` returning `GHFDB.objects.as_ghfdb_flat()`, set `list_display` to exact parent-level order (`ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`), configure `search_fields` for `name` and `ID_parent`, configure `list_filter` for `environment`, `corr_HP_flag`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`, keep `list_display_links = None` for read-only, and wrap user-facing strings in `_()` (reopened — BUG-001)
- [X] T064 [US1] Implement a constrained admin list filter class (e.g., `SimpleListFilter`) for `explo_purpose` in `project/ghfdb/admin.py` so filter lookups are vocabulary-scoped to `HeatFlowSite.explo_purpose`

### System Validation — Phase 3

- [X] T020 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [X] T021 ⚠️ Reopened CRITICAL: Re-run User Story 1 tests after admin refinement: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v` — ALL tests MUST pass including exact admin column-order/search/filter assertions (reopened — BUG-001)
- [X] T065 ⚠️ CRITICAL [US1] Re-run `poetry run pytest tests/test_ghfdb/test_admin.py -v` and confirm `explo_purpose` filter choices are vocabulary-scoped before closing BUG-001

**Checkpoint — US1 Complete**: Proxy model queryable, all scalar annotations verified, correction flags present, admin list view renders with exact refined column order plus required search/filter controls, and `explo_purpose` filter choices are vocabulary-scoped (BUG-001), query counts confirmed constant.

---

## Phase 3.5: Resources Package Setup (Prerequisite for US2 + US3)

**Purpose**: Create the `resources/` package skeleton and `test_resources/` test directory. The old monolithic `resources.py` is superseded by this split-package architecture. This must exist before any US2 or US3 tasks are started.

- [X] T022 Create `project/ghfdb/resources/` package: `__init__.py`, `_base.py`, `_widgets.py`, `parent.py`, `child.py`, `export.py` (all empty stubs with a module-level docstring)
- [X] T023 [P] Create `tests/test_ghfdb/test_resources/` directory with `__init__.py` and stub files: `test_widgets.py`, `test_parent_import.py`, `test_child_import.py`, `test_export.py`, `test_roundtrip.py`; copy/reuse the `heat_flow_chain` and `sample_ghfdb_row` fixtures from `tests/test_ghfdb/conftest.py` as needed via import; **also delete** orphaned top-level stubs `tests/test_ghfdb/test_import.py` and `tests/test_ghfdb/test_export.py` created by T001 (superseded by the `test_resources/` subdirectory)
- [X] T024 Implement `GHFDBImportFormat` (XLSX subclass: sheet `"data list"`, skip rows 1–5 and 7, use row 6 as headers, data rows from row 8), `GHFDB_COLUMN_ORDER` (all **62** GHFDB column names in canonical order, matching `ghfdb_colmeta.json`), `PARENT_COLUMNS` (18 parent-level column names), and `CORRECTION_COL_MAP` (`{"corr_IS_flag": "IS", …}` 9-entry dict) in `project/ghfdb/resources/_base.py`
- [X] T025 Verify `ParentHeatFlow.local_id` field exists (check `project/heat_flow/models/`); if absent, add `local_id = CharField(max_length=255, null=True, blank=True, db_index=True)` and generate migration; **also verify `HeatFlowSite.local_id` field exists** — FR-006 uses it as the stable upsert identifier for the parent record; if absent, add the same field definition to `HeatFlowSite`; if either field is new, generate a single combined migration: `poetry run python manage.py makemigrations heat_flow --name add_local_id_fields`

### System Validation — Phase 3.5

- [X] T026 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` -- MUST pass before proceeding to Phase 4
- [X] T026a ⚠️ CRITICAL: Run type checks: `poetry run mypy project/ghfdb/` -- MUST pass with no new errors (constitution §VI)
- [X] T026b ⚠️ CRITICAL: Run linting: `poetry run ruff check project/ghfdb/` -- MUST pass with zero violations (constitution §VI)

**Checkpoint — Resources Package Ready**: Stub modules created, `_base.py` constants in place, `ParentHeatFlow.local_id` verified.

---

## Phase 4: User Story 2 — Import GHFDB Spreadsheet (Priority: P2)

**Goal**: Staff can upload a GHFDB XLSX in the Django admin and select either the "GHFDB Parent" or "GHFDB Child" import resource to create/update `HeatFlowSite`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`, `HeatFlowCorrection`, and `ProbeMetadata` records with correct controlled-vocabulary mappings, upsert on `local_id`, and atomic rollback on any validation error.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_resources/test_widgets.py tests/test_ghfdb/test_resources/test_parent_import.py tests/test_ghfdb/test_resources/test_child_import.py -v`

### Tests for User Story 2 ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T027 [P] [US2] Write failing leaf-widget tests in `tests/test_ghfdb/test_resources/test_widgets.py`: `ConceptWidget.clean()` case-insensitive lookup + invalid-value `ValueError` listing valid options; `MultiConceptWidget.clean()` semicolon split + batched error for multiple invalid values; `QuantityWidget.clean()` returns `Quantity`, `.render()` returns plain magnitude; `YesNoWidget.clean()` maps `"Yes"`→`True`, `"No"`→`False`, empty→`None`
- [X] T028 [P] [US2] Write failing `RelatedModelWidget` and subclass tests in `tests/test_ghfdb/test_resources/test_widgets.py`: sentinel-column check skips instance creation when column is empty; `full_clean()` raises `ValueError` prefixed with model name; `set_m2m_relations()` sets correct M2M; `ParentWidget` creates `HeatFlowSite` + `Point` from lat/long columns; `IntervalWidget` creates `HeatFlowInterval`; `GradientWidget` skips when `T_grad_mean` is empty; `ConductivityWidget` skips when `tc_mean` is empty
- [ ] T029 ⚠️ Reopened [P] [US2] Write failing `GHFDBParentImportResource` tests in `tests/test_ghfdb/test_resources/test_parent_import.py`: upsert on `local_id` (re-import updates, does not duplicate); `before_import()` deduplication keeps first occurrence of each `ID_parent`; 18 parent columns mapped to correct fields; `ParentHeatFlow.sample` FK (to `HeatFlowSite`) created with correct `Point` location; `explo_purpose` M2M set; staff-only access control (anonymous admin import URL → 302); plus regression coverage for template rows without `ID_parent` using `lat_NS` + `long_EW` as natural upsert key (reopened — BUG-003)
- [ ] T030 ⚠️ Reopened [P] [US2] Write failing `GHFDBChildImportResource` tests in `tests/test_ghfdb/test_resources/test_child_import.py`: all 14 child field mappings; `parent` FK resolved via `ID_parent` `ForeignKeyWidget`; `after_save_instance()` creates 9 `HeatFlowCorrection` records with correct `correction_type` and `status`; `ProbeMetadata` created when probe columns are non-empty; `method` M2M set via `MultiConceptWidget`; `IntervalWidget`, `GradientWidget`, `ConductivityWidget` M2M set after save; plus regression coverage for template rows without `ID`/`ID_parent` using location + depth + `publication_reference` as child natural key (reopened — BUG-003)
- [X] T030a [US2] Write failing SC-005 schema-coverage test in `tests/test_ghfdb/test_resources/test_schema_coverage.py`: assert every column name in `GHFDB_COLUMN_ORDER` (from `_base.py`) appears as a declared `Field` in either `GHFDBParentImportResource` or `GHFDBChildImportResource` with no undocumented omissions; assert every column name also appears as a key in `ghfdb_colmeta.json`; assert `len(GHFDB_COLUMN_ORDER) == 62` (authoritative count from `ghfdb_colmeta.json`)
- [X] T066 [P] [US2] Add an authenticated admin regression test in `tests/test_ghfdb/test_resources/test_parent_import.py` asserting `GET /admin/ghfdb/ghfdb/import/` returns HTTP 200 for a staff user and renders the configured import resource options without a server error

### Implementation for User Story 2

- [X] T031 [US2] Implement leaf widgets (`ConceptWidget` — case-insensitive label lookup + cache; `MultiConceptWidget` — semicolon split + batch `ConceptWidget`; `QuantityWidget` — `Quantity(Decimal(value), unit)` ↔ `magnitude`; `YesNoWidget` — "Yes"/"No" ↔ `True`/`False`/`None`) in `project/ghfdb/resources/_widgets.py`; all user-facing error message strings MUST use `gettext_lazy()` (constitution §V — i18n compliance)
- [X] T032 [US2] Implement `RelatedModelWidget` base class in `project/ghfdb/resources/_widgets.py`: `__init__` accepts `model`, `field_map`, `m2m_map`, `sentinel_column`, `widget_map`; `clean()` checks sentinel → extracts + cleans scalars → `full_clean()` → `save()` → defers M2M; `set_m2m_relations(instance)` sets all M2M via widget `.clean()`; `full_clean()` `ValidationError` re-raised as `ValueError` prefixed with model name; `ValueError` prefix strings MUST use `gettext_lazy()` (constitution §V — i18n compliance)
- [X] T033 [US2] Implement `ParentWidget` in `project/ghfdb/resources/_widgets.py`: `RelatedModelWidget` for `HeatFlowSite` + `Point`, sentinel `"name"`, creates/updates `Point(x=long_EW, y=lat_NS)`, all scalar (`name`, `elevation`, `environment`, `explo_method`, `total_depth_MD`→`length`, `total_depth_TVD`→`vertical_depth`, `Country`, `Region`, `Continent`, `Domain`) and M2M (`explo_purpose`) mappings per `data-model.md`
- [X] T034 [US2] Implement `IntervalWidget` (sentinel `None`, `q_top`/`q_bottom` → `QuantityWidget("m")`, `geo_lithology`/`geo_stratigraphy` M2M), `GradientWidget` (sentinel `"T_grad_mean"`, 7 scalar + 4 M2M fields), and `ConductivityWidget` (sentinel `"tc_mean"`, 3 scalar + 7 M2M fields) in `project/ghfdb/resources/_widgets.py`
- [ ] T035 ⚠️ Reopened [US2] Implement `GHFDBParentImportResource` in `project/ghfdb/resources/parent.py`: 6 `Field` declarations (`local_id`, `value`, `uncertainty`, `comment`, `corr_HP_flag`, `sample`); `ParentWidget` instantiation; `before_import()` deduplication; `Meta` upsert strategy must be template-aware (`ID_parent` / `local_id` when present, otherwise `lat_NS` + `long_EW` for standard uploads) with transactional rollback preserved (reopened — BUG-003)
- [ ] T036 ⚠️ Reopened [US2] Implement `GHFDBChildImportResource` in `project/ghfdb/resources/child.py`: 14 `Field` declarations per `data-model.md`; widget instantiations (`IntervalWidget`, `GradientWidget`, `ConductivityWidget`, `ForeignKeyWidget(ParentHeatFlow, "local_id")`); `after_save_instance()` creating 9 `HeatFlowCorrection.objects.update_or_create()` calls via `CORRECTION_COL_MAP` + `ProbeMetadata.objects.update_or_create()` when probe columns are non-empty + `widget.set_m2m_relations()` for each `RelatedModelWidget` field; `Meta` upsert strategy must be template-aware (`ID` / `local_id` when present, otherwise `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`) with transactional rollback preserved (reopened — BUG-003)
- [X] T037 [US2] Update `project/ghfdb/resources/__init__.py` to publicly re-export `GHFDBParentImportResource`, `GHFDBChildImportResource`, `GHFDBExportResource`, `GHFDBImportFormat`
- [X] T038 ⚠️ Reopened [US2] Update `GHFDBAdmin` import integration in `project/ghfdb/admin.py`: keep `get_import_resource_classes()` returning `[GHFDBParentImportResource, GHFDBChildImportResource]` and `get_import_formats()` returning `[GHFDBImportFormat]`, but ensure all django-import-export admin hook overrides accept the request-aware method signatures required by the installed version so `/admin/ghfdb/ghfdb/import/` renders successfully (reopened — BUG-002)

### System Validation — Phase 4

- [X] T039 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [X] T039a ⚠️ CRITICAL: Run type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors (constitution §VI)
- [X] T039b ⚠️ CRITICAL: Run linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations (constitution §VI)
- [ ] T040 ⚠️ Reopened CRITICAL: Run User Story 2 tests: `poetry run pytest tests/test_ghfdb/test_resources/test_widgets.py tests/test_ghfdb/test_resources/test_parent_import.py tests/test_ghfdb/test_resources/test_child_import.py -v` — ALL tests MUST pass, including authenticated admin import-page rendering coverage for `/admin/ghfdb/ghfdb/import/` and template-without-ID regression coverage for parent and child natural-key upsert paths (reopened — BUG-002, BUG-003)

- [ ] T067 [P] [US2] Add regression tests in `tests/test_ghfdb/test_resources/test_parent_import.py` for standard upload rows without `ID_parent`: verify deduplication and re-import upsert via `lat_NS` + `long_EW`, and ensure no duplicate `ParentHeatFlow`/`HeatFlowSite` rows are created
- [ ] T068 [P] [US2] Add regression tests in `tests/test_ghfdb/test_resources/test_child_import.py` for standard upload rows without `ID`/`ID_parent`: verify re-import upsert via `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`, and verify different `publication_reference` values over the same site/depth interval remain distinct records
- [ ] T069 [US2] Update `project/ghfdb/resources/parent.py` to support template-aware parent upsert and deduplication (`ID_parent`/`local_id` when present; otherwise `lat_NS` + `long_EW`)
- [ ] T070 [US2] Update `project/ghfdb/resources/child.py` to support template-aware child upsert (`ID`/`local_id` when present; otherwise `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`) and ensure child matching does not collapse distinct references
- [ ] T071 ⚠️ CRITICAL [US2] Re-run `poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py tests/test_ghfdb/test_resources/test_child_import.py -v` and confirm both template-aware upsert paths pass before closing BUG-003

**Checkpoint — US2 Reopened (BUG-003)**: Parent and child import resources remain integrated in the admin UI and BUG-002 import-route compatibility is resolved, but US2 is not closed until template-aware upsert paths are implemented and validated for standard uploads without `ID` / `ID_parent` (T029, T030, T035, T036, T040, T067, T068, T069, T070, T071).

> **SC-003 Manual QA Gate** (not automated): Before marking this feature release-ready, manually import a 10,000-row GHFDB XLSX and confirm the complete error report is delivered within 60 seconds. The query-count guards (T008/T011) serve as the automated proxy.

---

## Phase 5: User Story 3 — Export Heat Flow Data to GHFDB Format (Priority: P2)

**Goal**: Staff can trigger an export from the Django admin that produces a valid GHFDB-format XLSX with all **62** columns in the canonical order, semicolons for M2M fields, and plain SI numeric values for Pint quantity fields.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_resources/test_export.py -v`

### Tests for User Story 3 ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T041 [P] [US3] Write failing tests in `tests/test_ghfdb/test_resources/test_export.py`: column set matches all **62** entries in `GHFDB_COLUMN_ORDER`; column order is identical to `GHFDB_COLUMN_ORDER`; Pint quantity field (`q`, `tc_mean`, etc.) renders as plain numeric magnitude (no unit symbol); M2M field (`q_method`, `tc_method`) renders as semicolon-separated labels; `get_queryset()` returns `GHFDB.objects.for_export()`; filtered queryset only exports matching records; staff-only access (anonymous admin export URL → 302)

### Implementation for User Story 3

- [X] T042 [US3] Implement `GHFDBExportResource` class scaffold in `project/ghfdb/resources/export.py`: `Meta` class (`model = GHFDB`, `export_order = GHFDB_COLUMN_ORDER` tuple imported from `_base.py`), `get_queryset()` returning `GHFDB.objects.for_export()`, all **62** explicit `Field` declarations with `attribute` pointing to annotation names from the `data-model.md` mapping table
- [X] T043 [US3] Implement `dehydrate_*` methods for all Pint quantity fields in `project/ghfdb/resources/export.py` (e.g. `dehydrate_q`, `dehydrate_q_uncertainty`, `dehydrate_tc_mean`, `dehydrate_tc_uncertainty`, `dehydrate_T_grad_mean`, `dehydrate_T_grad_uncertainty`, `dehydrate_T_grad_mean_cor`, etc.): `return obj.<annotation>.magnitude if obj.<annotation> else ""`
- [X] T044 [US3] Implement `dehydrate_*` methods for all M2M fields in `project/ghfdb/resources/export.py` (e.g. `dehydrate_q_method`, `dehydrate_explo_purpose`, `dehydrate_T_method_top`, `dehydrate_T_corr_top`, `dehydrate_tc_source`, etc.): `return "; ".join(c.label for c in obj.<prefetch_name>.all()) if ... else ""`; add `None`-guard on all dehydrate methods to return `""` not `"None"`
- [X] T045 [US3] Update `GHFDBAdmin.get_export_resource_classes()` to return `[GHFDBExportResource]` and `get_export_formats()` to return `[XLSX]` in `project/ghfdb/admin.py`

### System Validation — Phase 5

- [X] T046 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [X] T046a ⚠️ CRITICAL: Run type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors (constitution §VI)
- [X] T046b ⚠️ CRITICAL: Run linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations (constitution §VI)
- [X] T047 ⚠️ CRITICAL: Run User Story 3 tests: `poetry run pytest tests/test_ghfdb/test_resources/test_export.py -v` — ALL tests MUST pass

**Checkpoint — US3 Complete**: Export produces a valid GHFDB XLSX with correct **62**-column layout, correct order, M2M semicolon-joined, Pint values as plain numerics.

---

## Phase 6: User Story 4 — Web Map Viewer Page (Priority: P3)

**Goal**: The existing `GHFDBExploreView` and `explore.html` are enhanced with a graceful `onerror` fallback for unreachable iframes; the "Explore" menu item and URL routing are verified correct.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_views.py -v`

### Tests for User Story 4 ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T048 [P] [US4] Write failing test: anonymous `GET /ghfdb/explore/` returns HTTP 200 and response body contains `<iframe>` with `src="https://ihfc-iugg.github.io/HeatFlowMapping/"` in `tests/test_ghfdb/test_views.py`
- [X] T049 [P] [US4] Write failing test: rendered `explore.html` template source contains a visible fallback element (e.g. `class="explore-fallback"` or `id="map-error"`) for the unreachable-URL case in `tests/test_ghfdb/test_views.py`
- [X] T050 [P] [US4] Write no-auth test: map page returns HTTP 200 for an unauthenticated request (no redirect to login) in `tests/test_ghfdb/test_views.py`

### Implementation for User Story 4

- [X] T051 [US4] Update `project/ghfdb/templates/ghfdb/explore.html`: full-viewport iframe (`width="100%"`, `height="100vh"`, `style="border:none"`) embedding `https://ihfc-iugg.github.io/HeatFlowMapping/`; add `onerror="this.style.display='none'; document.getElementById('map-error').style.display='block';"` attribute and a `<div id="map-error" class="explore-fallback" style="display:none">` fallback message explaining the map is temporarily unavailable
- [X] T052 [US4] Verify `GHFDBExploreView` in `project/ghfdb/views.py` has no `LoginRequiredMixin` and uses template `"ghfdb/explore.html"`; confirm URL pattern in `project/ghfdb/urls.py` resolves as `name="explore"` (or `ghfdb-explore`)
- [X] T053 [US4] Verify the "Explore" `MenuItem` (in `project/heat_flow/menus.py` or `project/ghfdb/apps.py` — check FairDM nav registration pattern) points to the correct URL name and is configured to mark itself active when on the map page

### System Validation — Phase 6

- [X] T054 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [x] T054a ⚠️ CRITICAL: Run type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors (constitution §VI)
- [X] T054b ⚠️ CRITICAL: Run linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations (constitution §VI)
- [X] T055 ⚠️ CRITICAL: Run User Story 4 tests: `poetry run pytest tests/test_ghfdb/test_views.py -v` — ALL tests MUST pass

**Checkpoint — US4 Complete**: Map page accessible without auth, iframe present with `onerror` fallback, Explore menu item active.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Round-trip regression test (SC-001), retire legacy `resources.py`, citation compliance, and final full-suite validation.

- [X] T056 Create fixture GHFDB XLSX (`tests/test_ghfdb/fixtures/sample_ghfdb.xlsx`) with 3–5 rows covering: one parent with `explo_purpose` M2M; one child with all 9 correction flags; one child with `ThermalGradient` + `IntervalConductivity` including M2M method fields; quantity fields in SI units
- [X] T057 [P] Write round-trip regression test (SC-001) in `tests/test_ghfdb/test_resources/test_roundtrip.py`: (1) import `sample_ghfdb.xlsx` via `GHFDBParentImportResource` then `GHFDBChildImportResource`; (2) export via `GHFDBExportResource`; (3) assert exported text/vocabulary cells are identical and numeric cells differ by less than floating-point `1e-9`
- [X] T058 Retire legacy `project/ghfdb/resources.py`: first verify no remaining code imports from it (`grep -r "from .resources import\|from project.ghfdb.resources import" project/ --include="*.py"`); then delete (or rename to `_resources_legacy.py.bak`)
- [X] T059 [P] Update `docs/ghfdb_fields.md` to document `HeatFlow.local_id` (type, constraints, purpose, GHFDB spreadsheet `ID` column) and add a "Proxy Model Access Patterns" section citing key annotation names from the `data-model.md` mapping table
- [X] T059a [P] Document the large-export row limit in `docs/ghfdb_fields.md` and in the `GHFDBExportResource` class docstring: state the tested synchronous row limit (e.g. 50,000 rows), note that `get_queryset()` MUST use `.iterator()` to avoid loading the full queryset into memory, and document that exports exceeding the limit should be moved to a background task (deferred to a future spec)
- [X] T060 [P] Add Fuchs et al. (2021) and Fuchs et al. (2023) inline citations to `GHFDBParentImportResource`, `GHFDBChildImportResource`, and `GHFDBExportResource` class docstrings in their respective module files; **also** add a module-level docstring to `project/ghfdb/resources/_widgets.py` citing both references and summarising the widget hierarchy (leaf widgets → `RelatedModelWidget` → specialised sub-model widgets)

### System Validation — Final

- [X] T061 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass
- [x] T061a ⚠️ CRITICAL: Run final type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors (constitution §VI)
- [X] T061b ⚠️ CRITICAL: Run final linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations (constitution §VI)
- [X] T062 ⚠️ CRITICAL: Run full GHFDB test suite: `poetry run pytest tests/test_ghfdb/ -v` — ALL test modules MUST pass

**Checkpoint — Feature Complete**: System checks pass, all GHFDB tests green (proxy model + resources + views + round-trip), `ghfdb_fields.md` updated, legacy `resources.py` retired.

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends on | Blocks |
|---|---|---|
| Phase 1 — Setup | Nothing | Nothing |
| Phase 2 — Foundational (`HeatFlow.local_id`) | Phase 1 | ALL user stories |
| Phase 3 — US1 Proxy Model (P1) | Phase 2 | Phase 5 (US3 needs `for_export()`) |
| Phase 3.5 — Resources Package Setup | Phase 2 | Phase 4 (US2) and Phase 5 (US3) |
| Phase 4 — US2 Import (P2) | Phase 2 + Phase 3.5 | Phase 7 (round-trip) |
| Phase 5 — US3 Export (P2) | Phase 3 (US1) + Phase 3.5 | Phase 7 (round-trip) |
| Phase 6 — US4 Map Viewer (P3) | Phase 2 | Nothing (independent) |
| Phase 7 — Polish | Phases 3–6 | Nothing |

### User Story Dependencies

```
Phase 2 (Foundational)
  ├── Phase 3 (US1 Proxy Model) ──────────────────────────── Phase 5 (US3 Export)
  ├── Phase 3.5 (Resources Package) ──► Phase 4 (US2 Import) ──► Phase 7 round-trip
  │                                └──► Phase 5 (US3 Export)
  └── Phase 6 (US4 Map Viewer)   ── fully independent
```

### Within Each User Story

1. Write ALL story tests first; confirm they **FAIL**
2. Implement widgets / managers (data-layer)
3. Implement resources / views (service-layer)
4. Update admin registration (integration layer)
5. Run story tests — ALL must pass before the next story begins

### Parallel Opportunities

**Phase 3.5**: T022 ‖ T023 (different directories); T024 as soon as T022 is done
**Phase 3 (US1)**: T009 + T012 in parallel (`managers.py` ‖ `models.py`) after T008
**Phase 4 (US2)**: T027 ‖ T028 ‖ T029 ‖ T030 (different test files); T035 ‖ T036 (parent.py ‖ child.py) after T031–T034
**Phase 5 (US3)**: T041 (test) can be written while Phase 4 runs; T042 → T043 ‖ T044 in export.py
**Phase 6 (US4)**: T048 ‖ T049 ‖ T050 (tests); T051 ‖ T052 (template ‖ view)
**Phase 7**: T056 → T057 (fixture first); T058 ‖ T059 ‖ T060 (independent files)

---

## Parallel Example: User Story 2 (Phase 4)

```bash
# Step 1 — Write all four test files in parallel (after Phase 3.5 complete):
Task T027: test_widgets.py — leaf widget tests
Task T028: test_widgets.py — RelatedModelWidget tests  (add to same file)
Task T029: test_parent_import.py — GHFDBParentImportResource tests
Task T030: test_child_import.py — GHFDBChildImportResource tests

# Step 2 — Implement _widgets.py sequentially (same file):
T031 (leaf widgets) → T032 (RelatedModelWidget base) → T033 (ParentWidget) → T034 (Interval/Gradient/Conductivity)

# Step 3 — Implement resources in parallel (different files):
Task T035: parent.py — GHFDBParentImportResource
Task T036: child.py — GHFDBChildImportResource
```

---

## Implementation Strategy

### MVP First (User Stories 1 and 2 — bugfix follow-up)

US1 proxy and refined admin follow-up tasks were previously marked complete, and BUG-001 follow-up has been resolved (T013, T019, T021, T063, T064, T065). US2 import work was also previously marked complete, with BUG-002 route-compatibility follow-up resolved (T038, T066), but BUG-003 reopens template-aware upsert coverage and implementation tasks for standard uploads without `ID` / `ID_parent`.

**Next MVP**: Complete BUG-003 import upsert tasks for US2 (T029, T030, T035, T036, T040, T067, T068, T069, T070, T071), then revalidate parent/child import behavior before closing the feature.

### Recommended Delivery Order

1. ~~Phase 1 Setup~~ ✓ Complete
2. ~~Phase 2 Foundational~~ ✓ Complete
3. ~~Phase 3 US1 Proxy Model (BUG-001 follow-up)~~ ✓ Complete
4. **Phase 4 US2 Import (BUG-003 follow-up)**
5. ~~Phase 3.5 Resources Package~~ ✓ Complete
6. ~~Phase 5 US3 Export~~ ✓ Complete
7. ~~Phase 6 US4 Map Viewer~~ ✓ Complete
8. ~~Phase 7 Polish~~ ✓ Complete

### Parallel Team Strategy

With two developers, the remaining BUG-003 work can be split as follows:

- **Developer A**: T067 + T029 + T069 in `tests/test_ghfdb/test_resources/test_parent_import.py` and `project/ghfdb/resources/parent.py` for no-`ID_parent` natural-key coverage (`lat_NS` + `long_EW`) and dedup/upsert behavior
- **Developer B**: T068 + T030 + T070 in `tests/test_ghfdb/test_resources/test_child_import.py` and `project/ghfdb/resources/child.py` for child natural-key upsert (`lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`) and non-collapsing multi-reference behavior
- Both converge on T040 + T071 for final pytest revalidation

**Key risks**: location/depth matching must not collapse distinct references, and template-aware fallback matching must remain deterministic when `ID`/`ID_parent` are absent.

---

## Summary

| Phase | Tasks | User Story | Priority | Status |
|---|---|---|---|---|
| Phase 1 — Setup | T001–T003 | — | — | ✅ Complete |
| Phase 2 — Foundational | T004–T007 | — | — | ✅ Complete |
| Phase 3 — Proxy Model | T008–T021, T063–T065 | US1 | P1 🎯 | ✅ Complete (BUG-001 resolved) |
| Phase 3.5 — Resources Pkg | T022–T026, T026a–T026b | — | — | ✅ Complete |
| Phase 4 — Import | T027–T040, T030a, T039a–T039b, T066–T071 | US2 | P2 | 🔄 Reopened (BUG-003 in progress) |
| Phase 5 — Export | T041–T047, T046a–T046b | US3 | P2 | ✅ Complete |
| Phase 6 — Map Viewer | T048–T055, T054a–T054b | US4 | P3 | ✅ Complete |
| Phase 7 — Polish | T056–T062, T059a, T061a–T061b | — | — | ✅ Complete |
| **Total** | **71 numbered tasks (T001–T071)** + letter-suffixed validation tasks (`T026a`, `T026b`, `T039a`, `T039b`, `T046a`, `T046b`, `T054a`, `T054b`, `T059a`, `T061a`, `T061b`) | | | |

**Completed**: 61 of 71 numbered tasks.
**Remaining**: 10 numbered tasks — T029, T030, T035, T036, T040, T067, T068, T069, T070, T071 (BUG-003 follow-up).
**Tests**: 13 write-first test tasks (T027–T030, T030a, T041, T048–T050, T057), plus 4 bugfix regression tests (T063, T066, T067, T068).
**System-check tasks**: Reopened validation is captured by T040 and T071 for BUG-003 closure.

---

## Notes

- `[P]` = can be done in parallel with adjacent [P] tasks in different files
- `[Story]` label traces each task to its user story for independent delivery
- Tests MUST fail before implementation begins — this verifies test validity
- Do not delete legacy `project/ghfdb/resources.py` until T058 (after ALL features pass)
- Fixture XLSX `tests/test_ghfdb/fixtures/sample_ghfdb.xlsx` (T056) must be committed to the repository for reproducible CI
- Never modify `project/heat_flow/models/` beyond adding `local_id` fields — all import/export logic lives inside `project/ghfdb/resources/`
