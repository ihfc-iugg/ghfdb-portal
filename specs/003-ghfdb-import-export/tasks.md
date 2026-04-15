# Tasks: GHFDB Import/Export Pipeline

**Feature**: 003-ghfdb-import-export
**Branch**: `003-ghfdb-import-export`
**Input**: plan.md, spec.md, data-model.md, research.md, contracts/import-contract.md, contracts/export-contract.md, quickstart.md
**Split from**: `002-ghfdb-product-utilities` tasks.md (Phases 3.5–5 + relevant Phase 7 tasks)
**Propagated**: 2026-04-15 — Added controlled-vocabulary import normalization tasks (FR-016): T072 regression tests, T073 widget implementation, T074 validation gate.
**Propagated**: 2026-04-14 — Updated from spec.md refinement
**Bugfix**: 2026-04-14 — [BUG-002] Reopened admin import integration tasks and added import-page regression coverage for django-import-export hook compatibility.
**Bugfix**: 2026-04-14 — [BUG-003] Reopened import upsert tasks and added template-aware natural-key coverage for standard uploads without `ID` / `ID_parent`.
**Bugfix**: 2026-04-15 — [BUG-003] Reopened standard-upload upsert tasks for header-validation failure when `ID_parent` / `ID` headers are absent from file uploads.
**Bugfix**: 2026-04-15 — [BUG-004] Reopened T024 (GHFDBImportFormat off-by-one: `min_row=8` reads a metadata row; must be `min_row=9`).

**Prerequisite**: `002-ghfdb-product-utilities` must be complete before any task in this spec begins — specifically `GHFDB` proxy model, `GHFDBManager.for_export()`, and `local_id` fields on `HeatFlow`, `HeatFlowSite`, and `ParentHeatFlow`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no dependency on an incomplete task)
- **[US2/3]**: Mapped user story
- All tasks include an exact file path

---

## Phase 3.5: Resources Package Setup (Prerequisite)

**Purpose**: Create the `resources/` package skeleton and `test_resources/` test directory before any US2 or US3 tasks begin.

- [X] T022 Create `project/ghfdb/resources/` package: `__init__.py`, `_base.py`, `_widgets.py`, `parent.py`, `child.py`, `export.py` (all empty stubs with a module-level docstring)
- [X] T023 [P] Create `tests/test_ghfdb/test_resources/` directory with `__init__.py` and stub files: `test_widgets.py`, `test_parent_import.py`, `test_child_import.py`, `test_export.py`, `test_roundtrip.py`; copy/reuse the `heat_flow_chain` and `sample_ghfdb_row` fixtures from `tests/test_ghfdb/conftest.py` as needed via import; **also delete** orphaned top-level stubs `tests/test_ghfdb/test_import.py` and `tests/test_ghfdb/test_export.py` created previously (superseded by the `test_resources/` subdirectory)
- [X] T024 ⚠️ Reopened Implement `GHFDBImportFormat` (XLSX subclass: sheet `"data list"`, use row 6 as headers, skip rows 7 (unit labels) and 8 ("Allowed range of values"), data rows from row 9 — `ws.iter_rows(min_row=9)`) (reopened — BUG-004); `GHFDB_COLUMN_ORDER` (all **62** GHFDB column names in canonical order, matching `ghfdb_colmeta.json`), `PARENT_COLUMNS` (18 parent-level column names), and `CORRECTION_COL_MAP` (`{"corr_IS_flag": "IS", …}` 9-entry dict) in `project/ghfdb/resources/_base.py`
- [X] T025 Verify `ParentHeatFlow.local_id` field exists (check `project/heat_flow/models/`); if absent, add `local_id = CharField(max_length=255, null=True, blank=True, db_index=True)` and generate migration; **also verify `HeatFlowSite.local_id` field exists** — FR-006 uses it as the stable upsert identifier for the parent record; if absent, add the same field definition to `HeatFlowSite`; if either field is new, generate a single combined migration: `poetry run python manage.py makemigrations heat_flow --name add_local_id_fields`

### System Validation — Phase 3.5

- [X] T026 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding to Phase 4
- [X] T026a ⚠️ CRITICAL: Run type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors (constitution §VI)
- [X] T026b ⚠️ CRITICAL: Run linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations (constitution §VI)

**Checkpoint — Resources Package Ready**: Stub modules created, `_base.py` constants in place, `ParentHeatFlow.local_id` and `HeatFlowSite.local_id` verified.

---

## Phase 4: User Story 2 — Import GHFDB Spreadsheet (Priority: P2)

**Goal**: Staff can upload a GHFDB XLSX in the Django admin and select either the "GHFDB Parent" or "GHFDB Child" import resource to create/update `HeatFlowSite`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`, `HeatFlowCorrection`, and `ProbeMetadata` records with correct controlled-vocabulary mappings, upsert on natural keys (or `local_id` when present), and atomic rollback on any validation error. Vocabulary tokens must be normalised before matching: square brackets stripped and the result lowercased (FR-016).

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_resources/test_widgets.py tests/test_ghfdb/test_resources/test_parent_import.py tests/test_ghfdb/test_resources/test_child_import.py -v`

### Tests for User Story 2 ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T027 [P] [US2] Write failing leaf-widget tests in `tests/test_ghfdb/test_resources/test_widgets.py`: `ConceptWidget.clean()` case-insensitive lookup + invalid-value `ValueError` listing valid options; `MultiConceptWidget.clean()` semicolon split + batched error for multiple invalid values; `QuantityWidget.clean()` returns `Quantity`, `.render()` returns plain magnitude; `YesNoWidget.clean()` maps `"Yes"`→`True`, `"No"`→`False`, empty→`None`
- [X] T028 [P] [US2] Write failing `RelatedModelWidget` and subclass tests in `tests/test_ghfdb/test_resources/test_widgets.py`: sentinel-column check skips instance creation when column is empty; `full_clean()` raises `ValueError` prefixed with model name; `set_m2m_relations()` sets correct M2M; `ParentWidget` creates `HeatFlowSite` + `Point` from lat/long columns; `IntervalWidget` creates `HeatFlowInterval`; `GradientWidget` skips when `T_grad_mean` is empty; `ConductivityWidget` skips when `tc_mean` is empty
- [X] T029 ⚠️ Reopened [P] [US2] Write failing `GHFDBParentImportResource` tests in `tests/test_ghfdb/test_resources/test_parent_import.py`: upsert on `local_id` (re-import updates, does not duplicate); `before_import()` deduplication keeps first occurrence of each `ID_parent`; 18 parent columns mapped to correct fields; `ParentHeatFlow.sample` FK (to `HeatFlowSite`) created with correct `Point` location; `explo_purpose` M2M set; staff-only access control (anonymous admin import URL → 302); plus regression coverage for template rows without `ID_parent` using `lat_NS` + `long_EW` as natural upsert key (reopened — BUG-003)
- [X] T030 ⚠️ Reopened [P] [US2] Write failing `GHFDBChildImportResource` tests in `tests/test_ghfdb/test_resources/test_child_import.py`: all 14 child field mappings; `parent` FK resolved via `ID_parent` `ForeignKeyWidget`; `after_save_instance()` creates 9 `HeatFlowCorrection` records with correct `correction_type` and `status`; `ProbeMetadata` created when probe columns are non-empty; `method` M2M set via `MultiConceptWidget`; `IntervalWidget`, `GradientWidget`, `ConductivityWidget` M2M set after save; plus regression coverage for template rows without `ID`/`ID_parent` using location + depth + `publication_reference` as child natural key (reopened — BUG-003)
- [X] T030a [US2] Write failing SC-005 schema-coverage test in `tests/test_ghfdb/test_resources/test_schema_coverage.py`: assert every column name in `GHFDB_COLUMN_ORDER` (from `_base.py`) appears as a declared `Field` in either `GHFDBParentImportResource` or `GHFDBChildImportResource` with no undocumented omissions; assert every column name also appears as a key in `ghfdb_colmeta.json`; assert `len(GHFDB_COLUMN_ORDER) == 62` (authoritative count from `ghfdb_colmeta.json`)
- [X] T066 [P] [US2] Add an authenticated admin regression test in `tests/test_ghfdb/test_resources/test_parent_import.py` asserting `GET /admin/ghfdb/ghfdb/import/` returns HTTP 200 for a staff user and renders the configured import resource options without a server error
- [X] T072 [P] [US2] Write failing normalization regression tests in `tests/test_ghfdb/test_resources/test_widgets.py`: assert `ConceptWidget.clean("[Onshore (continental)]")` returns the correct `Concept` for `"onshore (continental)"`; assert `ConceptWidget.clean("[OFFSHORE (MARINE)]")` returns the correct `Concept` for `"offshore (marine)"`; assert `MultiConceptWidget.clean("[Offshore, continental]; [Onshore (continental)]")` splits on `;` and normalises each token independently; assert that a bracketed invalid token raises a `ValueError` whose message contains the **original** bracket-wrapped text (not the stripped/lowercased form) so users can locate the error in the source file (FR-016)

### Implementation for User Story 2

- [X] T031 [US2] Implement leaf widgets (`ConceptWidget` — case-insensitive label lookup + cache; `MultiConceptWidget` — semicolon split + batch `ConceptWidget`; `QuantityWidget` — `Quantity(Decimal(value), unit)` ↔ `magnitude`; `YesNoWidget` — "Yes"/"No" ↔ `True`/`False`/`None`) in `project/ghfdb/resources/_widgets.py`; all user-facing error message strings MUST use `gettext_lazy()` (constitution §V — i18n compliance)
- [X] T073 [US2] Update `ConceptWidget.clean()` and `MultiConceptWidget.clean()` in `project/ghfdb/resources/_widgets.py` to apply token normalisation (FR-016): add a `normalize_vocab_token(raw: str) -> str` module-level helper that returns `raw.strip("[]").lower()`; call it on each token **before** cache lookup or database query; error messages MUST include the **original** (pre-normalisation) token text so the user can locate the value in the source file; all message strings MUST use `gettext_lazy()` (constitution §V)
- [X] T032 [US2] Implement `RelatedModelWidget` base class in `project/ghfdb/resources/_widgets.py`: `__init__` accepts `model`, `field_map`, `m2m_map`, `sentinel_column`, `widget_map`; `clean()` checks sentinel → extracts + cleans scalars → `full_clean()` → `save()` → defers M2M; `set_m2m_relations(instance)` sets all M2M via widget `.clean()`; `full_clean()` `ValidationError` re-raised as `ValueError` prefixed with model name; `ValueError` prefix strings MUST use `gettext_lazy()` (constitution §V — i18n compliance)
- [X] T033 [US2] Implement `ParentWidget` in `project/ghfdb/resources/_widgets.py`: `RelatedModelWidget` for `HeatFlowSite` + `Point`, sentinel `"name"`, creates/updates `Point(x=long_EW, y=lat_NS)`, all scalar (`name`, `elevation`, `environment`, `explo_method`, `total_depth_MD`→`length`, `total_depth_TVD`→`vertical_depth`, `Country`, `Region`, `Continent`, `Domain`) and M2M (`explo_purpose`) mappings per `data-model.md`
- [X] T034 [US2] Implement `IntervalWidget` (sentinel `None`, `q_top`/`q_bottom` → `QuantityWidget("m")`, `geo_lithology`/`geo_stratigraphy` M2M), `GradientWidget` (sentinel `"T_grad_mean"`, 7 scalar + 4 M2M fields), and `ConductivityWidget` (sentinel `"tc_mean"`, 3 scalar + 7 M2M fields) in `project/ghfdb/resources/_widgets.py`
- [X] T035 ⚠️ Reopened [US2] Implement `GHFDBParentImportResource` in `project/ghfdb/resources/parent.py`: 6 `Field` declarations (`local_id`, `value`, `uncertainty`, `comment`, `corr_HP_flag`, `sample`); `ParentWidget` instantiation; `before_import()` deduplication; `Meta` upsert strategy must be template-aware (`ID_parent` / `local_id` when present, otherwise `lat_NS` + `long_EW` for standard uploads) with transactional rollback preserved (reopened — BUG-003)
- [X] T036 ⚠️ Reopened [US2] Implement `GHFDBChildImportResource` in `project/ghfdb/resources/child.py`: 14 `Field` declarations per `data-model.md`; widget instantiations (`IntervalWidget`, `GradientWidget`, `ConductivityWidget`, `ForeignKeyWidget(ParentHeatFlow, "local_id")`); `after_save_instance()` creating 9 `HeatFlowCorrection.objects.update_or_create()` calls via `CORRECTION_COL_MAP` + `ProbeMetadata.objects.update_or_create()` when probe columns are non-empty + `widget.set_m2m_relations()` for each `RelatedModelWidget` field; `Meta` upsert strategy must be template-aware (`ID` / `local_id` when present, otherwise `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`) with transactional rollback preserved (reopened — BUG-003)
- [X] T037 [US2] Update `project/ghfdb/resources/__init__.py` to publicly re-export `GHFDBParentImportResource`, `GHFDBChildImportResource`, `GHFDBExportResource`, `GHFDBImportFormat`
- [X] T038 ⚠️ Reopened [US2] Update `GHFDBAdmin` import integration in `project/ghfdb/admin.py`: keep `get_import_resource_classes()` returning `[GHFDBParentImportResource, GHFDBChildImportResource]` and `get_import_formats()` returning `[GHFDBImportFormat]`, but ensure all django-import-export admin hook overrides accept the request-aware method signatures required by the installed version so `/admin/ghfdb/ghfdb/import/` renders successfully (reopened — BUG-002)

### System Validation — Phase 4

- [X] T039 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [X] T039a ⚠️ CRITICAL: Run type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors (constitution §VI)
- [X] T039b ⚠️ CRITICAL: Run linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations (constitution §VI)
- [X] T040 ⚠️ CRITICAL: Run User Story 2 tests: `poetry run pytest tests/test_ghfdb/test_resources/test_widgets.py tests/test_ghfdb/test_resources/test_parent_import.py tests/test_ghfdb/test_resources/test_child_import.py -v` — ALL tests MUST pass, including authenticated admin import-page rendering coverage, template-without-ID regression coverage for parent and child natural-key upsert paths, files where `ID` / `ID_parent` headers are fully absent (resolved — BUG-002, BUG-003), and bracket-wrapped/mixed-case vocabulary normalisation regression coverage (FR-016, see T074)
- [X] T074 ⚠️ CRITICAL [US2] Re-run `poetry run pytest tests/test_ghfdb/test_resources/test_widgets.py -v` and confirm all normalization regression tests (T072) pass — bracketed tokens must match correctly after stripping and lowercasing, and invalid bracketed tokens must report the **original** token text in the `ValueError` message — before closing FR-016

- [X] T067 [P] [US2] Add regression tests in `tests/test_ghfdb/test_resources/test_parent_import.py` for standard upload rows without `ID_parent`: verify deduplication and re-import upsert via `lat_NS` + `long_EW`, ensure no duplicate `ParentHeatFlow`/`HeatFlowSite` rows are created, and cover files where `ID_parent` header is absent (not just blank cell values) (resolved — BUG-003)
- [X] T068 [P] [US2] Add regression tests in `tests/test_ghfdb/test_resources/test_child_import.py` for standard upload rows without `ID`/`ID_parent`: verify re-import upsert via `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`, verify different `publication_reference` values over the same site/depth interval remain distinct records, and cover files where `ID`/`ID_parent` headers are absent (resolved — BUG-003)
- [X] T069 [US2] Update `project/ghfdb/resources/parent.py` so template-aware parent upsert remains valid when `ID_parent` header is absent from uploaded files and does not fail `import_id_fields` header validation (resolved — BUG-003)
- [X] T070 [US2] Update `project/ghfdb/resources/child.py` so template-aware child upsert remains valid when `ID`/`ID_parent` headers are absent from uploaded files and does not fail `import_id_fields` header validation, while preserving distinct-reference matching (resolved — BUG-003)
- [X] T071 CRITICAL [US2] Re-run `poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py tests/test_ghfdb/test_resources/test_child_import.py -v` and confirm template-aware upsert passes for both blank-ID rows and truly missing `ID`/`ID_parent` headers before closing BUG-003 (resolved — BUG-003)

**Checkpoint — US2 Complete (BUG-003 resolved 2026-04-15)**: Template-aware natural-key upsert verified for both blank-ID rows and uploads where `ID` / `ID_parent` headers are entirely absent. All 25 import resource tests pass.

> **SC-003 Manual QA Gate** (not automated): Before marking this feature release-ready, manually import a 10,000-row GHFDB XLSX and confirm the complete error report is delivered within 60 seconds.

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

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Round-trip regression test (SC-001), retire legacy `resources.py`, documentation, and final full-suite validation.

- [X] T056 Create fixture GHFDB XLSX (`tests/test_ghfdb/fixtures/sample_ghfdb.xlsx`) with 3–5 rows covering: one parent with `explo_purpose` M2M; one child with all 9 correction flags; one child with `ThermalGradient` + `IntervalConductivity` including M2M method fields; quantity fields in SI units
- [X] T057 [P] Write round-trip regression test (SC-001) in `tests/test_ghfdb/test_resources/test_roundtrip.py`: (1) import `sample_ghfdb.xlsx` via `GHFDBParentImportResource` then `GHFDBChildImportResource`; (2) export via `GHFDBExportResource`; (3) assert exported text/vocabulary cells are identical and numeric cells differ by less than floating-point `1e-9`
- [X] T058 Retire legacy `project/ghfdb/resources.py`: first verify no remaining code imports from it (`grep -r "from .resources import\|from project.ghfdb.resources import" project/ --include="*.py"`); then delete (or rename to `_resources_legacy.py.bak`)
- [X] T059a [P] Document the large-export row limit in `docs/ghfdb_fields.md` and in the `GHFDBExportResource` class docstring: state the tested synchronous row limit (e.g. 50,000 rows), note that `get_queryset()` MUST use `.iterator()` to avoid loading the full queryset into memory, and document that exports exceeding the limit should be moved to a background task (deferred to a future spec)
- [X] T060 [P] Add Fuchs et al. (2021) and Fuchs et al. (2023) inline citations to `GHFDBParentImportResource`, `GHFDBChildImportResource`, and `GHFDBExportResource` class docstrings in their respective module files; **also** add a module-level docstring to `project/ghfdb/resources/_widgets.py` citing both references and summarising the widget hierarchy (leaf widgets → `RelatedModelWidget` → specialised sub-model widgets)

### System Validation — Final

- [X] T061 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass
- [X] T061a ⚠️ CRITICAL: Run final type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors (constitution §VI)
- [X] T061b ⚠️ CRITICAL: Run final linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations (constitution §VI)
- [X] T062 ⚠️ CRITICAL: Run full GHFDB test suite: `poetry run pytest tests/test_ghfdb/ -v` — ALL test modules MUST pass (includes proxy model, resources, views, round-trip)

**Checkpoint — Feature Complete**: System checks pass, all GHFDB tests green (import resources + export resource + round-trip), legacy `resources.py` retired, large-export limit documented.

---

## Dependencies & Execution Order

| Phase | Depends on | Blocks |
|---|---|---|
| Prerequisite: 002 complete | Nothing | Everything in this spec |
| Phase 3.5 — Resources Package Setup | 002 complete | Phase 4 (US2) and Phase 5 (US3) |
| Phase 4 — US2 Import (P2) | Phase 3.5 | Phase 6 (round-trip) |
| Phase 5 — US3 Export (P2) | Phase 3.5 + 002 (`for_export()`) | Phase 6 (round-trip) |
| Phase 6 — Polish & Round-trip | Phase 4 + Phase 5 | Nothing |
