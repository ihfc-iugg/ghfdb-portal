# Research: GHFDB Normalized Relational Data Model

**Phase 0 Output** | **Feature**: 001-heat-flow-data-model | **Date**: 2026-04-09
**Propagated**: 2026-04-22 — Updated ParentHeatFlow config fields list to reflect `ghfdb_id`/`quality` replacing `is_ghfdb`.

---

## R1: FairDM Base Class Inheritance Patterns

**Decision**: All primary models inherit from FairDM base classes as designed.

**Rationale**: FairDM's `Sample` and `Measurement` classes provide FAIR metadata infrastructure (DOI, contributor attribution, dataset linking, polymorphic querysets). Inheriting from these classes gives the GHFDB portal access to all framework features (admin, registry, API, filtering, tables) with zero custom view code. The `fairdm-geo` extensions (`GenericHole`, `GenericEarthSample`, `Interval`, `GeoDepthInterval`) add domain-specific borehole and geological fields.

**Inheritance map**:

| Model | Base Classes | Notes |
|-------|-------------|-------|
| HeatFlowSite | GenericHole → GenericEarthSample → Sample | Also mixes in `GeoDepthInterval` for site-level geology |
| HeatFlowInterval | Interval → Sample, GeoDepthInterval | Depth interval within a borehole |
| ParentHeatFlow | Measurement | `sample` FK → HeatFlowSite |
| HeatFlow | Measurement | `sample` FK → HeatFlowInterval |
| ThermalGradient | Measurement | `sample` FK → HeatFlowInterval |
| IntervalConductivity | Measurement | `sample` FK → HeatFlowInterval |
| ProbeMetadata | django.db.models.Model | OneToOne → HeatFlowInterval (not a Measurement) |
| HeatFlowCorrection | django.db.models.Model | FK → HeatFlow (not a Measurement) |

**Alternatives considered**:

- Making ProbeMetadata a Measurement → rejected; probe metadata is instrument context, not an independent scientific measurement.
- Making HeatFlowCorrection a Measurement → rejected; corrections are flags/statuses, not measured quantities.

---

## R2: Field Naming Convention

**Decision**: Use plain-language field names on Django models; do NOT mirror GHFDB short names (e.g., `T_grad_mean_meas`).

**Rationale**: The user explicitly requested plain-language names for readability. The GHFDB short names are cryptic and conflict with Python naming conventions. The field mapping between Django model fields and GHFDB CSV columns will be handled by the import/export layer (deferred to a later spec). Current models already follow this pattern (e.g., `value`, `uncertainty`, `corrected_value`, `corrected_uncertainty`).

**Naming examples**:

| GHFDB Short Name | Current Django Field | Notes |
|-----------------|---------------------|-------|
| q / qc | `value` | On ParentHeatFlow / HeatFlow |
| q_unc / qc_unc | `uncertainty` | On ParentHeatFlow / HeatFlow |
| T_grad_mean_meas | `value` | On ThermalGradient |
| T_grad_unc_meas | `uncertainty` | On ThermalGradient |
| T_grad_mean_cor | `corrected_value` | On ThermalGradient |
| tc_mean | `value` | On IntervalConductivity |
| tc_unc | `uncertainty` | On IntervalConductivity |
| corr_HP_flag | `corr_HP_flag` | Exception — retained for domain familiarity |
| T_shutin_top | `shutin_top` | On ThermalGradient |
| hf_pen | `penetration` | On ProbeMetadata |

**Alternatives considered**:

- Using GHFDB short names directly → rejected per user instruction; harms readability and violates Python naming conventions.
- Fully verbose names (e.g., `mean_thermal_conductivity_value`) → rejected; existing models already use compact plain-language (e.g., `value`, `uncertainty`).

---

## R3: GHFDB Mandatory Fields — DB Nullability Strategy

**Decision**: GHFDB-mandatory *auxiliary* fields are nullable at the DB level (`null=True, blank=True`). The **primary `value` field on every Measurement subclass is non-nullable** (`null=False`). Enforcement of auxiliary mandatory fields happens at the application/export boundary only.

**Rationale**: Per user instruction, the GHFDB marks many fields as "Mandatory" (M) in the field reference, but the portal must accept incomplete records during data entry and curation. Blocking saves on missing context fields would prevent incremental data entry, break import of historical records, and conflict with Constitution Principle I (FAIR-First: incomplete records must not be blocked at entry time). However, the primary `value` field on each Measurement subclass represents the core scientific datum — a Measurement record without its primary measured value is semantically meaningless and must not exist. Non-nullability is therefore applied uniformly to all `value` fields across the model hierarchy. Validation of other mandatory fields will occur at export time (deferred to the import/export spec).

**Applies to**:

| Model | Field | Null behaviour | Rationale |
|-------|-------|----------------|----------|
| ParentHeatFlow | `value` | **NOT NULL** | Primary measured heat flow — existing behaviour retained |
| HeatFlow | `value` | **NOT NULL** | Primary child heat flow value |
| ThermalGradient | `value` | **NOT NULL** | Primary gradient measurement |
| IntervalConductivity | `value` | **NOT NULL** | Primary conductivity measurement |
| All models | all other GHFDB-mandatory fields | nullable | Allow incomplete data entry |

**Alternatives considered**:

- Enforcing NOT NULL for ALL GHFDB-mandatory fields → rejected; would block incomplete data entry.
- Using default sentinel values (e.g., 0.0) for missing mandatory fields → rejected; corrupts data semantics.
- Nullable `value` on ThermalGradient/IntervalConductivity (previous position) → rejected; a Measurement without its primary datum is semantically meaningless.

---

## R4: Correction Flags — HeatFlowCorrection Model vs. Individual Fields

**Decision**: Correction flags (C11–C19) are stored as `HeatFlowCorrection` records (one per disturbance type per `HeatFlow`), NOT as individual boolean fields on the `HeatFlow` model.

**Rationale**: The existing implementation already uses a separate `HeatFlowCorrection` model with `correction_type` and `status` fields, plus `unique_together = [("heat_flow", "correction_type")]`. This normalized design:

- Avoids 9+ boolean columns on HeatFlow
- Allows each correction type to carry a status (present-corrected, present-uncorrected, not recognized, etc.) and a comment
- Maps cleanly to the GHFDB C11–C19 flag structure during import/export
- Makes adding future correction types trivial

**Current observation**: The existing `HeatFlowCorrection.CorrectionTypeChoices` already covers: IS, T, S, E, TOPO, PAL, SUR, CONV, HR — matching C11–C19 precisely. The `StatusChoices` map to the GHFDB flag values.

**Important**: Not all `StatusChoices` are semantically valid for all `CorrectionTypeChoices`. The valid combinations must be documented and enforced via `ValidationError` in `HeatFlowCorrection.save()`. The following table documents the intended mapping (to be confirmed against Fuchs et al. 2021/2023 during implementation):

| CorrectionType | Valid StatusChoices |
|----------------|--------------------|
| IS (in-situ conditions, probe) | present_corrected, present_not_corrected, not_recognized, not_considered, tilt_corrected, drift_corrected, unspecified |
| T (temperature) | present_corrected, present_not_corrected, not_corrected, corrected, not_recognized, not_considered, unspecified |
| S, E, TOPO, PAL, SUR, CONV, HR (environmental) | present_corrected, present_not_corrected, present_not_significant, not_recognized, considered_p, considered_t, considered_pt, not_considered, unspecified |

**Enforcement**: `HeatFlowCorrection.save()` must raise `ValidationError` when a `status` is assigned that is not in the valid set for the given `correction_type`. The `VALID_STATUS_FOR_TYPE` mapping should be defined as a class-level constant.

**Important note**: The existing `HeatFlow` model still has individual `corr_*_flag` ConceptField/ConceptManyToMany fields from an older design. These will need to be removed in this spec and replaced by the `HeatFlowCorrection` relation. The factory also references these fields. This cleanup is part of the implementation work.

**Alternatives considered**:

- Individual boolean fields on HeatFlow → rejected; already migrated to HeatFlowCorrection model in current codebase.
- Allowing all statuses for all correction types (no validation) → rejected; produces data that cannot be correctly mapped back to the GHFDB flat format during export.

---

## R5: HeatFlow → ThermalGradient / IntervalConductivity Link Type

**Decision**: Use nullable ForeignKey (not OneToOne) from HeatFlow to ThermalGradient and IntervalConductivity.

**Rationale**: Per spec clarification (FR-013), the relationship must allow:

1. Multiple `HeatFlow` records to reference the same `ThermalGradient` or `IntervalConductivity` (reuse of existing measurement data)
2. Recalculation scenarios where a new child determination is computed from existing gradient/conductivity data
3. Nullable links for incomplete records

**Current state**: The existing `child.py` uses `OneToOneField` for both. This MUST be changed to `ForeignKey` per FR-013.

**Migration impact**: Changing OneToOne to FK requires a migration. Since the data model is still in development, this is a safe change.

**Alternatives considered**:

- Keeping OneToOneField → rejected; spec explicitly requires FK for reuse/recalculation scenarios.
- M2M relationship → rejected; a single HeatFlow determination uses one gradient and one conductivity value; M2M is semantically incorrect.

---

## R6: ParentHeatFlow Uniqueness Constraint

**Decision**: Enforce one `ParentHeatFlow` per `HeatFlowSite` globally via a `UniqueConstraint` in `ParentHeatFlow.Meta.constraints` targeting the `sample_id` column.

**Rationale**: Per spec clarification, duplicate `ParentHeatFlow` records cannot exist at the same `HeatFlowSite` regardless of dataset. The `sample` FK on `ParentHeatFlow` inherits from FairDM's `Measurement` base class and **cannot be modified with `unique=True` directly** — that field is declared in the fairdm package, and overriding inherited FK fields in a Django subclass model is not supported and would likely break the ORM. Instead, a `UniqueConstraint` in `Meta.constraints` targets the underlying `sample_id` DB column directly, providing the same database-level enforcement without modifying the inherited field declaration.

**Implementation**:

```python
class Meta(Measurement.Meta):
    constraints = [
        models.UniqueConstraint(fields=["sample"], name="unique_parent_per_site"),
    ]
```

**Current state**: The existing `ParentHeatFlow.save()` method already has a manual check that raises `ValidationError` if another `ParentHeatFlow` exists for the same sample. The `UniqueConstraint` in Meta provides DB-level enforcement in addition to this existing app-layer guard.

**Alternatives considered**:

- `unique=True` on the inherited `sample` FK field → rejected; the `sample` field is declared in the fairdm package and cannot be safely overridden in a subclass model.
- Save-only enforcement (no DB constraint) → rejected; DB-level unique constraint is more robust and prevents race conditions.
- Scoping uniqueness to dataset → rejected; user explicitly said "regardless of dataset."

---

## R7: save()-Level Type Validation for Measurement Models

**Decision**: All four Measurement subclasses enforce their expected `sample` type in `save()` via `ValidationError`.

**Rationale**: Per spec clarifications (FR-008a, FR-010a, FR-016a, FR-018a), each measurement must validate that its `sample` FK points to the correct Sample subclass:

| Model | Expected sample type |
|-------|---------------------|
| ParentHeatFlow | HeatFlowSite |
| HeatFlow | HeatFlowInterval |
| ThermalGradient | HeatFlowInterval |
| IntervalConductivity | HeatFlowInterval |

This is application-level enforcement; the database FK constraint points to the polymorphic `Sample` table (since FairDM uses `django-polymorphic`), so a `ThermalGradient` could technically be linked to a `HeatFlowSite` at the DB level. The `save()` check prevents this.

**Pattern**:

```python
def save(self, *args, **kwargs):
    if self.sample_id and not isinstance(self.sample, HeatFlowInterval):
        raise ValidationError(_("Sample must be a HeatFlowInterval instance."))
    super().save(*args, **kwargs)
```

**Alternatives considered**:

- Relying on DB FK constraints alone → rejected; polymorphic FK targets `Sample` base table, not the specific subclass.
- Using `clean()` instead of `save()` → rejected; save() is called on all code paths, clean() is only called by forms/admin.

---

## R8: FairDM Registry Configuration — Scope for This Spec

**Decision**: Register ALL six FairDM Sample and Measurement subclasses — `HeatFlowSite`, `HeatFlowInterval`, `ParentHeatFlow`, `HeatFlow`, `ThermalGradient`, and `IntervalConductivity` — with the FairDM registry. `ProbeMetadata` and `HeatFlowCorrection` are plain `django.db.models.Model` subclasses and do not require registration.

**Rationale**: ALL FairDM `Sample` and `Measurement` subclasses must be registered with the FairDM registry — this is a framework requirement, not an optional feature. The FairDM registry drives admin, filtering, table views, API endpoint generation, and FAIR metadata exposure for every registered model. Omitting `ThermalGradient` and `IntervalConductivity` would mean those models are invisible to the portal's data management layer, breaking normal curation workflows. The existing `config.py` already registers `HeatFlowSite`, `HeatFlowInterval`, `HeatFlow`, and `ThermalGradient`. This spec:

- Adds `ParentHeatFlow` registration (currently missing)
- Adds `IntervalConductivity` registration (currently missing)
- Retains `ThermalGradient` registration (previously proposed for removal — **this proposal is reversed**)
- Updates `HeatFlow` config to remove old `corr_*_flag` fields from its `fields` list

**Config approach**: Keep registrations basic. Each registered model provides `fields`, `description`, and inherits IHFC authority/citation from `IHFCConfig`. `filterset_class` and `table_class` can be specified where they already exist.

**ParentHeatFlow config will include**: `model`, `description`, `fields` (value, uncertainty, corr_HP_flag, comment, ghfdb_id, quality), `authority`, `citation` (inherited from IHFCConfig). ~~`is_ghfdb` removed from fields list (2026-04-22 refinement).~~

**ThermalGradient and IntervalConductivity configs** will initially use minimal `fields` lists (value, uncertainty, and key method/quality fields).

**Alternatives considered**:

- Registering only 4 primary models, excluding ThermalGradient and IntervalConductivity → rejected; all FairDM Measurement/Sample subclasses must be registered.
- Skipping ParentHeatFlow → rejected per FR-023; it's a primary model that must be registered.

---

## R9: ProbeMetadata FK Target — HeatFlowInterval

**Decision**: `ProbeMetadata` links via OneToOne to `HeatFlowInterval`, not to `HeatFlow`.

**Rationale**: The existing code already has `ProbeMetadata.interval = OneToOneField("heat_flow.HeatFlowInterval")`. This is correct: probe metadata describes the instrument deployment in a depth interval, not the heat flow calculation derived from it. The `HeatFlow.is_probe` cached property can check whether the related interval has probe metadata.

**Current issue**: The existing `HeatFlow` model has inline probe fields (`probe_penetration`, `probe_length`, `probe_tilt`, `water_temperature`) that duplicate `ProbeMetadata`. These fields need to be cleaned up — `probe_penetration`, `probe_length`, `probe_tilt` should only exist on `ProbeMetadata`. `water_temperature` may stay on `HeatFlow` as it's a measurement context field (C24), not strictly probe metadata.

**Alternatives considered**:

- Linking ProbeMetadata to HeatFlow → rejected; probe metadata is about the physical instrument at a location, not about a specific heat flow calculation.

---

## R10: Existing Factory Compatibility

**Decision**: Update existing factories and create new ones (`ParentHeatFlowFactory`, `ProbeMetadataFactory`) to match the updated model structure. Keep all factory classes **minimal and flat** — no excessive `SubFactory` chains. Build complex multi-model object graphs (e.g., site → interval → gradient + conductivity → child heat flow + parent) using **pytest fixtures**, following the fairdm package conventions.

**Rationale**: Factory classes should set sensible defaults for a model's own fields and create the minimum required related objects. Deep `SubFactory` chains that auto-create entire model hierarchies are fragile, hard to debug, and couple factories to database schema in ways that make isolated unit tests brittle. Complex object graphs are better expressed as explicit pytest fixtures where the construction sequence is readable and controllable. This pattern is already used in the fairdm package's test suite and is the expected convention for portal tests.

**Factory guidelines**:

- Each factory provides defaults for the model's own scalar/choice fields.
- A factory MAY include one level of `SubFactory` where the FK is non-nullable and a related object is truly required (e.g., `HeatFlowIntervalFactory.sample = SubFactory(HeatFlowSiteFactory)`).
- A factory MUST NOT auto-create M2M records or second-level related objects through `SubFactory`.
- Multi-model fixture construction belongs in `conftest.py` pytest fixtures, not in factory `Meta` or `@factory.post_generation` hooks.

**Changes required**:

- `HeatFlowFactory`: Remove references to `corr_S_flag`, `corr_E_flag`, etc. (fields being removed from `HeatFlow`); remove `probe_penetration`, `probe_length`, `probe_tilt` (moving to `ProbeMetadata`).
- `ParentHeatFlowFactory`: Create new (currently missing).
- `ProbeMetadataFactory`: Create new (currently missing).

**Alternatives considered**:

- Deep factory chains that auto-build the full site → interval → child graph → rejected; produces fragile tests and obscures object construction intent.
- Leaving factories unchanged → rejected; factories must match the updated model structure.
