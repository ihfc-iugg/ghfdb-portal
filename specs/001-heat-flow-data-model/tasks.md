# Tasks: GHFDB Normalized Relational Data Model

**Input**: Design documents from `/specs/001-heat-flow-data-model/`
**Feature Branch**: `001-heat-flow-data-model`
**Generated**: 2026-04-09
**Propagated**: 2026-04-22 — `ghfdb_id`/`quality` added to `ParentHeatFlow` and `HeatFlow`; `is_ghfdb`/`local_id` removed. Amendment tasks T062–T067 added. T044 and T050 annotated with required corrections.
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no hard execution dependency)
- **[Story]**: User story this task belongs to (US1–US5)
- Tasks without `[P]` must be completed in order within a phase
- File paths are relative to the repository root

---

## Phase 1: Setup

**Purpose**: Confirm the development environment is working before touching any code.

- [x] T001 Verify environment: `poetry run python manage.py check` — note any pre-existing errors (expected: some warnings/errors from stale factory fields; record them as a baseline before Phase 2 changes)

### System Validation — Phase 1

- [x] T002 ⚠️ CRITICAL: Document baseline check output — Phase 2 cleanup must bring this to zero errors

**Checkpoint — Setup Complete**: Baseline recorded. Proceed to Phase 2.

---

## Phase 2: Foundational — Model Cleanup (Blocking Prerequisites)

**Purpose**: Remove stale/incorrect model fields and relationships that block all user stories. Every US depends on a correct model structure. These changes are **prerequisites** for writing any meaningful tests.

> **Note**: The existing `HeatFlowFactory` references fields that do not exist on the model (`probe_penetration`, `probe_length`, `probe_tilt`, `corr_S_flag_vocab`, `corr_E_flag_vocab`, etc.). These cause `AttributeError` at factory call time. The HeatFlow model also has `OneToOneField` relationships that spec FR-013 requires to be `ForeignKey`. Both must be fixed before any test can pass.

- [x] T003 In `project/heat_flow/factories.py` — remove stale field references from `HeatFlowFactory`: delete `probe_penetration`, `probe_length`, `probe_tilt`, `water_temperature` (probe context), and all `corr_*_flag` / `corr_*_flag_vocab` lines that reference non-existent HeatFlow fields (R10); **also** in `project/heat_flow/models/child.py` — update `HeatFlowQuerySet.with_related_data()`: change `select_related("probe_metadata")` → `select_related("sample__probe_metadata")`; update `probe_measurements()` filter `probe_metadata__isnull=False` → `sample__probe_metadata__isnull=False`; update `borehole_measurements()` identically — `ProbeMetadata` links to `HeatFlowInterval` (the `sample` FK on `HeatFlow`), not to `HeatFlow` directly (A3)

- [x] T004 In `project/heat_flow/models/child.py` — change `HeatFlow.thermal_gradient` from `OneToOneField` to `ForeignKey("heat_flow.ThermalGradient", on_delete=models.PROTECT, related_name="heat_flow_children", null=True, blank=True)` per FR-013 / R5; use **PROTECT** (not CASCADE) to prevent a `ThermalGradient` from being deleted while any `HeatFlow` still references it — required to support shared sub-measurement reuse (FR-013, A2); verify no code references the old OneToOne reverse accessor `heat_flow_child` before renaming to `heat_flow_children` (A8)

- [x] T005 [P] In `project/heat_flow/models/child.py` — change `HeatFlow.thermal_conductivity` from `OneToOneField` to `ForeignKey("heat_flow.IntervalConductivity", on_delete=models.PROTECT, related_name="heat_flow_children", null=True, blank=True)` per FR-013 / R5; same PROTECT rationale as T004; verify no code references the old reverse accessor `heat_flow_child` on `IntervalConductivity` before renaming (A2, A8)

- [x] T006 In `project/heat_flow/models/child.py` — make `ThermalGradient.value` non-nullable: remove `null=True, blank=True` from the field definition; keep all validators; add `blank=False` explicitly per R3 (primary scientific datum cannot be NULL)

- [x] T007 [P] In `project/heat_flow/models/child.py` — make `IntervalConductivity.value` non-nullable: remove `null=True, blank=True`; keep all validators per R3

- [x] T008 In `project/heat_flow/models/child.py` — remove `IGSN` field from `HeatFlow` model entirely (per spec.md spec clarification Session 2026-04-10: IGSN belongs on Sample, not Measurement; FR-010)

- [x] T009 In `project/heat_flow/migrations/` — create Django migration for all T004–T008 field changes: `poetry run python manage.py makemigrations heat_flow --name ghfdb_data_model_cleanup`

### System Validation — Phase 2

- [x] T010 ⚠️ CRITICAL: `poetry run python manage.py check` — must produce zero errors before proceeding to any user story
- [x] T011 ⚠️ CRITICAL: `poetry run python manage.py migrate` — all migrations must apply cleanly on development database

**Checkpoint — Foundation Ready**: System checks pass, migrations apply. User story phases can begin.

---

## Phase 3: User Story 1 — Site and Measurement Data Can Be Stored and Retrieved (Priority: P1) 🎯 MVP

**Goal**: Complete site → interval → (gradient + conductivity) → child heat flow + parent heat flow object graph can be created and retrieved with correct field values and relationship resolution.

**Independent Test**: A single `@pytest.mark.django_db` test that creates one `HeatFlowSite`, one `ParentHeatFlow` linked to it, one `HeatFlowInterval`, one `ThermalGradient` and one `IntervalConductivity` both linked to the interval, one `HeatFlow` child referencing parent + gradient + conductivity, verifies forward/reverse FK resolution, and asserts that `save()` raises `ValidationError` when a wrong sample type is assigned.

### Tests for User Story 1 ⚠️ Write FIRST — ensure they FAIL before implementing T021–T023

- [x] T012 [P] [US1] In `tests/test_heat_flow/conftest.py` — add (or update) module-level pytest fixtures that construct the complete object graph using direct `.objects.create()` calls (NOT factories): `site_fixture`, `interval_fixture`, `gradient_fixture`, `conductivity_fixture`, `parent_fixture`, `child_fixture`; these fixtures are shared across US1–US3 tests

- [x] T013 [P] [US1] In `tests/test_heat_flow/test_models.py` — write test `test_heat_flow_site_persistence`: create a `HeatFlowSite` with `name`, `country`, `continent`, `environment`, `explo_method`, and a `location` `Point` geometry (`from django.contrib.gis.geos import Point`; e.g. `Point(8.5, 47.4)`); persist; reload from DB; assert all field values match, including `site.location is not None` and the coordinate values; also write `test_heat_flow_site_explo_purpose_m2m`: after creation call `site.explo_purpose.add(<a vocabulary concept instance>)`, reload from DB, assert `site.explo_purpose.count() == 1` — this is the only M2M relationship on `HeatFlowSite` (FR-002, FR-003, H2, US1 scenario 1, SC-003)

- [x] T014 [P] [US1] In `tests/test_heat_flow/test_models.py` — write test `test_interval_links_to_site`: create `HeatFlowInterval` with `sample=site`, `top=0`, `bottom=500`; assert `interval.sample == site` and that the reverse FK from site to interval resolves; **before writing**: verify the exact `related_name` of the inherited `sample` FK by inspecting `fairdm/core/models.py` — if not `"measurements"` update the assertion accordingly (US1 scenario 2, A9)

- [x] T015 [P] [US1] In `tests/test_heat_flow/test_models.py` — write test `test_sub_measurements_on_interval`: create `ThermalGradient(sample=interval, value=25.0)` and `IntervalConductivity(sample=interval, value=2.5)`; assert both are retrievable via `interval.measurements.all()`; assert `gradient.value` is a Pint `Quantity` object with `gradient.value.magnitude == 25.0`; assert `interval.top` and `interval.bottom` are Pint `Quantity` objects by checking `hasattr(interval.top, "magnitude")` (FR-006, A5, US1 scenario 3)

- [x] T016 [P] [US1] In `tests/test_heat_flow/test_models.py` — write test `test_heat_flow_child_relationships`: create `HeatFlow` with `sample=interval`, `parent=parent`, `thermal_gradient=gradient`, `thermal_conductivity=conductivity`; assert `child.sample == interval`, `child.parent == parent`, `child.thermal_gradient == gradient`, `child.thermal_conductivity == conductivity`, `parent.children.filter(pk=child.pk).exists()`; also assert default quality score values `child.U_score == UScoreOptions.Ux` and `child.M_score == MScoreOptions.Mx` on a freshly created instance (FR-014, A11, US1 scenario 4)

- [x] T017 [P] [US1] In `tests/test_heat_flow/test_models.py` — write test `test_heat_flow_corrections`: create two `HeatFlowCorrection` records on a `HeatFlow` child; assert `child.corrections.count() == 2` (US1 scenario 5)

- [x] T018 [P] [US1] In `tests/test_heat_flow/test_models.py` — write tests for `save()` type validation:
  - `test_heat_flow_save_rejects_wrong_sample`: set `child.sample = site` (a `HeatFlowSite`) and call `.save()` → expect `ValidationError` (FR-010a)
  - `test_thermal_gradient_save_rejects_wrong_sample`: set `gradient.sample = site` → expect `ValidationError` (FR-016a)
  - `test_interval_conductivity_save_rejects_wrong_sample`: set `conductivity.sample = site` → expect `ValidationError` (FR-018a)

- [x] T019 [P] [US1] In `tests/test_heat_flow/test_models.py` — write test `test_value_non_nullable`: assert that `ThermalGradient.objects.create(sample=interval)` raises `IntegrityError` (or `ValidationError` if enforced at Django level before DB) when `value` is not provided; same for `IntervalConductivity` (R3)

- [x] T020 [P] [US1] In `tests/test_heat_flow/test_models.py` — write two tests:
  - `test_multiple_heatflow_can_share_gradient`: create two `HeatFlow` instances both referencing the same `ThermalGradient` FK; assert both can be saved without `IntegrityError` (FR-013 / R5)
  - `test_heat_flow_allows_null_gradient_and_conductivity`: create `HeatFlow(sample=interval, thermal_gradient=None, thermal_conductivity=None)` and call `.save()` → assert `pk is not None` and no exception is raised; spec Edge Case 2: "a `HeatFlow` child with neither gradient nor conductivity MUST be allowed (incomplete records MUST NOT be blocked at entry time)" (EC-002, M2)

- [x] T053 [US1] ⚠️ Write tests FIRST (ensure they fail before implementing `clean()`): in `tests/test_heat_flow/test_models.py` write `test_zero_thickness_interval_rejected` — create `HeatFlowInterval(sample=site, top=100, bottom=100)` and call `.full_clean()` → assert `ValidationError`; write `test_valid_interval_passes` — create `HeatFlowInterval(sample=site, top=0, bottom=500)` and call `.full_clean()` → assert no exception; **then implement**: add `clean(self)` method to `HeatFlowInterval` in `project/heat_flow/models/child.py` that raises `ValidationError(_("Interval bottom depth must be greater than top depth"))` if `self.top is not None and self.bottom is not None and self.top >= self.bottom`; ensure `HeatFlowInterval` calls `super().clean()` if a base `clean()` exists (spec.md EC-001, M4)

### Implementation for User Story 1

- [x] T021 [US1] In `project/heat_flow/models/child.py` — add `save(self, *args: Any, **kwargs: Any) -> None:` method to `HeatFlow` (add `from typing import Any` if not already imported); raise `ValidationError(_("sample must be a HeatFlowInterval"))` if `self.sample_id` is set and `not isinstance(self.sample, HeatFlowInterval)`; call `super().save(*args, **kwargs)` (FR-010a / R7, A12)

- [x] T022 [P] [US1] In `project/heat_flow/models/child.py` — add `save(self, *args: Any, **kwargs: Any) -> None:` method to `ThermalGradient`; raise `ValidationError(_("sample must be a HeatFlowInterval"))` if `self.sample_id` is set and `not isinstance(self.sample, HeatFlowInterval)`; call `super().save(*args, **kwargs)` (FR-016a / R7, A12)

- [x] T023 [P] [US1] In `project/heat_flow/models/child.py` — add `save(self, *args: Any, **kwargs: Any) -> None:` method to `IntervalConductivity`; raise `ValidationError(_("sample must be a HeatFlowInterval"))` if `self.sample_id` is set and `not isinstance(self.sample, HeatFlowInterval)`; call `self.calculate_score()` then `super().save(*args, **kwargs)`; preserve existing `calculate_score()` call behaviour (FR-018a / R7, A12)

### System Validation — Phase 3

- [x] T024 ⚠️ CRITICAL: `poetry run python manage.py check` — must pass before proceeding
- [x] T025 ⚠️ CRITICAL: `poetry run pytest tests/test_heat_flow/test_models.py -v -k "us1 or persistence or site or interval or gradient or conductivity or correction or relationships or non_nullable or share_gradient"` — ALL US1 tests must pass

**Checkpoint — US1 Complete**: Site → interval → (gradient + conductivity) → child heat flow persistence and retrieval fully functional.

---

## Phase 4: User Story 2 — Parent-Child Aggregation Relationship Is Correctly Modeled (Priority: P2)

**Goal**: Multiple child `HeatFlow` determinations can be associated with a single `ParentHeatFlow`; `is_relevant` filtering works; `ParentHeatFlow` uniqueness per site is enforced at both DB and application layers.

**Independent Test**: Create one `ParentHeatFlow` linked to three `HeatFlow` children (two `is_relevant=True`, one `False`). Assert `parent.children.all()` returns 3 and `parent.children.filter(is_relevant=True)` returns 2. Delete the parent; assert each child's `.parent` becomes `None`.

### Tests for User Story 2 ⚠️ Write FIRST — ensure they FAIL before implementing T030–T032

- [x] T026 [P] [US2] In `tests/test_heat_flow/test_models.py` — write test `test_parent_children_aggregation`: create one `ParentHeatFlow`, two children with `is_relevant=True`, one with `is_relevant=False`; assert `parent.children.count() == 3`; assert `parent.children.filter(is_relevant=True).count() == 2` (US2 Independent Test / US2 scenarios 1–2)

- [x] T027 [P] [US2] In `tests/test_heat_flow/test_models.py` — write test `test_parent_delete_sets_child_null`: create `ParentHeatFlow` with linked child; delete parent via `.delete()`; reload child from DB; assert `child.parent_id is None` (SET_NULL; US2 scenario 3, SC-004)

- [x] T028 [P] [US2] In `tests/test_heat_flow/test_models.py` — write tests for uniqueness enforcement:
  - `test_unique_parent_per_site_db_level`: create and save a `ParentHeatFlow(sample=site)`, then bypass `save()` entirely using `ParentHeatFlow.objects.bulk_create([ParentHeatFlow(sample_id=site.pk)])` → expect `django.db.IntegrityError` from the DB-level `UniqueConstraint`; **note**: cannot test via `.save()` because `ParentHeatFlow.save()` raises `ValidationError` before the DB is ever reached (H1)
  - `test_unique_parent_per_site_app_level`: create a second `ParentHeatFlow(sample=site)` and call `.save()` → expect `django.core.exceptions.ValidationError` from the uniqueness check in `ParentHeatFlow.save()` (app-layer guard)
  - `test_parent_with_zero_children_is_valid`: create `ParentHeatFlow` with no children; assert `.children.count() == 0` (edge case from spec)

- [x] T029 [P] [US2] In `tests/test_heat_flow/test_models.py` — write test `test_parent_save_rejects_wrong_sample`: set `parent.sample = interval` (a `HeatFlowInterval`) and call `.save()` → expect `ValidationError` (FR-008a)

### Implementation for User Story 2

- [x] T030 [US2] ~~`UniqueConstraint` reverted — SQLite MTI limitation: `sample_id` lives on the base `measurement_measurement` table, not on `ghfdb_parentheatflow`, so `UNIQUE` constraint causes `OperationalError: expressions prohibited in PRIMARY KEY and UNIQUE constraints`. App-level `save()` uniqueness check is the only enforcement.~~ In `project/heat_flow/models/parent.py` — add `UniqueConstraint(fields=["sample"], name="unique_parent_per_site")` to `ParentHeatFlow.Meta.constraints` list; create a `class Meta` block if not present (FR-009 / R6; note: the `sample` field is declared in fairdm package — `unique=True` on the field is not safe; use `UniqueConstraint` in Meta)

- [x] T031 [P] [US2] In `project/heat_flow/models/parent.py` — update `ParentHeatFlow.save()` signature to `save(self, *args: Any, **kwargs: Any) -> None:` (add `from typing import Any`); before the existing uniqueness check, raise `ValidationError(_("sample must be a HeatFlowSite"))` if `self.sample_id` is set and `not isinstance(self.sample, HeatFlowSite)`; note: `HeatFlowSite` is defined in the same file — no import needed (FR-008a / R7, A12)

- [x] T032 [US2] Migration created as `0008_update_parent_heat_flow_meta.py` (verbose_name change; constraint omitted due to SQLite MTI limitation — see T030 note)

### System Validation — Phase 4

- [x] T033 ⚠️ CRITICAL: `poetry run python manage.py check` — must pass before proceeding
- [x] T034 ⚠️ CRITICAL: `poetry run pytest tests/test_heat_flow/test_models.py -v -k "aggregation or parent or unique or zero_children"` — ALL US2 tests must pass

**Checkpoint — US2 Complete**: Parent-child aggregation semantics and uniqueness enforcement fully functional.

---

## Phase 5: User Story 3 — Marine Probe Measurements Have Supplementary Metadata (Priority: P3)

**Goal**: `ProbeMetadata` records can be attached to `HeatFlowInterval`, all probe fields are retrievable, cascade deletion works, and `HeatFlow.is_probe` correctly reports whether the associated interval has probe metadata.

**Independent Test**: Create a `HeatFlowInterval` with an attached `ProbeMetadata`; assert `interval.probe_metadata` resolves correctly; assert `child.is_probe` is `True`; delete the interval and assert the `ProbeMetadata` record is also deleted.

### Tests for User Story 3 ⚠️ Write FIRST — ensure they FAIL before implementing T039

- [x] T035 [P] [US3] In `tests/test_heat_flow/test_models.py` — write test `test_probe_metadata_linked_to_interval`: create `ProbeMetadata(interval=interval, penetration=3.5, length=5.0, tilt=2.0)`; assert `interval.probe_metadata.penetration` and `interval.probe_metadata.length` and `interval.probe_metadata.tilt` all return expected values (US3 scenario 1)

- [x] T036 [P] [US3] In `tests/test_heat_flow/test_models.py` — write test `test_interval_without_probe_raises`: create a fresh `HeatFlowInterval` with no `ProbeMetadata`; assert accessing `interval.probe_metadata` raises `RelatedObjectDoesNotExist` (US3 scenario 2)

- [x] T037 [P] [US3] In `tests/test_heat_flow/test_models.py` — write test `test_probe_metadata_cascade_on_interval_delete`: create `ProbeMetadata` linked to an interval; delete the interval; assert `ProbeMetadata.objects.filter(pk=probe_pk).exists()` is `False` (CASCADE; US3 scenario 3, SC-004)

- [x] T038 [P] [US3] In `tests/test_heat_flow/test_models.py` — write test `test_heat_flow_is_probe_property`: with probe metadata attached to interval, create `HeatFlow(sample=interval)`; assert `child.is_probe` is `True`; with a different interval (no probe metadata) assert `is_probe` is `False` (US3 Independent Test)

### Implementation for User Story 3

- [x] T039 [US3] In `project/heat_flow/models/child.py`:
  - Fix `ProbeMetadata.__str__` method: change `self.heat_flow` to `self.interval` (the actual field name on the model)
  - Fix `HeatFlow.is_probe` cached property: change `hasattr(self, 'probe_metadata')` to `hasattr(self.sample, 'probe_metadata') and self.sample.probe_metadata is not None` so it correctly traverses through `self.sample` (the `HeatFlowInterval`) to find its probe metadata
  - Verify `ProbeMetadata.interval` FK has `on_delete=CASCADE` and `related_name="probe_metadata"` (these are already correct per existing code — confirm and leave unchanged if so)

### System Validation — Phase 5

- [x] T040 ⚠️ CRITICAL: `poetry run python manage.py check` — must pass before proceeding
- [x] T041 ⚠️ CRITICAL: `poetry run pytest tests/test_heat_flow/test_models.py -v -k "probe"` — ALL US3 tests must pass

**Checkpoint — US3 Complete**: Marine probe metadata model and property behaviour fully functional.

---

## Phase 6: User Story 4 — All Models Are Registered with FairDM (Priority: P4)

**Goal**: All six FairDM `Sample`/`Measurement` subclasses (`HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`) are registered with the FairDM registry. `python manage.py check` returns zero errors.

**Independent Test**: `fairdm.registry.get_config(ParentHeatFlow)` and `fairdm.registry.get_config(IntervalConductivity)` both return non-`None` config objects. `python manage.py check` exits with zero errors.

### Tests for User Story 4 ⚠️ Write FIRST — ensure they FAIL before implementing T044–T046

- [x] T042 [US4] Create `tests/test_heat_flow/test_config.py` — write tests:
  - `test_all_six_models_registered`: import `fairdm` and all six models; for each model call `fairdm.registry.get_config(Model)` and assert result is not `None` (US4 scenario 1, FR-030, SC-005)
  - `test_registry_config_has_fields`: for **all six registered models** (`HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`) get the config via `fairdm.registry.get_config(Model)` and assert `bool(config.fields) is True` (non-empty); FR-024 requires all registered models to declare a `fields` list (M3)

- [x] T043 [P] [US4] In `tests/test_heat_flow/test_config.py` — write test `test_system_checks_pass`: use Django's `call_command("check")` or `from django.core.management import call_command; call_command("check")` and assert no `SystemCheckError` is raised (US4 scenario 2, SC-001)

### Implementation for User Story 4

- [x] T044 [US4] In `project/heat_flow/config.py` — add `ParentHeatFlow` to the existing imports block; create `@fairdm.register` decorated `ParentHeatFlowConfig(IHFCConfig)` with:
  - `model = ParentHeatFlow`
  - `description` (descriptive string in `_()`)
  - `fields = ["value", "uncertainty", "corr_HP_flag", "comment",` ~~`"is_ghfdb"`~~ `"ghfdb_id", "quality"]` ← **⚠️ Correction required — see T064**: original implementation used `"is_ghfdb"` which no longer exists on the model; must be replaced with `"ghfdb_id"` and `"quality"`
  - Inherits `authority` and `citation` from `IHFCConfig` (FR-023 / FR-024 / R8)
  - **FR-024 also requires `filterset_class` and `table_class`**: verify whether FairDM auto-generates these from `fields`; if not, create `ParentHeatFlowFilterSet` in `project/heat_flow/filters.py` and `ParentHeatFlowTable` in `project/heat_flow/tables.py` following the existing patterns for `HeatFlowFilterSet`/`HeatFlowTable`; confirm by asserting `config.filterset_class is not None` in T042 (M1)

- [x] T045 [P] [US4] In `project/heat_flow/config.py` — add `IntervalConductivity` to the existing imports block; create `@fairdm.register` decorated `IntervalConductivityConfig(IHFCConfig)` with:
  - `model = IntervalConductivity`
  - `description` (descriptive string in `_()`)
  - `fields = ["value", "uncertainty", "source", "method", "saturation", "number", "score"]`
  - Inherits `authority` and `citation` from `IHFCConfig` (FR-025 / R8)
  - **FR-024 also requires `filterset_class` and `table_class`**: same guidance as T044 — verify FairDM auto-generation; if manual creation is required, add `IntervalConductivityFilterSet` in `filters.py` and `IntervalConductivityTable` in `tables.py` following existing patterns (M1)

- [x] T046 [P] [US4] In `project/heat_flow/config.py` — verify `HeatFlowConfig.fields` contains no deleted fields (current list `[("value", "uncertainty"), "method", "expedition", "c_comment"]` does not reference `IGSN` or `corr_*` flags — this task is likely a no-op; confirm by inspection); consider adding `"date_acquired"` and `"is_relevant"` to `HeatFlowConfig.fields` for detail view completeness (A6)

### System Validation — Phase 6

- [x] T047 ⚠️ CRITICAL: `poetry run python manage.py check` — must return zero errors and zero warnings (SC-001)
- [x] T048 ⚠️ CRITICAL: `poetry run pytest tests/test_heat_flow/test_config.py -v` — ALL US4 tests must pass (SC-005)

**Checkpoint — US4 Complete**: All six FairDM models registered; admin site loads without error; system checks are green.

---

## Phase 7: User Story 5 — Test Factories Produce Valid Model Instances (Priority: P5)

**Goal**: Factory classes exist for all 7 models (`HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`, `ProbeMetadata`) and produce saved instances with non-null PKs in a single call. Complex multi-model graphs are built in conftest fixtures, not inside factory definitions.

**Independent Test**: Call each of the 7 factories in a `@pytest.mark.django_db` test and assert each returns a saved instance with `pk is not None`.

### Tests for User Story 5 ⚠️ Write FIRST — ensure they FAIL before implementing T050–T052

- [x] T049 [US5] In `tests/test_heat_flow/test_factories.py` — write `test_all_factories_produce_saved_instances`:

  ```python
  @pytest.mark.django_db
  def test_all_factories_produce_saved_instances():
      from heat_flow.factories import (
          HeatFlowSiteFactory, HeatFlowIntervalFactory,
          ParentHeatFlowFactory, HeatFlowFactory,
          ThermalGradientFactory, IntervalConductivityFactory,
          ProbeMetadataFactory,
      )
      assert HeatFlowSiteFactory().pk is not None
      assert HeatFlowIntervalFactory().pk is not None
      assert ParentHeatFlowFactory().pk is not None
      assert ThermalGradientFactory().pk is not None
      assert IntervalConductivityFactory().pk is not None
      assert HeatFlowFactory().pk is not None
      assert ProbeMetadataFactory().pk is not None
  ```

  Also write individual factory smoke tests (one per factory class), each creating one instance and asserting `pk is not None`; note: `ParentHeatFlowFactory()` creates with `sample=None` (null sample is valid since `save()` type validation is guarded by `if self.sample_id`); if a test requires a factory instance linked to a real `HeatFlowSite`, use the `site_fixture` from T012 rather than adding SubFactory chains to the factory class (A7, FR-028, SC-007)

### Implementation for User Story 5

- [x] T050 [US5] In `project/heat_flow/factories.py` — create `ParentHeatFlowFactory(MeasurementFactory)`:
  - `model = ParentHeatFlow`
  - `value = LazyAttribute(lambda _: round(random.gauss(mu=50, sigma=20), 2))`
  - ~~`is_ghfdb = True`~~ **⚠️ Correction required — see T065**: `is_ghfdb` field no longer exists; this line must be removed; `ghfdb_id` is nullable so no factory default is needed; `quality` is nullable so no default is needed either
  - **Set `sample = None` explicitly** to override any default sample SubFactory from `MeasurementFactory`; `save()` type validation is guarded by `if self.sample_id` so a null sample is valid and skips type checking entirely (A1)
  - **Note**: If `MeasurementFactory` requires a non-nullable `dataset` FK, check fairdm factory conventions and add `dataset = SubFactory(DatasetFactory)` at depth-1 only if required — do not add a `sample` SubFactory (A4)
  - Minimal scalar-only fields; no M2M or second-level SubFactory (R10)

- [x] T051 [P] [US5] In `project/heat_flow/factories.py` — create `ProbeMetadataFactory(factory.django.DjangoModelFactory)`:
  - `model = ProbeMetadata`
  - `interval = SubFactory(HeatFlowIntervalFactory)` (the only required FK; depth-1 SubFactory is acceptable per R10 guidelines: "A factory MAY include one level of SubFactory where a non-nullable FK is present")
  - `penetration = Faker("pyfloat", min_value=0, max_value=10)`
  - `length = Faker("pyfloat", min_value=1, max_value=10)`
  - `tilt = Faker("pyfloat", min_value=0, max_value=45)`

- [x] T052 [P] [US5] In `project/heat_flow/factories.py` — update `HeatFlowIntervalFactory`: confirm or add `sample = SubFactory(HeatFlowSiteFactory)` so the mandatory parent FK receives a valid value without requiring manual parent construction in tests (depth-1 SubFactory; acceptable per R10)

### System Validation — Phase 7

- [x] T054 ⚠️ CRITICAL: `poetry run python manage.py check` — must pass
- [x] T055 ⚠️ CRITICAL: `poetry run pytest tests/test_heat_flow/test_factories.py -v` — ALL US5 factory tests must pass (SC-007)

**Checkpoint — US5 Complete**: All 7 factory classes produce valid saved instances.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: HeatFlowCorrection status/type validation, documentation update, and final full-suite validation.

- [x] T056 [P] In `project/heat_flow/models/child.py` — add `VALID_STATUS_FOR_TYPE` class-level constant dict to `HeatFlowCorrection`:

  ```python
  VALID_STATUS_FOR_TYPE = {
      "IS": {"present_corrected", "present_not_corrected", "not_recognized",
             "not_considered", "tilt_corrected", "drift_corrected", "-"},
      "T":  {"present_corrected", "present_not_corrected", "not_corrected",
             "corrected", "not_recognized", "not_considered", "-"},
  }
  ENVIRONMENTAL_VALID = {"present_corrected", "present_not_corrected",
                         "present_not_significant", "not_recognized",
                         "considered_p", "considered_t", "considered_pt",
                         "not_considered", "-"}
  # S, E, TOPO, PAL, SUR, CONV, HR → ENVIRONMENTAL_VALID
  ```

  Then add `save()` method to `HeatFlowCorrection` that looks up `self.correction_type` in `VALID_STATUS_FOR_TYPE` (or the environmental set) and raises `ValidationError` if `self.status` is not in the valid set (spec.md FR-021 clarification; R4)

- [x] T057 [P] In `tests/test_heat_flow/test_models.py` — write tests for `HeatFlowCorrection.save()` validation:
  - `test_correction_valid_status_accepted`: `IS + tilt_corrected` → no exception
  - `test_correction_invalid_status_rejected`: `IS + considered_p` → `ValidationError`; `S + tilt_corrected` → `ValidationError`; `T + present_not_significant` → `ValidationError`
  - `test_correction_unspecified_always_valid`: `"-"` status valid for any correction type
  - `test_correction_invalid_type_rejected`: create `HeatFlowCorrection(heat_flow=child, correction_type="INVALID_TYPE", status="-")` and call `.full_clean()` → assert `ValidationError` from Django's field-level choices validation; tests spec EC-004: "a correction with an unrecognised `correction_type` value MUST be rejected" (L1, EC-004)

- [x] T058 In `docs/ghfdb_fields.md` — update the GHFDB P01–P13 and C01–C49 field mapping table to reflect the current Django model field structure: verify all field mappings listed in `data-model.md` are accurately captured; add entries for any newly confirmed field mappings; note fields removed (IGSN, old probe fields on HeatFlow) with rationale comments (FR-027 / Constitution Principle II); **note on automated mapping test obligation**: Constitution Principle VI requires an end-to-end schema-mapping test (model → export → flat row); this obligation is **explicitly deferred** together with the round-trip import/export feature (see spec.md § Out of Scope) — record acknowledgement of this deferral as a `<!-- TODO: add automated mapping test when import/export spec is implemented -->` comment in `docs/ghfdb_fields.md` (L3)

- [x] T059 [P] Verify all migrations apply cleanly on a fresh database: reset SQLite dev database and re-run `poetry run python manage.py migrate` from scratch; also review the migration history in `project/heat_flow/migrations/` — T009 and T032 produce two separate migration files; consider squashing them into one before merging if this is a greenfield branch with no deployed history (SC-002, A15)

### System Validation — Final

- [x] T060 ⚠️ CRITICAL: `poetry run python manage.py check` — zero errors/warnings ✅; `ruff check` — ruff not installed in project venv (configured in pyproject.toml but not added as a dependency); system check is the enforcement gate
- [x] T061 ⚠️ CRITICAL: `poetry run pytest tests/test_heat_flow/ -v` — 36 passed, 1 skipped (T028 DB-level constraint skip — intentional; SQLite MTI limitation documented in T030)

**Checkpoint — Feature Complete**: System checks clean, all migrations apply, Ruff clean, full test suite green.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup):         No dependencies — start immediately
Phase 2 (Foundational):  Depends on Phase 1 baseline recording
Phase 3 (US1):           Depends on Phase 2 (factory cleanup, FK refactor, value non-nullability)
Phase 4 (US2):           Depends on Phase 3 (needs site + interval fixtures; models correct)
Phase 5 (US3):           Depends on Phase 2; can run concurrently with Phase 4
Phase 6 (US4):           Depends on Phases 3–5 (all models must be correct before registering)
Phase 7 (US5):           Depends on Phase 6 (ParentHeatFlow and IntervalConductivity must be registered)
Phase 8 (Polish):        Depends on Phases 3–7
```

### User Story Completion Order

| Story | Depends On | Can Parallelize With |
|-------|-----------|---------------------|
| US1 (P1) | Phase 2 | — |
| US2 (P2) | Phase 2 + US1 fixtures | US3 (different files) |
| US3 (P3) | Phase 2 | US2 (different test cases) |
| US4 (P4) | US1 + US2 + US3 | — |
| US5 (P5) | US4 | — |

### Parallel Execution Within Phases

**Phase 3** (US1): All `[P]` test tasks (T013–T020) can be written simultaneously since they target different test functions in the same file. Implementation tasks T022 and T023 can be done concurrently (different model classes in same file).

**Phase 4** (US2): T026–T029 (writing tests) can be done in parallel.

**Phase 5** (US3): T035–T038 (writing tests) can be done in parallel.

**Phase 6** (US4): T044 and T045 (`ParentHeatFlowConfig` and `IntervalConductivityConfig`) can be written simultaneously.

**Phase 7** (US5): T050, T051, T052 (factory classes) can be written simultaneously.

---

## Implementation Strategy

### MVP Scope: Phase 2 + Phase 3 (US1)

The minimum viable deliverable for this feature is:

1. A correctly-structured model (Phase 2 cleanup)
2. A fully-tested persistence layer for the complete site → interval → (gradient + conductivity) → child heat flow + parent hierarchy (Phase 3 / US1)

This alone satisfies SC-003 and provides the foundation for all other stories.

### Incremental Delivery

- **After Phase 3**: US1 independently testable; core data model usable via ORM
- **After Phase 4**: US2 added; parent-child aggregation semantics verified
- **After Phase 5**: US3 added; marine probe measurements supported
- **After Phase 6**: US4 added; all models registered; portal infrastructure active
- **After Phase 7**: US5 added; factory-based test authoring enabled project-wide
- **After Phase 8**: Feature complete per all success criteria (SC-001 through SC-007)

### Format Validation Summary

- Total tasks: **68** (T001–T061 + T062–T067 amendment tasks added 2026-04-22)
- Tasks with `[P]` (parallelizable): 34 + 3 new
- Tasks with Story labels: 37
- System validation checkpoints: 10 + 1 (amendment checkpoint)
- All tasks follow format: `- [ ] TXXX [P?] [USn?] Description with file path` ✅

---

## Phase 9: Amendment Tasks — 2026-04-22 Spec Refinement

**Purpose**: Address discrepancies between the 2026-04-22 spec.md refinement and already-completed implementation tasks. The field `is_ghfdb` was removed from both `ParentHeatFlow` and `HeatFlow`; `local_id` was removed; `ghfdb_id` (PositiveIntegerField, nullable) and `quality` (CharField(13), nullable) were added to both models. Existing completed tasks (T044, T050) require correction, and a field-name typo (`ghdfb_id` → `ghfdb_id`) must be fixed.

- [x] T062 [P] In `project/heat_flow/models/parent.py` and `project/heat_flow/models/child.py` — rename field `ghdfb_id` → `ghfdb_id` in both `ParentHeatFlow` and `HeatFlow` (the existing implementation has a typo: "ghdfb" instead of "ghfdb"); also confirm and leave `null=True, blank=True, editable=False, db_index=True` on both; this rename will require a migration (see T066)

- [x] T063 [P] In `project/heat_flow/models/parent.py` and `project/heat_flow/models/child.py` — add `null=True, blank=True` to the `quality = models.CharField(max_length=13, ...)` field definition on both `ParentHeatFlow` and `HeatFlow`; `quality` is a GHFDB-derived code and will be absent for non-GHFDB entries — it must be nullable to avoid forcing a placeholder value; this change requires a migration (see T066)

- [x] T064 In `project/heat_flow/config.py` — update `ParentHeatFlowConfig.fields`: replace `"is_ghfdb"` with `"ghfdb_id"` and `"quality"` (correction of T044 implementation which used the removed field name); result: `fields = [("value", "uncertainty"), "corr_HP_flag", "comment", "ghfdb_id", "quality"]`

- [x] T065 In `project/heat_flow/factories.py` — remove `is_ghfdb = True` from `ParentHeatFlowFactory` (correction of T050 implementation; `is_ghfdb` no longer exists on the model); `ghfdb_id` and `quality` are now nullable so no factory defaults are required for them; also consider adding `quality = None` explicitly to make intent clear

- [x] T066 In `project/heat_flow/migrations/` — create migration for the changes from T062 and T063: rename `ghdfb_id` → `ghfdb_id` on both models and make `quality` nullable; run `poetry run python manage.py makemigrations heat_flow --name ghfdb_id_rename_and_quality_nullable`; verify the migration uses `RenameField` for the rename (not drop+add) to preserve existing data

- [x] T067 ⚠️ CRITICAL: System validation after amendment tasks — `poetry run python manage.py check` must pass with zero errors; `poetry run python manage.py migrate` must apply cleanly; `poetry run pytest tests/test_heat_flow/ -v` must pass all previously-passing tests (changes are backward-compatible: field rename and nullability addition should not break existing test assertions)
