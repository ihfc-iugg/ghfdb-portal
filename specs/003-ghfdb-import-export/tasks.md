# Tasks: GHFDB Import/Export Pipeline

**Feature**: 003-ghfdb-import-export
**Branch**: `003-ghfdb-import-export`
**Input**: plan.md, spec.md, data-model.md, research.md, contracts/import-contract.md, contracts/export-contract.md, quickstart.md
**Split from**: `002-ghfdb-proxy` tasks.md (Phases 3.5–5 + relevant Phase 7 tasks)
**Propagated**: 2026-04-23 — Updated from spec.md refinement (BUG-010): canonical constants in `constants.py` require five code changes — Phase 4b tasks T091–T101 added.
**Bugfix**: 2026-04-23 — [BUG-010] Canonical constants alignment: `constants.py` now defines `PARENT_COLUMNS`, `CHILD_COLUMNS`, `META_FIELDS`, and `GHFDB_COLUMN_ORDER = PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS` as single source of truth. Five code changes required: (1) remove old lowercase `GHFDB_COLUMN_ORDER` tuple from `constants.py`; (2) rename stale annotation keys in `GHFDBChildQuerySet.as_ghfdb_flat()` to match canonical names; (3) add `GHFDBParentQuerySet.as_ghfdb_flat()`; (4) fix `get_user_visible_fields()` in `child.py` to lowercase BOTH dict keys and `column_name`; (5) update stale `attribute=` values in `export.py`.
**Propagated**: 2026-04-20 — Added Phase 4a with second import format tasks (T084–T090): `GHFDBSimpleImportFormat` implementation, admin format-selection requirement, and round-trip coverage (Acceptance Scenarios 11–12).
**Propagated**: 2026-04-15 — Added controlled-vocabulary import normalization tasks (FR-016): T072 regression tests, T073 widget implementation, T074 validation gate.
**Propagated**: 2026-04-14 — Updated from spec.md refinement
**Bugfix**: 2026-04-14 — [BUG-002] Reopened admin import integration tasks and added import-page regression coverage for django-import-export hook compatibility.
**Bugfix**: 2026-04-14 — [BUG-003] Reopened import upsert tasks and added template-aware natural-key coverage for standard uploads without `ID` / `ID_parent`.
**Bugfix**: 2026-04-15 — [BUG-003] Reopened standard-upload upsert tasks for header-validation failure when `ID_parent` / `ID` headers are absent from file uploads.
**Bugfix**: 2026-04-15 — [BUG-004] Reopened T024 (GHFDBImportFormat off-by-one: `min_row=8` reads a metadata row; must be `min_row=9`).
**Bugfix**: 2026-04-15 — [BUG-005] Reopened T035 and T069; added T075 (confirm-page regression tests) and T076 (child.py synthetic-key removal + location-based parent resolution); T069 scoped to parent.py, T076 scoped to child.py to eliminate overlap.
**Bugfix**: 2026-04-15 — [BUG-006] Reopened T035 and T036 (field declaration order does not match template); added T077 (failing column-order assertions) and T078 (get_user_visible_fields() override in both resources).
**Bugfix**: 2026-04-16 — [BUG-007] Reopened T027 and T028 (widget tests: add int/float input regression cases); reopened T031 (widget implementation: add try/except AttributeError guards); added T079 (failing regression tests for numeric cell input) and T080 (implementation of the type-guard fix in `widgets.py`).
**Bugfix**: 2026-04-16 — [BUG-008] Reopened T028 (GradientWidget/ConductivityWidget numeric-sentinel tests must assert **success**, not ValueError); reopened T034 (sentinel check must treat int/float as present for quantity sentinels); reopened T079 (replace wrong error assertions for GradientWidget and ConductivityWidget with success assertions); reopened T080 (add `isinstance(raw_sentinel, (int, float))` bypass before the `.strip()` guard in `RelatedModelWidget.clean()`).
**Bugfix**: 2026-04-16 — [BUG-009] Reopened T034 (`geo_stratigraphy` M2M key must be `"age"` not `"stratigraphy"` in `IntervalWidget.m2m_map`); added T081 (fix key in `widgets.py`), T082 (regression test for non-empty `geo_stratigraphy`), T083 (critical validation gate).

**Prerequisite**: `002-ghfdb-proxy` must be complete before any task in this spec begins — specifically `GHFDB` proxy model, `GHFDBChildManager.for_export()`, and `local_id` fields on `HeatFlow`, `HeatFlowSite`, and `ParentHeatFlow`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no dependency on an incomplete task)
- **[US2/3]**: Mapped user story
- All tasks include an exact file path

---

## Phase 3.5: Resources Package Setup (Prerequisite)

**Purpose**: Create the `resources/` package skeleton and `test_resources/` test directory before any US2 or US3 tasks begin.

- [X] T022 Create `project/ghfdb/resources/` package: `__init__.py`, `formats.py`, `widgets.py`, `parent.py`, `child.py`, `export.py` (all empty stubs with a module-level docstring)
- [X] T023 [P] Create `tests/test_ghfdb/test_resources/` directory with `__init__.py` and stub files: `testwidgets.py`, `test_parent_import.py`, `test_child_import.py`, `test_export.py`, `test_roundtrip.py`; copy/reuse the `heat_flow_chain` and `sample_ghfdb_row` fixtures from `tests/test_ghfdb/conftest.py` as needed via import; **also delete** orphaned top-level stubs `tests/test_ghfdb/test_import.py` and `tests/test_ghfdb/test_export.py` created previously (superseded by the `test_resources/` subdirectory)
- [X] T024 ⚠️ Reopened Implement `GHFDBImportFormat` (XLSX subclass: sheet `"data list"`, use row 6 as headers, skip rows 7 (unit labels) and 8 ("Allowed range of values"), data rows from row 9 — `ws.iter_rows(min_row=9)`) (reopened — BUG-004); `GHFDB_COLUMN_ORDER` (all **62** GHFDB column names in canonical order, matching `ghfdb_colmeta.json`), `PARENT_COLUMNS` (18 parent-level column names), and `CORRECTION_COL_MAP` (`{"corr_IS_flag": "IS", …}` 9-entry dict) in `project/ghfdb/resources/formats.py`; **BUG-010 amendment**: `GHFDB_COLUMN_ORDER`, `PARENT_COLUMNS`, `CHILD_COLUMNS`, `META_FIELDS`, and `CORRECTION_COL_MAP` are now defined in `project/ghfdb/constants.py` — `formats.py` MUST import them from there rather than redeclaring
- [X] T025 Verify `ParentHeatFlow.local_id` field exists (check `project/heat_flow/models/`); if absent, add `local_id = CharField(max_length=255, null=True, blank=True, db_index=True)` and generate migration; **also verify `HeatFlowSite.local_id` field exists** — FR-006 uses it as the stable upsert identifier for the parent record; if absent, add the same field definition to `HeatFlowSite`; if either field is new, generate a single combined migration: `poetry run python manage.py makemigrations heat_flow --name add_local_id_fields`

### System Validation — Phase 3.5

- [X] T026 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding to Phase 4
- [X] T026a ⚠️ CRITICAL: Run type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors (constitution §VI)
- [X] T026b ⚠️ CRITICAL: Run linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations (constitution §VI)

**Checkpoint — Resources Package Ready**: Stub modules created, `formats.py` constants in place, `ParentHeatFlow.local_id` and `HeatFlowSite.local_id` verified.

---

## Phase 4: User Story 2 — Import GHFDB Spreadsheet (Priority: P2)

**Goal**: Staff can upload a GHFDB XLSX in the Django admin and select either the "GHFDB Parent" or "GHFDB Child" import resource to create/update `HeatFlowSite`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`, `HeatFlowCorrection`, and `ProbeMetadata` records with correct controlled-vocabulary mappings, upsert on natural keys (or `local_id` when present), and atomic rollback on any validation error. Vocabulary tokens must be normalised before matching: square brackets stripped and the result lowercased (FR-016).

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_resources/testwidgets.py tests/test_ghfdb/test_resources/test_parent_import.py tests/test_ghfdb/test_resources/test_child_import.py -v`

### Tests for User Story 2 ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T027 ⚠️ Reopened [P] [US2] Write failing leaf-widget tests in `tests/test_ghfdb/test_resources/testwidgets.py`: `ConceptWidget.clean()` case-insensitive lookup + invalid-value `ValueError` listing valid options; `MultiConceptWidget.clean()` semicolon split + batched error for multiple invalid values; `QuantityWidget.clean()` returns `Quantity`, `.render()` returns plain magnitude; `YesNoWidget.clean()` maps `"Yes"`→`True`, `"No"`→`False`, empty→`None`; **add**: assert passing an `int` to `ConceptWidget.clean()` raises `ValueError` whose message names the vocabulary (not a bare `AttributeError`) (reopened — BUG-007)
- [X] T028 ✅ Resolved (reopened — BUG-008) [P] [US2] Write failing `RelatedModelWidget` and subclass tests in `tests/test_ghfdb/test_resources/testwidgets.py`: sentinel-column check skips instance creation when column is empty; `full_clean()` raises `ValueError` prefixed with model name; `set_m2m_relations()` sets correct M2M; `ParentWidget` creates `HeatFlowSite` + `Point` from lat/long columns; `IntervalWidget` creates `HeatFlowInterval`; `GradientWidget` skips when `T_grad_mean` is empty; `ConductivityWidget` skips when `tc_mean` is empty; **add**: assert that `ParentWidget` with an `int` in the `name` column raises `ValueError` (text-sentinel error remains correct — BUG-007); **correct BUG-008**: assert that `GradientWidget.clean(row={"T_grad_mean": 800, ...})` **succeeds** and returns a `ThermalGradient` — a numeric sentinel value on a quantity sentinel column MUST NOT raise; assert equivalently for `ConductivityWidget` with a numeric `tc_mean`
- [X] T029 ⚠️ Reopened [P] [US2] Write failing `GHFDBParentImportResource` tests in `tests/test_ghfdb/test_resources/test_parent_import.py`: upsert on `local_id` (re-import updates, does not duplicate); `before_import()` deduplication keeps first occurrence of each `ID_parent`; 18 parent columns mapped to correct fields; `ParentHeatFlow.sample` FK (to `HeatFlowSite`) created with correct `Point` location; `explo_purpose` M2M set; staff-only access control (anonymous admin import URL → 302); plus regression coverage for template rows without `ID_parent` using `lat_NS` + `long_EW` as natural upsert key (reopened — BUG-003)
- [X] T030 ⚠️ Reopened [P] [US2] Write failing `GHFDBChildImportResource` tests in `tests/test_ghfdb/test_resources/test_child_import.py`: all 14 child field mappings; `parent` FK resolved via `ID_parent` `ForeignKeyWidget`; `after_save_instance()` creates 9 `HeatFlowCorrection` records with correct `correction_type` and `status`; `ProbeMetadata` created when probe columns are non-empty; `method` M2M set via `MultiConceptWidget`; `IntervalWidget`, `GradientWidget`, `ConductivityWidget` M2M set after save; plus regression coverage for template rows without `ID`/`ID_parent` using location + depth + `publication_reference` as child natural key (reopened — BUG-003)
- [X] T030a [US2] Write failing SC-005 schema-coverage test in `tests/test_ghfdb/test_resources/test_schema_coverage.py`: assert every column name in `GHFDB_COLUMN_ORDER` (from `constants.py`) appears as a declared `Field` in either `GHFDBParentImportResource` or `GHFDBChildImportResource` with no undocumented omissions; assert every column name also appears as a key in `ghfdb_colmeta.json`; assert `len(GHFDB_COLUMN_ORDER) == 62` (authoritative count from `ghfdb_colmeta.json`)
- [X] T066 [P] [US2] Add an authenticated admin regression test in `tests/test_ghfdb/test_resources/test_parent_import.py` asserting `GET /admin/ghfdb/ghfdb/import/` returns HTTP 200 for a staff user and renders the configured import resource options without a server error
- [X] T072 [P] [US2] Write failing normalization regression tests in `tests/test_ghfdb/test_resources/testwidgets.py`: assert `ConceptWidget.clean("[Onshore (continental)]")` returns the correct `Concept` for `"onshore (continental)"`; assert `ConceptWidget.clean("[OFFSHORE (MARINE)]")` returns the correct `Concept` for `"offshore (marine)"`; assert `MultiConceptWidget.clean("[Offshore, continental]; [Onshore (continental)]")` splits on `;` and normalises each token independently; assert that a bracketed invalid token raises a `ValueError` whose message contains the **original** bracket-wrapped text (not the stripped/lowercased form) so users can locate the error in the source file (FR-016)

### Implementation for User Story 2

- [X] T031 ⚠️ Reopened [US2] Implement leaf widgets (`ConceptWidget` — case-insensitive label lookup + cache; `MultiConceptWidget` — semicolon split + batch `ConceptWidget`; `QuantityWidget` — `Quantity(Decimal(value), unit)` ↔ `magnitude`; `YesNoWidget` — "Yes"/"No" ↔ `True`/`False`/`None`) in `project/ghfdb/resources/widgets.py`; all user-facing error message strings MUST use `gettext_lazy()` (constitution §V — i18n compliance); **add**: wrap `super().clean()` call in `ConceptWidget.clean()` with `try/except AttributeError` that re-raises a `ValueError` naming the vocabulary (reopened — BUG-007; see T080 for full widget-guard implementation)
- [X] T073 [US2] Update `ConceptWidget.clean()` and `MultiConceptWidget.clean()` in `project/ghfdb/resources/widgets.py` to apply token normalisation (FR-016): add a `normalize_vocab_token(raw: str) -> str` module-level helper that returns `raw.strip("[]").lower()`; call it on each token **before** cache lookup or database query; error messages MUST include the **original** (pre-normalisation) token text so the user can locate the value in the source file; all message strings MUST use `gettext_lazy()` (constitution §V)
- [X] T032 [US2] Implement `RelatedModelWidget` base class in `project/ghfdb/resources/widgets.py`: `__init__` accepts `model`, `field_map`, `m2m_map`, `sentinel_column`, `widget_map`; `clean()` checks sentinel → extracts + cleans scalars → `full_clean()` → `save()` → defers M2M; `set_m2m_relations(instance)` sets all M2M via widget `.clean()`; `full_clean()` `ValidationError` re-raised as `ValueError` prefixed with model name; `ValueError` prefix strings MUST use `gettext_lazy()` (constitution §V — i18n compliance)
- [X] T033 [US2] Implement `ParentWidget` in `project/ghfdb/resources/widgets.py`: `RelatedModelWidget` for `HeatFlowSite` + `Point`, sentinel `"name"`, creates/updates `Point(x=long_EW, y=lat_NS)`, all scalar (`name`, `elevation`, `environment`, `explo_method`, `total_depth_MD`→`length`, `total_depth_TVD`→`vertical_depth`, `Country`, `Region`, `Continent`, `Domain`) and M2M (`explo_purpose`) mappings per `data-model.md`
- [X] T034 ✅ Resolved (reopened — BUG-008, BUG-009) [US2] Implement `IntervalWidget` (sentinel `None`, `q_top`/`q_bottom` → `QuantityWidget("m")`, `geo_lithology`/`geo_stratigraphy` M2M), `GradientWidget` (sentinel `"T_grad_mean"`, 7 scalar + 4 M2M fields), and `ConductivityWidget` (sentinel `"tc_mean"`, 3 scalar + 7 M2M fields) in `project/ghfdb/resources/widgets.py`; sentinel check for `GradientWidget` and `ConductivityWidget` MUST treat a native `int` or `float` in the sentinel column as **present** (delegate to `QuantityWidget` which handles numeric input natively) — see T080 for the implementation detail; `geo_stratigraphy` M2M key MUST be `"age"` not `"stratigraphy"` (reopened — BUG-009; see T081)
- [X] T035 ⚠️ Reopened [US2] Implement `GHFDBParentImportResource` in `project/ghfdb/resources/parent.py`: 6 `Field` declarations (`local_id`, `value`, `uncertainty`, `comment`, `corr_HP_flag`, `sample`); `ParentWidget` instantiation; `before_import()` deduplication; `Meta` upsert strategy must be template-aware (`ID_parent` / `local_id` when present, otherwise `lat_NS` + `long_EW` for standard uploads) with transactional rollback preserved; `get_user_visible_fields()` must return fields in `PARENT_COLUMNS` order (reopened — BUG-003, BUG-005, BUG-006)
- [X] T036 ⚠️ Reopened [US2] Implement `GHFDBChildImportResource` in `project/ghfdb/resources/child.py`: 14 `Field` declarations per `data-model.md`; widget instantiations (`IntervalWidget`, `GradientWidget`, `ConductivityWidget`, `ForeignKeyWidget(ParentHeatFlow, "local_id")`); `after_save_instance()` creating 9 `HeatFlowCorrection.objects.update_or_create()` calls via `CORRECTION_COL_MAP` + `ProbeMetadata.objects.update_or_create()` when probe columns are non-empty + `widget.set_m2m_relations()` for each `RelatedModelWidget` field; `Meta` upsert strategy must be template-aware (`ID` / `local_id` when present, otherwise `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`) with transactional rollback preserved; `get_user_visible_fields()` must return fields in `GHFDB_COLUMN_ORDER` order (reopened — BUG-003, BUG-006)
- [X] T037 [US2] Update `project/ghfdb/resources/__init__.py` to publicly re-export `GHFDBParentImportResource`, `GHFDBChildImportResource`, `GHFDBExportResource`, `GHFDBImportFormat`
- [X] T038 ⚠️ Reopened [US2] Update `GHFDBChildAdmin` import integration in `project/ghfdb/admin.py`: keep `get_import_resource_classes()` returning `[GHFDBParentImportResource, GHFDBChildImportResource]` and `get_import_formats()` returning `[GHFDBImportFormat]`, but ensure all django-import-export admin hook overrides accept the request-aware method signatures required by the installed version so `/admin/ghfdb/ghfdb/import/` renders successfully (reopened — BUG-002)

### System Validation — Phase 4

- [X] T039 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [X] T039a ⚠️ CRITICAL: Run type checks: `poetry run mypy project/ghfdb/` — MUST pass with no new errors (constitution §VI)
- [X] T039b ⚠️ CRITICAL: Run linting: `poetry run ruff check project/ghfdb/` — MUST pass with zero violations (constitution §VI)
- [X] T040 ⚠️ CRITICAL: Run User Story 2 tests: `poetry run pytest tests/test_ghfdb/test_resources/testwidgets.py tests/test_ghfdb/test_resources/test_parent_import.py tests/test_ghfdb/test_resources/test_child_import.py -v` — ALL tests MUST pass, including authenticated admin import-page rendering coverage, template-without-ID regression coverage for parent and child natural-key upsert paths, files where `ID` / `ID_parent` headers are fully absent (resolved — BUG-002, BUG-003), and bracket-wrapped/mixed-case vocabulary normalisation regression coverage (FR-016, see T074)
- [X] T074 ⚠️ CRITICAL [US2] Re-run `poetry run pytest tests/test_ghfdb/test_resources/testwidgets.py -v` and confirm all normalization regression tests (T072) pass — bracketed tokens must match correctly after stripping and lowercasing, and invalid bracketed tokens must report the **original** token text in the `ValueError` message — before closing FR-016

- [X] T067 [P] [US2] Add regression tests in `tests/test_ghfdb/test_resources/test_parent_import.py` for standard upload rows without `ID_parent`: verify deduplication and re-import upsert via `lat_NS` + `long_EW`, ensure no duplicate `ParentHeatFlow`/`HeatFlowSite` rows are created, and cover files where `ID_parent` header is absent (not just blank cell values) (resolved — BUG-003)
- [X] T068 [P] [US2] Add regression tests in `tests/test_ghfdb/test_resources/test_child_import.py` for standard upload rows without `ID`/`ID_parent`: verify re-import upsert via `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`, verify different `publication_reference` values over the same site/depth interval remain distinct records, and cover files where `ID`/`ID_parent` headers are absent (resolved — BUG-003)
- [X] T069 ⚠️ Reopened [US2] Update `project/ghfdb/resources/parent.py` to remove `_effective_parent_id()`, `_normalize_decimal()`, and the synthetic-key injection in `before_import_row()`; deduplicate in `before_import()` by `(lat_NS, long_EW)` tuple directly; update `_get_or_create_site()` to look up existing `HeatFlowSite` by `location__x` / `location__y` when `ID_parent` is absent; leave `ParentHeatFlow.local_id` empty for template rows without explicit IDs; keep `Meta.import_id_fields = ("ID_parent",)` mapped to `local_id` — the confirm-page column will now show the real `local_id` or empty, not a synthetic key (reopened — BUG-005)
- [X] T070 [US2] Update `project/ghfdb/resources/child.py` so template-aware child upsert remains valid when `ID`/`ID_parent` headers are absent from uploaded files and does not fail `import_id_fields` header validation, while preserving distinct-reference matching (resolved — BUG-003)
- [X] T071 CRITICAL [US2] Re-run `poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py tests/test_ghfdb/test_resources/test_child_import.py -v` and confirm template-aware upsert passes for both blank-ID rows and truly missing `ID`/`ID_parent` headers before closing BUG-003 (resolved — BUG-003)
- [X] T075 [P] [US2] Write failing regression tests in `tests/test_ghfdb/test_resources/test_parent_import.py`: for a standard-upload import row (no `ID_parent` header), assert that after import no `ParentHeatFlow.local_id` value contains `AUTO_PARENT:`; assert that the `ID_parent` column in the dry-run result shows either the real `ParentHeatFlow.local_id` value or an empty string; add equivalent coverage in `tests/test_ghfdb/test_resources/test_child_import.py` asserting no `HeatFlow.local_id` value contains `AUTO_CHILD:` after import (BUG-005)
- [X] T076 [P] [US2] Update `project/ghfdb/resources/child.py` to remove `_effective_parent_id()`, `_effective_child_id()`, `_normalize_decimal()`, and `before_import_row()`; add `_resolve_parent_by_location(row)` to look up `ParentHeatFlow` via `HeatFlowSite.objects.filter(location__x=lon, location__y=lat)` when `ForeignKeyWidget` returns no match; depends on T069 (parent.py location-based lookup already in place before child.py resolves parents by location) (BUG-005)
- [X] T077 [P] [US2] Write failing column-order assertions in `tests/test_ghfdb/test_resources/test_parent_import.py`: assert that `GHFDBParentImportResource().get_user_visible_fields()` returns fields whose `column_name` values appear in the exact order of `PARENT_COLUMNS` (skipping any fields not present in `PARENT_COLUMNS`); add equivalent assertions in `tests/test_ghfdb/test_resources/test_child_import.py` asserting that `GHFDBChildImportResource().get_user_visible_fields()` yields `column_name` values in `GHFDB_COLUMN_ORDER` order (BUG-006)
- [X] T078 [US2] Override `get_user_visible_fields()` in `GHFDBParentImportResource` (`project/ghfdb/resources/parent.py`) to sort the list returned by `super()` by each field's `column_name` position in `PARENT_COLUMNS` (unknown `column_name` values sorted to the end); apply the equivalent override in `GHFDBChildImportResource` (`project/ghfdb/resources/child.py`) sorting by position in `GHFDB_COLUMN_ORDER`; the canonical-order lists are imported from `.formats` (BUG-006); **BUG-010 amendment**: since `GHFDB_COLUMN_ORDER` now contains mixed-case column names (`T_grad_mean`, `lat_NS`, `corr_HP_flag`), the sort dict MUST lowercase keys: `{col.lower(): i for i, col in enumerate(GHFDB_COLUMN_ORDER)}` and the field lookup MUST also lowercase `column_name`: `order.get(f.column_name.lower(), len(GHFDB_COLUMN_ORDER))`; import from `constants` not `formats` — see T098 (BUG-010)
- [X] T079 ✅ Resolved (reopened — BUG-008) [P] [US2] Update regression tests in `tests/test_ghfdb/test_resources/testwidgets.py` for numeric cell input: (1) `ConceptWidget.clean(42, row={})` raises `ValueError` whose message contains the vocabulary class name and the value `42` — **not** `AttributeError` (unchanged — BUG-007); (2) **correct BUG-008**: `GradientWidget.clean("", row={"T_grad_mean": 800, ...})` **succeeds** and returns a `ThermalGradient` with a Pint quantity `value` — replace the now-wrong `pytest.raises(ValueError)` assertion with a success assertion; (3) **correct BUG-008**: `ConductivityWidget.clean("", row={"tc_mean": 2.5, ...})` **succeeds** and returns an `IntervalConductivity` — replace the now-wrong `pytest.raises(ValueError)` assertion with a success assertion; (4) `ParentWidget.clean("", row={"name": 1, ...})` raises `ValueError` naming `"name"` column (unchanged — BUG-007, text-sentinel guard still correct)
- [X] T080 ✅ Resolved (reopened — BUG-008) [US2] Update `try/except AttributeError` type-guards in `project/ghfdb/resources/widgets.py` (BUG-007, amended by BUG-008): (1) `ConceptWidget.clean()` — keep existing guard unchanged; (2) `RelatedModelWidget.clean()` sentinel guard — **add `isinstance` bypass before the `.strip()` call**: `if isinstance(raw_sentinel, (int, float)): pass  # numeric → treat as present` — only convert `AttributeError` → `ValueError` when `raw_sentinel` is non-numeric and `.strip()` actually raises; (3) `ParentWidget.clean()` `name` guard — keep existing guard unchanged (numeric site name is always an error); all messages MUST use `gettext_lazy()` (constitution §V)

- [X] T081 ✅ Resolved [US2] Fix `IntervalWidget.m2m_map` in `project/ghfdb/resources/widgets.py`: change the key `"stratigraphy"` to `"age"` so that `geo_stratigraphy` values are stored on `HeatFlowInterval.age` (`ConceptManyToManyField(vocabulary=GeologicalTimescale)`) rather than `HeatFlowInterval.stratigraphy` (`ManyToManyField(to="stratigraphy.StratigraphicUnit")`); the latter cannot accept `research_vocabs.Concept` objects and raises `"Field 'id' expected a number but got <gts2020: ...>"` at runtime (BUG-009)
- [X] T082 ✅ Resolved [P] [US2] Add regression test for `geo_stratigraphy` in `tests/test_ghfdb/test_resources/testwidgets.py`: given a `HeatFlowInterval` instance saved to the DB and an `IntervalWidget` whose `_last_row` contains `"geo_stratigraphy": "Holocene"`, assert that `set_m2m_relations(interval)` completes without error and that `interval.age.filter(name="Holocene").exists()` returns `True` (BUG-009); also add a child-import integration assertion in `tests/test_ghfdb/test_resources/test_child_import.py` that a row with `geo_stratigraphy="Holocene"` imports successfully
- [X] T083 ✅ Resolved ⚠️ CRITICAL [US2] Re-run `poetry run pytest tests/test_ghfdb/test_resources/testwidgets.py tests/test_ghfdb/test_resources/test_child_import.py -v` and confirm all geo_stratigraphy regression tests (T082) pass — non-empty `geo_stratigraphy` values must set `HeatFlowInterval.age`, not raise a type error — before closing BUG-009

**Checkpoint — US2 Complete (BUG-003 resolved 2026-04-15)**: Template-aware natural-key upsert verified for both blank-ID rows and uploads where `ID` / `ID_parent` headers are entirely absent. All 25 import resource tests pass.

> **SC-003 Manual QA Gate** (not automated): Before marking this feature release-ready, manually import a 10,000-row GHFDB XLSX and confirm the complete error report is delivered within 60 seconds.

---

## Phase 4a: Second Import Format — Simple Template (US2)

**Purpose**: Add `GHFDBSimpleImportFormat` for XLSX files with 5 metadata rows, headers at row 6, and data from row 7 (no unit-label or allowed-range skip rows). Expose both format classes in the admin import page so staff can select the correct layout before uploading.

**Depends on**: Phase 4 complete

### Tests for Phase 4a ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T084 [P] [US2] Write failing `GHFDBSimpleImportFormat` unit tests in `tests/test_ghfdb/test_resources/test_parent_import.py`: use `openpyxl` to build an in-memory workbook whose sheet `"data list"` has rows 1–5 as arbitrary metadata text, row 6 as column headers matching the first few entries of `GHFDB_COLUMN_ORDER`, and rows 7–8 as genuine data rows; call `GHFDBSimpleImportFormat().create_dataset(stream)` and assert (a) the returned `tablib.Dataset` has exactly 2 data rows, (b) no metadata-row content (e.g. the text `"metadata"`) appears as a data cell value, and (c) column headers match row 6 of the workbook
- [X] T085 [P] [US2] Write failing admin format-selection tests in `tests/test_ghfdb/test_resources/test_parent_import.py`: instantiate `GHFDBAdmin(GHFDB, AdminSite())` and assert `get_import_formats()` returns a list of exactly 2 items; assert the first item's `get_title()` (or class name) is `"GHFDB Official Template"` and the second is `"GHFDB Simple Template"`; assert `GET /admin/ghfdb/ghfdb/import/` for a staff user returns HTTP 200 and the response body contains both format title strings

### Implementation for Phase 4a

- [X] T086 [US2] Implement `GHFDBSimpleImportFormat` in `project/ghfdb/resources/formats.py`: subclass `GHFDBImportFormat`; override `create_dataset()` replacing `ws.iter_rows(min_row=9)` with `ws.iter_rows(min_row=7)` (skip only the 5 metadata rows, not rows 7–8); override `get_title()` to return `"GHFDB Simple Template"`; also add `get_title()` to the existing `GHFDBImportFormat` returning `"GHFDB Official Template"` so both formats appear with distinct human-readable labels in the admin dropdown
- [X] T087 [US2] Update `GHFDBAdmin.get_import_formats()` in `project/ghfdb/admin.py` to return `[GHFDBImportFormat, GHFDBSimpleImportFormat]`; add `GHFDBSimpleImportFormat` to the import from `project/ghfdb/resources`
- [X] T088 [US2] Update `project/ghfdb/resources/__init__.py` to add `GHFDBSimpleImportFormat` to the public re-exports alongside `GHFDBImportFormat`

### System Validation — Phase 4a

- [X] T089 ⚠️ CRITICAL: Run Django system checks: `poetry run python manage.py check` — MUST pass before proceeding
- [X] T089a ⚠️ CRITICAL [US2] Re-run `poetry run pytest tests/test_ghfdb/test_resources/ -v` — all existing Phase 4 tests MUST remain green and new format-selection and simple-template tests (T084, T085) MUST also pass

### Round-trip Coverage — Phase 4a

- [X] T090 [P] [US2] Update `tests/test_ghfdb/test_resources/test_roundtrip.py` (SC-001): add a second round-trip pass using the simple-template layout — create an in-memory XLSX with 5 metadata rows, headers at row 6, and the same data rows as `sample_ghfdb.xlsx` starting at row 7; import via `GHFDBParentImportResource` then `GHFDBChildImportResource` with a `GHFDBSimpleImportFormat` stream; assert the same records are created and that an export through `GHFDBExportResource` produces output identical to the official-template round-trip

**Checkpoint — Phase 4a Complete**: `GHFDBSimpleImportFormat` verified; admin import page presents both named format options; all format-selection and simple-template round-trip tests pass.

---

## Phase 4b: BUG-010 — Canonical Constants Alignment

**Purpose**: Remove the stale hardcoded `GHFDB_COLUMN_ORDER` tuple from `constants.py`; rename all stale annotation keys in `GHFDBChildQuerySet.as_ghfdb_flat()` to match canonical names; add `GHFDBParentQuerySet.as_ghfdb_flat()`; fix two-sided case-insensitive column ordering in `child.py`; update stale `attribute=` values in `export.py`. These changes make `constants.py` the single source of truth for the GHFDB spreadsheet column structure.

**Depends on**: Phase 3.5 complete

### Tests for Phase 4b ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T091 [P] Write failing schema-coverage tests in `tests/test_ghfdb/test_resources/test_schema_coverage.py`: assert `GHFDB_COLUMN_ORDER` is a `list` (not `tuple`); assert `GHFDB_COLUMN_ORDER == PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS`; assert case-sensitive names such as `"lat_NS"`, `"T_grad_mean"`, `"corr_HP_flag"` appear correctly cased (BUG-010)
- [X] T092 [P] Write failing queryset annotation tests in `tests/test_ghfdb/test_resources/` (new file `test_managers.py`): call `.as_ghfdb_flat()` on a `GHFDBChildQuerySet` and assert annotation keys match canonical names (e.g. `"lat_NS"` not `"lat_ns"`, `"q"` not `"p_q"`, `"name"` not `"site_name"`, `"corr_HP_flag"` not `"p_corr_hp_flag"`); assert `GHFDBParentQuerySet` exposes `as_ghfdb_flat()` and its keys match `PARENT_COLUMNS` names (BUG-010)
- [X] T093 [P] Write failing case-sensitivity test in `tests/test_ghfdb/test_resources/test_child_import.py`: call `GHFDBChildImportResource().get_user_visible_fields()`; assert fields with `column_name` values `"T_grad_mean"`, `"lat_NS"`, `"corr_IS_flag"` appear at correct ordinal positions (not sorted to end) (BUG-010)
- [X] T094 [P] Write failing export attribute tests in `tests/test_ghfdb/test_resources/test_export.py`: assert `GHFDBExportResource` field attributes match renamed annotation keys — e.g. `fields["q"].attribute == "q"` not `"p_q"`, `fields["name"].attribute == "name"` not `"site_name"`, `fields["elevation"].attribute == "elevation"` not `"site_elevation"` (BUG-010)

### Implementation for Phase 4b

- [X] T095 Remove old `GHFDB_COLUMN_ORDER: tuple[str, ...]` from `project/ghfdb/constants.py`; update module docstring to document all four canonical lists (`PARENT_COLUMNS`, `CHILD_COLUMNS`, `META_FIELDS`, `GHFDB_COLUMN_ORDER`) (BUG-010)
- [X] T096 Rename stale annotation keys in `GHFDBChildQuerySet.as_ghfdb_flat()` in `project/ghfdb/managers.py`: `"id_parent"` → `"ID_parent"`, `"p_q"` → `"q"`, `"p_q_uncertainty"` → `"q_uncertainty"`, `"site_name"` → `"name"`, `"site_elevation"` → `"elevation"`, `"site_environment"` → `"environment"`, `"p_corr_hp_flag"` → `"corr_HP_flag"`, `"total_depth_md"` → `"total_depth_MD"`, `"total_depth_tvd"` → `"total_depth_TVD"`, `"site_explo_method"` → `"explo_method"`; retain `site_country`, `site_region`, `site_continent`, `site_domain` (BUG-010)
- [X] T097 Add `GHFDBParentQuerySet.as_ghfdb_flat()` and `GHFDBParentManager.as_ghfdb_flat()` delegate to `project/ghfdb/managers.py`; annotate all scalar `PARENT_COLUMNS` fields from `ParentHeatFlow` and `HeatFlowSite` model paths using canonical `PARENT_COLUMNS` names as annotation keys (BUG-010)
- [X] T098 [P] Fix `get_user_visible_fields()` in `project/ghfdb/resources/child.py`: build the sort lookup dict as `{col.lower(): i for i, col in enumerate(GHFDB_COLUMN_ORDER)}` and look up each field as `order.get(f.column_name.lower(), len(GHFDB_COLUMN_ORDER))`; import `GHFDB_COLUMN_ORDER` from `project.ghfdb.constants` (BUG-010)
- [X] T099 Update all stale `attribute=` values and `dehydrate_*` `getattr` calls in `project/ghfdb/resources/export.py` to match the renamed annotation keys from T096 (BUG-010)

### System Validation — Phase 4b

- [X] T100 ⚠️ CRITICAL: `poetry run python manage.py check ; poetry run mypy project/ghfdb/` — MUST pass before proceeding to Phase 5 (BUG-010)
- [X] T101 ⚠️ CRITICAL: `poetry run pytest tests/test_ghfdb/ -v` — all tests including T091–T094 MUST pass before proceeding to Phase 5 (BUG-010)

**Checkpoint — Phase 4b Complete**: Canonical constants aligned; all `as_ghfdb_flat()` annotation keys match canonical names; `get_user_visible_fields()` column ordering is case-insensitive on both sides; export `attribute=` values updated; all tests pass.

---

## Phase 5: User Story 3 — Export Heat Flow Data to GHFDB Format (Priority: P2)

**Goal**: Staff can trigger an export from the Django admin that produces a valid GHFDB-format XLSX with all **62** columns in the canonical order, semicolons for M2M fields, and plain SI numeric values for Pint quantity fields.

**Independent Test**: `poetry run pytest tests/test_ghfdb/test_resources/test_export.py -v`

### Tests for User Story 3 ⚠️ Write FIRST — verify they FAIL before implementing

- [X] T041 [P] [US3] Write failing tests in `tests/test_ghfdb/test_resources/test_export.py`: column set matches all **62** entries in `GHFDB_COLUMN_ORDER`; column order is identical to `GHFDB_COLUMN_ORDER`; Pint quantity field (`q`, `tc_mean`, etc.) renders as plain numeric magnitude (no unit symbol); M2M field (`q_method`, `tc_method`) renders as semicolon-separated labels; `get_queryset()` returns `GHFDB.objects.for_export()`; filtered queryset only exports matching records; staff-only access (anonymous admin export URL → 302)

### Implementation for User Story 3

- [X] T042 [US3] Implement `GHFDBExportResource` class scaffold in `project/ghfdb/resources/export.py`: `Meta` class (`model = GHFDB`, `export_order = GHFDB_COLUMN_ORDER` tuple imported from `formats.py`), `get_queryset()` returning `GHFDB.objects.for_export()`, all **62** explicit `Field` declarations with `attribute` pointing to annotation names from the `data-model.md` mapping table
- [X] T043 [US3] Implement `dehydrate_*` methods for all Pint quantity fields in `project/ghfdb/resources/export.py` (e.g. `dehydrate_q`, `dehydrate_q_uncertainty`, `dehydrate_tc_mean`, `dehydrate_tc_uncertainty`, `dehydrate_T_grad_mean`, `dehydrate_T_grad_uncertainty`, `dehydrate_T_grad_mean_cor`, etc.): `return obj.<annotation>.magnitude if obj.<annotation> else ""`
- [X] T044 [US3] Implement `dehydrate_*` methods for all M2M fields in `project/ghfdb/resources/export.py` (e.g. `dehydrate_q_method`, `dehydrate_explo_purpose`, `dehydrate_T_method_top`, `dehydrate_T_corr_top`, `dehydrate_tc_source`, etc.): `return "; ".join(c.label for c in obj.<prefetch_name>.all()) if ... else ""`; add `None`-guard on all dehydrate methods to return `""` not `"None"`
- [X] T045 [US3] Update `GHFDBChildAdmin.get_export_resource_classes()` to return `[GHFDBExportResource]` and `get_export_formats()` to return `[XLSX]` in `project/ghfdb/admin.py`

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
- [X] T060 [P] Add Fuchs et al. (2021) and Fuchs et al. (2023) inline citations to `GHFDBParentImportResource`, `GHFDBChildImportResource`, and `GHFDBExportResource` class docstrings in their respective module files; **also** add a module-level docstring to `project/ghfdb/resources/widgets.py` citing both references and summarising the widget hierarchy (leaf widgets → `RelatedModelWidget` → specialised sub-model widgets)

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
| Phase 4 — US2 Import (P2) | Phase 3.5 | Phase 4a, Phase 6 (round-trip) |
| Phase 4a — Second Import Format (US2) | Phase 4 | Phase 6 (round-trip) |
| Phase 4b — BUG-010 Canonical Constants Alignment | Phase 3.5 | Phase 5 (export attribute=), Phase 6 (round-trip) |
| Phase 5 — US3 Export (P2) | Phase 3.5 + 002 (`for_export()`) + Phase 4b (annotation keys) | Phase 6 (round-trip) |
| Phase 6 — Polish & Round-trip | Phase 4 + Phase 4a + Phase 4b + Phase 5 | Nothing |
