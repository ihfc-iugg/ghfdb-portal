# Feature Specification: Heat flow held as a normalised relational model

**Feature Branch**: `001-heat-flow-data-model`

**Created**: 2026-04-09

**Rewritten**: 2026-08-20 — audited against the implementation and rewritten in place. The
adjudications behind every change are recorded in [decisions.md](decisions.md).

**Status**: Draft

**Goals**: G1 — heat flow data held as a normalised relational model, designed for the science
rather than for the spreadsheet

**Roadmap**: R1

**References**: Fuchs et al. (2021); Fuchs et al. (2023); constitution principles I, II, III, VI,
VII; ADR-0001, ADR-0004, ADR-0006, ADR-0007

## Overview

The International Heat Flow Commission distributes the Global Heat Flow Database as a flat
spreadsheet. That shape suits data entry and suits nothing else: one row carries site metadata,
interval geometry, two independent measurements and a derived result, so the same site is restated
on every row that mentions it and no field can be constrained without constraining all of them.

The portal stores the science instead. A site is fixed by its coordinate pair and holds at most one
aggregated published value. Within that site are the depth intervals over which measurements were
made. Over each interval sit a thermal gradient and a thermal conductivity, and from that pair a
child heat flow determination is computed and the corrections applied to it are recorded. Every
model extends the framework's `Sample` or `Measurement` base class and is registered with its
registry, so list views, filtering, tables and admin come from configuration rather than custom
view code.

The flat spreadsheet is an import and export product, not the source of truth. Translating between
the two is specified separately in `002-ghfdb-proxy` and `003-ghfdb-import-export`. What belongs
here is the model those features read from and write to, and the documentation that lets an outside
reader follow a published column back to the field that expresses it.

## User Scenarios & Testing

### User Story 1 — A complete heat flow record can be stored and read back (Priority: P1)

A curator or a developer builds a full record through the ORM — a site, an interval within it, a
thermal gradient and a thermal conductivity over that interval, the child determination computed
from them, the corrections applied to it, and the site's aggregated value — then reads every part
of it back with values, units and relationships intact.

**Why this priority**: nothing else in the portal has anything to work on until this holds. Import,
export, the API and the map viewer all read this graph.

**Independent Test**: create the whole graph in one test and assert every field value and every
forward and reverse relationship resolves.

**Acceptance Scenarios**:

1. **Given** an empty database, **When** a site is created with its geographic and exploration
   metadata, **Then** every field is persisted and reads back with its correct value and type.
2. **Given** a stored site, **When** an interval is created against it, **Then** the interval
   resolves to its site, the site lists it among its intervals, and the depth fields read back as
   quantities carrying units.
3. **Given** a stored interval, **When** a thermal gradient and a thermal conductivity are created
   over it, **Then** both resolve to the interval and appear among its measurements.
4. **Given** a stored gradient and conductivity, **When** a child determination is created
   referencing both and linked to the site's aggregated value, **Then** every forward and reverse
   relationship resolves.
5. **Given** a stored child determination, **When** corrections are attached to it, **Then** each
   is reachable from the determination and its type and status are validated.
6. **Given** a child determination with neither a gradient nor a conductivity, **When** it is
   saved, **Then** it is accepted — an incomplete record must not be blocked at entry.

---

### User Story 2 — A site is its coordinates (Priority: P2)

A curator adding a site at a coordinate pair the database already holds is refused, and told which
site already occupies it, rather than creating a duplicate that splits one location's measurements
across two records.

**Why this priority**: coordinates are the only identifier every contributor supplies and the only
one that means the same thing across a century of publications (ADR-0006). A duplicated site is not
a cosmetic problem — it silently divides the measurements at one location, and the aggregated value
each half produces is computed from part of the evidence.

**Independent Test**: create a site at a coordinate pair, attempt a second at the same pair, assert
the second is refused and the first is untouched.

**Acceptance Scenarios**:

1. **Given** a site at a coordinate pair, **When** a second site is saved at the same pair,
   **Then** it is refused with an error naming the coordinate pair.
2. **Given** a site at a coordinate pair, **When** that same site is saved again, **Then** it is
   accepted — the rule constrains other sites, not the record itself.
3. **Given** two sites without coordinates, **When** both are saved, **Then** both are accepted —
   the rule binds only where a location is set.
4. **Given** a site at a coordinate pair, **When** a file is imported carrying a different site
   identifier at that same pair, **Then** the import resolves to the existing site rather than
   creating a second one.
5. **Given** two coordinate pairs a few metres apart, **When** both are saved, **Then** both are
   accepted — coordinates are taken exactly as supplied, with no rounding, tolerance or merging.

---

### User Story 3 — One published value per site, aggregated from its children (Priority: P3)

A curator associates several child determinations with the site's single published value and
records which of them the published value was computed from.

**Why this priority**: the parent and child split is the database's central scientific claim — a
quality-controlled surface value synthesised from potentially many interval measurements. A site
carrying two published values has no defensible answer to which one is the database's.

**Independent Test**: link three children to one site's value, two marked as contributing and one
not, then assert the reverse relation returns all three and the filter returns two. Separately,
attempt a second published value for the same site and assert it is refused.

**Acceptance Scenarios**:

1. **Given** a site's published value, **When** several child determinations are linked to it,
   **Then** all of them are returned by its reverse relation.
2. **Given** children with mixed contribution flags, **When** the relation is filtered on that
   flag, **Then** only the contributing children are returned.
3. **Given** a site's published value with children, **When** it is deleted, **Then** each child
   survives with its link cleared — cascading deletion of scientific measurements is prohibited.
4. **Given** a site that already has a published value, **When** a second is saved against it,
   **Then** it is refused, on every write path in the project including the import path.
5. **Given** a site's published value with no children, **When** it is read, **Then** it is a valid
   record — a newly entered value with no children yet is an ordinary state.

---

### User Story 4 — Marine measurements carry their instrument metadata (Priority: P4)

A curator attaches probe metadata to an interval measured by marine probe, recording the probe
type, its length, how far it penetrated and how far it tilted.

**Why this priority**: marine data is a substantial part of the database, and without instrument
metadata a marine record cannot be quality-assessed or told apart from a borehole record.

**Independent Test**: attach probe metadata to an interval, assert it resolves from the interval
and that a child determination over that interval reports itself as a probe measurement.

**Acceptance Scenarios**:

1. **Given** an interval, **When** probe metadata is created against it, **Then** it resolves from
   the interval and every probe field reads back as a quantity carrying units.
2. **Given** an interval with no probe metadata, **When** the relation is accessed, **Then** the
   framework raises its does-not-exist error, marking the interval as non-marine.
3. **Given** an interval carrying probe metadata, **When** the interval is deleted, **Then** the
   probe metadata is deleted with it.
4. **Given** a child determination over an interval carrying probe metadata, **When** it is asked
   whether it is a probe measurement, **Then** it answers yes, and no otherwise.

---

### User Story 5 — Every model is served by the framework, without custom view code (Priority: P5)

A developer adding a model to this app gets its list view, filtering, table and admin from the
framework by declaring a configuration, and a portal user can browse and filter every scientific
model the app defines.

**Why this priority**: registration is the join between the domain model and the portal's
infrastructure, and it is a constitution principle III requirement. The failure mode here is not a
missing configuration but a configuration that looks complete and is not read — an attribute under
a name the registry does not recognise is set, ignored, and indistinguishable from a working one by
inspection.

**Independent Test**: query the registry for each registered model, assert it carries the
commission's authority and citation and resolves to a usable filter set and table, and assert that
no configuration in the app declares an attribute the registry does not read.

**Acceptance Scenarios**:

1. **Given** the app is loaded, **When** the registry is queried for each of the six models
   extending `Sample` or `Measurement`, **Then** each returns a valid configuration.
2. **Given** a registered configuration, **When** its metadata is read, **Then** it carries the
   commission's authority and its citation.
3. **Given** a registered configuration, **When** its filter set and table are resolved, **Then**
   each yields a usable class, whether supplied or generated.
4. **Given** every configuration in this app, **When** its declared attributes are compared against
   those the registry reads, **Then** none is declared that the registry ignores.
5. **Given** all registrations in place, **When** the framework's system checks run, **Then** they
   report no errors and no warnings.

---

### User Story 6 — Every model has test data, including its vocabulary fields (Priority: P6)

A developer writing a test for any part of this app builds the data it needs from a factory in one
line, and the data it produces includes the controlled-vocabulary fields rather than leaving them
empty.

**Why this priority**: without factories every test assembles the whole graph by hand, which is how
test suites become too expensive to extend. Vocabulary fields matter specifically because they are
the ones the flat format's controlled terms map onto — a factory that leaves them empty means no
test in the repository ever exercises the fields the import and export features depend on.

**Independent Test**: call every factory in a database test and assert each returns a saved
instance whose vocabulary fields are populated.

**Acceptance Scenarios**:

1. **Given** a test database, **When** any factory is called with no arguments, **Then** it returns
   a saved instance and creates whatever related records it needs.
2. **Given** a factory for a model with vocabulary fields, **When** it is called, **Then** those
   fields are populated with concepts drawn from the field's own vocabulary.
3. **Given** any relationship defined in this app, **When** the test suite runs, **Then** at least
   one test exercises it, including the many-to-many relationships and the deletion behaviours.

---

### User Story 7 — A reader can follow a published column to the field that holds it (Priority: P7)

Someone outside the project — a data user, a reviewer, a contributor to the published database —
opens the portal's documentation and finds every column of the published spreadsheet mapped to the
model and field expressing it, alongside a diagram of the models and their relationships. Both
render in the built documentation.

**Why this priority**: the whole justification for a normalised model is that it represents the
science better than the flat format does. That claim is only inspectable if the correspondence
between the two is written down. Constitution principle VII already requires the field map to be
current with every schema change, and today nothing checks that it is.

**Independent Test**: build the documentation and confirm the diagram renders as a diagram; run the
map's test and confirm it fails when a column is removed from the map.

**Acceptance Scenarios**:

1. **Given** the published column definitions, **When** the field map is checked against them,
   **Then** every column appears in the map and names a field or documented accessor that exists on
   the model it cites.
2. **Given** a column added to the published definitions but not to the map, **When** the test
   suite runs, **Then** it fails and names the missing column.
3. **Given** the documentation is built, **When** the data model page is opened, **Then** the
   entity relationship diagram renders as a diagram rather than as source text.
4. **Given** the diagram, **When** it is compared with the models, **Then** it shows every model
   this app defines, the relationships between them and their cardinalities.

---

### Edge Cases

- An interval whose top and bottom are equal, or inverted — validation rejects it.
- A child determination with neither gradient nor conductivity — accepted, per constitution
  principle I: incomplete records are not blocked at entry.
- A site's published value with no children — a valid state.
- A correction whose status is not meaningful for its type, such as a tilt correction on an erosion
  disturbance — rejected on save.
- A second correction of the same type on one determination — rejected; the type is what
  distinguishes them.
- Two sites at coordinate pairs a few metres apart — both accepted. They are two sites.
- A site with no coordinates at all — accepted, and it constrains no other site.

## Clarifications

### Session 2026-08-20 (audit against the implementation)

- Q: Does this feature own `heat_flow/quality.py` and the score calculation it contains? → A: No.
  This feature owns the stored score fields. Calculation is deferred and belongs to the roadmap's
  quality items, which are specified separately. The scoring methods on the models are a deferred
  interface, not dead code, and are left as they stand.
- Q: FR-009 of the original specification required a database `UniqueConstraint` for one published
  value per site, which cannot be declared: `Measurement` is polymorphic, so the `sample` column
  lives on the base measurement table rather than on the model. Database guarantee or application
  guarantee? → A: Application guarantee. The requirement is rewritten to demand enforcement in
  `save()` across every write path, tested through the import path, and the constraint is dropped.
  A partial index on the base table would have to hard-code a content type id in an immutable
  predicate and would work only on PostgreSQL, and there is no bulk write path in the project for
  it to catch.
- Q: The original specification linked an interval to its site through the inherited `sample`
  foreign key, and the code uses an explicit `site` foreign key. Which was intended? → A: The code.
  ADR-0001 records the reasoning, and a test pins the field's name and forbids "parent" and "child"
  in its naming, those words being reserved for the relationship between measurements.
- Q: The original specification presented the `quality` field alongside `ghfdb_id` as
  spreadsheet-derived. ADR-0004 makes the portal's computed code authoritative and rejects imported
  codes. Which holds? → A: ADR-0004. The field remains as storage, and its provenance is the
  portal's own computation.
- Q: ADR-0006 identifies a site by its coordinate pair, and nothing in the model expresses it.
  Document the rule, or enforce it? → A: Enforce it. One site per coordinate pair is a hard
  requirement for the research team and must hold within the application, not only in the import
  path.
- Q: Does the documentation requirement include a maintained diagram? → A: Yes. A diagram in
  Mermaid, rendering in the built documentation, superseding the Graphviz sources and generated
  images alongside it.

## Requirements

### Functional Requirements

**Site**

- **FR-001**: The system MUST provide a `HeatFlowSite` model extending the framework's `Sample`
  base class through the geographic and borehole abstractions, storing site name, country, region,
  continent, geological domain, site type, environment, exploration method, exploration purpose,
  elevation, elevation datum, azimuth, inclination and borehole depth.
- **FR-002**: A site MUST carry its geographic location as a point relationship provided by the
  framework, storing longitude and latitude.
- **FR-003**: Exploration purpose MUST be a many-to-many vocabulary field — several purposes may
  apply to one site.
- **FR-004**: The system MUST refuse a `HeatFlowSite` whose location is a coordinate pair already
  held by another site. The rule applies only where a location is set, does not constrain a site
  against itself, and MUST hold on every write path in the project, including the import path.
  Enforcement is application-level: the framework declares `location` on the polymorphic `Sample`
  base, so the column lives on the base table and a model-level database constraint is not
  declarable.
- **FR-005**: Coordinates MUST be stored exactly as supplied. The system MUST perform no rounding,
  no tolerance matching and no merging of sites that are near each other without being identical
  (ADR-0006).

**Interval**

- **FR-006**: The system MUST provide a `HeatFlowInterval` model extending the framework's `Sample`
  base class through the interval and depth-interval abstractions, storing top depth, bottom depth,
  vertical depth, lithology, geological age and stratigraphic unit.
- **FR-007**: An interval MUST link to its site through an explicit `site` foreign key, reachable
  in reverse as the site's intervals, and deleted with its site. Neither "parent" nor "child" may
  appear in the field's name or its labels — both words are reserved for the relationship between
  measurements (ADR-0001).
- **FR-008**: Interval depth fields MUST be physical quantity fields carrying units, not bare
  numbers.
- **FR-009**: An interval whose top depth is not less than its bottom depth MUST be rejected by
  validation.

**Published site value**

- **FR-010**: The system MUST provide a `ParentHeatFlow` model extending the framework's
  `Measurement` base class, storing the aggregated surface heat flow value in mW/m², its one-sigma
  uncertainty, a heat production correction flag, a comment, a nullable `ghfdb_id` recording the
  record's identifier in the published spreadsheet, and a `quality` code of up to thirteen
  characters. Membership of the published database is expressed by `ghfdb_id` being set; there is
  no separate flag.
- **FR-011**: A published site value MUST link to its site through the inherited `sample` foreign
  key, and MUST reject a sample that is not a `HeatFlowSite`.
- **FR-012**: The system MUST hold at most one `ParentHeatFlow` per site. Enforcement is
  application-level for the reason given in FR-004, and MUST hold on every write path in the
  project, including the import path.
- **FR-013**: The `quality` field MUST be storage only. The portal computes the code it holds and
  that computed value is authoritative, so a code arriving in an imported file is not stored
  (ADR-0004). The computation itself is out of scope for this feature.

**Child determination**

- **FR-014**: The system MUST provide a `HeatFlow` model extending the framework's `Measurement`
  base class, whose `sample` targets a `HeatFlowInterval` and rejects anything else, storing the
  heat flow value in mW/m² with its uncertainty, calculation method as a many-to-many vocabulary
  field, expedition or vessel name, bottom water temperature, date acquired, a numerical
  uncertainty score, a methodological quality score, a comment, a nullable `ghfdb_id` and a
  `quality` code of up to thirteen characters.
- **FR-015**: A child determination MUST link to its site's published value through a nullable
  foreign key that clears rather than cascades on deletion, reachable in reverse as that value's
  children.
- **FR-016**: A child determination MUST record whether it contributed to the published value.
- **FR-017**: A child determination MUST link to its thermal gradient and its thermal conductivity
  through nullable foreign keys rather than one-to-one relationships, so that several
  determinations may share one gradient or one conductivity. Neither may be deleted while a
  determination references it.
- **FR-018**: The numerical uncertainty and methodological quality scores MUST be enumerated choice
  fields taking U1 to U4 and M1 to M4 respectively, each with an additional value for not
  determined, which is the default.

**Thermal gradient**

- **FR-019**: The system MUST provide a `ThermalGradient` model extending the framework's
  `Measurement` base class, storing the measured gradient in K/km with its uncertainty, the
  corrected gradient with its uncertainty, temperature determination methods at the interval top
  and bottom as many-to-many vocabulary fields, shut-in times at top and bottom, correction methods
  at top and bottom as many-to-many vocabulary fields, the number of temperature recordings behind
  the mean, and a score.
- **FR-020**: A thermal gradient MUST link to its interval through the inherited `sample` foreign
  key, and MUST reject a sample that is not a `HeatFlowInterval`.

**Thermal conductivity**

- **FR-021**: The system MUST provide an `IntervalConductivity` model extending the framework's
  `Measurement` base class, storing the mean conductivity in W/mK with its uncertainty, and, as
  many-to-many vocabulary fields, the sample source, the data location, the determination method,
  the saturation state, the pressure and temperature conditions, the pressure and temperature
  correction function and the averaging strategy, together with the number of determinations behind
  the mean and a score.
- **FR-022**: A thermal conductivity MUST link to its interval through the inherited `sample`
  foreign key, and MUST reject a sample that is not a `HeatFlowInterval`.

**Probe metadata**

- **FR-023**: The system MUST provide a `ProbeMetadata` model in a one-to-one relationship with an
  interval, storing probe type as a many-to-many vocabulary field, probe length, penetration depth
  and tilt angle.
- **FR-024**: Deleting an interval MUST delete its probe metadata.
- **FR-025**: A child determination MUST report whether it was acquired by marine probe, which is
  true when its interval carries probe metadata.

**Corrections**

- **FR-026**: The system MUST provide a `HeatFlowCorrection` model linked to a child determination,
  recording a disturbance type drawn from a fixed set and the status of that disturbance and its
  correction.
- **FR-027**: A determination MUST accept several corrections, at most one per disturbance type.
- **FR-028**: A status that is not meaningful for its disturbance type MUST be rejected when the
  correction is saved. The valid combinations MUST be documented in the data model documentation.

**Registration**

- **FR-029**: Every model in this app extending `Sample` or `Measurement` MUST be registered with
  the framework's registry, using a shared base carrying the commission's authority and citation.
  Models that extend neither — probe metadata and corrections — are managed through their parents
  and are not registered.
- **FR-030**: The authority, citation, keywords and repository link MUST be declared where the
  registry reads them, so that a registered model describes and credits itself. Declaring them
  under names the registry does not read leaves a model uncredited while appearing configured.
- **FR-031**: Each registered configuration MUST declare a field list, and MUST declare only
  attributes the registry reads. Where a configuration needs a filter set or a table that differs
  from the generated one, it MUST supply a class rather than options the registry ignores.
  Configuration that names nothing real is worse than no configuration, because it reads as
  deliberate.
- **FR-032**: A configuration MUST NOT supply a component class where the generated one serves,
  per constitution principle IX.

**Migrations and system integrity**

- **FR-033**: Every model change MUST be captured in a migration within this app, and those
  migrations MUST apply cleanly to an empty database, proven by a test that applies them.
- **FR-034**: The framework's system checks MUST report no errors and no warnings.

**Test data and coverage**

- **FR-035**: A factory MUST exist for every model this app defines.
- **FR-036**: Factories MUST populate controlled-vocabulary fields with concepts drawn from each
  field's own vocabulary, rather than leaving them empty.
- **FR-037**: Tests MUST cover, for every model, creation and persistence of its fields, every
  relationship it declares including many-to-many relationships, and every deletion behaviour.

**Documentation**

- **FR-038**: The field map MUST record, for every column of the published spreadsheet, the model
  that expresses it, the field or documented accessor that holds it, and the model that declares
  that field.
- **FR-039**: An automated test MUST assert that the field map covers every column in the canonical
  column definitions and that each mapping names a field or documented accessor that exists.
- **FR-040**: The documentation MUST carry an entity relationship diagram covering every model this
  app defines, its relationships and their cardinalities, written in Mermaid and rendering as a
  diagram in the built documentation.
- **FR-041**: The Mermaid diagram MUST be the only maintained diagram source. The Graphviz sources,
  the generation script, the installation instructions and the images generated from them MUST be
  removed.

### Key Entities

- **HeatFlowSite** — the location where heat flow was measured, a borehole or a probe site,
  identified by its coordinate pair. Holds geographic context, borehole geometry, exploration
  context and the geological properties of the site-level interval.
- **HeatFlowInterval** — a depth-stratified section within a site over which measurements were
  made. A site may have many.
- **ParentHeatFlow** — the aggregated, quality-controlled surface heat flow for a site, and the
  value the published database carries. One per site at most.
- **HeatFlow** — a single interval-level determination, computed from one thermal gradient and one
  thermal conductivity, contributing or not contributing to its site's published value.
- **ThermalGradient** — the temperature gradient measured over an interval, as measured and as
  corrected, with the methods and shut-in times behind it.
- **IntervalConductivity** — the mean thermal conductivity over an interval, with the source,
  method, saturation and pressure and temperature conditions behind it.
- **ProbeMetadata** — the instrument parameters of a marine probe deployment. One per interval at
  most.
- **HeatFlowCorrection** — one disturbance affecting a determination and the status of its
  correction. One per disturbance type per determination.

## Success Criteria

- **SC-001**: The framework's system checks report no errors and no warnings.
- **SC-002**: Every migration in this app applies cleanly to an empty database.
- **SC-003**: The complete graph, from site through interval and its two measurements to the child
  determination and the site's published value, can be built from factory calls alone in a single
  test.
- **SC-004**: A second site at an occupied coordinate pair is refused, and the refusal is proven
  through the import path as well as through the model.
- **SC-005**: A second published value for a site is refused, and the refusal is proven through the
  import path as well as through the model.
- **SC-006**: Every deletion behaviour this feature defines is proven by at least one test:
  clearing a child's link when the published value is deleted, deleting probe metadata with its
  interval, deleting an interval with its site, and refusing to delete a gradient or conductivity a
  determination still references.
- **SC-007**: The registry returns a configuration for each of the six registered models, each one
  carrying the commission's authority and citation and a field list, and each resolving to a usable
  filter set and table.
- **SC-007a**: No configuration in this app declares an attribute the registry does not read.
- **SC-008**: Every model this app defines has a factory, and every controlled-vocabulary field is
  populated by the factory of the model that declares it.
- **SC-009**: Every column in the canonical published column definitions appears in the field map,
  proven by a test that fails when one is missing.
- **SC-010**: The entity relationship diagram renders as a diagram in the built documentation, and
  no Graphviz source, generation script or generated image remains beside it.
- **SC-011**: The test suite passes with no failures.

## Out of Scope

- Quality score calculation, and the scoring interface already present on the models. Both belong
  to the roadmap's quality items and are specified separately. The stored score fields are in
  scope; what fills them is not.
- Translation between this model and the flat published format, in either direction —
  `002-ghfdb-proxy` and `003-ghfdb-import-export` own that. This feature is referenced from the
  import path only to prove that its rules hold there.
- Conceptual and narrative data model documentation beyond the field map and the diagram.
- REST endpoints and serialisers for these models.
- Spatial and geometric query functionality.
- Admin customisation beyond what registration provides.
- Any release or version dimension on the stored data (ADR-0007).

## Assumptions

- The framework's `Sample` and `Measurement` base classes, its polymorphic behaviour and its
  point location model are stable and installed. `Point` already constrains its coordinate pair to
  be unique, so a coordinate pair resolves to exactly one point record.
- The geographic package provides the borehole, earth sample, interval and depth-interval
  abstractions that the site and interval models extend.
- Physical quantity fields from the framework are used for every value carrying units.
- The vocabulary package's concept fields are used for every controlled-term field, and this app's
  vocabulary module is the canonical source of the database's own controlled terms.
- The canonical published column definitions in the extraction app are the authority the field map
  is checked against.
- The portal runs SQLite in development and PostgreSQL in production, so a constraint that only one
  of them can express is not available to this feature.
- Factories use `factory_boy`, one level deep, with multi-model graphs assembled by fixtures rather
  than by chained sub-factories.
