# Feature Specification: GHFDB Normalized Relational Data Model

**Feature Branch**: `001-heat-flow-data-model`
**Created**: 2026-04-09
**Status**: Draft
**References**: Fuchs et al. (2021); Fuchs et al. (2023); Constitution Principles I, II, III

## Overview

The Global Heat Flow Database (GHFDB) distributes data as a flat spreadsheet schema defined by the International Heat Flow Commission (IHFC). Internally, the portal must store that data in a normalized relational schema that:

1. Faithfully represents the **parent/child conceptual hierarchy** defined by the World Heat Flow Database (WHDB) Project — site → interval → measurement cascade.
2. Conforms to the **FairDM `Sample`/`Measurement` base-class architecture** so the portal inherits FAIR data infrastructure without custom reimplementation.
3. Is fully testable at the field, relationship, constraint, and factory level.

Round-trip import/export between the portal schema and the GHFDB spreadsheet format is explicitly **deferred** to a later feature spec. Quality score *calculations* (U-score, M-score algorithms) are also **deferred**, though the score *fields* (as stored values) are within scope.

---

## User Scenarios & Testing

### User Story 1 — Site and Measurement Data Can Be Stored and Retrieved (Priority: P1)

A portal developer or data curator creates heat flow records from scratch using the Django ORM and can persist and retrieve a complete site → interval → child hierarchy with all scientifically meaningful fields intact.

**Why this priority**: This is the foundational capability. All other stories, features, and workflows depend on a correctly modeled, persistable data structure. Without this, nothing else works.

**Independent Test**: A test that creates one `HeatFlowSite`, one `ParentHeatFlow` linked to that site, one `HeatFlowInterval` linked to the site, one `HeatFlow` child with associated `ThermalGradient` and `IntervalConductivity` (with `parent` FK pointing to the `ParentHeatFlow`), and then reads them back from the database asserting all field values are correct — this alone delivers a working persistence layer for the complete site → interval → (gradient + conductivity) → child heat flow + parent heat flow graph.

**Acceptance Scenarios**:

1. **Given** a clean database, **When** a `HeatFlowSite` is created with geographic and exploration metadata fields, **Then** it is persisted and all fields are retrievable with correct values and types.
2. **Given** a persisted `HeatFlowSite`, **When** a `HeatFlowInterval` is created referencing that site as its sample, **Then** the interval is linked to the site and its depth/geological fields are retrievable.
3. **Given** a persisted `HeatFlowInterval`, **When** a `ThermalGradient` and an `IntervalConductivity` are created linked to that interval, **Then** both sub-measurements are retrievable via the interval's reverse relations.
4. **Given** persisted `ThermalGradient` and `IntervalConductivity`, **When** a `HeatFlow` child record is created referencing both via nullable ForeignKey relations and linked to a `ParentHeatFlow`, **Then** all forward and reverse relationships resolve correctly.
5. **Given** a persisted `HeatFlow` child, **When** `HeatFlowCorrection` records are attached (one per disturbance type), **Then** all corrections are retrievable via the child's reverse relation and the `correction_type` / `status` choices are validated.

---

### User Story 2 — Parent-Child Aggregation Relationship Is Correctly Modeled (Priority: P2)

A curator can associate multiple child `HeatFlow` determinations with a single `ParentHeatFlow` record and flag which children were used in computing the parent value.

**Why this priority**: The parent/child aggregation structure is the GHFDB's core scientific claim — a quality-controlled surface heat flow value synthesised from potentially many interval measurements. Modelling this correctly is required by Constitution Principle I.

**Independent Test**: Create one `ParentHeatFlow` linked to three `HeatFlow` children (two marked `is_relevant=True`, one `is_relevant=False`). Verify the `children` reverse queryset returns all three, and filtering by `is_relevant` returns only the two relevant ones.

**Acceptance Scenarios**:

1. **Given** a `ParentHeatFlow`, **When** multiple `HeatFlow` children are linked to it via the `parent` ForeignKey, **Then** `parent.children.all()` returns all linked children.
2. **Given** children with mixed `is_relevant` flags, **When** filtering `parent.children.filter(is_relevant=True)`, **Then** only children marked relevant are returned.
3. **Given** a `ParentHeatFlow` is deleted, **When** querying its formerly linked children, **Then** each child's `parent` field is set to `NULL` (not deleted — cascading deletion of scientific measurements is prohibited).

---

### User Story 3 — Marine Probe Measurements Have Supplementary Metadata (Priority: P3)

A data curator can attach probe instrument metadata to any `HeatFlowInterval` that represents a marine measurement, capturing probe type, length, penetration, and tilt.

**Why this priority**: Marine heat flow data constitutes a significant proportion of the GHFDB. Probe metadata is required to contextualise marine child measurements and distinguish them from borehole measurements. Without it, marine records cannot be fully curated.

**Independent Test**: Create a `HeatFlowInterval` with an attached `ProbeMetadata` record and assert that `interval.probe_metadata` resolves correctly and that `is_probe` returns `True` on the linked `HeatFlow` record.

**Acceptance Scenarios**:

1. **Given** a `HeatFlowInterval`, **When** a `ProbeMetadata` record is created referencing it, **Then** `interval.probe_metadata` resolves to the probe record and all probe fields (type, length, penetration, tilt) are retrievable.
2. **Given** a `HeatFlowInterval` with no linked probe metadata, **When** `probe_metadata` is accessed, **Then** a `RelatedObjectDoesNotExist` error is raised (or `None` if the accessor is wrapped), indicating a non-marine interval.
3. **Given** a probe metadata record, **When** the associated interval is deleted, **Then** the `ProbeMetadata` record is also deleted (CASCADE).

---

### User Story 4 — All Models Are Registered with FairDM (Priority: P4)

All primary models (`HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`) are registered with the FairDM registry using `@fairdm.register` so that the framework can provide FAIR data infrastructure (metadata, list views, admin, filtering, tables) without custom view code.

**Why this priority**: FairDM registration is the integration point between the domain model and the portal's infrastructure layer. Without it, registered models cannot be discovered or served by the portal. This is a Constitution Principle II requirement.

**Independent Test**: Import `fairdm` and assert that `fairdm.registry.get_config(HeatFlowSite)` returns a non-`None` config object. Repeat for all six registered models: `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, and `IntervalConductivity` (see FR-025, FR-030). Run `python manage.py check` and assert zero errors.

**Acceptance Scenarios**:

1. **Given** the portal application is started, **When** `fairdm.registry` is queried for `HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, and `HeatFlow`, **Then** a valid `ModelConfiguration` is returned for each.
2. **Given** registered models, **When** `python manage.py check` is executed, **Then** it exits with zero errors and zero warnings.
3. **Given** the FairDM registry has configurations for all four primary models, **When** the admin site is loaded, **Then** all four models appear in the admin panel without error.

---

### User Story 5 — Test Factories Produce Valid Model Instances (Priority: P5)

Factory classes exist for all models in the `heat_flow` app so that tests can create realistic data fixtures with a single line of code.

**Why this priority**: Without factories, every test must manually construct a full object graph (site → interval → gradient → conductivity → heat flow), creating brittle, verbose test code. Factories are a prerequisite for efficient test coverage of all later features.

**Independent Test**: Call `HeatFlowSiteFactory()`, `HeatFlowIntervalFactory()`, `HeatFlowFactory()`, `ThermalGradientFactory()`, `IntervalConductivityFactory()`, and `ProbeMetadataFactory()` in a `@pytest.mark.django_db` test and assert that each call produces a saved instance with a non-null PK.

**Acceptance Scenarios**:

1. **Given** a test database, **When** `HeatFlowSiteFactory()` is called, **Then** a saved `HeatFlowSite` instance is returned with valid geographic and exploration fields.
2. **Given** a test database, **When** `HeatFlowFactory()` is called, **Then** a complete child heat flow record is returned, linked to a `HeatFlowInterval` and a `ParentHeatFlow`.
3. **Given** factories for all sub-measurement types, **When** any factory is called in isolation, **Then** it creates any required related objects automatically (no manual parent setup required by the test).

---

### Edge Cases

- A `HeatFlowInterval` with `top == bottom` (zero-thickness interval) — field-level validation should reject this.
- A `HeatFlow` child with neither `thermal_gradient` nor `thermal_conductivity` — the system must allow incomplete records (in line with Constitution Principle I: incomplete records must not be blocked at entry time).
- A `ParentHeatFlow` with zero children (`children.count() == 0`) — this is a valid state for a newly entered parent that has no child measurements yet.
- A `HeatFlowCorrection` created with an unrecognised `correction_type` value — the field's `choices` constraint must reject it.
- Multiple `ParentHeatFlow` records linked to the same `HeatFlowSite` — MUST be rejected; FR-009 enforces a `UniqueConstraint` in `ParentHeatFlow.Meta.constraints` on the `sample` column (one per site, globally; not version-scoped).

---

## Clarifications

### Session 2026-04-10 (Corrections Pass 2)

- Q: Should `IGSN` be retained as a field on `HeatFlow`, or should it be handled through FairDM's Sample identifier relationship? → A: Remove `IGSN` from `HeatFlow`. IGSNs are persistent identifiers for physical rock or sediment samples, not for measurements. FairDM's `Sample` base class provides a generic identifier relationship that covers both `HeatFlowSite` and `HeatFlowInterval`. The GHFDB C49 field maps to those sample-level identifiers, not to the heat flow determination itself. FR-010 updated.
- Q: Should the primary `value` field be non-nullable at DB level on ALL Measurement subclasses (not only ParentHeatFlow)? → A: Yes — the `value` field is the primary scientific datum on every Measurement subclass; a record with no value is semantically meaningless. `null=False` (no `null=True`) applies to `value` on HeatFlow.value, ThermalGradient.value, and IntervalConductivity.value. R3 updated to reflect this wider rule.
- Q: Should only certain `StatusChoices` be valid for each `CorrectionTypeChoices` in `HeatFlowCorrection`? → A: Yes — some statuses are only semantically meaningful for specific correction types (e.g., `tilt_corrected`/`drift_corrected` apply only to IS/T probe-type corrections; environmental statuses only to P-flag corrections). A valid-combinations table must be documented in the data model and enforced via `ValidationError` in `HeatFlowCorrection.save()`.
- Q: Given that the `sample` FK is declared in the fairdm package, can `unique=True` be added directly to the inherited field on ParentHeatFlow? → A: No — modifying a field declared in a parent package's models is not safe in Django. Use `UniqueConstraint` in `ParentHeatFlow.Meta.constraints` instead. The existing `save()`-level uniqueness check remains as an additional application-layer guard. FR-009 updated.
- Q: Should `ThermalGradient` and `IntervalConductivity` be registered with the FairDM registry? → A: Yes — ALL Measurement and Sample subclasses must be registered with the FairDM registry. FR-025 is reversed: both `ThermalGradient` and `IntervalConductivity` require `@fairdm.register` configs in `config.py`. `ProbeMetadata` and `HeatFlowCorrection` remain unregistered (they are plain `Model` subclasses, not FairDM Measurement/Sample subclasses). Factory note (no formal Q): Keep factory classes minimal — one level deep, no excessive `SubFactory` chains. Build complex multi-model object graphs via pytest fixtures, following the fairdm package conventions.

### Session 2026-04-09

- Q: How should US1's Independent Test be updated to cover `ParentHeatFlow`? → A: Add `ParentHeatFlow` to US1's Independent Test — create one linked to `HeatFlowSite` and set it as the child's `parent`; US2 stays focused on aggregation semantics.
- Q: How should `ThermalGradient` and `IntervalConductivity` link to `HeatFlowInterval`? → A: Both inherit from FairDM `Measurement` and link via the inherited `sample` FK; a `save()`-level validation must enforce that only a `HeatFlowInterval` instance is assigned to `sample`.
- Q: What does `HeatFlow.sample` target? → A: `HeatFlow.sample` → `HeatFlowInterval`; and `HeatFlow`'s links to `ThermalGradient`/`IntervalConductivity` MUST be ForeignKeys (nullable, not OneToOne) to allow reuse of existing records across multiple child determinations and future recalculations.
- Q: What does `HeatFlow.sample` target, and what relationship type links `HeatFlow` to `ThermalGradient`/`IntervalConductivity`? → A: `HeatFlow.sample` → `HeatFlowInterval`; links to `ThermalGradient` and `IntervalConductivity` are nullable ForeignKeys (not OneToOne) to allow reuse of existing records and recalculation of child heat flow from existing data.
- Q: Should `save()`-level `ValidationError` enforcement of the correct `sample` type be applied to all four measurement models? → A: Yes — apply `save()`-level `ValidationError` to all four (`HeatFlow`, `ParentHeatFlow`, `ThermalGradient`, `IntervalConductivity`) for consistent enforcement across all code paths.

---

## Requirements

### Functional Requirements

**Site & Geographic Context**

- **FR-001**: The system MUST provide a `HeatFlowSite` model that inherits from the FairDM `Sample` base class (via `fairdm-geo` geographic and borehole abstractions) and stores site-level metadata including name, country, region, continent, geological domain, environment type, exploration method, exploration purpose, site type, elevation, azimuth, inclination, and borehole depth.
- **FR-002**: `HeatFlowSite` MUST support a geographic location via a point geometry field inherited from the FairDM/fairdm-geo base class.
- **FR-003**: Exploration purpose on `HeatFlowSite` MUST be a many-to-many vocabulary concept field (multiple purposes may apply).

**Depth Interval**

- **FR-004**: The system MUST provide a `HeatFlowInterval` model that inherits from both the FairDM `Sample` base class and the `fairdm-geo` `GeoDepthInterval` abstract, storing top depth, bottom depth, vertical depth, lithology, geologic age, and stratigraphic unit.
- **FR-005**: `HeatFlowInterval` MUST be linked to its parent `HeatFlowSite` via the FairDM `sample` foreign key relationship.
- **FR-006**: The interval depth fields MUST use physical quantity fields (with units) rather than bare numeric fields.

**Parent Heat Flow**

- **FR-007**: The system MUST provide a `ParentHeatFlow` model that inherits from the FairDM `Measurement` base class, storing the aggregated surface heat flow value (mW/m²), a 1-sigma uncertainty, a heat production correction flag, a comment field, and a GHFDB membership flag.
- **FR-008**: `ParentHeatFlow` MUST be linked to its `HeatFlowSite` via the FairDM `sample` FK (inherited from `Measurement`).
- **FR-008a**: `ParentHeatFlow.save()` MUST raise `ValidationError` if `sample` is not an instance of `HeatFlowSite`.
- **FR-009**: The system MUST prevent more than one `ParentHeatFlow` record per `HeatFlowSite`, regardless of dataset. This is enforced via a `UniqueConstraint` in `ParentHeatFlow.Meta.constraints` on the `sample` FK column (the `sample` field is declared in the fairdm package and cannot be modified with `unique=True` directly). The existing `save()`-level uniqueness check is retained as an additional application-layer guard.

**Child Heat Flow**

- **FR-010**: The system MUST provide a `HeatFlow` (child) model that inherits from the FairDM `Measurement` base class with `sample` FK targeting `HeatFlowInterval` (validated at `save()` to reject non-`HeatFlowInterval` objects). It stores: heat flow value (mW/m²) with uncertainty, calculation method (vocabulary, many-to-many), expedition/ship name, bottom water temperature, date acquired, U-score, M-score, and a comment field. **Note**: The `IGSN` field previously assigned to `HeatFlow` is removed; C49/IGSN is served by FairDM's Sample identifier relationship on `HeatFlowSite` and `HeatFlowInterval`.
- **FR-010a**: `HeatFlow.save()` MUST raise `ValidationError` if `sample` is not an instance of `HeatFlowInterval`, consistent with FR-008a, FR-016a, and FR-018a.
- **FR-011**: `HeatFlow` MUST have a nullable ForeignKey to `ParentHeatFlow` (on_delete=SET_NULL) with a related name of `children`.
- **FR-012**: `HeatFlow` MUST have an `is_relevant` boolean field indicating whether this child was used in computing the parent value.
- **FR-013**: `HeatFlow` MUST have nullable ForeignKey relationships (not OneToOne) to `ThermalGradient` and `IntervalConductivity`, enabling multiple `HeatFlow` records to reference the same gradient or conductivity measurement for reuse and recalculation scenarios.
- **FR-014**: U-score and M-score fields on `HeatFlow` MUST use enumerated choice fields with values U1/U2/U3/U4/Ux and M1/M2/M3/M4/Mx respectively, defaulting to Ux/Mx (unknown).

**Thermal Gradient**

- **FR-015**: The system MUST provide a `ThermalGradient` model storing: raw gradient (K/km) with uncertainty, corrected gradient (K/km) with uncertainty, temperature acquisition methods at top and bottom boundaries (vocabulary, many-to-many), shut-in times at top and bottom (hours), correction method, and a quality score.
- **FR-016**: `ThermalGradient` MUST inherit from the FairDM `Measurement` base class and link to a `HeatFlowInterval` via the inherited `sample` FK.
- **FR-016a**: `ThermalGradient.save()` MUST raise `ValidationError` if `sample` is not an instance of `HeatFlowInterval` (app-level enforcement; does not rely solely on the DB constraint).

**Interval Thermal Conductivity**

- **FR-017**: The system MUST provide an `IntervalConductivity` model storing: mean thermal conductivity (W/mK) with uncertainty, sample source type (vocabulary), data location (vocabulary), determination method (vocabulary), saturation state (vocabulary), pressure-temperature correction method, averaging methodology, number of measurements, and a quality score.
- **FR-018**: `IntervalConductivity` MUST inherit from the FairDM `Measurement` base class and link to a `HeatFlowInterval` via the inherited `sample` FK.
- **FR-018a**: `IntervalConductivity.save()` MUST raise `ValidationError` if `sample` is not an instance of `HeatFlowInterval` (app-level enforcement; mirrors FR-016a).

**Probe Metadata**

- **FR-019**: The system MUST provide a `ProbeMetadata` model with a one-to-one relationship to `HeatFlowInterval`, storing probe type (vocabulary, many-to-many), probe length (m), probe penetration depth (m), and tilt angle (degrees).
- **FR-020**: Deleting a `HeatFlowInterval` MUST cascade-delete its associated `ProbeMetadata`.

**Heat Flow Corrections**

- **FR-021**: The system MUST provide a `HeatFlowCorrection` model with a ForeignKey to `HeatFlow`, a `correction_type` choice field (IS, T, S, E, TOPO, PAL, SUR, CONV, HR), and a `status` choice field indicating whether the disturbance is present-corrected, present-uncorrected, not recognised, not considered, etc.
- **FR-022**: Multiple `HeatFlowCorrection` records MAY be associated with a single `HeatFlow` determination (one per disturbance type).

**FairDM Registration**

- **FR-023**: `HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, and `HeatFlow` MUST each be registered with the FairDM registry via `@fairdm.register` in `heat_flow/config.py`, using an `IHFCConfig` base that provides IHFC authority and citation metadata.
- **FR-024**: Each registered model MUST declare a `fields` list (for form/detail view rendering) and be associated with a `filterset_class` and `table_class`.
- **FR-025**: ALL `Measurement` subclasses (`HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, and `IntervalConductivity`) MUST be registered with the FairDM registry via `@fairdm.register`. `ProbeMetadata` and `HeatFlowCorrection` are plain `django.db.models.Model` subclasses (not FairDM `Measurement`/`Sample` subclasses) and do not require registration; they are managed inline via their parent models.

**Migrations & System Integrity**

- **FR-026**: All model changes MUST be captured in Django migrations within the `heat_flow` app.
- **FR-027**: Running `python manage.py check` MUST produce zero errors and zero warnings after all models and registrations are in place.

**Testing & Factories**

- **FR-028**: A factory class MUST exist for each of the following models: `HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`, `ProbeMetadata`.
- **FR-029**: Tests MUST verify model creation, field value persistence, all defined relationships (FK, one-to-one, M2M), and cascade/set-null deletion behaviour for each model.
- **FR-030**: Tests for FairDM registration MUST verify that `fairdm.registry` returns a valid configuration for each of the six registered models: `HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, and `IntervalConductivity`.

---

### Key Entities

- **HeatFlowSite**: The geographic measurement location (a borehole or probe site). Inherits FairDM `Sample` + `fairdm-geo` `GenericHole` + `GeoDepthInterval`. Stores site identity, geographic context (country, region, continent, domain), borehole geometry (azimuth, inclination, depth), exploration context, and geological properties (lithology, age, stratigraphy) of the site-level interval.

- **HeatFlowInterval**: A depth-stratified section within a borehole over which a child heat flow determination is made. Inherits FairDM `Sample` + `fairdm-geo` `Interval` + `GeoDepthInterval`. Multiple intervals may exist for one site.

- **ParentHeatFlow**: The aggregated, quality-controlled surface heat flow for a site. Inherits FairDM `Measurement`. One-to-many with `HeatFlowSite` (via `sample` FK). The authoritative published value.

- **HeatFlow** (child): A single interval-level heat flow determination computed from one `ThermalGradient` and one `IntervalConductivity`. Inherits FairDM `Measurement`; `sample` FK targets `HeatFlowInterval` (validated at `save()`). References a `ParentHeatFlow` via nullable FK. Links to `ThermalGradient` and `IntervalConductivity` via nullable ForeignKeys (not OneToOne) to allow reuse of existing records across multiple determinations and recalculations. Carries U-score and M-score quality fields.

- **ThermalGradient**: Temperature gradient measurement over a `HeatFlowInterval`. Inherits FairDM `Measurement`; links to `HeatFlowInterval` via the `sample` FK (validated at `save()` to reject non-`HeatFlowInterval` objects). Stores raw and corrected gradients (K/km), measurement methods, shut-in times. Linked one-to-one to a `HeatFlow` child.

- **IntervalConductivity**: Mean thermal conductivity (W/mK) over a `HeatFlowInterval`. Inherits FairDM `Measurement`; links to `HeatFlowInterval` via the `sample` FK (validated at `save()` to reject non-`HeatFlowInterval` objects; mirrors `ThermalGradient`). Stores conductivity value, measurement method, source type, saturation, and P-T correction details. Linked one-to-one to a `HeatFlow` child.

- **ProbeMetadata**: Instrument parameters for marine probe deployments. One-to-one with `HeatFlowInterval`. Stores probe type, length, penetration, and tilt.

- **HeatFlowCorrection**: A record of a single environmental or methodological disturbance and its correction status. Many-to-one to `HeatFlow`. One record per disturbance type per heat flow determination.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: `python manage.py check` returns zero errors and zero warnings with all heat_flow models and FairDM registrations in place.
- **SC-002**: All migrations in the `heat_flow` app apply cleanly on a fresh database with no errors.
- **SC-003**: The full site → interval → gradient/conductivity → child heat flow object graph can be created, persisted, and retrieved using only factory calls in a single `@pytest.mark.django_db` test.
- **SC-004**: All defined deletion cascade and SET_NULL behaviours are verified by at least one test each (parent deleted → child `parent` field becomes NULL; interval deleted → probe metadata deleted).
- **SC-005**: FairDM registry queries for all six registered models (`HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`) each return a non-None config, confirmed by passing tests.
- **SC-006**: The `heat_flow` test suite (models, factories, relations, registration) passes with zero failures.
- **SC-007**: All eight model classes (`HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, `IntervalConductivity`, `ProbeMetadata`, `HeatFlowCorrection`) have at least one factory or direct-creation test.

---

## Out of Scope

- Round-trip import/export between the portal schema and the GHFDB flat spreadsheet format (deferred).
- U-score and M-score *calculation algorithms* (`get_U_score()`, `get_M_score()` logic) — deferred to a dedicated quality-scoring spec. Score *fields* (as stored values) remain in scope.
- Admin UI customisation beyond basic FairDM registration (inline formsets, custom admin actions, etc.) — deferred.
- REST API endpoints or serializers for these models — deferred to the API spec.
- Spatial/GIS query functionality (e.g., PostGIS geometry operations) — deferred.

---

## Assumptions

- `fairdm-geo` provides `GenericHole`, `GenericEarthSample`, `Interval`, and `GeoDepthInterval` abstract base classes that `HeatFlowSite` and `HeatFlowInterval` inherit from. These base classes are assumed stable and already installed.
- FairDM `Sample` and `Measurement` base classes provide the `sample` ForeignKey relationship pattern used to link measurements to their parent samples (i.e., linking `HeatFlow` → `HeatFlowInterval`, `ParentHeatFlow` → `HeatFlowSite`).
- Physical quantity fields (e.g., `QuantityField`, `DecimalQuantityField`) from `fairdm.db.models` are used for all mW/m², K/km, W/mK, and metre measurements to ensure unit-safe storage.
- `research_vocabs` `ConceptField` and `ConceptManyToManyField` are used for all vocabulary-backed fields (environment, exploration method, probe type, etc.) and are already installed.
- The `heat_flow` app's `vocabularies.py` module already defines the required vocabulary classes and is the canonical source for all GHFDB-specific controlled terms.
- The portal runs SQLite in development and PostgreSQL in production; model constraints that are incompatible with SQLite (e.g., `CheckConstraint` on `QuantityField`) may be noted but are not hard-required in migrations for this spec.
- Factories use `factory_boy` following existing patterns in `heat_flow/factories.py`; no new factory library is introduced.
- The existing `heat_flow/config.py` `IHFCConfig` base class and `@fairdm.register` pattern are the correct integration points and will be used as-is or extended (not replaced).
