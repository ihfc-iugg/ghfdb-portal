# Progress — 004 Import a completed upload template into a dataset

## 2026-09-11 — Spec gate: approved

Sam approved the specification, with one amendment: fold #190 into this run. The all-or-nothing
refusal in US-4 rests on `rollback_on_validation_errors` being honoured, and today it is declared in
a place the library never reads. Fixing it inside US-4 rather than leaving the guarantee resting on
a declaration that does nothing.

Approved surface: epic #199, stories #200 through #205, draft PR #206, `spec.md` and `decisions.md`
on branch `004-import-upload-template`.

## 2026-09-11 — Implementer US-1 · T001

Did: copied `docs/constitution/references/data_upload_template.xlsx` into
`tests/fixtures/official_upload_template.xlsx`, byte-identical, and added the
`official_upload_template_workbook` pytest fixture
(`tests/test_ghfdb/test_resources/conftest.py`) that opens it.

Verified: `poetry run pytest tests/test_ghfdb/test_resources/test_template_columns.py -v`
— 2 passed. Confirmed both tests fail for the right reason (`FileNotFoundError`)
with the fixture file temporarily removed, then pass with it restored.

Next: T002 — the failing reconciliation test.

Watch: none.

## 2026-09-11 — Implementer US-1 · T002

Did: added `TestTemplateColumnsMatchTheCanonicalConstants` to
`test_template_columns.py`. Reads the template's Short Name row (row 6 of
the `data list` sheet, column B onward — column A carries the row's own
label) and asserts every name resolves against
`PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS`.

Verified: `poetry run pytest tests/test_ghfdb/test_resources/test_template_columns.py -v`
— fails exactly as expected: `template columns not covered by PARENT_COLUMNS
+ CHILD_COLUMNS + META_FIELDS: ['Continent', 'Country', 'Domain', 'ID',
'Ref_ISGN', 'Region', 'Review_date', 'Reviewer_comment', 'Reviewer_name',
'tc_pT_fuction']` — ten names, matching the brief's prediction exactly.

Next: T003 — judge each of the ten.

Watch: the raw *symmetric* difference between the header and the constants
is actually larger (`ID_parent`, `quality_parent`, `quality_child`,
`Quality_Code_Child`, `Quality_Score_Parent` are in the constants but not
the template). The test is one-directional by design — see decisions.md D7
— because those five are pre-existing, load-bearing retentions this story
does not touch.

## 2026-09-11 — Implementer US-1 · T003

Did: wrote decisions.md D7, judging each of the ten disagreements. None are
simple renames: two are ADR 0003 misspelling exceptions, four are D8
portal-addition exceptions (carried over from `specs/002-ghfdb-proxy`), and
four (`ID`, `Reviewer_name`, `Reviewer_comment`, `Review_date`) are
accepted-and-not-stored additions bound for `META_FIELDS`.

Verified: read `docs/adr/0003-...md` and
`specs/002-ghfdb-proxy/decisions.md` D8 directly; confirmed the D8 exception
is still load-bearing by reading `admin.py`'s `GHFDBParentAdmin` docstring
and `list_display` (geography columns rendered separately from
`ColumnDisplay.list_display_for(PARENT_COLUMNS)`) and
`tests/test_ghfdb/test_admin.py::test_the_geography_follows_the_published_block`.

Next: T004 — apply the verdicts.

Watch: none.

## 2026-09-11 — Implementer US-1 · T004

Did: added `ID`, `Reviewer_name`, `Reviewer_comment`, `Review_date` to
`META_FIELDS`. Added `REJECTED_MISSPELLED_COLUMNS` and
`PORTAL_ADDITION_COLUMNS` to `constants.py`, documenting the other six
disagreements as permanent exceptions rather than renames, and updated
T002's own assertion (`test_template_columns.py`) to treat membership in
either as resolving, alongside `PARENT_COLUMNS + CHILD_COLUMNS +
META_FIELDS`. No change to `PARENT_COLUMNS`, `CHILD_COLUMNS`, or
`columns.py` — no rename touched a name either module already carries, and
`META_FIELDS` is not consumed by `admin.py`'s `ColumnDisplay.list_display_for()`,
so the four additions carry no admin-regression risk.

Verified:
- `poetry run pytest tests/test_ghfdb/test_resources/test_template_columns.py -v`
  — 3 passed (T002 green).
- `poetry run pytest tests/test_ghfdb/test_resources/test_schema_coverage.py
  tests/test_ghfdb/test_resources/test_export.py tests/test_ghfdb/test_admin.py
  tests/test_ghfdb/test_columns.py -v` — 78 passed, 8 xfailed (the same 8 that
  were xfailed before this change — the `strict=True` xfail tests referencing
  issue #122 in `test_schema_coverage.py` and `test_export.py` did not flip to
  an unexpected pass).

Next: T005 — the accepted-and-not-stored named collection.

Watch: `ID_parent`, `quality_parent`, `quality_child`, `Quality_Code_Child`,
`Quality_Score_Parent` remain in the constants without a template
counterpart — pre-existing, out of this story's scope (decisions.md D7).

## 2026-09-11 — Implementer US-1 · T005

Did: added `ACCEPTED_UNSTORED_COLUMNS` to `constants.py` (`ID`,
`Reviewer_name`, `Reviewer_comment`, `Review_date`). Added
`TestEveryTemplateColumnIsMappedOrAccepted` to `test_template_columns.py`,
asserting every template column — other than the two ADR 0003 misspellings,
which T006 refuses outright rather than mapping or accepting — is either
mapped by a resource field's `column_name` (not its dict key, which is
lowercase on several `GHFDBChildImportResource` fields) or a member of the
new collection.

Verified:
- Wrote the test importing `ACCEPTED_UNSTORED_COLUMNS` before it existed;
  confirmed it failed for the right reason (`ImportError`).
- `poetry run pytest tests/test_ghfdb/test_resources/test_template_columns.py -v`
  — 4 passed, after adding the constant.
- Probed the assertion: temporarily dropped `Reviewer_comment` from
  `ACCEPTED_UNSTORED_COLUMNS` — the new test failed, naming it. Restored.
- `poetry run pytest tests/test_ghfdb/test_resources/test_template_columns.py
  tests/test_ghfdb/test_resources/test_schema_coverage.py
  tests/test_ghfdb/test_resources/test_export.py tests/test_ghfdb/test_admin.py
  tests/test_ghfdb/test_columns.py -q` — 82 passed, 8 xfailed (unchanged from
  T004's run).

Next: T006 — refuse a file whose header isn't the template's.

Watch: none.

## 2026-09-11 — Implementer US-1 · T006

Did: added `validate_official_header()` and `OFFICIAL_TEMPLATE_HEADER` to
`constants.py`. Raises `ValueError` naming the header when it is not
exactly `PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS +
PORTAL_ADDITION_COLUMNS`. Pure — inspects only the header it is given, so a
refusal happens before any row is read and before anything could be
written.

Deviation, recorded rather than silently assumed: the test's original
"official header validates" case was wrong. The *currently distributed*
template itself carries the two ADR 0003 misspellings
(`tc_pT_fuction`, `Ref_ISGN`), so it is exactly the case ADR 0003 says must
be refused, not accepted — proven when the first version of this test
failed against the real fixture. `test_template_columns.py` now uses the
real, currently-distributed template as the refusal case (asserting both
misspellings are named), and a header built from the corrected spellings
as the positive case.

Verified:
- Wrote the test importing `validate_official_header`/`OFFICIAL_TEMPLATE_HEADER`
  before they existed; confirmed `ImportError` (right reason).
- After implementing: `poetry run pytest
  tests/test_ghfdb/test_resources/test_template_columns.py -v` — 7 passed.
- Probed: a header missing one column from `OFFICIAL_TEMPLATE_HEADER` still
  raises.
- `poetry run pytest tests/test_ghfdb/ -q` (whole app, narrower than the
  full repo suite but the widest scope touching these constants) — 261
  passed, 13 xfailed, no change in the xfail set from before this story.

Concern, not fixed (outside this story's file scope — constants.py and
columns.py only): `validate_official_header()` is not wired into any import
resource's `before_import` hook, so no actual upload attempt is refused by
it yet. It is exercised directly at the reader level, matching spec.md's
"Independent Test" framing for US-1. Wiring it into the resource pipeline
is US-2/US-4's `importers.py` entry point (T013) or a dedicated task —
flagging for Forge to route.

Next: none — US-1 (T001-T006) complete. Full verify pending.

Watch: the five pre-existing constants (`ID_parent`, `quality_parent`,
`quality_child`, `Quality_Code_Child`, `Quality_Score_Parent`) and issue
#122's half-landed BUG-010 work remain untouched, per decisions.md D7.

## 2026-09-11 — Implementer US-2 · T007

Did: added `TestGHFDBParentImportRequiresNamedDataset` to
`test_parent_import.py`. Calls `before_import()` directly with no
`fairdm_dataset` kwarg, with a real `Dataset` present in the database (the
`dataset` fixture), and asserts it raises — proving the old fallback would
have silently used that dataset rather than refusing.

Verified: `poetry run pytest
tests/test_ghfdb/test_resources/test_parent_import.py::TestGHFDBParentImportRequiresNamedDataset -q`
— failed first (`DID NOT RAISE ValueError`), confirming the fallback is
still live; passed after T008.

Next: T008 — remove the fallback.

Watch: none.

## 2026-09-11 — Implementer US-2 · T008

Did: removed `kwargs.get("fairdm_dataset") or FairDataset.all_objects.first()`
from both `GHFDBParentImportResource.before_import` and
`GHFDBChildImportResource.before_import`; each now raises `ValueError`
naming the resource when `fairdm_dataset` is absent. No lookup logic is
added or removed for the case where a dataset IS named — the caller
already passes a resolved instance, so the "reach private datasets"
caution (R1 in plan.md) has nothing to narrow.

Verified:
- `poetry run pytest
  tests/test_ghfdb/test_resources/test_parent_import.py::TestGHFDBParentImportRequiresNamedDataset -q`
  — 1 passed (T007 green).
- `poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py
  tests/test_ghfdb/test_resources/test_child_import.py -q` — 37 failed, 13
  passed, 5 xfailed. All 37 failures are pre-existing tests calling
  `import_data()` without `fairdm_dataset=`, unknowingly relying on the
  removed fallback (same root cause in every case, confirmed by reading the
  traceback of each). Not modified, per craft-tdd — recorded in
  decisions.md D11 for Forge to apply the one-line fix each needs
  (`fairdm_dataset=dataset`, the pattern already used in
  `test_roundtrip.py`).

Next: T009 — two sites, each with its parent value, in a named dataset.

Watch: the full repo verify at the end of this story will report these 37
as failing. This is the accepted, documented consequence in decisions.md
D11, not a regression introduced by a later task.

## 2026-09-11 — Implementer US-2 · T009-T010

Did: added `TestGHFDBParentImportTwoCoordinatePairs` to
`test_parent_import.py` (T009): two rows at two coordinate pairs, imported
with `fairdm_dataset=dataset`, asserted as two `HeatFlowSite` + two
`ParentHeatFlow`, each with its own P-column value and both attached to
the named dataset.

T010 (make it pass) needed no production change: the per-site dataset
wiring already existed in `before_save_instance` / `_get_or_create_site`
(pre-dating this story) — T008 was what stood between it and a caller
that could actually reach it. Probed rather than assumed: temporarily
disabled `site.dataset = self._fairdm_dataset` in
`_get_or_create_site` and confirmed the test fails
(`site.dataset_id == dataset.pk`); restored.

Verified:
- `poetry run pytest
  tests/test_ghfdb/test_resources/test_parent_import.py::TestGHFDBParentImportTwoCoordinatePairs -q`
  — 1 passed.
- `poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py -q`
  — 18 failed, 11 passed, 5 xfailed. Same 18 pre-existing failures as
  before T009 (decisions.md D11) — no new regression from this test.

Next: T011 — geography columns stored as supplied, never recomputed.

Watch: none.

## 2026-09-11 — Implementer US-2 · T011

Did: added `TestGHFDBParentImportGeographyStoredAsSupplied` to
`test_parent_import.py`. Country/Region/Continent/Domain are set to
values that deliberately disagree with what the row's own coordinates
would suggest (Germany/Europe), so a passing test proves the stored
values come from the row rather than being derived (FR-008). Required no
production change — `ParentWidget`'s `scalar_map` already carries all
four with no widget override, i.e. no recomputation path exists.

Verified:
- `poetry run pytest
  tests/test_ghfdb/test_resources/test_parent_import.py::TestGHFDBParentImportGeographyStoredAsSupplied -q`
  — 1 passed.
- Probed: temporarily removed the four `scalar_map` entries in
  `ParentWidget.__init__` — test failed (`site.country == "Nowhereland"` no
  longer holds, since neither is set). Restored; re-ran green.

Next: T012 — reviewer columns and ID accepted without being stored.

Watch: none.

## 2026-09-11 — Implementer US-2 · T012

Did: added `TestGHFDBParentImportAcceptsUnstoredColumns` to
`test_parent_import.py` and `TestGHFDBChildImportAcceptsUnstoredColumns`
to `test_child_import.py`. Each imports a row carrying
`Reviewer_name`/`Reviewer_comment`/`Review_date` (plus `ID` on the parent
side, where it is not a declared field) and asserts the import completes
without error (FR-009). Required no production change — neither resource
declares these columns, and `django-import-export` ignores any dataset
column a resource's `Meta.fields` does not name.

The child-side test does not use this module's pre-existing
`import_parents()` helper: like 37 other pre-existing call sites across
both files (decisions.md D11), it omits `fairdm_dataset=` and T008 now
refuses that. The new test names its dataset explicitly throughout
instead, rather than touching the shared helper.

Verified: `poetry run pytest
tests/test_ghfdb/test_resources/test_parent_import.py::TestGHFDBParentImportAcceptsUnstoredColumns
tests/test_ghfdb/test_resources/test_child_import.py::TestGHFDBChildImportAcceptsUnstoredColumns -q`
— 2 passed.

Concern (lint tooling, not scope): `poetry run ruff check` with this
repo's `fix = true` rewrote an unrelated pre-existing test's import block
(`test_child_import.py::TestGHFDBChildPrivateDatasetRegression`) on a
scoped run against the file I was editing — the violation already existed
at this story's base commit (confirmed by checking it against a stash of
only my own edits). Reverted by hand both times it recurred; every lint
check after T012 uses `ruff check --no-fix` on scoped paths instead.

Next: T013 — the callable entry point.

Watch: none.

## 2026-09-11 — Implementer US-2 · T013

Did: added `project/ghfdb/importers.py` with the public callable
`import_ghfdb_template(file, dataset)` (FR-001). Accepts either raw XLSX
bytes/a binary file-like object or an already-parsed `tablib.Dataset`,
runs the parent pass then the child pass — each against its own
`copy.deepcopy` of the parsed rows, since the parent resource's
`before_import()` dedups rows in place and the child pass needs every row
— inside one `transaction.atomic()`, wired to `dataset` through
`fairdm_dataset`. Returns a `GHFDBImportOutcome(parent, child)` dataclass.

Also overrode `GHFDBParentAdmin.process_dataset()` to call the entry point
rather than the framework's default single-resource commit (D12) — the
one admin path this story touches, since site+parent import is US-2's own
territory. `GHFDBChildAdmin`'s separate wizard is untouched.

Decision recorded (decisions.md D12): no dataset-selection surface exists
on either admin route, and adding one is out of this feature's scope
(spec.md Assumptions: "nothing... has a person clicking anything" — the
upload page belongs to R6/R7). The admin route therefore always raises
the FR-002 error once it reaches `process_dataset` — no worse than always
silently writing to whichever dataset happened to be first, which is what
it did before this story.

Verified:
- `poetry run pytest tests/test_ghfdb/test_importers.py -v` — 4 passed.
  Confirmed RED first: temporarily moved `importers.py` aside,
  `ModuleNotFoundError` on all four; restored, green again.
- `poetry run pytest
  tests/test_ghfdb/test_admin.py::TestGHFDBParentAdmin::test_process_dataset_delegates_to_the_shared_entry_point -v`
  — 1 passed. Confirmed RED first: temporarily reverted the
  `process_dataset` override via a tagged stash — fails with
  `AttributeError: 'NoneType' object has no attribute 'cleaned_data'`
  (the framework default expects a real confirm form); restored from the
  stash by its SHA, dropped it.
- `poetry run pytest tests/test_ghfdb/test_admin.py -q` — 42 passed, no
  regression.
- Updated `docs/guides/importing-data.md` with a "Running an import"
  section. Verified its example against this branch with a scratch test
  using a real file-like object (`io.BytesIO`, exercising the `file.read()`
  branch, not just raw bytes) — passed, then deleted the scratch file.

Next: full repo verify (§5), then the completion report.

Watch: `GHFDBParentAdmin`'s import route cannot complete a real import
until a dataset-selection surface exists (D12) — not a regression, since
it never safely chose the right dataset before either.

## 2026-09-11 — Implementer US-2 · TC01

Did: repaired the 37 pre-existing tests D11 left failing when the
dataset-guessing fallback was removed from both resources'
`before_import()`. Each `import_data()` call site in
`test_parent_import.py` and `test_child_import.py` that omitted
`fairdm_dataset=` now passes `fairdm_dataset=dataset` — the fixture every
one of those tests already receives — matching the pattern
`test_roundtrip.py` already used. In `test_child_import.py`, the shared
`import_parents()` helper (already parameterized on `dataset`) covers
most of its callers with a single fix at the helper itself. No assertion,
fixture, row, expected value, class or name in either module changed;
`ruff check`'s `fix = true` reordered one unrelated import block in
`test_child_import.py` (`TestGHFDBChildPrivateDatasetRegression`) as a
side effect of a scoped lint run — reverted by hand to its original
ordering, confirmed byte-identical to the pre-task committed file.
Two commits, one per module (decisions.md D13).

Verified:
- `poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py
  tests/test_ghfdb/test_resources/test_child_import.py -q` before any
  edit — 37 failed, 17 passed, 5 xfailed, confirming D11's count.
- `poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py
  -q` after that module's fix — 31 passed, 5 xfailed.
- `poetry run pytest tests/test_ghfdb/test_resources/test_child_import.py
  -q` after that module's fix — 23 passed.
- `poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py
  tests/test_ghfdb/test_resources/test_child_import.py -q` — 54 passed, 5
  xfailed (the same 5 pre-existing BUG-006/#122 xfails, untouched).
- `poetry run ruff check` and `poetry run ruff format --check`, each
  scoped to the one file just edited.

Next: full repo verify (§5), then the completion report.

Watch: none.

## 2026-09-11 — Implementer US-3 · T014

Did: added `TestGHFDBChildMultipleDeterminationsPerSite` to
`test_child_import.py` (FR-007): two child rows sharing one `ID_parent`,
with distinct `q_top`/`q_bottom`, must produce two `HeatFlow` records
beneath the same site, each carrying its own `HeatFlowInterval`.

Verified: `poetry run pytest
tests/test_ghfdb/test_resources/test_child_import.py::TestGHFDBChildMultipleDeterminationsPerSite
-x -q` — passed on first run, no production change made yet. Carried to
T015 for the non-vacuity probe the brief requires before this counts as
covered.

Next: T015 — probe the passing test before accepting it.

## 2026-09-11 — Implementer US-3 · T015

Did: T014's test passed against the unmodified tree, so `child.py`
already satisfies FR-007's per-row interval requirement — no production
change was needed. Probed the test per the brief's non-vacuity rule
rather than accepting the green result at face value: temporarily edited
`GHFDBChildImportResource._build_interval` to cache and reuse the first
row's `HeatFlowInterval` across subsequent rows on the same resource
instance, ran the T014 test, watched it fail
(`assert child_a.sample_id != child_b.sample_id` — both were `2`), then
restored `child.py` from a pre-edit copy and confirmed the restored file
diffed clean against the copy and the test passed again.

Verified:
- Probe (broken): `poetry run pytest
  tests/test_ghfdb/test_resources/test_child_import.py::TestGHFDBChildMultipleDeterminationsPerSite
  -x -q` — 1 failed, `assert 2 != 2` on `sample_id`.
- Restore: `diff` against the pre-edit copy of `child.py` — no
  differences.
- Restored: same command — 1 passed.

No decisions.md entry: nothing ambiguous was resolved, and no production
code changed. `child.py` is untouched by this task.

Next: T016 — sub-measurement values land on their own determination.

## 2026-09-11 — Implementer US-3 · T016

Did: added `TestGHFDBChildSubMeasurementsPerDetermination` to
`test_child_import.py` (FR-007): two determinations with distinct
gradient (`T_grad_mean`), conductivity (`tc_mean`), correction
(`corr_T_flag`/`corr_S_flag`) and probe (`probe_penetration`) values must
each keep their own values rather than one bleeding onto the other.
Column names checked against `columns.py`'s `PublishedColumns.ENTRIES`
and the official template fixture's header row (both confirm `T_grad_*`,
`tc_*`, `corr_*_flag`, `probe_*` as the real names; the template's
`tc_pT_fuction` misspelling is out of scope here — ADR 0003 already
refuses it, and this test does not touch that column).

Verified: `poetry run pytest
tests/test_ghfdb/test_resources/test_child_import.py::TestGHFDBChildSubMeasurementsPerDetermination
-x -q` — passed on first run, no production change made. Carried to T017
for the non-vacuity probe.

Next: T017 — probe the passing test before accepting it.

## 2026-09-11 — Implementer US-3 · T017

Did: T016's test passed against the unmodified tree, so no production
change was needed. Probed per the brief's non-vacuity rule: temporarily
edited `GHFDBChildImportResource._build_gradient` to cache and reuse the
first row's `ThermalGradient` across subsequent rows on the same resource
instance (the same shape of bug T015 probed on the interval), ran the
T016 test, watched it fail on the gradient-value assertions, then
restored `child.py` from a pre-edit copy and confirmed a clean diff and a
passing re-run.

Verified:
- Probe (broken): `poetry run pytest
  tests/test_ghfdb/test_resources/test_child_import.py::TestGHFDBChildSubMeasurementsPerDetermination
  -x -q` — 1 failed (`child_b.thermal_gradient.value` was 20.0, not 40.0).
- Restore: `diff` against the pre-edit copy of `child.py` — no
  differences.
- Restored: same command — 1 passed; full module —
  `poetry run pytest tests/test_ghfdb/test_resources/test_child_import.py -q`
  — 25 passed.

No decisions.md entry: nothing ambiguous was resolved, and no production
code changed.

Next: T018 — `relevant_child` names exactly the contributing children.
