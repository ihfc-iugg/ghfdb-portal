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
