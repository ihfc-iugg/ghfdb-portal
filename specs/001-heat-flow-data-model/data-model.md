# Data Model: GHFDB Normalized Relational Data Model

**Phase 1 Output** | **Feature**: 001-heat-flow-data-model | **Date**: 2026-04-09

---

## Entity Relationship Overview

```text
┌─────────────────┐
│  HeatFlowSite   │ ← Sample (via GenericHole + GeoDepthInterval + GenericEarthSample)
│  (site-level)   │
└────────┬────────┘
         │ sample FK (unique=True)         sample FK (1:N)
         ▼                                        │
┌─────────────────┐                    ┌──────────▼──────────┐
│ ParentHeatFlow  │ ← Measurement      │  HeatFlowInterval   │ ← Sample (via Interval + GeoDepthInterval)
│  (aggregated)   │                    │  (depth interval)    │
└────────┬────────┘                    └──┬──────┬──────┬────┘
         │ parent FK (1:N, SET_NULL)      │      │      │
         │                                │      │      │ OneToOne
         │      ┌─────────────────────────┘      │      ▼
         │      │ sample FK (1:N)                 │  ┌──────────────┐
         │      ▼                                 │  │ProbeMetadata │ ← Model
         │  ┌──────────────┐                      │  │(marine only) │
         │  │ThermalGradient│ ← Measurement       │  └──────────────┘
         │  └──────┬───────┘                      │
         │         │ FK (nullable, 1:N)           │ sample FK (1:N)
         │         │                              │
         │      ┌──▼──────────────────────────────▼──┐
         └─────►│         HeatFlow (child)           │ ← Measurement
                │  thermal_gradient FK ──────────────┤
                │  thermal_conductivity FK ──────────┤
                └──────────────┬─────────────────────┘
                               │ FK (1:N, CASCADE)
                               ▼
                     ┌──────────────────┐
                     │HeatFlowCorrection│ ← Model
                     │(per disturbance) │
                     └──────────────────┘
```

Also:

- `IntervalConductivity` (Measurement) links to `HeatFlowInterval` via `sample` FK (1:N)
- `HeatFlow.thermal_conductivity` → nullable FK to `IntervalConductivity`

---

## Entity Definitions

### 1. HeatFlowSite

**Inherits**: `GenericHole` → `GenericEarthSample` → `Sample` (from fairdm-geo); also mixes in `GeoDepthInterval`

**Purpose**: The geographic measurement location — a borehole, mine shaft, or marine probe site.

**GHFDB mapping**: Parent-level fields P01–P13 (site context only; P01–P02 live on ParentHeatFlow).

| Field | Django Type | Units | Null | Validators | GHFDB Ref | Notes |
|-------|-----------|-------|------|------------|-----------|-------|
| *Inherited from GenericHole* |
| `name` | CharField(255) | — | ✓ | — | P03 | Inherited from Sample |
| `location` | PointField | — | ✓ | — | P04, P05 | Inherited from Sample (PostGIS) |
| `azimuth` | DecimalQuantityField | ° | ✓ | 0–360 | — | Borehole azimuth |
| `inclination` | DecimalQuantityField | ° | ✓ | -90–90 | — | Borehole inclination |
| `length` | QuantityField | m | ✓ | ≥0 | P10 | Total measured depth (MD) |
| *Inherited from GeoDepthInterval* |
| `top` | QuantityField | m | ✓ | — | — | Site-level top depth (defaults to 0) |
| `bottom` | QuantityField | m | ✓ | — | — | Site-level bottom depth |
| `vertical_depth` | QuantityField | m | ✓ | — | P11 | Total true vertical depth (TVD) |
| `vertical_datum` | ConceptField | — | ✓ | — | — | Vertical datum reference |
| `lithology` | ConceptManyToManyField | — | blank | — | — | M2M, site-level lithology |
| `age` | ConceptManyToManyField | — | blank | — | — | M2M, geologic age |
| `stratigraphy` | ConceptManyToManyField | — | blank | — | — | M2M, stratigraphic unit |
| *Own fields* |
| `type` | ConceptField | — | — | — | — | SiteType vocabulary, default "unknown" |
| `elevation_datum` | ConceptField | — | — | — | — | ElevationDatum vocabulary, default "MSL" |
| `elevation` | QuantityField | m | ✓ | — | P06 | Elevation above/below sea level |
| `environment` | ConceptField | — | — | — | P07 | GeographicEnvironment vocabulary |
| `explo_method` | ConceptField | — | ✓ | — | P12 | ExplorationMethod vocabulary |
| `explo_purpose` | ConceptManyToManyField | — | blank | — | P13 | ExplorationPurpose vocabulary |
| `country` | CharField(100) | — | ✓ | — | — | Country (future: auto from GIS) |
| `region` | CharField(100) | — | ✓ | — | — | Region |
| `continent` | CharField(100) | — | ✓ | — | — | Continent |
| `domain` | CharField(100) | — | ✓ | — | — | Geological domain |

**Meta**:

- `verbose_name`: "Heat Flow Site"
- `db_table_comment`: Describes purpose
- Indexes: `country`, `continent`, `environment`

**Properties**:

- `total_depth_MD` → returns `self.length`
- `total_depth_TVD` → returns `self.vertical_depth`

**save() behaviour**: Sets `top = 0` if not provided.

---

### 2. HeatFlowInterval

**Inherits**: `Interval` → `Sample` (from fairdm-geo); also mixes in `GeoDepthInterval`

**Purpose**: A depth-stratified section within a borehole over which child heat flow measurements are made.

**GHFDB mapping**: C04 (interval top), C05 (interval bottom), C25 (lithology), C26 (stratigraphy).

| Field | Django Type | Units | Null | Validators | GHFDB Ref | Notes |
|-------|-----------|-------|------|------------|-----------|-------|
| *Inherited from Interval / GeoDepthInterval* |
| `top` | QuantityField | m | ✓ | — | C04 | True vertical depth of interval top |
| `bottom` | QuantityField | m | ✓ | — | C05 | True vertical depth of interval bottom |
| `vertical_depth` | QuantityField | m | ✓ | — | — | Vertical depth |
| `vertical_datum` | ConceptField | — | ✓ | — | — | Vertical datum |
| `lithology` | ConceptManyToManyField | — | blank | — | C25 | M2M, interval-level lithology |
| `age` | ConceptManyToManyField | — | blank | — | — | M2M, geologic age |
| `stratigraphy` | ConceptManyToManyField | — | blank | — | C26 | M2M, stratigraphic unit |
| *Inherited from Sample* |
| `sample` | FK → Sample | — | ✓ | — | — | Parent sample (→ HeatFlowSite) |

**Meta**:

- `verbose_name`: "Depth interval"

**No own fields** — all fields are inherited.

---

### 3. ParentHeatFlow

**Inherits**: `Measurement`

**Purpose**: The aggregated, quality-controlled surface heat flow value for a site. One per HeatFlowSite (globally unique).

**GHFDB mapping**: P01 (heat flow value), P02 (uncertainty), P08 (comment), P09 (HP flag).

| Field | Django Type | Units | Null | Validators | GHFDB Ref | Notes |
|-------|-----------|-------|------|------------|-----------|-------|
| *Inherited from Measurement* |
| `sample` | FK → Sample | — | ✓ | — | — | → HeatFlowSite; **UniqueConstraint in Meta** |
| *Own fields* |
| `value` | QuantityField | mW/m² | — | ±10⁶ | P01 | Aggregated heat flow |
| `uncertainty` | QuantityField | mW/m² | ✓ | 0–10⁶ | P02 | 1σ uncertainty |
| `corr_HP_flag` | BooleanField | — | ✓ | — | P09 | Heat production correction flag |
| `comment` | TextField | — | ✓ | — | P08 | General comments |
| `ghfdb_id` | PositiveIntegerField| — | ✓ | — | — | Nullable spreadsheet reference integer; correlates DB entries to GHFDB spreadsheet release; `IS NOT NULL` implies GHFDB membership |
| `quality` | CharField(13) | — | ✓ | — | — | 13-character quality code string,  nullable for non-GHFDB entries |
| ~~`is_ghfdb`~~ | ~~BooleanField~~ | — | — | — | — | ~~Removed — membership now determined by `ghfdb_id IS NOT NULL`~~ |
| ~~`local_id`~~ | ~~CharField(255)~~ | — | — | — | — | ~~Removed — function assumed by `ghfdb_id`~~ |

**Meta**:

- `verbose_name`: "Heat Flow" (singular & plural)
- `db_table`: "ghfdb_parentheatflow"
- Indexes: `ghfdb_id`, `corr_HP_flag`

**Constraints**:

- `Meta.constraints`: `UniqueConstraint(fields=["sample"], name="unique_parent_per_site")` — one `ParentHeatFlow` per `HeatFlowSite` globally. The `sample` FK is declared in the fairdm package and cannot be modified with `unique=True` directly; `UniqueConstraint` in `Meta` achieves the same DB-level enforcement.

**save() behaviour**:

- Validates `sample` is instance of `HeatFlowSite` (FR-008a)
- Existing save()-level uniqueness check is retained as an additional application-layer guard alongside the `Meta.constraints` DB constraint

---

### 4. HeatFlowInterval → HeatFlow → ParentHeatFlow Hierarchy

This section documents the aggregation relationship.

- `HeatFlowSite` ←(sample FK, unique)— `ParentHeatFlow`
- `HeatFlowSite` ←(sample FK, 1:N)— `HeatFlowInterval`
- `HeatFlowInterval` ←(sample FK, 1:N)— `HeatFlow`
- `ParentHeatFlow` ←(parent FK, 1:N, SET_NULL)— `HeatFlow`

A `ParentHeatFlow` aggregates multiple `HeatFlow` children. Each child has an `is_relevant` flag indicating whether it contributed to the parent value.

---

### 5. HeatFlow (Child)

**Inherits**: `Measurement`

**Purpose**: A single interval-level heat flow determination computed from one ThermalGradient and one IntervalConductivity.

**GHFDB mapping**: C01–C03, C09–C10, C20, C24, C38.

| Field | Django Type | Units | Null | Validators | GHFDB Ref | Notes |
|-------|-----------|-------|------|------------|-----------|-------|
| *Inherited from Measurement* |
| `sample` | FK → Sample | — | ✓ | — | — | → HeatFlowInterval (validated in save()) |
| *Own fields — Heat Flow Density* |
| `value` | QuantityField | mW/m² | — | ±10⁶ | C01 | Child heat flow value |
| `uncertainty` | QuantityField | mW/m² | ✓ | 0–10⁶ | C02 | 1σ uncertainty |
| `method` | ConceptManyToManyField | — | blank | — | C03 | HeatFlowMethod vocabulary |
| *Own fields — Metadata* |
| `expedition` | CharField(255) | — | ✓ | — | C20 | Expedition/platform/ship |
| `water_temperature` | QuantityField | °C | ✓ | -10–1000 | C24 | Bottom water temperature |
| `date_acquired` | PartialDateField | — | ✓ | — | C38 | Acquisition date (YYYY-MM-DD) |
| `c_comment` | TextField | — | ✓ | — | C10 | Child-level comments |
| *Own fields — Quality Scores (stored, not computed)* |
| `U_score` | CharField(2) | — | — | choices | — | UScoreOptions enum, default Ux |
| `M_score` | CharField(2) | — | — | choices | — | MScoreOptions enum, default Mx |
| *Own fields — Relationships* |
| `parent` | FK → ParentHeatFlow | — | ✓ | — | — | SET_NULL; related_name="children" |
| `is_relevant` | BooleanField | — | — | — | C09 | Used in parent computation? default False |
| `thermal_gradient` | FK → ThermalGradient | — | ✓ | — | — | **Changed from OneToOne to FK (FR-013)** |
| `thermal_conductivity` | FK → IntervalConductivity | — | ✓ | — | — | **Changed from OneToOne to FK (FR-013)** |
| *Own fields — GHFDB Reference* |
| `ghfdb_id` | PositiveIntegerField| — | ✓ | — | — | Nullable spreadsheet reference integer; correlates DB child entries to GHFDB spreadsheet release |
| `quality` | CharField(13) | — | — | — | — | 13-character quality code string |
| ~~`local_id`~~ | ~~CharField(255)~~ | — | — | — | — | ~~Removed — function assumed by `ghfdb_id`~~ |

**Meta**:

- `verbose_name`: "Heat Flow"
- Indexes: `U_score`, `M_score`

**save() behaviour**:

- Validates `sample` is instance of `HeatFlowInterval` (FR-010a)

**Fields to REMOVE** (cleanup from older design):

- `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag` → replaced by `HeatFlowCorrection` records
- `probe_penetration`, `probe_length`, `probe_tilt` → belong on `ProbeMetadata`
- ~~`local_id`~~ → removed; function assumed by `ghfdb_id`

**Methods to KEEP but defer implementation**:

- `get_U_score()` — algorithm deferred per spec
- `get_M_score()` — algorithm deferred per spec
- `is_probe` — cached property, checks interval for probe metadata

---

### 6. ThermalGradient

**Inherits**: `Measurement`

**Purpose**: Temperature gradient measurement over a HeatFlowInterval.

**GHFDB mapping**: C27–C37.

| Field | Django Type | Units | Null | Validators | GHFDB Ref | Notes |
|-------|-----------|-------|------|------------|-----------|-------|
| *Inherited from Measurement* |
| `sample` | FK → Sample | — | ✓ | — | — | → HeatFlowInterval (validated in save()) |
| *Own fields — Gradient Values* |
| `value` | DecimalQuantityField(7,2) | K/km | — | ±10⁵ | C27 | Measured gradient (**NOT NULL**) |
| `uncertainty` | DecimalQuantityField(7,2) | K/km | ✓ | 0–10⁵ | C28 | Measured gradient uncertainty |
| `corrected_value` | DecimalQuantityField(5,2) | K/km | ✓ | ±10⁵ | C29 | Corrected gradient |
| `corrected_uncertainty` | DecimalQuantityField(5,2) | K/km | ✓ | ±10⁵ | C30 | Corrected gradient uncertainty |
| *Own fields — Temperature Method* |
| `method_top` | ConceptManyToManyField | — | blank | — | C31 | TemperatureMethod vocabulary |
| `method_bottom` | ConceptManyToManyField | — | blank | — | C32 | TemperatureMethod vocabulary |
| `shutin_top` | PositiveIntegerQuantityField | hour | ✓ | ≤10000 | C33 | Shut-in time at top |
| `shutin_bottom` | PositiveIntegerQuantityField | hour | ✓ | ≤10000 | C34 | Shut-in time at bottom |
| `correction_top` | ConceptManyToManyField | — | blank | — | C35 | TemperatureCorrection vocabulary |
| `correction_bottom` | ConceptManyToManyField | — | blank | — | C36 | TemperatureCorrection vocabulary |
| *Own fields — Quality* |
| `number` | PositiveSmallIntegerField | — | ✓ | >0 | C37 | Number of temperature recordings |
| `score` | FloatField | — | — | 0.0–1.0 | — | Quality score, default 1.0 |

**Meta**:

- `verbose_name`: "Thermal Gradient"
- Indexes: `score`, `number`
- Constraints: `number > 0` (when not null)

**save() behaviour**:

- Validates `sample` is instance of `HeatFlowInterval` (FR-016a)

---

### 7. IntervalConductivity

**Inherits**: `Measurement`

**Purpose**: Mean thermal conductivity over a HeatFlowInterval.

**GHFDB mapping**: C39–C48.

| Field | Django Type | Units | Null | Validators | GHFDB Ref | Notes |
|-------|-----------|-------|------|------------|-----------|-------|
| *Inherited from Measurement* |
| `sample` | FK → Sample | — | ✓ | — | — | → HeatFlowInterval (validated in save()) |
| *Own fields — Conductivity Values* |
| `value` | DecimalQuantityField(4,2) | W/mK | — | 0–100 | C39 | Mean conductivity (**NOT NULL**) |
| `uncertainty` | DecimalQuantityField(4,2) | W/mK | ✓ | 0–100 | C40 | Conductivity uncertainty |
| *Own fields — Method & Source* |
| `source` | ConceptManyToManyField | — | blank | — | C41 | ConductivitySource vocabulary |
| `location` | ConceptManyToManyField | — | blank | — | C42 | ConductivityLocation vocabulary |
| `method` | ConceptManyToManyField | — | blank | — | C43 | ConductivityMethod vocabulary |
| `saturation` | ConceptManyToManyField | — | blank | — | C44 | ConductivitySaturation vocabulary |
| `pT_conditions` | ConceptManyToManyField | — | blank | — | C45 | ConductivityPTConditions vocabulary |
| `pT_function` | ConceptManyToManyField | — | blank | — | C46 | ConductivityPTFunction vocabulary |
| `strategy` | ConceptManyToManyField | — | blank | — | C48 | ConductivityStrategy vocabulary |
| *Own fields — Quality* |
| `number` | PositiveSmallIntegerField | — | ✓ | ≤10000 | C47 | Number of conductivity determinations |
| `score` | FloatField | — | — | 0.0–1.1 | — | Quality score, default 1.1 |

**Meta**:

- `verbose_name`: "Thermal Conductivity"
- Indexes: `number`

**save() behaviour**:

- Validates `sample` is instance of `HeatFlowInterval` (FR-018a)
- Recalculates `score` via `calculate_score()` (existing behaviour)

---

### 8. ProbeMetadata

**Inherits**: `django.db.models.Model` (NOT Measurement)

**Purpose**: Instrument parameters for marine heat flow probe deployments.

**GHFDB mapping**: C06, C21, C22, C23.

| Field | Django Type | Units | Null | Validators | GHFDB Ref | Notes |
|-------|-----------|-------|------|------------|-----------|-------|
| `interval` | OneToOneField → HeatFlowInterval | — | — | — | — | CASCADE; related_name="probe_metadata" |
| `penetration` | DecimalQuantityField(5,2) | m | ✓ | 0–100 | C06 | Probe penetration depth |
| `probe_type` | ConceptManyToManyField | — | blank | — | C21 | ProbeType vocabulary |
| `length` | DecimalQuantityField(5,2) | m | ✓ | 0–100 | C22 | Probe length |
| `tilt` | DecimalQuantityField(4,2) | ° | ✓ | 0–90 | C23 | Probe tilt angle |

**Meta**:

- `verbose_name`: "Probe Metadata"

**Deletion**: CASCADE from HeatFlowInterval (FR-020).

---

### 9. HeatFlowCorrection

**Inherits**: `django.db.models.Model` (NOT Measurement)

**Purpose**: Records of environmental/methodological disturbances and their correction status.

**GHFDB mapping**: C11–C19 (correction flags).

| Field | Django Type | Units | Null | Validators | GHFDB Ref | Notes |
|-------|-----------|-------|------|------------|-----------|-------|
| `heat_flow` | FK → HeatFlow | — | — | — | — | CASCADE; related_name="corrections" |
| `correction_type` | CharField(10) | — | — | choices | C11–C19 | CorrectionTypeChoices enum |
| `status` | CharField(25) | — | — | choices | — | StatusChoices enum, default "unspecified" |
| `comment` | TextField | — | ✓ | — | — | Correction comment |

**CorrectionTypeChoices**: IS, T, S, E, TOPO, PAL, SUR, CONV, HR

**StatusChoices**: present_corrected, present_not_corrected, present_not_significant, not_recognized, considered_p, considered_t, considered_pt, not_considered, tilt_corrected, drift_corrected, not_corrected, corrected, unspecified

**Valid status per correction type** (enforced in `save()`):

| CorrectionType | Valid StatusChoices |
|----------------|--------------------|
| IS (in-situ / probe) | present_corrected, present_not_corrected, not_recognized, not_considered, tilt_corrected, drift_corrected, unspecified |
| T (temperature) | present_corrected, present_not_corrected, not_corrected, corrected, not_recognized, not_considered, unspecified |
| S, E, TOPO, PAL, SUR, CONV, HR (environmental) | present_corrected, present_not_corrected, present_not_significant, not_recognized, considered_p, considered_t, considered_pt, not_considered, unspecified |

**save() behaviour**: Raises `ValidationError` when `status` is not in the valid set for the given `correction_type`. A class-level `VALID_STATUS_FOR_TYPE` constant dict drives the lookup.

**Meta**:

- `verbose_name`: "Heat Flow Correction"
- `unique_together`: `[("heat_flow", "correction_type")]`
- Indexes: `correction_type`, `status`

---

## Relationship Summary

| From | To | Type | on_delete | Constraint | Related Name |
|------|----|------|-----------|------------|-------------|
| ParentHeatFlow | HeatFlowSite | FK (via sample) | CASCADE | UniqueConstraint in Meta | measurements |
| HeatFlowInterval | HeatFlowSite | FK (via sample) | CASCADE | — | measurements |
| HeatFlow | HeatFlowInterval | FK (via sample) | CASCADE | — | measurements |
| HeatFlow | ParentHeatFlow | FK (parent) | SET_NULL | nullable | children |
| HeatFlow | ThermalGradient | FK | CASCADE | nullable | heat_flow_children |
| HeatFlow | IntervalConductivity | FK | CASCADE | nullable | heat_flow_children |
| ThermalGradient | HeatFlowInterval | FK (via sample) | CASCADE | — | measurements |
| IntervalConductivity | HeatFlowInterval | FK (via sample) | CASCADE | — | measurements |
| ProbeMetadata | HeatFlowInterval | OneToOne | CASCADE | — | probe_metadata |
| HeatFlowCorrection | HeatFlow | FK | CASCADE | unique_together w/ type | corrections |

---

## GHFDB Field Coverage Matrix

### Parent Level (P01–P13)

| GHFDB ID | Field Name | Django Model.field | Status |
|----------|------------|-------------------|--------|
| P01 | Heat Flow Value | ParentHeatFlow.value | ✅ Existing |
| P02 | Heat Flow Uncertainty | ParentHeatFlow.uncertainty | ✅ Existing |
| P03 | Site Name | HeatFlowSite.name | ✅ Inherited from Sample |
| P04 | Latitude | HeatFlowSite.location (PointField) | ✅ Inherited from Sample |
| P05 | Longitude | HeatFlowSite.location (PointField) | ✅ Inherited from Sample |
| P06 | Elevation | HeatFlowSite.elevation | ✅ Existing |
| P07 | Geographic Environment | HeatFlowSite.environment | ✅ Existing |
| P08 | General Comments | ParentHeatFlow.comment | ✅ Existing |
| P09 | HP Correction Flag | ParentHeatFlow.corr_HP_flag | ✅ Existing |
| P10 | Total Measured Depth | HeatFlowSite.length (via GenericHole) | ✅ Inherited |
| P11 | Total True Vertical Depth | HeatFlowSite.vertical_depth (via GeoDepthInterval) | ✅ Inherited |
| P12 | Exploration Method | HeatFlowSite.explo_method | ✅ Existing |
| P13 | Exploration Purpose | HeatFlowSite.explo_purpose | ✅ Existing |

### Child Level (C01–C49)

| GHFDB ID | Field Name | Django Model.field | Status |
|----------|------------|-------------------|--------|
| C01 | Heat Flow Value | HeatFlow.value | ✅ Existing |
| C02 | Heat Flow Uncertainty | HeatFlow.uncertainty | ✅ Existing |
| C03 | Heat Flow Method | HeatFlow.method | ✅ Existing |
| C04 | Interval Top | HeatFlowInterval.top | ✅ Inherited |
| C05 | Interval Bottom | HeatFlowInterval.bottom | ✅ Inherited |
| C06 | Penetration Depth | ProbeMetadata.penetration | ✅ Existing |
| C07 | Primary Publication | *FairDM Dataset.literature* | ✅ Inherited via FairDM |
| C08 | Additional References | *FairDM Dataset.literature* | ✅ Inherited via FairDM |
| C09 | Relevant Child | HeatFlow.is_relevant | ✅ Existing |
| C10 | General Comments | HeatFlow.c_comment | ✅ Existing |
| C11 | Flag In-Situ | HeatFlowCorrection(type=IS) | ✅ Existing |
| C12 | Flag Temperature | HeatFlowCorrection(type=T) | ✅ Existing |
| C13 | Flag Sedimentation | HeatFlowCorrection(type=S) | ✅ Existing |
| C14 | Flag Erosion | HeatFlowCorrection(type=E) | ✅ Existing |
| C15 | Flag Topography | HeatFlowCorrection(type=TOPO) | ✅ Existing |
| C16 | Flag Paleoclimate | HeatFlowCorrection(type=PAL) | ✅ Existing |
| C17 | Flag Bottom Water | HeatFlowCorrection(type=SUR) | ✅ Existing |
| C18 | Flag Convection | HeatFlowCorrection(type=CONV) | ✅ Existing |
| C19 | Flag Heat Refraction | HeatFlowCorrection(type=HR) | ✅ Existing |
| C20 | Expedition | HeatFlow.expedition | ✅ Existing |
| C21 | Probe Type | ProbeMetadata.probe_type | ✅ Existing |
| C22 | Probe Length | ProbeMetadata.length | ✅ Existing |
| C23 | Probe Tilt | ProbeMetadata.tilt | ✅ Existing |
| C24 | Bottom Water Temp | HeatFlow.water_temperature | ✅ Existing |
| C25 | Lithology | HeatFlowInterval.lithology | ✅ Inherited |
| C26 | Stratigraphic Age | HeatFlowInterval.stratigraphy | ✅ Inherited |
| C27 | Thermal Gradient | ThermalGradient.value | ✅ Existing |
| C28 | Gradient Uncertainty | ThermalGradient.uncertainty | ✅ Existing |
| C29 | Corrected Gradient | ThermalGradient.corrected_value | ✅ Existing |
| C30 | Corrected Gradient Unc | ThermalGradient.corrected_uncertainty | ✅ Existing |
| C31 | Temp Method (Top) | ThermalGradient.method_top | ✅ Existing |
| C32 | Temp Method (Bottom) | ThermalGradient.method_bottom | ✅ Existing |
| C33 | Shut-In Time (Top) | ThermalGradient.shutin_top | ✅ Existing |
| C34 | Shut-In Time (Bottom) | ThermalGradient.shutin_bottom | ✅ Existing |
| C35 | Correction Method (Top) | ThermalGradient.correction_top | ✅ Existing |
| C36 | Correction Method (Bot) | ThermalGradient.correction_bottom | ✅ Existing |
| C37 | Num Temperature Records | ThermalGradient.number | ✅ Existing |
| C38 | Date of Acquisition | HeatFlow.date_acquired | ✅ Existing |
| C39 | Mean TC | IntervalConductivity.value | ✅ Existing |
| C40 | TC Uncertainty | IntervalConductivity.uncertainty | ✅ Existing |
| C41 | TC Source | IntervalConductivity.source | ✅ Existing |
| C42 | TC Location | IntervalConductivity.location | ✅ Existing |
| C43 | TC Method | IntervalConductivity.method | ✅ Existing |
| C44 | TC Saturation | IntervalConductivity.saturation | ✅ Existing |
| C45 | TC pT Conditions | IntervalConductivity.pT_conditions | ✅ Existing |
| C46 | TC pT Function | IntervalConductivity.pT_function | ✅ Existing |
| C47 | TC Number | IntervalConductivity.number | ✅ Existing |
| C48 | TC Averaging Strategy | IntervalConductivity.strategy | ✅ Existing |
| C49 | IGSN | HeatFlowSite.identifiers / HeatFlowInterval.identifiers (FairDM Sample) | ✅ Inherited | Note: IGSN identifies the physical sample, not the heat flow measurement; served by FairDM’s generic identifier relationship on both Sample subclasses. `HeatFlow.IGSN` field removed. |

**Coverage**: 62/62 fields mapped (P01–P13 + C01–C49). All fields have corresponding Django model fields, either through direct declaration or inheritance from FairDM/fairdm-geo base classes.

---

## Validation Rules

### save()-Level Type Enforcement

All four Measurement subclasses validate their `sample` FK target type in `save()`:

```python
# Pattern applied to ParentHeatFlow, HeatFlow, ThermalGradient, IntervalConductivity
def save(self, *args, **kwargs):
    if self.sample_id:
        # Force polymorphic downcast evaluation
        sample = self.sample
        if not isinstance(sample, ExpectedSampleClass):
            raise ValidationError(
                _("Sample must be a {expected} instance.").format(
                    expected=ExpectedSampleClass.__name__
                )
            )
    super().save(*args, **kwargs)
```

### Field-Level Validators

| Model | Field | Validator | Notes |
|-------|-------|-----------|-------|
| ParentHeatFlow | value | MinVal(-10⁶), MaxVal(10⁶) | ±1,000,000 mW/m² |
| ParentHeatFlow | uncertainty | MinVal(0), MaxVal(10⁶) | Non-negative |
| HeatFlow | value | MinVal(-10⁶), MaxVal(10⁶) | Same as parent |
| HeatFlow | uncertainty | MinVal(0), MaxVal(10⁶) | Non-negative |
| HeatFlow | water_temperature | MinVal(-10), MaxVal(1000) | °C range |
| ThermalGradient | value | MinVal(-10⁵), MaxVal(10⁵) | K/km |
| ThermalGradient | uncertainty | MinVal(0), MaxVal(10⁵) | Non-negative |
| ThermalGradient | number | >0 (CheckConstraint) | When not null |
| IntervalConductivity | value | MinVal(0), MaxVal(100) | W/mK |
| IntervalConductivity | uncertainty | MinVal(0), MaxVal(100) | |
| ProbeMetadata | penetration | MinVal(0), MaxVal(100) | m |
| ProbeMetadata | length | MinVal(0), MaxVal(100) | m |
| ProbeMetadata | tilt | MinVal(0), MaxVal(90) | degrees |

### Uniqueness Constraints

| Model | Field(s) | Type |
|-------|----------|------|
| ParentHeatFlow | sample | UniqueConstraint in Meta (1 parent per site) |
| HeatFlowCorrection | (heat_flow, correction_type) | unique_together |

### Cascade/SET_NULL Rules

| When Deleted | Effect on Related |
|-------------|-------------------|
| HeatFlowSite | CASCADE → ParentHeatFlow, HeatFlowInterval |
| HeatFlowInterval | CASCADE → HeatFlow, ThermalGradient, IntervalConductivity, ProbeMetadata |
| ParentHeatFlow | SET_NULL → HeatFlow.parent becomes NULL |
| HeatFlow | CASCADE → HeatFlowCorrection |
| ThermalGradient | CASCADE → HeatFlow.thermal_gradient becomes NULL? |

**Note on ThermalGradient/IntervalConductivity deletion**: With the change from OneToOne to FK, the `on_delete` semantics need clarification. The existing code uses `CASCADE` for the OneToOne field. With FK, `CASCADE` on HeatFlow's gradient/conductivity FK would mean deleting a ThermalGradient cascades to delete all HeatFlow children that reference it — which is likely NOT desired for scientific data. Recommend changing to `SET_NULL` for these FKs. However, the spec says `on_delete=models.CASCADE` on the existing fields; this should be reviewed and updated to `SET_NULL` for safety during implementation.

---

## Changes from Current Codebase

### Must Change

1. **HeatFlow.thermal_gradient**: `OneToOneField` → `ForeignKey` (nullable), `on_delete=CASCADE` → consider `SET_NULL`
2. **HeatFlow.thermal_conductivity**: `OneToOneField` → `ForeignKey` (nullable), `on_delete=CASCADE` → consider `SET_NULL`
3. **HeatFlow: Remove old correction flag fields**: `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag`
4. **HeatFlow: Remove duplicate probe fields**: `probe_penetration`, `probe_length`, `probe_tilt` (these belong on ProbeMetadata)
5. **ParentHeatFlow uniqueness**: Add `UniqueConstraint(fields=["sample"], name="unique_parent_per_site")` in `Meta.constraints` (the `sample` FK is declared in the fairdm package and cannot be altered with `unique=True`)
6. **All four Measurement save()**: Add/verify `ValidationError` for incorrect sample type
7. **config.py**: Add `ParentHeatFlowConfig` and `IntervalConductivityConfig` registrations
8. **config.py**: Retain `ThermalGradientConfig` registration (ALL Measurement subclasses must be registered; previous proposal to remove is reversed)
9. **factories.py**: Add `ParentHeatFlowFactory`, `ProbeMetadataFactory`; update `HeatFlowFactory` to remove deleted fields; keep factories minimal (see R10)
10. **HeatFlow**: Remove `IGSN` field; C49 is served by FairDM Sample identifier relationship on `HeatFlowSite` and `HeatFlowInterval`
11. **HeatFlowCorrection.save()**: Add `ValidationError` for invalid status/correction_type combinations (see R4 valid-combinations table)

### Already Correct (No Change Needed)

1. HeatFlowSite model structure and fields
2. HeatFlowInterval model structure
3. ThermalGradient model fields
4. IntervalConductivity model fields
5. ProbeMetadata model structure
6. HeatFlowCorrection model structure
7. All vocabulary definitions
8. IHFCConfig base class

---

## FairDM Registry Configurations

### Registered Models (6)

| Config Class | Model | Inherits | Key Config |
|-------------|-------|----------|------------|
| HeatFlowSiteConfig | HeatFlowSite | IHFCConfig | fields, filterset_class, table_class |
| HeatFlowIntervalConfig | HeatFlowInterval | IHFCConfig | fields, table_class |
| ParentHeatFlowConfig | ParentHeatFlow | IHFCConfig | fields, description **(NEW)** |
| HeatFlowConfig | HeatFlow | IHFCConfig | fields, filterset_class, table_class |
| ThermalGradientConfig | ThermalGradient | IHFCConfig | fields **(RETAINED — was proposed for removal)** |
| IntervalConductivityConfig | IntervalConductivity | IHFCConfig | fields **(NEW)** |

### Unregistered Models (2)

`ProbeMetadata` and `HeatFlowCorrection` — plain `django.db.models.Model` subclasses (not FairDM `Measurement`/`Sample`); managed inline via their parent models.

### ParentHeatFlowConfig (New)

```python
@fairdm.register
class ParentHeatFlowConfig(IHFCConfig):
    model = ParentHeatFlow
    description = _(
        "The aggregated, quality-controlled surface heat flow value for a "
        "heat flow site, representing the representative heat flux after all "
        "corrections and quality assessment."
    )
    keywords = []
    fields = [
        ("value", "uncertainty"),
        "corr_HP_flag",
        "comment",
        "ghfdb_id",
        "quality",
    ]
```

### IntervalConductivityConfig (New)

```python
@fairdm.register
class IntervalConductivityConfig(IHFCConfig):
    model = IntervalConductivity
    description = _(
        "Mean thermal conductivity measurement over a depth interval, used "
        "together with the measured thermal gradient to compute the child heat flow."
    )
    keywords = []
    fields = [
        ("value", "uncertainty"),
        "number",
        "score",
    ]
```
