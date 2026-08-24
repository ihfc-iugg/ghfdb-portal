# Tasks — 002 the published structure read from the model

Written from `spec.md`, `research.md` and `decisions.md` as though the repository held no
implementation of this feature. Nothing here was derived by reading the proxy models, the managers,
the admin, the resources or the existing tests. `constants.py` was read, because it is the canonical
data definition this feature treats as its authority, not an implementation of it.

Writing the list this way is deliberate. A task list written by reading the implementation can only
describe the implementation, which is how a specification audit turns into a rubber stamp. The
difference between this list and what the repository holds is the measurement the exercise exists to
produce.

Tests come before the implementation they cover, per constitution principle VI. Every task is one
increment — one class, one method, one test class. Every implementation task names the test that
proves it and the assertion that fails before it exists.

Nothing here is done. Every box is unchecked, including for behaviour the repository may already
have.

**Names used below.** `GHFDBChild` and `GHFDBParent` in `project/ghfdb/models.py`,
`GHFDBChildQuerySet` / `GHFDBChildManager` / `GHFDBParentQuerySet` / `GHFDBParentManager` in
`project/ghfdb/managers.py`, the published-column mapping in `project/ghfdb/columns.py`, and the two
registrations in `project/ghfdb/admin.py`. Tests mirror that tree under `tests/test_ghfdb/`, per
`tests/README.md`.

---

## Phase 1 — Foundations

Blocking. Every story depends on these. They serve US-1, US-2 and US-3 alike.

- [ ] **T001** *foundations* — The test tree mirroring `project/ghfdb/`: `tests/test_ghfdb/` holding
  `conftest.py`, `test_models.py`, `test_managers.py`, `test_columns.py` and `test_admin.py`, each
  carrying the `ghfdb` marker. `test_views.py` and `test_resources/` are also present in the package
  and belong to other features; they are left alone.
  **Test**: `pytest tests/test_ghfdb --collect-only` names all five modules. Before: collection
  errors with "file or directory not found".

- [ ] **T002** *foundations* — Autouse fixture preloading the controlled-vocabulary concepts into
  the test database, matching the idiom in `tests/test_heat_flow/conftest.py`. Every vocabulary this
  feature filters on needs concept rows to exist.
  **Test**: `TestFixtures::test_vocabulary_concepts_are_present` asserts concepts exist for
  `GeographicEnvironment`, `ExplorationMethod` and `ExplorationPurpose`. Before: each query returns
  nothing.

- [ ] **T003** *foundations* — `dataset` fixture wrapping `DatasetFactory`. Infrastructure, not
  subject, so a factory is correct here per `tests/README.md`.
  **Test**: `TestFixtures::test_dataset_fixture_is_saved` asserts a primary key. Before: fixture
  not found.

- [ ] **T004** *foundations* — `published_chain` fixture building one complete record chain by
  direct ORM calls: site, interval, probe metadata, thermal gradient, interval conductivity, parent
  heat flow, child heat flow, and one correction of each of the nine types, with the published
  identifier set on both the parent and the child.
  **Test**: `TestFixtures::test_published_chain_is_complete` walks each relationship and asserts
  both published identifiers are set. Before: fixture not found.

- [ ] **T005** *foundations* — `published_chains` counted fixture, per R2: a callable fixture that
  builds *n* complete chains and returns them. This is the fixture every query-constancy test takes,
  at two sizes.
  **Test**: `TestFixtures::test_published_chains_builds_the_number_asked_for` calls it at 2 and at 4
  and asserts the row counts. Before: fixture not found.

- [ ] **T006** *foundations* — `unpublished_chain` fixture: the same graph with the published
  identifier unset on both the parent and the child. This is what SC-005 is proven against.
  **Test**: `TestFixtures::test_unpublished_chain_has_no_published_identifier` asserts both are
  `None`. Before: fixture not found.

- [ ] **T007** *foundations* — Partial-chain fixtures: `chain_without_gradient`,
  `chain_without_conductivity`, `chain_without_probe_metadata`, and `chain_missing_correction` taking
  a correction type and omitting only that one.
  **Test**: `TestFixtures::test_partial_chains_omit_only_what_they_name` asserts the named
  relationship is absent and every other one still resolves. Before: fixtures not found.

- [ ] **T008** *foundations* — `sites_by_contribution` fixture building four sites: one whose
  determinations all contributed to the representative value, one where only some did, one where
  none did, and one holding no determinations at all. SC-004 names exactly these four.
  At least one of the four carries two exploration purposes, so that the one many-valued parent
  column is exercised — without it nothing would notice a site rendering twice.
  **Test**: `TestFixtures::test_sites_by_contribution_covers_the_four_shapes` asserts the four child
  populations and that one site has two exploration purposes. Before: fixture not found.

- [ ] **T009** *foundations* — `staff_client` fixture: a logged-in staff user holding view
  permission on both proxies and nothing more.
  **Test**: `TestFixtures::test_staff_client_reaches_the_admin_index` asserts a 200. Before:
  fixture not found.

- [ ] **T010** *foundations* — `constant_query_count` helper fixture, per R2: it runs a callable at
  two row counts under `django_assert_num_queries` and asserts the two counts are equal to each
  other rather than to a literal. Six query-constancy claims and both changelists call it, so the
  abstraction has its callers.
  **Test**: `TestConstantQueryCount` holds two cases — a deliberately linear callable that the
  helper must reject, and a constant one it must accept. The gate is proven against the defect it
  exists to catch, not only against the passing case. Before: helper not found.

---

## Phase 2 — US-1: Determinations read in the published shape (P1)

Discharges FR-001 to FR-007 and FR-011 for the child, and SC-001, SC-003, SC-005, SC-006.

### Tests

- [ ] **T011** *US-1 · FR-001* — `TestGHFDBChildModel::test_proxy_adds_no_table`: `Meta.proxy` is
  true, the database table is the one `HeatFlow` uses, and the proxy declares no local fields.

- [ ] **T012** *US-1 · FR-001* — `TestGHFDBChildModel::test_meta_carries_translated_verbose_names`:
  both verbose names are set, wrapped in `gettext_lazy`, and name the published determination view
  rather than repeating the model's own name.

- [ ] **T013** *US-1 · FR-002, SC-005* —
  `TestGHFDBChildManager::test_determination_without_a_published_identifier_is_absent`: the
  unpublished chain's determination is not returned by the default manager, and is returned by
  `HeatFlow.objects` so the fixture is proven to exist.

- [ ] **T014** *US-1 · FR-002, FR-003, SC-005* —
  `TestGHFDBChildManager::test_scope_survives_filtering_ordering_counting_slicing_and_chaining`: the
  restriction holds after each operation and after two of them chained. R6 records that a test
  exercising the manager alone proves less than it appears to.

- [ ] **T015** *US-1 · FR-003* —
  `TestGHFDBChildManager::test_ordinary_operations_match_the_model_it_stands_in_for`: filtering,
  ordering, counting and slicing through the proxy return what the same operations return on
  `HeatFlow` restricted to published rows.

- [ ] **T016** *US-1 · FR-004* —
  `TestChildFlattening::test_every_scalar_published_child_column_resolves_on_every_row`: the column
  names come from `CHILD_COLUMNS` less the many-valued set and less the three that resolve to
  nothing, both read from the mapping module rather than written out as a literal.

- [ ] **T017** *US-1 · FR-004* —
  `TestChildFlattening::test_the_sites_representative_value_is_restated_on_every_row`: the parent
  block reaches each child row, because the published file restates it per row.

- [ ] **T018** *US-1 · FR-005, SC-003* —
  `TestChildFlattening::test_query_count_is_equal_at_two_row_counts`, through the T010 helper at 2
  and 4 chains.

- [ ] **T019** *US-1 · FR-006, SC-006* —
  `TestChildFlattening::test_a_row_without_a_gradient_is_returned_with_those_columns_empty`.

- [ ] **T020** *US-1 · FR-006, SC-006* —
  `TestChildFlattening::test_a_row_without_a_conductivity_is_returned_with_those_columns_empty`.

- [ ] **T021** *US-1 · FR-006, SC-006* —
  `TestChildFlattening::test_a_row_without_probe_metadata_is_returned_with_those_columns_empty`.

- [ ] **T022** *US-1 · FR-006, SC-006* —
  `TestChildFlattening::test_a_missing_correction_leaves_only_its_own_column_empty`, parametrised
  over the nine entries of `CORRECTION_COL_MAP`. SC-006 requires each correction type proven
  independently, so nine cases rather than one.

- [ ] **T023** *US-1 · FR-011* —
  `TestChildFlattening::test_annotations_carry_their_published_names`: every annotation key equals
  its published column name, except those on a declared collision list, and each name on that list
  is checked to be a field the framework's base class actually declares. Without the second half the
  list is an escape hatch rather than a rule.

- [ ] **T024** *US-1 · SC-001* —
  `TestChildExportQuerySet::test_every_published_child_column_resolves_on_the_complete_row`: read
  after the export method, per R3, since fifteen of the columns are many-valued and cannot be
  annotated. The column list is `CHILD_COLUMNS` itself.

- [ ] **T025** *US-1 · FR-007, SC-003* —
  `TestChildExportQuerySet::test_query_count_is_equal_at_two_row_counts`.

- [ ] **T026** *US-1 · FR-007* —
  `TestChildExportQuerySet::test_many_valued_columns_read_without_further_queries`: reading each
  many-valued column on every row inside `django_assert_num_queries(0)` after the queryset is
  evaluated.

- [ ] **T027** *US-1 · FR-006* —
  `TestChildExportQuerySet::test_columns_nothing_resolves_are_present_and_empty`: `Ref_IGSN`,
  `publication_reference` and `data_reference` are on the row and empty, per R4 and D3.

### Implementation

- [ ] **T028** *US-1 · FR-001* — `GHFDBChild`, a proxy over `HeatFlow`, with its `Meta` and its
  translated verbose names. Proves T011 and T012. Before: `ImportError` on the name.

- [ ] **T029** *US-1 · FR-001* — The migration recording `GHFDBChild`'s existence and its
  permissions, and no other operation. A proxy adds no table, so any `AddField` or `AlterField` in
  this migration is the defect.
  **Test**: `tests/test_migrations.py` — `makemigrations --check` is clean, and the new migration's
  operations are asserted to be a proxy `CreateModel` alone. Before: "Your models have changes that
  are not yet reflected in a migration".

- [ ] **T030** *US-1 · FR-002, FR-003* — `GHFDBChildQuerySet` and `GHFDBChildManager`, the manager's
  `get_queryset()` restricting to rows whose published identifier is set, assigned as the proxy's
  default manager. Proves T013, T014 and T015. Before: the unpublished determination is among the
  results.

- [ ] **T031** *US-1 · FR-004, FR-005* — `as_ghfdb_flat()` opening with the `select_related` spine
  the annotations below need: the interval through the inheritance accessor, the interval's site,
  the parent, the gradient and the conductivity. This is the task that makes the count constant.
  Proves T018. Before: the count at four chains exceeds the count at two.

- [ ] **T032** *US-1 · FR-004* — The scalar annotation set of `as_ghfdb_flat()`: the interval's
  depth range, the determination's own values, the gradient, the conductivity, the probe metadata
  reached through the interval, the site block restated per row, and one column per entry of
  `CORRECTION_COL_MAP` built by iterating that mapping rather than writing nine annotations out.
  One dictionary, so one task. Proves T016, T017 and part of T022. Before: `AttributeError` reading
  `q_top` off a row.

- [ ] **T039** *US-1 · FR-006* — Absent-relationship behaviour across every annotation above: a
  missing relationship yields an empty column, never a dropped row and never an exception. Proves
  T019, T020, T021 and T022. Before: the row is absent from the result, or evaluation raises.

- [ ] **T040** *US-1 · FR-007* — `for_export()`, calling `as_ghfdb_flat()` and chaining the
  prefetches for the many-valued columns FR-007 names: calculation method, exploration purpose, the
  gradient's methods and corrections, the conductivity's descriptive vocabularies, lithology,
  stratigraphy and probe type. Proves T024, T025 and T026. Before: reading a many-valued column
  issues a query per row.

- [ ] **T041** *US-1 · FR-006* — The three columns nothing resolves — `Ref_IGSN`,
  `publication_reference` and `data_reference` — treated as explicitly empty rather than guarded with
  a defensive attribute lookup, so a reader cannot mistake a guard for a working accessor (R4). The
  same task raises the two reference columns as a gap against the roadmap item that attaches
  literature to records, since they are waiting rather than settled. Proves T027. Before:
  `AttributeError` reading `publication_reference` off a row.

---

## Phase 3 — US-2: Sites read in the published shape, with their determination counts (P1)

Discharges FR-001 to FR-003 and FR-008 to FR-011 for the parent, and SC-002 to SC-005.

### Tests

- [ ] **T042** *US-2 · FR-001* — `TestGHFDBParentModel::test_proxy_adds_no_table`: `Meta.proxy` is
  true, the table is `ParentHeatFlow`'s, and no local field is declared.

- [ ] **T043** *US-2 · FR-001* — `TestGHFDBParentModel::test_meta_carries_translated_verbose_names`.

- [ ] **T044** *US-2 · FR-002, SC-005* —
  `TestGHFDBParentManager::test_site_without_a_published_identifier_is_absent`.

- [ ] **T045** *US-2 · FR-002, FR-003, SC-005* —
  `TestGHFDBParentManager::test_scope_survives_filtering_ordering_counting_slicing_and_chaining`.

- [ ] **T046** *US-2 · FR-008* —
  `TestParentFlattening::test_every_scalar_published_parent_column_resolves_on_every_row`, with the
  column names taken from `PARENT_COLUMNS` less the one many-valued column.

- [ ] **T047** *US-2 · FR-008, SC-003* —
  `TestParentFlattening::test_query_count_is_equal_at_two_row_counts`.

- [ ] **T048** *US-2 · FR-011* —
  `TestParentFlattening::test_the_colliding_site_name_is_annotated_distinctly`: the published `name`
  column is annotated under a distinct name because the framework's base class declares `name`, and
  the published name is restored at the surface that presents it.

- [ ] **T049** *US-2 · FR-011* —
  `TestParentFlattening::test_a_column_that_does_not_collide_keeps_its_published_name`: elevation is
  annotated as `elevation`, not under a prefix. D6 settles this, and the rule is only readable if a
  non-colliding case is pinned alongside a colliding one.

- [ ] **T050** *US-2 · FR-009, SC-004* —
  `TestParentCounts::test_counts_are_correct_for_all_some_and_no_contributing_determinations`, over
  the `sites_by_contribution` fixture.

- [ ] **T051** *US-2 · FR-009, SC-004* —
  `TestParentCounts::test_a_site_with_no_determinations_counts_zero_rather_than_empty`. The
  distinction between zero and null is the assertion.

- [ ] **T052** *US-2 · FR-009, SC-003* —
  `TestParentCounts::test_query_count_is_equal_at_two_row_counts`.

- [ ] **T053** *US-2 · FR-010* —
  `TestParentChildAttachment::test_reading_each_sites_determinations_costs_no_query_per_site`:
  iterate every site's determinations inside `django_assert_num_queries(0)` after evaluation.

- [ ] **T054** *US-2 · FR-010, SC-003* —
  `TestParentChildAttachment::test_query_count_is_equal_at_two_row_counts`.

- [ ] **T055** *US-2 · SC-002* —
  `TestParentPublishedColumns::test_every_published_parent_column_resolves_on_the_complete_row`, read
  after flattening and attachment together, per R3, so that the one many-valued parent column is
  included. The column list is `PARENT_COLUMNS` itself.

### Implementation

- [ ] **T056** *US-2 · FR-001* — `GHFDBParent`, a proxy over `ParentHeatFlow`, with its `Meta`.
  Proves T042 and T043. Before: `ImportError` on the name.

- [ ] **T057** *US-2 · FR-001* — The migration recording `GHFDBParent`'s existence and its
  permissions, and no other operation.
  **Test**: `tests/test_migrations.py`, as T029. Before: `makemigrations --check` reports an
  unrecorded model.

- [ ] **T058** *US-2 · FR-002, FR-003* — `GHFDBParentQuerySet` and `GHFDBParentManager`, restricting
  to sites whose published identifier is set, assigned as the proxy's default manager. Proves T044
  and T045.

- [ ] **T059** *US-2 · FR-008, FR-011* — The scalar annotation set of the parent
  `as_ghfdb_flat()`: the site name under its distinct annotation name, latitude, longitude,
  elevation, environment, both total depths, the exploration method, the published identifier, the
  value, its uncertainty, the site comment, the heat production correction flag and the quality code
  under its published parent name. **`explo_purpose` is excluded**: it is a many-to-many field, and
  annotating it with `F()` makes the queryset return one row per site-and-purpose pair. Verified —
  a site carrying two exploration purposes currently returns two rows. Proves T046, T048 and T049.
  Before: `AttributeError` reading `lat_NS` off a row.

- [ ] **T061** *US-2 · FR-009* — `with_counts()`, annotating the number of determinations a site
  holds and the number that contributed, by aggregation rather than per row, and yielding zero rather
  than null for a site holding none. Proves T050, T051 and T052. Before: the counts are absent, and
  the empty site reads `None`.

- [ ] **T062** *US-2 · FR-010* — `with_children()`, attaching each site's determinations so reading
  them costs no query per site, and prefetching the site's exploration purposes — the one many-valued
  parent column, which T059 excludes from the annotations for the reason recorded there. Proves T053,
  T054 and T055. Before: iterating the children issues one query per site, and the exploration
  purpose column either duplicates rows or costs a query each.

- [ ] **T122** *US-2 · D7* — Remove `GHFDBParent.as_dict()` and the `PARENT_COLUMNS` import it is
  the only user of. It has no caller, and it raises on every published column that exists only as an
  annotation, so it cannot work as written. `decisions.md` D7 rules it out and no other task removed
  it.
  **Test**: `TestGHFDBParentModel::test_no_dictionary_accessor` asserts the attribute is absent, and
  the suite passes with it gone. Before: the attribute resolves and raises when called.

---

## Phase 4 — US-3: The assessment team reads the database in the terms they know (P2)

Discharges FR-012 to FR-021, and SC-003, SC-005, SC-007 to SC-010.

### Tests — the published-column mapping

Per R1, one mapping from published column name to its group and accessor, and a factory that turns
it into display callables and the `list_display` tuple. The mapping is the only place a published
column name appears in the admin, and the order is never restated.

- [ ] **T063** *US-3 · FR-013, FR-015* —
  `TestPublishedColumns::test_every_published_column_has_an_entry`, over `CHILD_COLUMNS` and
  `PARENT_COLUMNS` read from `constants.py`.

- [ ] **T064** *US-3 · FR-013, FR-015, SC-007* —
  `TestPublishedColumns::test_a_column_the_map_does_not_cover_is_refused_and_named`: reinstate the
  defect by asking the builder for a column list carrying a name the map does not hold, and assert it
  raises with that name in the message. This is the assertion SC-007 means by "fails when the
  canonical definitions change and the changelist does not".

- [ ] **T065** *US-3 · FR-013, FR-015* —
  `TestPublishedColumns::test_each_heading_is_the_published_name_verbatim`, case included, and
  covering the four names D2 settles: `tc_pT_function`, `Ref_IGSN`, `quality_child` and
  `quality_parent`.

- [ ] **T066** *US-3 · FR-013* —
  `TestPublishedColumns::test_an_annotation_column_reads_the_annotation_off_the_row` — R1 group one.

- [ ] **T067** *US-3 · FR-013, FR-015* —
  `TestPublishedColumns::test_a_field_column_reads_the_field_and_can_override_its_heading` — R1 group
  two, which is what lets `quality` appear as `quality_child` and `quality_parent`.

- [ ] **T068** *US-3 · FR-013, FR-019* —
  `TestPublishedColumns::test_a_many_valued_column_joins_its_labels_and_issues_no_query_when_prefetched`
  — R1 group three, and the N+1 this feature exists to avoid.

- [ ] **T069** *US-3 · FR-013* —
  `TestPublishedColumns::test_a_column_nothing_resolves_renders_empty` — R1 group four and R4.

- [ ] **T070** *US-3 · FR-013, FR-015* —
  `TestPublishedColumns::test_headings_are_the_canonical_order`: the *headings* the built tuple
  produces equal the order `constants.py` gives, asserted against that module rather than a copy of
  it. Headings rather than entry names, because T077 requires the entries to be named differently
  from the columns they render.

### Implementation — the published-column mapping

- [ ] **T071** *US-3 · FR-013, FR-015* — `project/ghfdb/columns.py` holding a `PublishedColumns`
  class with one entry per published column, naming its group and its accessor and nothing else.
  Grouped on a class rather than left as loose functions, per constitution principle IX and the house
  grouping rule. Proves T063. Before: `ImportError` on the module.

- [ ] **T072** *US-3 · FR-013* — The annotation display callable. Proves T066. Before: the changelist
  entry is a bare attribute name and takes the field's verbose name as its heading.

- [ ] **T073** *US-3 · FR-013, FR-015* — The field display callable, carrying a heading override.
  Proves T067. Before: the quality column is headed "quality score" rather than `quality_child`.

- [ ] **T074** *US-3 · FR-013* — The many-valued display callable, joining the related terms' labels.
  Proves T068. Before: the column renders a queryset repr.

- [ ] **T075** *US-3 · FR-013* — The empty display callable for the three columns nothing resolves.
  Proves T069. Before: rendering raises `AttributeError`.

- [ ] **T076** *US-3 · FR-013, FR-015* — The `list_display` builder, taking a canonical column list
  and returning the callables in that list's order, raising at import time on a column the map does
  not hold. R1 records that this makes a drifted column a startup failure rather than a broken page.
  Proves T064 and T070. Before: the unmapped column passes silently and fails later at `admin.E108`.

- [ ] **T077** *US-3 · FR-013, FR-015* — `short_description` set from the published name verbatim on
  every callable the factory produces, and **every callable bound under a name that is not a field on
  the model**. Django resolves a `list_display` entry against the model's fields before the admin's
  attributes and reads `short_description` only when no field matches, so a callable bound under a
  published name that is also a field name is silently ignored and the field's `verbose_name` is
  shown instead. Measured on the current changelists: `expedition` renders as
  "expedition/platform/ship", `c_comment` as "comment", `water_temperature` as "bottom water
  temperature", and the leading identifier as "ID Child". Four headings are wrong today for exactly
  this reason. Proves T065. Before: the heading is the field's `verbose_name`.

### Tests — the determination changelist

- [ ] **T078** *US-3 · FR-012* —
  `TestGHFDBChildAdmin::test_changelist_renders_for_a_staff_user` (US-3 acceptance scenario 1).

- [ ] **T079** *US-3 · FR-013, SC-007* —
  `TestGHFDBChildAdmin::test_published_child_columns_appear_in_the_canonical_order`: the headings
  Django renders for the tail of `list_display` equal `CHILD_COLUMNS`, read from `constants.py` and
  never from a literal in the test. Asserted through the rendered headings rather than by reading
  `short_description` off the callables, since T077 records that the two can disagree.

- [ ] **T080** *US-3 · FR-014* —
  `TestGHFDBChildAdmin::test_the_leading_columns_are_the_four_orientation_columns_and_nothing_else`:
  the record's published identifier, the site's published identifier, the site name and the site's
  two coordinate columns, in that order, and no sixth (US-3 acceptance scenario 2).

- [ ] **T081** *US-3 · FR-014* —
  `TestGHFDBChildAdmin::test_site_values_are_not_restated_on_every_row`: the intersection of
  `list_display` with the published parent columns is exactly the orientation columns T080 names,
  and nothing further. Those four are themselves published parent columns, so this is an equality
  against that set rather than an absence. The familiarity being protected is the child block's, per
  the 2026-08-23 clarification.

- [ ] **T082** *US-3 · FR-016* —
  `TestGHFDBChildAdmin::test_search_matches_site_name_and_published_site_identifier`, exercised
  through the rendered changelist with a query string rather than against the attribute.

- [ ] **T083** *US-3 · FR-017* — `TestGHFDBChildAdmin::test_the_eight_filters_are_offered`:
  environment, heat production correction flag, exploration method, exploration purpose, country,
  region, continent and geological domain, each producing matching rows when applied.

- [ ] **T084** *US-3 · FR-018, SC-009* —
  `TestGHFDBChildAdmin::test_each_vocabulary_filter_offers_exactly_its_own_terms_as_labels`, over
  environment, exploration method and exploration purpose. Three assertions per filter: every term of
  its vocabulary is offered, no term of another vocabulary is, and the choice text is the label
  rather than the stored key.

- [ ] **T085** *US-3 · FR-012, SC-008* —
  `TestGHFDBChildAdmin::test_there_is_no_route_to_add_change_or_delete`: the three permission hooks
  return false, the rendered page carries no add link, and no row links into a form. Those three
  hooks are not the whole surface — the import route writes without consulting any of them, and
  T123 covers it.

- [ ] **T086** *US-3 · FR-002, SC-005* —
  `TestGHFDBChildAdmin::test_an_unpublished_determination_is_absent_from_the_rendered_rows`. R6
  records this as the assertion that would catch an override that stopped going through the scoped
  manager.

- [ ] **T087** *US-3 · FR-019, SC-003* —
  `TestGHFDBChildAdmin::test_query_count_is_equal_at_two_row_counts`, measured on the rendered
  changelist (US-3 acceptance scenario 8).

- [ ] **T088** *US-3 · FR-020* —
  `TestGHFDBChildAdmin::test_every_declared_path_resolves_on_the_model`: the framework's admin checks
  report nothing for this registration, covering the display, filter and search declarations
  together.

- [ ] **T089** *US-3 · FR-021, SC-010* —
  `TestGHFDBChildAdmin::test_it_carries_the_determination_import_resource_and_the_export_resource`,
  asserted on both the import and the export attachment.

### Implementation — the determination changelist

- [ ] **T090** *US-3 · FR-013, FR-014* — The `GHFDBChild` registration, its `list_display` built as
  the four orientation columns followed by the mapping's tuple for `CHILD_COLUMNS`, with the display
  callables bound onto the class. Proves T078, T079, T080 and T081. Before: the model is absent from
  the admin registry.

- [ ] **T091** *US-3 · FR-012* — The read-only guarantees on this admin: the three permission hooks
  return false and no column links into a form. Written out on this class rather than shared with the
  site changelist through a base, per constitution principle IX. Proves T085. Before: the add button
  renders and each row links to a change form.

- [ ] **T092** *US-3 · FR-002, FR-019* — `get_queryset()` going through the scoped manager and the
  export queryset, so the rendered rows are both restricted and complete. Proves T086, and T087 in
  part. Before: the unpublished determination renders, and reading a many-valued column issues a
  query per row.

- [ ] **T093** *US-3 · FR-016, FR-020* — `search_fields` on the site name and the site's published
  identifier, by paths that exist from the determination. Proves T082. Before: searching returns no
  match, or the admin check reports an unresolvable path.

- [ ] **T094** *US-3 · FR-017* — The plain filters on this admin: heat production correction flag,
  country, region, continent and geological domain. Proves T083 in part.

- [ ] **T095** *US-3 · FR-018* — A vocabulary-scoped filter class taking a vocabulary, a lookup path
  and the **lookup mode**, offering that vocabulary's terms by label. Two modes are needed, not one.
  Environment and exploration method are single-valued concept fields, whose choices come from the
  vocabulary and match on the stored value. Exploration purpose is many-valued, whose choices come
  from the concept rows and match on their primary key. Six callers across the two changelists, so
  one class with two modes is earned. If the two shapes will not read clearly in one class, two
  classes of three callers each is the alternative and is equally acceptable. Proves T084 in part.
  Before: the filter offers every stored key present in the table, including terms of other
  vocabularies.

- [ ] **T096** *US-3 · FR-018, FR-020, SC-009* — The three vocabulary filters wired onto this admin
  at their paths from the determination. Proves T084 and the rest of T083.

- [ ] **T097** *US-3 · FR-021* — The determination import resource and the export resource attached
  to this changelist, and no other. The resources themselves belong to `003-ghfdb-import-export` and
  are not written here. Proves T089. Before: neither attachment exists.

### Tests — the site changelist

- [ ] **T098** *US-3 · FR-012* —
  `TestGHFDBParentAdmin::test_changelist_renders_for_a_staff_user` (US-3 acceptance scenario 3).

- [ ] **T099** *US-3 · FR-015, SC-007* —
  `TestGHFDBParentAdmin::test_published_parent_columns_appear_in_the_canonical_order`: the rendered
  headings, read from `PARENT_COLUMNS`, asserted as T079 asserts them.

- [ ] **T100** *US-3 · FR-015* —
  `TestGHFDBParentAdmin::test_the_geography_follows_the_published_block`: country, region, continent
  and geological domain, in that order, immediately after the published columns. D8 keeps them, and
  places them after rather than among.

- [ ] **T101** *US-3 · FR-015* —
  `TestGHFDBParentAdmin::test_the_two_determination_counts_come_last`, and render their values.

- [ ] **T102** *US-3 · FR-016* —
  `TestGHFDBParentAdmin::test_search_matches_site_name_and_published_site_identifier`.

- [ ] **T103** *US-3 · FR-017* — `TestGHFDBParentAdmin::test_the_eight_filters_are_offered`, each
  producing matching rows when applied.

- [ ] **T104** *US-3 · FR-018, SC-009* —
  `TestGHFDBParentAdmin::test_each_vocabulary_filter_offers_exactly_its_own_terms_as_labels`. SC-009
  requires this proven on both changelists, not once.

- [ ] **T105** *US-3 · FR-012, SC-008* —
  `TestGHFDBParentAdmin::test_there_is_no_route_to_add_change_or_delete`, as T085, with the same
  note about the import route and T123.

- [ ] **T106** *US-3 · FR-002, SC-005* —
  `TestGHFDBParentAdmin::test_an_unpublished_site_is_absent_from_the_rendered_rows`.

- [ ] **T107** *US-3 · FR-019, SC-003* —
  `TestGHFDBParentAdmin::test_query_count_is_equal_at_two_row_counts`.

- [ ] **T108** *US-3 · FR-020* —
  `TestGHFDBParentAdmin::test_every_declared_path_resolves_on_the_model`.

- [ ] **T109** *US-3 · FR-021, SC-010* —
  `TestGHFDBParentAdmin::test_it_carries_the_site_import_resource_and_no_export_resource`. The
  negative half is as much of the requirement as the positive.

- [ ] **T110** *US-3 · FR-021, SC-010* —
  `TestResourceAttachment::test_no_resource_is_attached_to_both_changelists`.

### Implementation — the site changelist

- [ ] **T111** *US-3 · FR-015* — The `GHFDBParent` registration, its `list_display` opening with the
  mapping's tuple for `PARENT_COLUMNS`. Proves T098 and T099. Before: the model is absent from the
  admin registry.

- [ ] **T112** *US-3 · FR-015* — The four geography columns after the published block. Proves T100.

- [ ] **T113** *US-3 · FR-015* — The two determination-count columns last, reading the annotations
  rather than counting per row. Proves T101. Before: the columns are absent.

- [ ] **T114** *US-3 · FR-012* — The read-only guarantees on this admin. Proves T105.

- [ ] **T115** *US-3 · FR-002, FR-019* — `get_queryset()` going through the scoped manager and
  chaining the flattening, the counts and the child attachment, so every column on this changelist is
  read from the queryset rather than by walking a relationship per column (R5). Proves T106 and T107.
  Before: the unpublished site renders, and the count at four sites exceeds the count at two.

- [ ] **T116** *US-3 · FR-016, FR-020* — `search_fields` on the site name and the site's published
  identifier, by paths that exist from the representative value. Proves T102.

- [ ] **T117** *US-3 · FR-017* — The plain filters on this admin. Proves T103 in part.

- [ ] **T118** *US-3 · FR-018, FR-020, SC-009* — The three vocabulary filters wired onto this admin
  at their paths from the representative value, reusing T095's class. Proves T104 and the rest of
  T103.

- [ ] **T119** *US-3 · FR-021* — The site import resource attached to this changelist, and no export
  resource. Proves T109 and T110. Before: the attachment is absent, or the export resource is present
  on both changelists.

- [ ] **T123** *US-3 · FR-012* — Gate the import route on both changelists behind the model's add
  permission at the user level. `django-import-export` grants import to any staff user whenever
  `IMPORT_EXPORT_IMPORT_PERMISSION_CODE` is unset, and it is unset in this project — verified. So
  both registrations, which declare no add, no change and no delete, carry a route that writes
  records and that a user holding only view permission can reach. Override it on these two
  registrations rather than in project settings, so the change reaches nothing else.
  **Test**: `TestImportPermission`, on both changelists — a staff user with view permission only is
  refused the import URL, and one holding the model's add permission is not. Before: the
  view-permission-only user reaches the import page and can write.

---

## Phase 5 — Feature-wide

- [ ] **T120** *US-1, US-2, US-3 · SC-011* —
  `TestSuiteHealth::test_no_test_in_this_feature_is_expected_to_fail`: no test module under
  `tests/test_ghfdb/` carries an `xfail` or an unconditional `skip`. SC-011 is a statement about the
  suite, so it needs an assertion about the suite.

- [ ] **T121** *US-1, US-2, US-3 · constitution VII* — Documentation for the query surface this
  feature adds: the two proxies, their scoping rule, the five queryset methods and the two
  changelists, plus the field mapping documentation brought current for anything these tasks touched.
  **Test**: the documentation build passes with warnings treated as errors, and the page names every
  public queryset method this feature defines. Before: the build reports an undocumented reference,
  and the assertion finds no mention of the export queryset.

---

## Convergence gates

Not tasks, and deliberately unnumbered — nothing dispatches them. They are the conditions the
feature exits on, checked once the stories are done.

- The full test suite passes, run once, at the end.
- Lint, formatting and type checks pass on every changed file. CI runs raw ruff, which is a wider
  scope than the pre-commit gate.
- `manage.py check` reports no errors and no warnings with both registrations live.
- The branch's migrations are squashed to one change set, and they apply cleanly to an empty
  database. Neither may touch data.
- No column list, in code or in a test, is a copy of one `constants.py` already holds.
- Every comment and docstring in a file this run touches describes what the file now does. Four are
  known wrong today and are corrected in passing rather than given tasks: `constants.py`'s header
  and its two per-list comments miscount their own lists, `managers.py`'s module docstring says "31
  scalar columns" where the dictionary holds 34, `managers.py`'s parent flattening docstring says
  `explo_purpose` is excluded where the code annotates it, and `admin.py`'s docstrings cite
  requirement numbers and defect handles from the superseded specification.
- No name introduced by this run carries a leading underscore. The display factory this run replaces
  is called `_scalar`; its replacement is not.
