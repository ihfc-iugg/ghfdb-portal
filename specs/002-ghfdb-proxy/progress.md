# Progress — 002-ghfdb-proxy

## 2026-08-23T23:40:00Z · Implementer foundations · T001

Did: Created `tests/test_ghfdb/test_columns.py` (empty module carrying the `ghfdb`
marker only — its test classes belong to the mapping tasks, out of this phase's
scope). Added `pytestmark = pytest.mark.ghfdb` to the three pre-existing modules
that lacked it: `test_models.py`, `test_managers.py`, `test_admin.py`. Left
`test_views.py` and `test_resources/` untouched, per the task's own carve-out.

Verified: Before, `poetry run pytest tests/test_ghfdb/test_columns.py --collect-only`
exited 4 with `ERROR: file or directory not found: tests/test_ghfdb/test_columns.py` —
the exact failure text T001 names. After creating the file, the same command exits 5
with `no tests collected` (file found, zero items — expected for a module whose tests
land in a later phase). `poetry run pytest tests/test_ghfdb/test_models.py
tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py
tests/test_ghfdb/test_columns.py -q` → `23 passed, 1 xfailed`.

Next: T002, the autouse vocabulary-concept fixture's own contract test.

Watch: `test_columns.py` collects zero tests until the mapping-module tasks (T063+)
land test classes in it. That is expected, not a defect in this task.

## 2026-08-24T00:05:00Z · Implementer foundations · T002

Did: Added `TestFixtures::test_vocabulary_concepts_are_present` to `test_models.py`,
asserting `Concept.get_for_vocabulary(...)` is non-empty for `GeographicEnvironment`,
`ExplorationMethod` and `ExplorationPurpose`. Found the test genuinely failing against
the pre-existing `load_concepts` fixture: `Concept.preload()` only preloads
vocabularies present in `research_vocabs`' `vocab_registry`, and registration there is
a side effect of `RelatedConceptMixin.__init__` (used by `ConceptManyToManyField`,
e.g. `explo_purpose`) — but `BaseConceptField.__init__` (the single-valued
`ConceptField`, used by `environment` and `explo_method`) has its own
`registry.register(self.scheme)` call commented out upstream. Fixed by having
`load_concepts` register `GeographicEnvironment` and `ExplorationMethod` explicitly
before calling `Concept.preload()`.

Verified: RED observed directly — with the registration fix reverted (temporary
one-line probe, reverted immediately after), the test failed with
`AssertionError: no concepts preloaded for GeographicEnvironment`. After the fix,
`poetry run pytest tests/test_ghfdb/test_models.py -q` -> `3 passed`.

Next: T003, the `dataset` fixture's own contract test.

Watch: this is an upstream gap in `research_vocabs`, not something to fix in that
package from here. Any other `ConceptField` (non-M2M) vocabulary anywhere in the
project has the same silent gap; only the three this feature's fixtures touch are
closed here.

## 2026-08-24T00:15:00Z · Implementer foundations · T003

Did: Added `TestFixtures::test_dataset_fixture_is_saved`, asserting the pre-existing
`dataset` fixture (wraps `DatasetFactory`) returns a saved instance.

Verified: RED observed directly — temporarily renamed the `dataset` fixture in
`conftest.py`, ran the new test, got a fixture-not-found error, restored the name.
`poetry run pytest tests/test_ghfdb/test_models.py -q` -> `4 passed`.

Next: T004, the `published_chain` fixture.

Watch: nothing.

## 2026-08-24T00:25:00Z · Implementer foundations · T004

Did: Added `build_site_and_parent`, `build_child` and `build_published_chain` helpers
plus the `published_chain` fixture to `conftest.py` — one complete site -> interval ->
parent -> child chain, all nine correction types, direct ORM calls per
`tests/README.md`, published identifier (`ghfdb_id`) set on both parent and child.
Added `TestFixtures::test_published_chain_is_complete`, walking every relationship the
task names.

Verified: RED observed directly — ran the new test before the fixture existed, got a
fixture-not-found error. After implementing, `poetry run pytest
tests/test_ghfdb/test_models.py -q` -> `5 passed`.

Next: T005, the `published_chains` counted fixture (R2).

Watch: `build_child` and `build_published_chain` take keyword arguments
(`include_gradient`, `missing_correction`, `is_relevant`, ...) that T005-T008's
fixtures will reuse rather than duplicate — this is scaffolding those tasks depend on,
not scope creep for T004 alone.

## 2026-08-24T00:32:00Z · Implementer foundations · T005

Did: Added the `published_chains` counted fixture (R2) — a callable building *n*
complete, published chains via `build_published_chain`. Added
`TestFixtures::test_published_chains_builds_the_number_asked_for`, calling it at 2
and at 4 within one test and asserting the cumulative `HeatFlow` row count at each
size.

Verified: RED observed directly — ran the new test before the fixture existed, got a
fixture-not-found error. After implementing, `poetry run pytest
tests/test_ghfdb/test_models.py -q` -> `6 passed`.

Next: T006, the `unpublished_chain` fixture.

Watch: each call to `published_chains(n)` numbers its own chains' `ghfdb_id` from 1,
so two calls in the same test produce duplicate `ghfdb_id` values across the two
batches. Neither model enforces uniqueness on that field (index only, no unique
constraint), and nothing in this phase's tests depends on cross-batch uniqueness, so
this is a note rather than a defect.

## 2026-08-24T00:38:00Z · Implementer foundations · T006

Did: Added the `unpublished_chain` fixture — the same graph as `published_chain`
with `published=False`, so `ghfdb_id` is unset on both parent and child. Added
`TestFixtures::test_unpublished_chain_has_no_published_identifier`.

Verified: RED observed directly — ran the new test before the fixture existed, got a
fixture-not-found error. After implementing, `poetry run pytest
tests/test_ghfdb/test_models.py -q` -> `7 passed`.

Next: T007, the four partial-chain fixtures.

Watch: nothing.

## 2026-08-24T00:48:00Z · Implementer foundations · T007

Did: Added `chain_without_gradient`, `chain_without_conductivity`,
`chain_without_probe_metadata` and `chain_missing_correction` (a callable taking a
correction type), each reusing `build_published_chain`'s existing keyword arguments to
omit exactly the one piece it names. Added
`TestFixtures::test_partial_chains_omit_only_what_they_name`, asserting the named
absence and that every other relationship still resolves, for all four.

Verified: RED observed directly — ran the new test before the fixtures existed, got a
fixture-not-found error. After implementing, `poetry run pytest
tests/test_ghfdb/test_models.py -q` -> `8 passed`.

Next: T008, the `sites_by_contribution` fixture.

Watch: nothing.

## 2026-08-24T00:58:00Z · Implementer foundations · T008

Did: Added the `sites_by_contribution` fixture, building four sites with
`build_site_and_parent`/`build_child`: all children `is_relevant=True`, some,
none, and one site with zero children. The `all_contributing` site's
`HeatFlowSite.explo_purpose` (a `ConceptManyToManyField`) is set to two
`ExplorationPurpose` concepts, exercising the one many-valued parent column SC-004
calls out. Added `TestFixtures::test_sites_by_contribution_covers_the_four_shapes`.

Verified: RED observed directly — ran the new test before the fixture existed, got a
fixture-not-found error. After implementing, it passed first try; `poetry run pytest
tests/test_ghfdb/test_models.py -q` -> `9 passed`.

Next: T009, the `staff_client` fixture.

Watch: nothing.

## 2026-08-24T01:05:00Z · Implementer foundations · T009

Did: Added the `staff_client` fixture — a staff `Person` holding only
`ghfdb.view_ghfdbchild` and `ghfdb.view_ghfdbparent` (both proxy models get their
own content type and permissions, confirmed via
`ContentType.objects.get_for_model(GHFDBChild, for_concrete_model=False)`), logged in
via `client.force_login`. Added
`TestFixtures::test_staff_client_reaches_the_admin_index`.

Verified: RED observed directly — ran the new test before the fixture existed, got a
fixture-not-found error. Before writing the fixture, confirmed by inspecting
`fairdm.contrib.contributors.models.Person` that `USERNAME_FIELD = "email"` and
`username = None` (no such field exists), and that
`fairdm.contrib.contributors.managers.UserManager.create_user` takes `email` as its
first positional argument, not `username` — so the fixture uses `email=`, not
`username=`. It passed first try; `poetry run pytest tests/test_ghfdb/test_models.py
-q` -> `10 passed`.

Next: T010, the `constant_query_count` gate.

Watch: nothing.

## 2026-08-24T01:15:00Z · Implementer foundations · T010

Did: Added the `constant_query_count` fixture — runs `build(low)`, captures the query
count `call()` issues via `CaptureQueriesContext`, runs `build(high)`, then asserts
`call()` issues the same count again through `django_assert_num_queries`, comparing
the two counts to each other rather than to a literal (R2). Added
`TestConstantQueryCount` with two cases: a callable whose query count scales with a
mutable row count (must be rejected) and one that always issues one query (must be
accepted).

Verified: RED observed directly — ran both new tests before the fixture existed, got
fixture-not-found errors for both. After implementing, both passed first try — the
linear case raises inside `django_assert_num_queries`, caught by
`pytest.raises(pytest.fail.Exception)`, and the constant case passes clean.
`poetry run pytest tests/test_ghfdb/test_models.py -q` -> `12 passed`.

Next: none — T001-T010 (Phase 1 foundations) are complete. US-1 (T011+) is out of
this story's scope.

Watch: nothing.

## 2026-08-23T22:00:00Z · Implementer US-1 · T011, T012

Did: Added `TestGHFDBChildModel` to `test_models.py` — `test_proxy_adds_no_table`
(`Meta.proxy` is true, `db_table` equals `HeatFlow`'s, `local_fields` is empty) and
`test_meta_carries_translated_verbose_names` (both verbose names are `Promise`
instances — lazy translations — reading "GHFDB Child"/"GHFDB Children", distinct from
`HeatFlow`'s own verbose name).

Verified: both tests passed on first run against the already-built `GHFDBChild.Meta`
(`project/ghfdb/models.py:57-60`) — no code change. `poetry run pytest
tests/test_ghfdb/test_models.py::TestGHFDBChildModel -q` -> `2 passed`.

Next: T013-T015, the manager's scoping.

Watch: nothing.

## 2026-08-23T22:05:00Z · Implementer US-1 · T013, T014, T015

Did: Added `TestGHFDBChildManager` to `test_managers.py` — absence of the
unpublished chain (T013), the restriction surviving filter/order/count/slice and a
chained pair (T014), and equivalence with `HeatFlow.objects.filter(ghfdb_id__isnull=False)`
across count/filter/order/slice (T015).

Verified: all three passed on first run against the already-built
`GHFDBChildManager.get_queryset()` (`project/ghfdb/managers.py:178`) — no code change.
`poetry run pytest tests/test_ghfdb/test_managers.py::TestGHFDBChildManager -q` ->
`3 passed`.

Next: T016-T023, the scalar annotation set.

Watch: nothing.

## 2026-08-23T22:15:00Z · Implementer US-1 · T016, T017, T018, T019, T020, T021, T022, T023, T032

Did: Added `TestChildFlattening` to `test_managers.py`, covering the whole scalar
annotation set in one pass since T032 ("one dictionary, so one task") is what all of
these prove. T016 (every scalar CHILD_COLUMNS entry, less a test-local many-valued
set and the three nothing-resolves columns, resolves), T017 (the site/parent block
values are correctly restated on the child row), T018 (query count constant at 2 vs
4 chains, through the T010 helper), T019-T021 (a missing gradient/conductivity/
probe-metadata empties only its own columns), T022 (a missing correction empties
only its own flag, parametrised over all nine `CORRECTION_COL_MAP` entries), T023
(every annotation key equals its published name except the one declared collision —
`site_name` for `name` — checked against a real `HeatFlow` field).

Verified: RED observed directly. `test_every_scalar_published_child_column_resolves_on_every_row`
failed first run with `AttributeError: 'HeatFlow' object has no attribute
'quality_child'` — CHILD_COLUMNS names it, HeatFlow has a `quality` field, and
nothing aliased it. Added `"quality_child": F("quality")` to `as_ghfdb_flat()`'s
scalar annotation set (`project/ghfdb/managers.py`), mirroring the `quality_parent`
pattern already used on the parent side. Re-ran: passed. Two of my own test
assertions were also wrong on first write (comparing an annotated raw value against
the model-descriptor-wrapped one for a `ConceptField` and a `QuantityField`) — fixed
in the test, not the code, since the annotation values were correct and only the
comparison was naive. `poetry run pytest tests/test_ghfdb/test_managers.py::TestChildFlattening -q`
-> `16 passed`.

Next: T024, T025, T026, T027, T041 — the export queryset's complete row.

Watch: nothing.

## 2026-08-23T22:35:00Z · Implementer US-1 · T024, T025, T027, T041

Did: Added `TestChildExportQuerySet` to `test_managers.py` — every `CHILD_COLUMNS`
entry resolves on a `for_export()` row, including the fifteen many-valued ones via a
test-local accessor map since no canonical column-to-accessor mapping exists yet
(that is `003-ghfdb-import-export`'s `columns.py`) (T024); the query count is
constant at 2 vs 4 chains (T025); `Ref_IGSN`, `publication_reference` and
`data_reference` are present and empty (T027).

Verified: RED observed directly. Both T024 and T027 failed first run with
`AttributeError` reading `publication_reference`/`data_reference` — neither
column had any annotation, and `HeatFlow` has no reference relationship at all
(confirmed by reading `project/heat_flow/models/child.py`: no `Ref_IGSN`,
`publication_reference` or `data_reference` field or relation exists). Added the
three as explicit `Value("", output_field=CharField())` annotations (T041), per R4/D3
— explicit rather than a defensive `getattr`, so a reader cannot mistake a guard for
a working accessor. Re-ran: all three tests passed.
`poetry run pytest tests/test_ghfdb/test_managers.py::TestChildExportQuerySet -q` ->
`3 passed` (T026 not yet attempted at this point).

Next: T026, the many-valued zero-query read.

Watch: nothing.

## 2026-08-23T22:45:00Z · Implementer US-1 · T026, T040 — BLOCKED

Did: Wrote `test_many_valued_columns_read_without_further_queries`, wrapping every
many-valued `CHILD_COLUMNS` accessor for every row in `django_assert_num_queries(0)`
after `for_export()`'s queryset is evaluated.

Verified: RED observed directly and for the right reason —
`Failed: Expected to perform 0 queries but 4 were done` (2 chains x 2 unprefetched
relations). Root cause: `for_export()` prefetches 14 M2M paths but is missing
`sample__heatflowinterval__lithology` and `...stratigraphy` — `geo_lithology` and
`geo_stratigraphy` resolve (T024 passes) but cost a query each to read. This matches
T040's own text, which names "lithology, stratigraphy" among what `for_export()`
must chain, and matches `project/ghfdb/admin.py`'s `get_queryset()`, which already
prefetches both paths itself to compensate.

Attempted the fix: added both prefetches to `for_export()`. The new test then
passed (`poetry run pytest
tests/test_ghfdb/test_managers.py::TestChildExportQuerySet -q` -> `4 passed`), but
running the wider class
(`poetry run pytest tests/test_ghfdb/test_managers.py::TestGHFDBChildQuerySet
tests/test_ghfdb/test_managers.py::TestChildExportQuerySet -q`) turned up
`TestGHFDBChildQuerySet::test_for_export_max_queries` failing —
`Expected to perform 16 queries or less but 17 were done`. That test is
pre-existing, not authored in this story, and the brief prohibits modifying it.
Reverted the two prefetches. `T026` and the lithology/stratigraphy chunk of `T040`
are BLOCKED on this conflict; everything else T040 covers (the other twelve M2M
paths, T024, T025, T027) is unaffected and green. See `decisions.md` for the
recorded decision. attempts_used: 1 (single reproduce-fix-observe-revert cycle;
the conflict is structural, not a bug to iterate on).

Next: T028-T032, T039, T041 verification and T029's migration test.

Watch: whoever picks up `003-ghfdb-import-export`'s `columns.py`, or a later pass on
this story, needs Sam's call on whether `test_for_export_max_queries`'s bound moves
to 18 (or is retired in favour of the T025 constant-query-count test, which already
supersedes it methodologically) before `geo_lithology`/`geo_stratigraphy` can be
read at zero query cost.

## 2026-08-23T22:55:00Z · Implementer US-1 · D6 correction

Did: Corrected `TestGHFDBChildQuerySet::test_as_ghfdb_flat_scalar_columns` and
removed its `xfail(strict=True)`. The list expected `site_elevation` and six other
names that no longer match the queryset's annotation keys (`site_environment`,
`site_explo_method`, `total_depth_md`/`total_depth_tvd` casing,
`p_q`/`p_q_uncertainty`/`p_corr_hp_flag` prefixes) — all stale, predating the
constants module's move to the published spreadsheet casing. D6 rules the queryset
right: corrected every name to what `as_ghfdb_flat()` actually annotates
(`elevation`, `environment`, `explo_method`, `total_depth_MD`, `total_depth_TVD`,
`q`, `q_uncertainty`, `corr_HP_flag`), keeping the `site_`-prefixed geography columns
as-is since D8 rules those are not published columns at all.

Verified: `poetry run pytest
"tests/test_ghfdb/test_managers.py::TestGHFDBChildQuerySet::test_as_ghfdb_flat_scalar_columns"
-q` -> `1 passed`, no longer xfailed.
`poetry run pytest tests/test_ghfdb/test_managers.py::TestGHFDBChildQuerySet -q` ->
`5 passed`.

Next: T029, the migration shape test.

Watch: nothing.

## 2026-08-23T23:00:00Z · Implementer US-1 · T029

Did: Added `TestGHFDBChildProxyMigrations` to `test_migrations.py` — the initial
migration (`0002_ghfdb.py`) is a single bare proxy `CreateModel`, and the rename
migration (`0003_ghfdbchild_ghfdbparent.py`) carries no `AddField`/`AlterField`/
`RemoveField` anywhere, with exactly one `RenameModel` from `GHFDB` to `GHFDBChild`.
Scoped to `GHFDBChild` only — the `GHFDBParent` `CreateModel` in the same file is
`T057`'s, a different story.

Verified: both passed on first run against the already-recorded migrations — no code
change. `poetry run pytest tests/test_migrations.py::TestGHFDBChildProxyMigrations -q`
-> `2 passed`.

Next: none — T011-T041 (this story's slice) are complete except T026/T040's blocked
chunk.

Watch: the tree-wide xfailed count should now read 13, not 14 (D6's correction).
Confirm at the story's full-suite run.

## 2026-08-23T23:40:00Z · Implementer US-2 · T042, T043, T122

Did: Added `TestGHFDBParentModel` to `test_models.py`, mirroring `TestGHFDBChildModel`'s
shape for the child proxy: `test_proxy_adds_no_table` (proxy Meta, shared table with
`ParentHeatFlow`, no local fields) and `test_meta_carries_translated_verbose_names`
(both verbose names are `Promise` instances and name the site view, not
`ParentHeatFlow`'s own name). Both proved green immediately — `GHFDBParent`'s Meta was
already built (`project/ghfdb/models.py`). Also added `test_no_dictionary_accessor`
(T122, D7): asserted red first (`as_dict` was present and would raise on every
annotation-only column), then removed `GHFDBParent.as_dict()` and the now-unused
`PARENT_COLUMNS` import from `models.py`.

Verified: `poetry run pytest tests/test_ghfdb/test_models.py::TestGHFDBParentModel -q`
before the removal -> `1 failed, 2 passed` (test_no_dictionary_accessor failed with
`assert not True`, the right reason). After removing `as_dict()` -> `3 passed`.

Next: T045, T057 (both citable against existing code).

Watch: nothing.

## 2026-08-23T23:45:00Z · Implementer US-2 · T045, T057

Did: Added `TestGHFDBParentManager::test_scope_survives_filtering_ordering_counting_slicing_and_chaining`
to `test_managers.py` (T045), mirroring T014's shape for the site proxy, and
`TestGHFDBParentProxyMigrations::test_the_create_model_is_a_bare_proxy` to
`test_migrations.py` (T057), asserting the `GHFDBParent` `CreateModel` operation in
`0003_ghfdbchild_ghfdbparent.py` declares no fields and `proxy: True`. Both closed
already per reconciliation.md's Phase 3 table (`managers.py:278`, migration recorded)
— no production change.

Verified: `poetry run pytest tests/test_ghfdb/test_managers.py::TestGHFDBParentManager
tests/test_migrations.py::TestGHFDBParentProxyMigrations -q` -> `2 passed`, first run.

Next: T046 (TestParentFlattening), which also carries T059's correction.

Watch: nothing.

## 2026-08-23T23:52:00Z · Implementer US-2 · T046, T059

Did: Added `TestParentFlattening::test_every_scalar_published_parent_column_resolves_on_every_row`,
built over `sites_by_contribution` rather than `published_chains`, specifically so the
row count assertion (`len(records) == len(sites_by_contribution)`, i.e. 4) catches the
defect the reconciliation and D9 flag: `as_ghfdb_flat()` annotated `explo_purpose` with
`F()`, and that column is a many-to-many field, so the site carrying two exploration
purposes came back as two rows. Ran red first — `assert 5 == 4` — confirming the
duplication measured in the design review. Removed the `"explo_purpose": F(...)`
annotation from `GHFDBParentQuerySet.as_ghfdb_flat()` in `managers.py` (T059); the
method's own docstring already claimed the exclusion, the code did not.

Verified: red — `poetry run pytest
tests/test_ghfdb/test_managers.py::TestParentFlattening -q` -> `1 failed`,
`AssertionError: assert 5 == 4`. Green after the fix — same command -> `1 passed`.
Wider file scope: `poetry run pytest tests/test_ghfdb/test_managers.py -q` ->
`35 passed`.

Next: T047 (query count), T048/T049 (annotation naming).

Watch: nothing.

## 2026-08-23T23:58:00Z · Implementer US-2 · T047

Did: Added `TestParentFlattening::test_query_count_is_equal_at_two_row_counts`, through
the `constant_query_count` helper at 2 and 4 chains.

Verified: `poetry run pytest
tests/test_ghfdb/test_managers.py::TestParentFlattening -q` -> `2 passed`, first run —
`as_ghfdb_flat()`'s `select_related` spine already makes the count constant.

Next: T048, T049.

Watch: nothing.

## 2026-08-24T00:03:00Z · Implementer US-2 · T048, T049

Did: Added `test_the_colliding_site_name_is_annotated_distinctly` (T048): asserts
`ParentHeatFlow` declares `name` (so the collision is real, not assumed) and that the
row's `site_name` annotation equals the site's actual `name`. Added
`test_a_column_that_does_not_collide_keeps_its_published_name` (T049): sets a real
elevation value on the site and reads it back as `record.elevation` (not a prefixed
key), unlike the earlier defect the design review recorded — a `.none()`-based test on
the wrong (child) model that never read a value off a row.

Verified: `poetry run pytest
tests/test_ghfdb/test_managers.py::TestParentFlattening -q` -> `4 passed`, first run —
both annotation names were already correct in `managers.py`.

Next: T050, T051 (TestParentCounts).

Watch: nothing.

## 2026-08-24T00:08:00Z · Implementer US-2 · T050, T051

Did: Added `TestParentCounts` with
`test_counts_are_correct_for_all_some_and_no_contributing_determinations` (T050),
covering three of the four `sites_by_contribution` shapes against
`with_child_counts()`, and `test_a_site_with_no_determinations_counts_zero_rather_than_empty`
(T051), asserting the fourth shape's counts are `0`, not `None`. The existing test this
story inherited (`TestGHFDBParentQuerySet::test_parent_with_child_counts_correctness`)
covers only one site with one contributing determination — SC-004's other three shapes
were genuinely untested before this.

Verified: `poetry run pytest tests/test_ghfdb/test_managers.py::TestParentCounts -q`
-> `2 passed`, first run — `Count()` aggregation already returns `0` rather than
`None` for a site with no children.

Next: T052 (query count).

Watch: nothing.

## 2026-08-24T00:12:00Z · Implementer US-2 · T052

Did: Added `TestParentCounts::test_query_count_is_equal_at_two_row_counts`, through
`constant_query_count` at 2 and 4 chains.

Verified: `poetry run pytest tests/test_ghfdb/test_managers.py::TestParentCounts -q`
-> `3 passed`, first run.

Next: T053, T054 (TestParentChildAttachment).

Watch: nothing.

## 2026-08-24T00:16:00Z · Implementer US-2 · T053, T054

Did: Added `TestParentChildAttachment` with
`test_reading_each_sites_determinations_costs_no_query_per_site` (T053, evaluates
`with_children()` at 2 chains then reads every site's `children.all()` inside
`django_assert_num_queries(0)`) and `test_query_count_is_equal_at_two_row_counts`
(T054).

Verified: `poetry run pytest
tests/test_ghfdb/test_managers.py::TestParentChildAttachment -q` -> `2 passed`, first
run — `with_children()`'s existing `prefetch_related("children")` already satisfies
both.

Next: T055 (TestParentPublishedColumns), which also carries T062's prefetch.

Watch: nothing.

## 2026-08-24T00:30:00Z · Implementer US-2 · T055; T062 blocked (D11)

Did: Added `TestParentPublishedColumns::test_every_published_parent_column_resolves_on_the_complete_row`,
read after `as_ghfdb_flat()` and `with_children()` together (R3), over the
`sites_by_contribution` site carrying two exploration purposes, so a reintroduced
`F()` duplication is caught here too. Tried satisfying T062 in full: added
`"sample__heatflowsite__explo_purpose"` to `with_children()`'s `prefetch_related()`
alongside `"children"`, and wrapped the T055 test's column loop in
`django_assert_num_queries(0)`. That combination passed in isolation, but running the
wider class broke a pre-existing test not authored in this story:
`TestGHFDBParentQuerySet::test_parent_with_children_no_extra_queries`
(`django_assert_max_num_queries(3)`) — measured 7 queries, because `sample` is a
polymorphic FK and prefetching the M2M through its MTI chain to `HeatFlowSite` costs
four further queries, not one. Reverted the `explo_purpose` prefetch and the
zero-query assertion in T055's test; the rest of T055 (every column resolves, no row
duplication) does not depend on the prefetch and stays green. Recorded the conflict as
D11 in `decisions.md`, following D10's precedent from the previous story exactly:
implementer does not edit a pre-existing test, blocks the task, and documents both
sides of the conflict for the resolution above this level.

Verified: red — `poetry run pytest
tests/test_ghfdb/test_managers.py::TestGHFDBParentQuerySet::test_parent_with_children_no_extra_queries -q`
after adding the prefetch -> `1 failed`, `Expected to perform 3 queries or less but 7
were done`. After reverting -> `poetry run pytest tests/test_ghfdb/test_managers.py -q`
-> `44 passed`. attempts_used: 1 (single try-fails-revert cycle; the conflict is
structural, matching D10's shape, not a bug to iterate on).

Next: none — T042-T059, T061 (this story's slice) are complete except T062's blocked
`explo_purpose`-prefetch half.

Watch: whoever resolves D10 for `003-ghfdb-import-export`'s carried-over conflict
should resolve D11 the same pass — both ask the same question of
`django_assert_max_num_queries`-style pre-existing tests versus the T010
constant-query-count methodology this feature standardises on.

## 2026-08-24T02:20:00Z · mapping · T063–T077

**Did**: the published-column mapping and its builder. One entry per published
column naming its group and its accessor, and a builder turning a canonical
column list into display callables in that list's order, refusing a column the
mapping does not hold and naming it. 65 entries, exactly the union of
`CHILD_COLUMNS` and `PARENT_COLUMNS` — no dead entries, none missing.

Every callable is bound under a name that is not a model field name, because
Django resolves a `list_display` entry against the model's fields before the
admin's attributes. Two tests pin that: one proves the built callables keep
their published heading, the other proves the obvious binding loses it, so the
rule reads as a measurement rather than as superstition.

Scalar columns keep a sort key. The changelist is read at database scale and the
current one sorts on about thirty columns, so dropping every sort key would have
been a regression the specification never asked for. Correction flags are
correlated subqueries and carry none, which is what they carry today.

**Verified**: `poetry run pytest tests/test_ghfdb/test_columns.py -q` → 12 passed.
`ruff check` and `ruff format --check` clean on both files.

**Next**: both changelists rebuilt on this (T078–T119, T123).

**Watch**: `list_display_for` returns callables rather than names, so the
changelists lose Django's automatic column-name lookup. That is the point, and
the heading tests are what hold it.

## 2026-08-24T07:52:00Z · Implementer child-admin · T078-T089

**Did**: wrote the twelve tests for the determination changelist, in
`TestGHFDBChildAdmin`, and discharged T079's own cleanup — removed
`EXPECTED_LIST_DISPLAY`, the 54-entry literal `test_ghfdb_admin_changelist_refined_configuration`
compared `list_display` against, and replaced that one assertion with a
heading comparison read from `constants.CHILD_COLUMNS`. That is the only
pre-existing test touched; every other one is untouched.

Several tests (T078, T082, T084, T085, T086, T089) passed on first run against
the *old* `admin.py` — genuine coverage, not tautological: each exercises a
real code path (permission hooks, search, filter scoping, resource
attachment) that prior work already got right, and each would fail if that
behaviour regressed. T080 also passed immediately; the four orientation
columns were already correctly headed and ordered in the old
`_scalar`-generated `list_display`, confirmed by reading the failure diff
before accepting the pass. T079, T081 and the corrected pre-existing test
fail for the right reason: three headings and one ordering swap have not yet
moved to the canonical spelling (D2), and T081's intersection check reads
`get_id_parent` (a bound-method-name *string* on the old admin) rather than a
callable, which is exactly the shape T090 replaces.

T087 (query-count constancy on the rendered changelist) needed real
investigation: raw HTTP-level query counts were not comparable at all,
regardless of admin correctness — recorded as D12. With that confound
removed, the count was already constant (31 at two chains, 31 at four),
before any implementation change here.

**Verified**: `poetry run pytest tests/test_ghfdb/test_admin.py -q` →
`3 failed, 20 passed` — the three RED tests named above, everything else
green. Each new test's exact command and result is in its own commit.

**Next**: T090-T097, rebuilding `GHFDBChildAdmin` on `ColumnDisplay` to turn
T079 and T081 green, plus the corrected pre-existing assertion.

**Watch**: `constant_query_count`, used through a full HTTP request for the
first time in this feature, is polluted by `orbit`'s global audit logging and
a first-request singleton cost (D12). Any future admin-changelist-level
query-count test needs the same `override_settings(ORBIT={"ENABLED": False})`
plus one warm-up call, not the bare fixture.

## 2026-08-24T08:00:00Z · Implementer child-admin · T090-T097

**Did**: rebuilt `GHFDBChildAdmin` on the mapping (T090). `list_display` is now
`("ghfdb_id",)` plus four `ColumnDisplay.build(...)` calls for the orientation
columns (`ID_parent`, `name`, `lat_NS`, `long_EW` — all published parent
columns the child queryset already restates per row) followed by
`ColumnDisplay.list_display_for(CHILD_COLUMNS)`. Deleted the `_scalar`
factory, the `_interval` static helper, `get_id_parent`, the thirty-one
`_scalar`-generated attributes, and all nineteen hand-written `get_*` display
methods for many-valued and empty columns — every one of them is now covered
by the mapping. `get_queryset()` reads `GHFDBChild.objects.for_export()`
rather than restating its own copy of the fifteen-entry prefetch list (T092)
— `for_export()` already carried the identical set, so this is a pure
de-duplication, not a behaviour change. Read-only guarantees (T091), the
plain filters (T094), the vocabulary filters' wiring (T096) and the
import/export resource attachment (T097) needed no code change — each was
already correct and is now proven by a real test rather than only by
inspection.

Introduced `VocabularyListFilter` (T095): one `SimpleListFilter` base taking
a lookup path and one of two modes — `FIELD` for a single-valued
`ConceptField` matching on the stored value, `CONCEPT` for a many-valued
field matching on the concept row's primary key. `EnvironmentListFilter`,
`ChildExplorationMethodListFilter` and `ExplorePurposeListFilter` are now
three-line subclasses of it, same names, same `lookups()`/`queryset()`
behaviour as before — verified against the pre-existing
`TestGHFDBAdminListFilters` tests, which import and instantiate those classes
directly and still pass unchanged. `GHFDBParentAdmin` and its own three
filter classes (`Parent*ListFilter`) are untouched, per this dispatch's
scope; a later dispatch wiring the site changelist onto this same base is
what earns the class's "six callers" framing in `tasks.md`.

Corrected the module docstring and `GHFDBChildAdmin`'s and the three filter
classes' docstrings, which cited `US2`, `BUG-001` and `BUG-004` — defect
handles and a requirement number from the superseded specification.

Two tasks (T093) needed a decision rather than a change: `search_fields`
already carries the two names T093 asks for, plus the determination's own
`ghfdb_id`, which this dispatch left in place rather than narrow — see D13.

**Verified**: `poetry run pytest tests/test_ghfdb/test_admin.py -q` →
`23 passed`. `poetry run ruff check project/ghfdb/admin.py` → All checks
passed (one `RUF005` fixed along the way: iterable unpacking instead of
tuple concatenation for `list_display`). `poetry run ruff format --check
project/ghfdb/admin.py` → already formatted.

**Next**: none — T078-T097 (this dispatch's whole scope) are complete. T098
onward (the site changelist, `GHFDBParentAdmin`) is a later dispatch's.

**Watch**: `admin.py` lost roughly 230 lines in this pass — the `_scalar`
factory, `_interval`, and the eighteen hand-written display methods it and
the many-valued columns needed. Nothing was added back except the four
`ColumnDisplay.build(...)` calls and the `VocabularyListFilter` base (about
30 lines). The next dispatch touching `GHFDBParentAdmin` will find the same
shape of duplication waiting there (`get_*` methods R5 already names) and the
same `VocabularyListFilter` ready to take its three filter classes.
