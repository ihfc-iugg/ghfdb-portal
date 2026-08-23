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
