# Tasks: GHFDB Product Layer

**Feature**: 002-ghfdb-product-utilities
**Branch**: `002-ghfdb-product-utilities`
**Input**: plan.md, spec.md, data-model.md, research.md, contracts/api-contracts.md
**Generated**: 2026-04-10

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no dependency on an incomplete task)
- **[US1/2/3/4]**: Mapped user story
- All tasks include an exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the new test package and directory structure before all implementation begins.

- [ ] T001 Create `tests/test_ghfdb/` package with `__init__.py` and empty placeholder files: `test_models.py`, `test_managers.py`, `test_import.py`, `test_export.py`, `test_admin.py`, `test_views.py` in `tests/test_ghfdb/`
- [ ] T002 Create `tests/test_ghfdb/conftest.py` with a `heat_flow_chain` pytest fixture that builds a complete record chain: `HeatFlowSite` → `HeatFlowInterval` (with `ProbeMetadata`) → `ParentHeatFlow` → `HeatFlow` (linked to `ThermalGradient`, `IntervalConductivity`, and `HeatFlowCorrection` instances for all 9 correction types); include a `sample_ghfdb_row` fixture with a minimal valid dict of GHFDB flat-column values

### System Validation — Phase 1

- [ ] T003 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding to Phase 2

**Checkpoint — Setup Complete**: Package structure exists and system checks pass.

---

## Phase 2: Foundational (Blocking Prerequisite — `HeatFlow.local_id`)

**Purpose**: Add the `local_id` field to `HeatFlow` and generate its migration. US2 import upsert and all import tests depend on this field; it must be migrated before any user story work begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete and the migration is verified.

- [ ] T004 Add `local_id = models.CharField(max_length=255, null=True, blank=True, db_index=True, help_text=_("GHFDB spreadsheet ID column — used as the stable key for import upsert"))` to the `HeatFlow` model in `project/heat_flow/models/child.py`; add a Fuchs et al. (2021) inline comment referencing the `ID` column in the GHFDB spreadsheet schema; **also** add a `local_id` row to the relevant section of `docs/ghfdb_fields.md` in the same commit (Constitution II: field mapping docs MUST be updated in the same PR as schema changes)
- [ ] T005 Generate migration: run `poetry run python manage.py makemigrations heat_flow` and verify the resulting file in `project/heat_flow/migrations/` adds only a nullable `local_id` varchar column with a `db_index`

### System Validation — Phase 2

- [ ] T006 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [ ] T007 ⚠️ CRITICAL: Apply migration and verify: `poetry run python manage.py migrate` — MUST succeed cleanly before proceeding to any user story

**Checkpoint — Foundation Ready**: `HeatFlow.local_id` exists in the database. All user story phases can now begin.

---

## Phase 3: User Story 1 — GHFDB Proxy Model (Priority: P1) 🎯 MVP

**Goal**: A `GHFDB` proxy model over `HeatFlow` with a `GHFDBQuerySet` returning all **40 scalar + correction-flag columns** via `as_ghfdb_flat()` (31 `F()`-annotated scalars + 9 correction-flag subqueries; ≤2 DB queries, constant) and the full **65 GHFDB columns** (the 40 above plus 14 M2M fields, plus remaining scalars) via `for_export()` (~16 queries, constant), registered as a read-only Django admin view labelled "GHFDB Entries".

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v`

### Tests for User Story 1 ⚠️ Write FIRST — verify they FAIL before implementing

- [ ] T008 [P] [US1] Write query-count test: assert `GHFDB.objects.as_ghfdb_flat()` executes ≤2 DB queries using `django_assert_max_num_queries(2)` with the `heat_flow_chain` fixture in `tests/test_ghfdb/test_managers.py`
- [ ] T009 [P] [US1] Write scalar-column completeness test: assert all 31 select_related annotations (`site_name`, `lat_ns`, `long_ew`, `p_q`, `p_q_uncertainty`, `interval_top`, `interval_bottom`, `tgrad_value`, `tc_value`, `probe_penetration`, etc.) are accessible as attributes on records from `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [ ] T010 [P] [US1] Write correction-flags test: assert all 9 `corr_*_flag` annotations (`corr_IS_flag`, `corr_T_flag`, `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag`) are accessible as attributes on records from `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [ ] T011 [P] [US1] Write `for_export()` query-count test: assert `GHFDB.objects.for_export()` executes ≤16 DB queries using `django_assert_max_num_queries(16)` in `tests/test_ghfdb/test_managers.py`
- [ ] T012 [P] [US1] Write standard queryset operability test: assert `filter()`, `order_by()`, and `count()` work without error on the queryset returned by `as_ghfdb_flat()` in `tests/test_ghfdb/test_managers.py`
- [ ] T013 [P] [US1] Write admin registration test: assert a GET to the `GHFDB` admin changelist returns HTTP 200, the page title contains "GHFDB Entries", and all displayed columns are readable without a `FieldError` in `tests/test_ghfdb/test_admin.py`

### Implementation for User Story 1

- [ ] T014 [US1] Create `project/ghfdb/managers.py` and implement `_correction_subqueries()` helper: iterates `HeatFlowCorrection.CorrectionTypeChoices.choices`, returns a dict of 9 correlated `Subquery` annotations keyed as `corr_{type}_flag`, each selecting `HeatFlowCorrection.status` filtered by `heat_flow=OuterRef("pk")` and `correction_type=choice_value`
- [ ] T015 [US1] Implement `GHFDBQuerySet.as_ghfdb_flat()` in `project/ghfdb/managers.py`: chain `select_related(...)` for paths `sample__sample`, `sample__sample__location`, `parent`, `thermal_gradient`, `thermal_conductivity`, `sample__probe_metadata`; then `annotate(...)` with `F()` expressions for all 31 scalar columns per the data-model.md mapping table; then merge the 9 `_correction_subqueries()` annotations
- [ ] T016 [US1] Implement `GHFDBQuerySet.for_export()` in `project/ghfdb/managers.py`: call `self.as_ghfdb_flat()` and chain `prefetch_related(...)` for all 14 M2M paths: `method`, `sample__sample__explo_purpose`, `thermal_gradient__method_top`, `thermal_gradient__method_bottom`, `thermal_gradient__correction_top`, `thermal_gradient__correction_bottom`, `thermal_conductivity__source`, `thermal_conductivity__location`, `thermal_conductivity__method`, `thermal_conductivity__saturation`, `thermal_conductivity__pT_conditions`, `thermal_conductivity__pT_function`, `thermal_conductivity__strategy`, `sample__probe_metadata__probe_type`
- [ ] T017 [US1] Implement `GHFDBManager(models.Manager)` in `project/ghfdb/managers.py`: override `get_queryset()` to return `GHFDBQuerySet(self.model, using=self._db)`, and add `as_ghfdb_flat()` and `for_export()` delegation methods
- [ ] T018 [US1] Implement `GHFDB` proxy model in `project/ghfdb/models.py`: inherits `HeatFlow`, `objects = GHFDBManager()`, `class Meta: proxy = True; verbose_name = _("GHFDB Entry"); verbose_name_plural = _("GHFDB Entries")`; add class docstring citing Fuchs et al. (2021, 2023). **Note — registry exemption**: `GHFDB` is a proxy over `HeatFlow`, not a direct `Sample` or `Measurement` subclass. FairDM registry (`@fairdm.register`) applies only to direct `Sample`/`Measurement` subtypes that need auto-generated views/tables/filters; this proxy is intentionally admin-only and does not require registry registration. **Also**: add a minimal smoke test to `tests/test_ghfdb/test_models.py`: `from project.ghfdb.models import GHFDB` / `assert GHFDB._meta.proxy is True` / `assert GHFDB._meta.verbose_name == "GHFDB Entry"`.
- [ ] T019 [US1] Create `project/ghfdb/admin.py` with `GHFDBAdmin(admin.ModelAdmin)` registered for `GHFDB`: override `get_queryset()` to return `GHFDB.objects.as_ghfdb_flat()`; set `list_display` with key flat columns (`site_name`, `lat_ns`, `long_ew`, `p_q`, `value`); set `list_display_links = None` to enforce read-only; wrap all user-facing strings in `_()`.

### System Validation — Phase 3

- [ ] T020 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [ ] T021 ⚠️ CRITICAL: Run User Story 1 tests: `poetry run pytest tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py -v` — ALL tests MUST pass

**Checkpoint — US1 Complete**: Proxy model queryable, all scalar annotations verified, correction flags present, admin list view renders without field errors, query counts confirmed constant.

---

## Phase 4: User Story 2 — Import GHFDB Spreadsheet (Priority: P2)

**Goal**: Refactor `GHFDBResource` → `GHFDBImportResource` (with upsert by `local_id`, atomic full-file validation, and vocabulary-to-Concept mapping), extract shared constants to `GHFDBBaseResource`, and surface the import action via `GHFDBAdmin`.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_import.py -v`

### Tests for User Story 2 ⚠️ Write FIRST — verify they FAIL before implementing

- [ ] T022 [P] [US2] Write single-row happy-path import test: call `GHFDBImportResource` with a minimal valid flat row dict; assert `HeatFlowSite`, `ParentHeatFlow`, `HeatFlowInterval`, `ThermalGradient`, `IntervalConductivity`, and `HeatFlow` (with correct `local_id`) are all created in the database in `tests/test_ghfdb/test_import.py`
- [ ] T023 [P] [US2] Write vocabulary-translation test: import a row with semicolon-separated display labels for `q_method` and `tc_method`; assert the resulting `HeatFlow` has the expected `Concept` instances on its M2M relations in `tests/test_ghfdb/test_import.py`
- [ ] T024 [P] [US2] Write full-rollback validation test: provide an import dataset where one row has a valid vocabulary value and another has an invalid value; assert `ValidationError` errors are collected for all invalid rows and zero records are written to the database in `tests/test_ghfdb/test_import.py`
- [ ] T025 [P] [US2] Write upsert test: import a row with `ID="GHFDB-001"` (mapped to `local_id`), then re-import a modified version of the same row; assert exactly one `HeatFlow` record with `local_id="GHFDB-001"` exists and its fields reflect the updated values in `tests/test_ghfdb/test_import.py`
- [ ] T026 [P] [US2] Write `GHFDBImportFormat` test: assert that parsing a minimal GHFDB-template XLSX (headers at row 6, data from row 8, sheet name "data list") yields the correct column names and data values in `tests/test_ghfdb/test_import.py`
- [ ] T060 [P] [US2] Write staff-only access control test: assert that an anonymous `GET` to the Django admin import URL for the `GHFDB` model (e.g., `/admin/ghfdb/ghfdb/import/`) returns HTTP 302 redirecting to the login page; assert a non-staff authenticated user also cannot access the page (HTTP 302 or 403) in `tests/test_ghfdb/test_import.py` (FR-003 security requirement)
- [ ] T061 [P] [US2] Write import schema-coverage test (SC-005 import side): load `project/ghfdb/data/ghfdb_colmeta.json`; collect all columns with `obligation="M"`; assert every such column name either appears in `GHFDBImportResource.Meta.fields` or is explicitly handled in `before_import_row()` (verified by inspecting the resource's declared field names); fail with a descriptive message listing any uncovered mandatory columns in `tests/test_ghfdb/test_import.py`

### Implementation for User Story 2

- [ ] T027 [US2] Extract shared widget classes (`ConceptWidget`, `MultiConceptWidget`, `YesNoWidget`) and column-name constants (`GHFDB_COLUMNS`, `CHOICE_FIELDS`, `MULTI_CHOICE_FIELDS`) into a `GHFDBBaseResource` base class at the top of `project/ghfdb/resources.py`, removing the `dataset` constructor argument requirement from the base. (`QuantityWidget` is export-specific and will be implemented separately in T040; do not include it here.)
- [ ] T028 [US2] Rename `GHFDBResource` → `GHFDBImportResource` in `project/ghfdb/resources.py`; update `Meta` to add `import_id_fields = ("local_id",)`, `use_transactions = True`, `rollback_on_validation_errors = True`, `raise_errors = False`, `clean_model_instances = True`
- [ ] T029 [US2] Update `before_import_row()` in `project/ghfdb/resources.py` to map the spreadsheet `ID` column to `row["local_id"]` before calling downstream helpers, and map `ID_parent` to the `local_id` used in `get_heat_flow_site()` and `get_parent_heat_flow()` for parent-level upsert via `get_or_create(local_id=..., dataset=...)`
- [ ] T030 [US2] Verify `GHFDBImportFormat.create_dataset()` in `project/ghfdb/resources.py` correctly reads headers from row 6, starts data at row 8, and asserts sheet name is "data list"; add a clear `ValueError` if the sheet is missing
- [ ] T031 [US2] Update `ConceptWidget.clean()` and `MultiConceptWidget.clean()` in `project/ghfdb/resources.py` to raise `ValidationError` with a message that includes the column name and the offending value string, and to use case-insensitive vocabulary lookup
- [ ] T032 [US2] Add `get_import_resource_classes()` returning `[GHFDBImportResource]` and `get_import_formats()` returning `[GHFDBImportFormat]` to `GHFDBAdmin` in `project/ghfdb/admin.py`; change admin base class to `ImportExportMixin, admin.ModelAdmin`

### System Validation — Phase 4

- [ ] T033 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [ ] T034 ⚠️ CRITICAL: Run User Story 2 tests: `poetry run pytest tests/test_ghfdb/test_import.py -v` — ALL tests MUST pass

**Checkpoint — US2 Complete**: GHFDB XLSX can be imported atomically with upsert, vocabulary mapping, and full error reporting; zero records persisted on any validation failure.

> **SC-003 Manual QA Gate** (not automated): Before marking this feature release-ready, manually import a 10,000-row GHFDB XLSX and confirm the complete validation error report (all invalid rows) is delivered to the admin UI within 60 seconds. Wall-clock timing is deployment-environment-dependent and cannot be pinned as a pytest assertion; the query-count guard in T008/T011 is the automated proxy.

---

## Phase 5: User Story 3 — Export to GHFDB Spreadsheet (Priority: P2)

**Goal**: New `GHFDBExportResource` with explicit `export_order`, `dehydrate_*` methods for all 65 columns (Pint magnitude stripping, M2M semicolon joining, correction flags), and admin export action producing a GHFDB-compliant XLSX.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_export.py -v`

### Tests for User Story 3 ⚠️ Write FIRST — verify they FAIL before implementing

- [ ] T035 [P] [US3] Write column-completeness test: export a queryset with one record and assert the XLSX header row contains all expected GHFDB column names sourced from `ghfdb_colmeta.json` in `tests/test_ghfdb/test_export.py`
- [ ] T036 [P] [US3] Write column-order test: assert the XLSX header row matches the exact sequence defined in `GHFDBExportResource.Meta.export_order` (cross-checked against the `ghfdb_colmeta.json` prescribed order) in `tests/test_ghfdb/test_export.py`
- [ ] T037 [P] [US3] Write Pint magnitude-stripping test: export a record where a heat-flow quantity field has a `Pint Quantity` value; assert the exported cell is a plain numeric string with no unit symbol in `tests/test_ghfdb/test_export.py`
- [ ] T038 [P] [US3] Write M2M semicolon-joining test: export a record with multiple `Concept` objects on `tc_method`; assert the exported cell value is a semicolon-joined label string (e.g., `"Needle probe;Divided bar"`) in `tests/test_ghfdb/test_export.py`
- [ ] T062 [P] [US3] Write staff-only access control test: assert that an anonymous `GET` to the Django admin export URL for the `GHFDB` model returns HTTP 302 redirecting to the login page; assert a non-staff authenticated user also cannot access the page (HTTP 302 or 403) in `tests/test_ghfdb/test_export.py` (FR-007 security requirement)
- [ ] T039 [US3] Write round-trip regression test (SC-001): import a known minimal GHFDB spreadsheet, then export; assert text and vocabulary columns are byte-for-byte identical and numeric column values differ by less than floating-point epsilon in `tests/test_ghfdb/test_export.py`

### Implementation for User Story 3

- [ ] T040 [P] [US3] Implement `QuantityWidget` in `project/ghfdb/resources.py` (inside or just after `GHFDBBaseResource`): `render(self, value, obj=None)` returns `""` for `None`, otherwise `str(getattr(value, "magnitude", value))`
- [ ] T041 [US3] Implement `GHFDBExportResource` skeleton in `project/ghfdb/resources.py`: `Meta.model = GHFDB`, `Meta.export_order = (...)` tuple listing all ~65 GHFDB column names in the exact order from `ghfdb_colmeta.json`, `Meta.fields` enumerating the same columns; inherit from `GHFDBBaseResource`
- [ ] T042 [US3] Implement all `dehydrate_*` methods on `GHFDBExportResource` in `project/ghfdb/resources.py`: (a) scalar FK annotations — read from the pre-annotated attribute (e.g., `return obj.site_name`); (b) M2M fields — `";".join(c.label for c in getattr(obj, field_name).all())`; (c) correction flags — read `corr_*_flag` annotation; (d) `None`-guard all cells to return `""` not `"None"`
- [ ] T043 [US3] Override `get_queryset()` on `GHFDBExportResource` in `project/ghfdb/resources.py` to return `GHFDB.objects.for_export()` so all M2M relations are pre-fetched before dehydration
- [ ] T044 [US3] Add `get_export_resource_classes()` returning `[GHFDBExportResource]` and `get_export_formats()` returning `[XLSX]` to `GHFDBAdmin` in `project/ghfdb/admin.py`

### System Validation — Phase 5

- [ ] T045 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [ ] T046 ⚠️ CRITICAL: Run User Story 3 tests: `poetry run pytest tests/test_ghfdb/test_export.py -v` — ALL tests MUST pass

**Checkpoint — US3 Complete**: Export produces a GHFDB-compliant XLSX with correct column order, Pint values stripped to numerics, M2M fields semicolon-joined, round-trip regression test passes.

---

## Phase 6: User Story 4 — Web Map Viewer Page (Priority: P3)

**Goal**: The existing `GHFDBExploreView` and `explore.html` are enhanced with a graceful degradation fallback for unreachable iframes; the "Explore" menu item and URL routing are verified correct.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_views.py -v`

### Tests for User Story 4 ⚠️ Write FIRST — verify they FAIL before implementing

- [ ] T047 [P] [US4] Write map page load test: assert an anonymous `GET /ghfdb/explore/` returns HTTP 200 and the response body contains the iframe `src` attribute pointing to `https://ihfc-iugg.github.io/HeatFlowMapping/` in `tests/test_ghfdb/test_views.py`
- [ ] T048 [P] [US4] Write no-auth test: assert the map page returns HTTP 200 for an unauthenticated request (no redirect to login) in `tests/test_ghfdb/test_views.py`
- [ ] T049 [P] [US4] Write graceful degradation test: assert the `explore.html` template source contains a visible fallback element (e.g., `class="explore-fallback"`) inside or adjacent to the iframe for the unreachable-URL case in `tests/test_ghfdb/test_views.py`

### Implementation for User Story 4

- [ ] T050 [US4] Add a fallback `<div class="explore-fallback">` message inside the `<iframe>` tag in `project/ghfdb/templates/ghfdb/explore.html`; ensure the iframe has `style="width:100%;height:100vh;border:none"` and the enclosing element has no horizontal overflow; verify (or add) `frame-src https://ihfc-iugg.github.io` to the portal's Content Security Policy in `config/settings.py` (or the CSP middleware configuration) so browsers do not block the iframe
- [ ] T051 [US4] Verify `GHFDBExploreView` in `project/ghfdb/views.py` has no `LoginRequiredMixin` and uses template `ghfdb/explore.html`; confirm the URL pattern in `project/ghfdb/urls.py` resolves as `ghfdb-explore`
- [ ] T052 [US4] Verify the "Explore" `MenuItem` in `project/heat_flow/menus.py` points to the `ghfdb-explore` URL name and is configured to mark itself active when the user is on that URL

### System Validation — Phase 6

- [ ] T053 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [ ] T054 ⚠️ CRITICAL: Run User Story 4 tests: `poetry run pytest tests/test_ghfdb/test_views.py -v` — ALL tests MUST pass

**Checkpoint — US4 Complete**: Map page accessible without auth, iframe URL present, graceful fallback visible in template.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation currency, citation compliance (constitution II & VII), and final full-suite validation.

- [ ] T055 [P] Update `docs/ghfdb_fields.md` to add a "Proxy Model Access Patterns" section documenting all 40 annotation names, their ORM source paths, and the corresponding GHFDB spreadsheet column — sourced from data-model.md column-mapping tables
- [ ] T056 [P] Add Fuchs et al. (2021) and Fuchs et al. (2023) inline docstring citations to `GHFDBImportResource` and `GHFDBExportResource` class docstrings in `project/ghfdb/resources.py`, and to `GHFDBAdmin` in `project/ghfdb/admin.py` (the `GHFDB` model docstring was handled in T018)
- [ ] T057 Run `poetry run python manage.py check --deploy` and confirm no NEW warnings introduced by the changes in this feature (pre-existing deploy warnings acceptable)

### System Validation — Final

- [ ] T058 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass
- [ ] T059 ⚠️ CRITICAL: Run full GHFDB test suite: `poetry run pytest tests/test_ghfdb/ -v` — ALL 6 test modules MUST pass

**Checkpoint — Feature Complete**: System checks pass, all GHFDB tests green, `ghfdb_fields.md` updated, citations present in all new classes.

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends on | Blocks |
|---|---|---|
| Phase 1 — Setup | Nothing | Nothing |
| Phase 2 — Foundational | Phase 1 | ALL user stories |
| Phase 3 — US1 (P1) | Phase 2 | Phase 5 (US3 needs `for_export()`) |
| Phase 4 — US2 (P2) | Phase 2 | Nothing |
| Phase 5 — US3 (P2) | Phase 3 (US1) | Nothing |
| Phase 6 — US4 (P3) | Phase 2 | Nothing |
| Phase 7 — Polish | Phases 3–6 | Nothing |

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 — no inter-story dependency
- **US2 (P2)**: Starts after Phase 2 — can run in parallel with US1
- **US3 (P2)**: Starts after US1 is complete — requires `GHFDB.objects.for_export()`
- **US4 (P3)**: Starts after Phase 2 — fully independent of US1–US3

### Within Each User Story

1. Write ALL story tests first; confirm they FAIL
2. Implement managers / models (data-layer code)
3. Implement resources / views (service-layer code)
4. Implement admin registration (integration)
5. Run story tests — ALL must pass before starting the next story

### Parallel Opportunities

**Phase 3 (US1)** — after T015/T016/T017 complete:

- T018 (`models.py`) and T019 (`admin.py`) can run in parallel

**Phase 4 (US2)** — test-writing tasks:

- T022–T026 can all be written in parallel (one test module)

**Phase 5 (US3)** — within resources.py:

- T040 (`QuantityWidget`) can be written in parallel with T041 (`GHFDBExportResource` skeleton)

**Phase 6 (US4)** — implementation tasks:

- T050 (template) and T051+T052 (view + menu) can run in parallel

**Phase 7**:

- T055 (docs) and T056 (citations) can run in parallel

---

## Implementation Strategy

**MVP scope** (minimum for a working GHFDB product view):
→ Phase 1 → Phase 2 → Phase 3 (US1 only) — delivers the flat proxy queryset and read-only admin display.

**Recommended delivery order**:
→ Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 + Phase 6 in parallel → Phase 5 (US3) → Phase 7

**Key risk**: The `resources.py` refactor in US2 touches ~900 lines of existing import logic. Preserve all existing widget classes and `before_import_row()` orchestration; rename and extend rather than rewrite. Run import tests frequently during T027–T032.

---

## Summary

| Phase | Tasks | User Story | Priority |
|---|---|---|---|
| Phase 1 — Setup | T001–T003 | — | — |
| Phase 2 — Foundational | T004–T007 | — | — |
| Phase 3 — Proxy Model | T008–T021 | US1 | P1 🎯 |
| Phase 4 — Import | T022–T034, T060, T061 | US2 | P2 |
| Phase 5 — Export | T035–T046, T062 | US3 | P2 |
| Phase 6 — Map Viewer | T047–T054 | US4 | P3 |
| Phase 7 — Polish | T055–T059 | — | — |
| **Total** | **62 tasks** | | |
