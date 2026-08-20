# Tasks — 001 heat flow data model

Written from `spec.md` as though the repository were empty, then reconciled against the code. The
reconciliation is in `reconciliation.md`, and `feature-state.json` records which tasks it proved
already satisfied.

Writing the list this way is deliberate. A task list written by reading the implementation can only
describe the implementation, which is how a specification audit turns into a rubber stamp.

Tests come before the implementation they cover, per constitution principle VI.

## Phase 1 — Foundations

Blocking. Every story depends on these.

- **T001** Test settings and database strategy: pytest-django configured, a test database that
  applies every migration, and transaction rollback between tests.
- **T002** Shared fixtures: a dataset every model can be attached to, and fixtures assembling the
  multi-model graphs the stories need, so factories stay one level deep.
- **T003** The app's vocabulary module, defining every controlled term set the models reference:
  geographic environment, exploration method, exploration purpose, heat flow method, temperature
  method, temperature correction, probe type, and the seven conductivity vocabularies.
- **T004** App configuration and settings registration.

## Phase 2 — US-1: A complete heat flow record can be stored and read back (P1)

### Tests

- **T005** A site persists every scalar field and reads back with correct values and types.
- **T006** A site's exploration purpose accepts several concepts and reads them back.
- **T007** A site persists and reads back its location as a coordinate pair.
- **T008** An interval resolves to its site, and the site lists it among its intervals.
- **T009** An interval's depth fields read back as quantities carrying units.
- **T010** An interval whose top is not less than its bottom is rejected by validation.
- **T011** A valid interval passes validation.
- **T012** A thermal gradient and a thermal conductivity resolve to their interval and appear among
  its measurements.
- **T013** A gradient rejects a sample that is not an interval.
- **T014** A conductivity rejects a sample that is not an interval.
- **T015** A gradient's value is required at the database layer.
- **T016** A conductivity's value is required at the database layer.
- **T017** A gradient's corrected value, methods, shut-in times and recording count persist.
- **T018** A conductivity's vocabulary fields, determination count and score persist.
- **T019** A child determination resolves to its interval, its gradient, its conductivity and its
  site's published value, and each reverse relation resolves.
- **T020** A child determination rejects a sample that is not an interval.
- **T021** A child determination with neither gradient nor conductivity is accepted.
- **T022** Several child determinations may reference one gradient, and one conductivity.
- **T023** A gradient referenced by a determination cannot be deleted, and neither can a
  conductivity.
- **T024** A child determination's uncertainty and methodological scores default to their
  not-determined values.
- **T025** Corrections attach to a determination and are reachable from it.
- **T026** A second correction of the same type on one determination is rejected.
- **T027** A correction status that is not meaningful for its type is rejected on save.
- **T028** A correction whose type is not in the fixed set is rejected by validation.
- **T029** Deleting a site deletes its intervals.

### Implementation

- **T030** `HeatFlowSite`, extending the framework's sample base through the borehole, earth sample
  and depth-interval abstractions, with every field FR-001 lists.
- **T031** `HeatFlowInterval`, extending the sample base through the interval and depth-interval
  abstractions, with its explicit `site` foreign key and its depth validation.
- **T032** `ThermalGradient`, extending the measurement base, with its sample type guard.
- **T033** `IntervalConductivity`, extending the measurement base, with its sample type guard.
- **T034** `HeatFlow`, extending the measurement base, with its sample type guard, its links to
  gradient and conductivity, and its score fields.
- **T035** `HeatFlowCorrection`, with its type and status sets, its one-per-type constraint and its
  combination validation.
- **T036** The valid status combinations per disturbance type, documented in the data model
  documentation.
- **T037** Migrations for every model above, applying cleanly to an empty database.

## Phase 3 — US-2: A site is its coordinates (P2)

### Tests

- **T038** A second site saved at a coordinate pair another site already holds is refused, and the
  error names the pair.
- **T039** Saving an existing site again is accepted — the rule does not constrain a site against
  itself.
- **T040** Two sites without a location are both accepted.
- **T041** Two sites at coordinate pairs a few metres apart are both accepted.
- **T042** A coordinate pair resolves to one point record, however many sites reference it over
  time.
- **T043** Importing a row whose coordinates match an existing site resolves to that site rather
  than creating a second.
- **T044** Importing a row that carries a site identifier and coordinates belonging to a different
  existing site does not create a duplicate at an occupied pair.

### Implementation

- **T045** Coordinate uniqueness enforcement for sites, at the application layer, binding only
  where a location is set.
- **T046** One notion of site identity in the import path, reconciling the identifier lookup and
  the coordinate lookup so they cannot disagree.

## Phase 4 — US-3: One published value per site (P3)

### Tests

- **T047** A site's published value returns all its children.
- **T048** Filtering those children on the contribution flag returns only the contributing ones.
- **T049** Deleting a published value leaves its children in place with their link cleared.
- **T050** A second published value for a site is refused when saved through the model.
- **T051** A second published value for a site is refused through the import path.
- **T052** A published value with no children is a valid record.
- **T053** A published value rejects a sample that is not a site.
- **T054** A published value persists its uncertainty, correction flag, comment, published
  identifier and quality code.

### Implementation

- **T055** `ParentHeatFlow`, extending the measurement base, with every field FR-010 lists.
- **T056** The one-per-site guarantee, at the application layer, on every write path.
- **T057** Migrations for the published value model.

## Phase 5 — US-4: Marine measurements carry their instrument metadata (P4)

### Tests

- **T058** Probe metadata resolves from its interval, and every probe field reads back as a
  quantity carrying units.
- **T059** Probe metadata accepts several probe type concepts.
- **T060** An interval with no probe metadata raises the framework's does-not-exist error.
- **T061** Deleting an interval deletes its probe metadata.
- **T062** A determination over an interval carrying probe metadata reports itself as a probe
  measurement, and one over an interval without reports the opposite.

### Implementation

- **T063** `ProbeMetadata`, one-to-one with an interval, with its probe fields.
- **T064** The probe-measurement accessor on the child determination.
- **T065** Migration for probe metadata.

## Phase 6 — US-5: Every model is served by the framework (P5)

### Tests

- **T066** The registry returns a configuration for each of the six models extending the sample or
  measurement bases.
- **T067** Each of those configurations declares a field list.
- **T068** Each configuration's metadata carries the commission's authority and its citation.
- **T069** Each configuration resolves to a usable filter set class and a usable table class,
  whether supplied or generated.
- **T070** No configuration in this app declares an attribute the registry does not read.
- **T071** The framework's system checks report no errors and no warnings.
- **T072** Models extending neither base are absent from the registry.

### Implementation

- **T073** The shared configuration base, declaring the commission's authority, citation, keywords
  and repository link as the metadata the registry reads.
- **T074** Every configuration's declarations moved onto attributes the registry reads, and any
  that name nothing removed.
- **T075** A supplied filter set or table only where the generated one will not serve, with the
  reason recorded.

## Phase 7 — US-6: Every model has test data (P6)

### Tests

- **T076** Every factory called with no arguments returns a saved instance.
- **T077** Every factory creates whatever related records its model requires.
- **T078** Each factory populates its model's controlled-vocabulary fields with concepts drawn from
  each field's own vocabulary.
- **T079** The complete graph, site through to published value, is buildable from factory calls
  alone in one test.

### Implementation

- **T080** Factories for all eight models.
- **T081** Vocabulary population in every factory whose model declares a concept field.

## Phase 8 — US-7: A reader can follow a published column to its field (P7)

### Tests

- **T082** Every column in the canonical published column definitions appears in the field map.
- **T083** Every mapping in the field map names a model that exists and a field or documented
  accessor that resolves on it.
- **T084** A column present in the definitions and absent from the map fails the test, naming the
  column.
- **T085** The built documentation renders the entity relationship diagram as a diagram rather than
  as source text.

### Implementation

- **T086** The field map brought current with the model, covering every canonical column.
- **T087** The diagram renderer configured so Mermaid renders in the built documentation.
- **T088** The entity relationship diagram rewritten against the current model, covering every
  model this app defines, its relationships and their cardinalities.
- **T089** The Graphviz sources, the generation script, the installation instructions and the
  images generated from them removed, and the documentation index reconciled.

## Convergence gates

Not tasks, and deliberately unnumbered — nothing dispatches them. They are the conditions the
feature exits on, checked once the stories are done.

- The full test suite passes.
- Lint, formatting and type checks pass on every changed file.
- Migrations are squashed to one change set per model, and apply cleanly to an empty database.
- Documentation touched by any change in this feature is current, per constitution principle VII.
