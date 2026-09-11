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

## 2026-09-11 — Implementer US-3 · T018

Did: added `TestGHFDBChildRelevantChildFlag` to `test_child_import.py`
(FR-006): two determinations, one `relevant_child="Yes"` and one
`relevant_child="No"`, and asserted both directions — the contributing
child is marked `is_relevant=True`, the non-contributing one
`is_relevant=False`.

Verified: `poetry run pytest
tests/test_ghfdb/test_resources/test_child_import.py::TestGHFDBChildRelevantChildFlag
-x -q` — passed on first run, no production change made. Carried to T019
for the non-vacuity probe.

Next: T019 — probe the passing test before accepting it.

## 2026-09-11 — Implementer US-3 · T019

Did: T018's test passed against the unmodified tree, so no production
change was needed. Probed per the brief's non-vacuity rule: temporarily
added `instance.is_relevant = True` unconditionally in
`GHFDBChildImportResource.before_save_instance`, ran the T018 test,
watched it fail on the non-contributing child's assertion, then restored
`child.py` from a pre-edit copy and confirmed a clean diff and a passing
re-run.

Verified:
- Probe (broken): `poetry run pytest
  tests/test_ghfdb/test_resources/test_child_import.py::TestGHFDBChildRelevantChildFlag
  -x -q` — 1 failed (`child_b.is_relevant` was `True`, expected `False`).
- Restore: `diff` against the pre-edit copy of `child.py` — no
  differences.
- Restored: full module —
  `poetry run pytest tests/test_ghfdb/test_resources/test_child_import.py -q`
  — 26 passed.

No decisions.md entry: nothing ambiguous was resolved, and no production
code changed.

Next: T020 — every child object attaches to the named dataset, proven
against a decoy.

## 2026-09-11 — Implementer US-3 · T020

Did: added `TestGHFDBChildObjectsAttachToNamedDataset` to
`test_child_import.py`. Creates a decoy `Dataset` before importing, then
asserts every child object that holds a `dataset` FK —
`HeatFlow`/determination, `HeatFlowInterval`/depth interval,
`ThermalGradient`, `IntervalConductivity` — is attached to the named
dataset and not the decoy. Confirmed `HeatFlowCorrection` and
`ProbeMetadata` hold no `dataset` field of their own (checked against
`heat_flow/models/child.py`), so the test asserts `not hasattr(...,
"dataset")` for those two rather than a dataset comparison the model
cannot support.

This test's acceptance text does not carry the brief's explicit "same
non-vacuity rule as T015" instruction, unlike T014/T016/T018 — but it
passed on first run for the same reason those three did (the child pass
already resolves `dataset` correctly), so I probed it anyway per
craft-tdd's general rule, rather than only where the brief said to.
Temporarily removed the `conductivity.dataset = self._fairdm_dataset`
line in `_build_conductivity`, ran the test, watched it fail (a NOT NULL
constraint surfaced as a row error), then restored `child.py` from a
pre-edit copy and confirmed a clean diff and a passing re-run.

Verified:
- Probe (broken): `poetry run pytest
  tests/test_ghfdb/test_resources/test_child_import.py::TestGHFDBChildObjectsAttachToNamedDataset
  -x -q` — 1 failed (`result.has_errors()` was `True` — the row raised
  saving `IntervalConductivity` with no dataset).
- Restore: `diff` against the pre-edit copy of `child.py` — no
  differences.
- Restored: full module —
  `poetry run pytest tests/test_ghfdb/test_resources/test_child_import.py -q`
  — 27 passed.

No decisions.md entry: nothing ambiguous was resolved, and no production
code changed. This closes US-3's task list (T014-T020); every task's
acceptance criterion was already satisfied by the tree at dispatch — no
production code in `project/ghfdb/resources/child.py` changed across the
whole story, only `tests/test_ghfdb/test_resources/test_child_import.py`.

## 2026-09-11 — US-4 · T021

Did: added `TestGHFDBTemplateRefusedWhole` to `test_importers.py`,
reproducing #190 directly: two child rows, the second carrying a `qc`
value `QuantityWidget` cannot parse. Confirmed against the tree as
dispatched (before any US-4 change) that row 1's `HeatFlow` survives the
import even though row 2 faults — the reproduction failed for exactly
that reason.

Verified:
- Reproduction (red): `poetry run pytest
  tests/test_ghfdb/test_importers.py::TestGHFDBTemplateRefusedWhole -x -q`
  — 1 failed, `AssertionError` on `not HeatFlow.objects.filter(ghfdb_id=1).exists()`
  (row 1 was written).

No decisions.md entry: nothing ambiguous, this task is the reproduction
itself.

Next: T022 — pass `rollback_on_validation_errors` from the entry point.

## 2026-09-11 — US-4 · T022

Did: removed `rollback_on_validation_errors = True` from both resources'
`Meta` (`parent.py`, `child.py`) and added `clean_model_instances = True`
to both instead; `importers.py` now passes
`rollback_on_validation_errors=True` explicitly to both `import_data()`
calls. Discovered along the way that `clean_model_instances = True` alone
refused every row, on `sample`/`dataset`/`name` rather than on anything
the file got wrong — `before_save_instance()` (where both resources set
those three) runs after `full_clean()`, not before it. Fixed by
overriding `validate_instance()` on both resources to exclude those three
fields from `full_clean()`, recorded as D15.

Verified:
- T021 green: `poetry run pytest
  tests/test_ghfdb/test_importers.py::TestGHFDBTemplateRefusedWhole -q`
  — 1 passed.
- Full module: `poetry run pytest tests/test_ghfdb/test_importers.py -q`
  — 5 passed.
- No regression: `poetry run pytest
  tests/test_ghfdb/test_resources/test_parent_import.py
  tests/test_ghfdb/test_resources/test_child_import.py -q` — 58 passed, 5
  xfailed (same 5 pre-existing xfails as before this story).
- Wider check: `poetry run pytest tests/test_ghfdb/ -q` — 276 passed, 13
  xfailed.
- Lint, scoped: `poetry run ruff check project/ghfdb/resources/parent.py
  project/ghfdb/resources/child.py project/ghfdb/importers.py
  tests/test_ghfdb/test_importers.py` — all checks passed.

decisions.md D15 records the `validate_instance()` exclusion and why it is
scoped to `sample`/`dataset`/`name` rather than a larger hook-order
restructure.

Next: T023 — probe that reinstating the old `Meta` form makes the guard
fail.

## 2026-09-11 — US-4 · T023

Did: probed T021's test against the pre-T022 form, exactly as it was
declared before this story: temporarily removed the
`rollback_on_validation_errors=True` keyword from both `import_data()`
calls in `importers.py` and added `rollback_on_validation_errors = True`
back to both resources' `Meta` (`clean_model_instances = True` left in
place — DR-002's other half). No test file touched.

Verified:
- Probe (broken): `poetry run pytest
  tests/test_ghfdb/test_importers.py::TestGHFDBTemplateRefusedWhole -x -q`
  — 1 failed, same `AssertionError` as T021's original red (row 1 written
  despite row 2's fault) — confirming the entry-point keyword, not the
  `Meta` declaration, is what the guard actually depends on.
- Restore: `diff` of `importers.py`, `resources/parent.py`,
  `resources/child.py` against the pre-probe (post-T022) copies — no
  differences in any of the three.
- Restored: `poetry run pytest tests/test_ghfdb/test_importers.py -q` —
  5 passed.

No decisions.md entry: nothing ambiguous was resolved, this task is the
probe itself.

Next: T024 — test two widely separated faults are both reported.

## 2026-09-11 — US-4 · T024

Did: added `test_two_widely_separated_faults_are_both_reported_and_nothing_lands`
to `TestGHFDBTemplateRefusedWhole`. Three rows: the first entirely clean,
the second and third each carrying their own child-side fault only (`qc`,
then `qc_uncertainty`) — the parent side (site, parent heat flow) has no
fault on any of the three rows, so the parent pass alone would commit
cleanly. Asserts both faults are named by row (`invalid.number`) and
column (`invalid.field_specific_errors` keys), and that nothing from
either resource lands.

Verified:
- Red, for the intended reason: `poetry run pytest
  "tests/test_ghfdb/test_importers.py::TestGHFDBTemplateRefusedWhole::test_two_widely_separated_faults_are_both_reported_and_nothing_lands"
  -x -q` — 1 failed on the first assertion, `outcome.has_errors()` was
  `False` despite two validation faults — `GHFDBImportOutcome.has_errors()`
  does not check `has_validation_errors()` on either pass, the same gap
  T021 traces back to.

No decisions.md entry: the gap this test exposes is the same one D15/T022
already named, no new ambiguity.

Next: T025 — make it green without breaking the parent pass's dependency
on cross-pass visibility.

## 2026-09-11 — US-4 · T025

Did: `GHFDBImportOutcome.has_errors()` now also checks
`has_validation_errors()` on both passes. `import_ghfdb_template()` checks
the combined outcome after both passes complete and calls
`transaction.set_rollback(True)` before the shared `with
transaction.atomic():` block exits if either pass reports any error —
covering the case each pass's own `rollback_on_validation_errors` cannot:
one pass at fault while the other has nothing wrong with it and would
otherwise commit its own rows.

Considered and rejected calling both passes with `dry_run=True` first, as
the brief's wording literally reads. Confirmed empirically (D16) that each
`import_data()` call's own savepoint rolls back unconditionally at the end
of *that* call when `dry_run=True`, before the next pass runs — so the
child pass, which resolves its parent via `ID_parent`/coordinates, would
never see the parent pass's rows and would refuse every file, clean ones
included. `transaction.set_rollback` on the shared outer transaction gets
the same "nothing commits unless both passes are clean" property without
disturbing that dependency. Recorded as D16 with the query that confirmed
it.

Verified:
- T024 green: `poetry run pytest tests/test_ghfdb/test_importers.py -q`
  — 6 passed.
- No regression: `poetry run pytest tests/test_ghfdb/ -q` — 277 passed,
  13 xfailed.
- Lint, scoped: `poetry run ruff check project/ghfdb/importers.py
  tests/test_ghfdb/test_importers.py` — all checks passed.

decisions.md D16 records why a literal dry-run-first design does not
work here and what replaces it.

Next: T026 — a clean file imports with nothing reported, every row
landed, counted rather than merely checked for existence.

## 2026-09-11 — US-4 · T026

Did: added `test_a_clean_file_reports_nothing_and_every_row_lands` to
`TestGHFDBTemplateRefusedWhole`: three rows, no fault anywhere, asserts
`HeatFlowSite.objects.count() == 3`, `ParentHeatFlow.objects.count() ==
3`, `HeatFlow.objects.count() == 3` — the count, not existence. Passed on
first run (T022/T025 already make a clean import commit correctly), so
probed per craft-tdd rather than accepted on trust: inverted the
`if outcome.has_errors():` condition T025 added in `importers.py` to
`if not outcome.has_errors():`, so a clean file's writes would be rolled
back instead of a faulty one's.

Verified:
- Probe (broken): `poetry run pytest
  "tests/test_ghfdb/test_importers.py::TestGHFDBTemplateRefusedWhole::test_a_clean_file_reports_nothing_and_every_row_lands"
  -x -q` — 1 failed, `HeatFlowSite.objects.count()` was `0`, expected `3`.
- Restore: `diff` against the pre-probe copy of `importers.py` — no
  differences.
- Restored: `poetry run pytest tests/test_ghfdb/test_importers.py -q` —
  7 passed.

No decisions.md entry: nothing ambiguous, no production code changed.

Next: T026a — an empty mandatory model field names its row and column, in
a translated message, and refuses the whole file.

## 2026-09-11 — US-4 · T026a

Did: added
`test_an_empty_mandatory_model_field_names_its_row_and_column_and_refuses_the_file`
to `TestGHFDBTemplateRefusedWhole`. One row, otherwise clean, with `q`
(the parent heat-flow value) left empty. Passed on first run against the
already-landed T022/T025 tree, so probed rather than accepted on trust:
temporarily set `clean_model_instances = False` on
`GHFDBParentImportResource.Meta` — the exact pre-T022 form for this
option — and re-ran.

Verified:
- Probe (broken): `poetry run pytest
  "tests/test_ghfdb/test_importers.py::TestGHFDBTemplateRefusedWhole::test_an_empty_mandatory_model_field_names_its_row_and_column_and_refuses_the_file"
  -x -q` — 1 failed, `outcome.parent.has_validation_errors()` was `False`
  — confirming DR-002's claim directly: this fault type had no
  enforcement path before `clean_model_instances` was turned on.
- Restore: `diff` against the pre-probe copy of `resources/parent.py` —
  no differences.
- Restored: `poetry run pytest tests/test_ghfdb/test_importers.py -q` —
  8 passed.
- Wider check: `poetry run pytest tests/test_ghfdb/ -q` — 279 passed, 13
  xfailed.
- Lint, scoped: `poetry run ruff check project/ghfdb/importers.py
  project/ghfdb/resources/parent.py project/ghfdb/resources/child.py
  tests/test_ghfdb/test_importers.py` — 1 import-order fix applied to the
  new test's own import block, nothing else changed; re-ran the module
  after, still 8 passed.

The actual Django message the model raises for this field is "This field
cannot be null." (QuantityField checks null before blank), not "This
field cannot be blank." as first guessed — corrected in the assertion
against what the probe actually showed, not the docstring's initial
assumption. No decisions.md entry: nothing ambiguous, no production code
changed for this task — T022 already carries the fix, this task is its
proof.

## 2026-09-11 — US-5 · T027

Did: added `TestControlledVocabularyDecides` to `test_ghfdb/test_importers.py`
with `test_an_unrecognised_vocabulary_value_names_row_column_and_value_and_refuses_the_file`
— one row, otherwise clean, with `environment` (a single-valued
controlled-vocabulary column, via `ConceptWidget`) set to a value the
portal's `GeographicEnvironment` vocabulary holds no concept for.

First draft used `"not_a_real_environment"` as the bogus value and
asserted `"environment" in message`; it passed immediately, for the wrong
reason — the assertion was vacuously true because the substring
`"environment"` appears inside `"not_a_real_environment"` itself, not
because the fault names the column. Caught by printing the actual message
before trusting the pass: `"HeatFlowSite: Invalid value
'not_a_real_environment' for GeographicEnvironment vocabulary. Valid
options are: [...]"` — the column name `environment` never appears in it
at all, only the vocabulary class name `GeographicEnvironment` and the
value. Rewrote with a bogus value that shares no substring with the
column name (`"not_a_real_value"`) to make the assertion honest.

Verified:
- Red: `poetry run pytest
  "tests/test_ghfdb/test_importers.py::TestControlledVocabularyDecides::test_an_unrecognised_vocabulary_value_names_row_column_and_value_and_refuses_the_file"
  -x -q` — 1 failed on `assert "environment" in message`, against
  `"HeatFlowSite: Invalid value 'not_a_real_value' for
  GeographicEnvironment vocabulary. ..."` — the right reason: `environment`
  is a pass-through resource field with no `attribute`, so its value is
  never routed through `import_field()`/`import_instance()`'s column-aware
  `ValidationError` wrapping; `ConceptWidget.clean()` is instead called
  directly from `ParentWidget`/`RelatedModelWidget.clean()` inside
  `_get_or_create_site()` (`before_save_instance`), and the plain
  `ValueError` it raises falls into `import_row()`'s generic
  `except Exception` handler, which records the message string but has no
  concept of "column".

No decisions.md entry: the ambiguity this task surfaced (why the column
is missing) is the mechanism T028 fixes, not a judgement call of its own.

Next: T028 — make the test pass in `ConceptWidget.clean` and
`MultiConceptWidget.clean`.

## 2026-09-11 — US-5 · T028

Did: `ConceptWidget.clean()` and `MultiConceptWidget.clean()`
(`project/ghfdb/resources/widgets.py`) now accept an optional `column`
keyword; when a value fails to resolve, the raised message is prefixed
`"Column '%(column)s': "` whenever the caller supplies one, falling back
to the original unprefixed message otherwise so every existing caller and
test that does not pass `column` sees no change at all.
`RelatedModelWidget.clean()`'s scalar loop — the one caller that already
holds the row's column name (`row_col`) at the point it calls
`col_widget.clean(...)` — now passes `column=row_col` through.
`QuantityWidget.clean()` (the only other widget reachable via
`widget_map`) already accepts `**kwargs`, so the added keyword is a no-op
there.

Verified:
- Green: `poetry run pytest
  tests/test_ghfdb/test_importers.py::TestControlledVocabularyDecides
  tests/test_ghfdb/test_resources/test_widgets.py -q` — 41 passed. T027
  goes green; every pre-existing widget test (including the ones that
  assert on the unprefixed message shape) is unaffected.
- Lint, scoped: `poetry run ruff check
  project/ghfdb/resources/widgets.py` and `poetry run ruff format --check
  project/ghfdb/resources/widgets.py` — both clean.

No decisions.md entry: T028's brief already named the exact fix location
and shape; nothing left ambiguous.

Next: T028a — close the swallow in `RelatedModelWidget.set_m2m_relations`
so the many-valued vocabulary path enforces the same rule.

## 2026-09-11 — US-5 · T028a, T028b

Did: `RelatedModelWidget.set_m2m_relations()` no longer swallows
`(ValueError, ValidationError)` from `m2m_widget.clean(...)` with a bare
`except: pass`. It now mirrors the scalar loop in `clean()` that T028
already exercises: catch, wrap as `ValueError("%(model)s: %(err)s")`,
re-raise `from exc` — and pass `column=row_col` through so the
many-valued path names its column the same way the scalar path now does.
Added `test_an_unrecognised_value_in_a_many_valued_column_refuses_the_file`
(T028b) to `TestControlledVocabularyDecides`, using `tc_method` (one of
the thirteen many-valued columns DR-001 named, reached through
`ConductivityWidget`'s `m2m_map`) rather than a single-valued column, per
the brief's own warning that a single-valued test would pass over the top
of this defect.

T028b passed on first run against the already-fixed tree, so probed per
`craft-tdd`/D14 rather than accepted on trust: saved a pre-probe copy of
`widgets.py`, mechanically reverted `set_m2m_relations` to the original
bare `except (ValueError, ValidationError): pass` (moving the `.set(qs)`
call back inside the `try`, dropping the `column=` argument), re-ran,
then restored from the saved copy and diffed to confirm a byte-clean
restore.

Verified:
- Probe (broken): `poetry run pytest
  "tests/test_ghfdb/test_importers.py::TestControlledVocabularyDecides::test_an_unrecognised_value_in_a_many_valued_column_refuses_the_file"
  -q` — 1 failed on `assert outcome.has_errors()` — `False`: with the
  swallow restored, the unrecognised `tc_method` concept is silently
  discarded, `IntervalConductivity.method` (etc.) simply never gets set,
  and the row commits as if nothing were wrong.
- Restore: `diff /tmp/widgets_pre_probe.py
  project/ghfdb/resources/widgets.py` — no differences (confirmed
  byte-clean before any further edit).
- Restored green: `poetry run pytest
  tests/test_ghfdb/test_importers.py::TestControlledVocabularyDecides
  tests/test_ghfdb/test_resources/test_widgets.py -q` — 41 passed.
- Lint, scoped: `poetry run ruff check project/ghfdb/resources/widgets.py
  tests/test_ghfdb/test_importers.py` and `poetry run ruff format --check`
  on the same two files — both clean.

decisions.md D17 records where the brief flagged genuine uncertainty:
whether a fault raised from inside `set_m2m_relations` (called from
`after_save_instance`, after the row is already saved) reaches the
resource's fault-recording mechanism the same way a `before_save_instance`
fault does. Traced and confirmed empirically (see D17): it does, unaided
— `save_instance()` calls `before_save_instance()`, saves, then
`after_save_instance()`, all inside `import_row()`'s one outer `try`, so
narrowing the swallow was the whole fix; no new recording channel was
needed.

Next: T029 — a value the template's own vocabulary sheet lists, which the
portal does not hold, is still refused.

## 2026-09-11 — US-5 · T029, T030

Did: added `test_a_value_the_templates_sheet_lists_but_the_portal_does_not_hold_is_still_refused`
(T029) and `test_a_value_the_portal_holds_but_the_templates_sheet_does_not_list_is_accepted`
(T030) to `TestControlledVocabularyDecides`. Both read the real
`official_upload_template_workbook` fixture's `"controlled vocabulary"`
sheet at test run time and diff its values against the portal's own
`Concept` labels for a chosen vocabulary — T029 picks a value only the
sheet lists (`"Type of exploration method"` / `ExplorationMethod`: the
sheet lists `"other (specify in comments)"`, the portal holds only
`"other"`), T030 picks a value only the portal holds (`"Heat-flow
method"` / `HeatFlowMethod`: the portal holds `"other"`, the sheet's
column for it lists only `"other (specify in coments)"` [sic] and
`"unspecified"`). Neither value is hard-coded — each test asserts its
set difference is non-empty before using it, so a future edit to the
fixture or the portal's vocabularies that erases the disagreement fails
the test loudly rather than passing vacuously on an empty set.

Both passed on first run. Probed per `craft-tdd`/D14: saved a pre-probe
copy of `widgets.py`, temporarily made `ConceptWidget.clean()` return the
normalised value instead of raising for an unrecognised choice (bypassing
the refusal T027/T028 cover), and re-ran both. T030 still passed, as
expected — it doesn't depend on refusal. T029 also still passed, but for
an unintended reason: with the widget-level check disabled, the garbage
`explo_method` value the parent pass accepts is carried through to the
child pass, where it trips a `ValueError` from a URI-construction routine
serialising a concept key with spaces and parentheses in it — an
incidental crash from the probe's own invalid state, not evidence about
the mechanism T029 exists to cover. Restored the pre-probe copy and
confirmed a byte-clean diff before re-running the suite.

This did not weaken confidence in T029: the widget-level rejection it
depends on is the exact mechanism T027 already probed cleanly (breaking
it there produced the intended, on-topic failure). T029 and T030 add the
thing T027 alone cannot: proof that the values in play are genuinely
sourced from the real template fixture and genuinely disagree with the
portal, which is what FR-014's "stated backwards on purpose" acceptance
criterion asks for. Recorded here rather than reworking the probe target,
per `craft-tdd`'s own instruction to say what was tried rather than force
a clean mutation onto a test where the honest one is noisy.

Verified:
- Green (post-restore): `poetry run pytest
  tests/test_ghfdb/test_importers.py::TestControlledVocabularyDecides
  tests/test_ghfdb/test_resources/test_widgets.py -q` — 43 passed.
- Restore: `diff` against the pre-probe copy of `widgets.py` — no
  differences.
- Lint, scoped: `poetry run ruff check tests/test_ghfdb/test_importers.py`
  and `poetry run ruff format --check tests/test_ghfdb/test_importers.py`
  — both clean.

No decisions.md entry: FR-013/FR-014 already state the rule; nothing here
resolves an ambiguity, it demonstrates the already-decided rule against
real data.

Next: T031 — assert nothing in the import path opens the template's
"controlled vocabulary" sheet.

## 2026-09-11 — US-5 · T031

Did: added `test_the_import_never_opens_the_controlled_vocabulary_sheet`
to `TestControlledVocabularyDecides`. Patches `openpyxl.load_workbook`
(the exact name `GHFDBImportFormat.create_dataset` imports fresh on every
call, so patching the `openpyxl` module attribute — not
`project.ghfdb.resources.formats.load_workbook`, which does not exist as
a module-level name — is what actually intercepts it) with a wrapper
that returns the real workbook wrapped in a thin proxy recording every
sheet name passed to `__getitem__`, then imports the real, unmodified
`official_upload_template.xlsx` fixture through `import_ghfdb_template`.
Asserts `"data list"` was accessed (the tracking actually engaged) and
`"controlled vocabulary"` was not — proven by name, not by absence of a
crash.

Passed on first run, so probed per `craft-tdd`/D14: saved a pre-probe
copy of `formats.py`, added one line inside `create_dataset()` —
`wb["controlled vocabulary"]`, simulating a future change that starts
honouring the sheet — and re-ran. Restored the pre-probe copy and
confirmed a byte-clean diff before re-running the suite.

Verified:
- Probe (broken): `poetry run pytest
  "tests/test_ghfdb/test_importers.py::TestControlledVocabularyDecides::test_the_import_never_opens_the_controlled_vocabulary_sheet"
  -x -q` — 1 failed: `AssertionError: assert 'controlled vocabulary' not
  in ['data list', 'controlled vocabulary']` — the right reason.
- Restore: `diff` against the pre-probe copy of `formats.py` — no
  differences.
- Restored green: `poetry run pytest tests/test_ghfdb/test_importers.py
  -q` — 13 passed.
- Lint, scoped: `poetry run ruff check
  tests/test_ghfdb/test_importers.py project/ghfdb/resources/formats.py`
  and `poetry run ruff format --check` on the same two files — both
  clean; `ruff format` (not `--check`) applied one reformat to the new
  test's own body (blank-line spacing inside the nested class), reviewed
  before committing.

No decisions.md entry: FR-014 already states the rule; this proves it
holds, it does not resolve an ambiguity.

Next: full repo verify, then the completion report.

## 2026-09-11 — US-6 · T032/T033

Did: added `TestGHFDBTemplateRepeatImport` to `test_importers.py` — two
tests, both against rows with `ID`/`ID_parent` dropped entirely, matching
the real template's shape. The first imports one row twice unchanged and
asserts `HeatFlowSite`/`ParentHeatFlow`/`HeatFlow` counts are each 1
after both imports. The second imports the same row twice and asserts
the site, parent and child primary keys are identical across the two
imports, and that the child's `parent_id` still points at that same
parent — proving the coordinate fallback matched the existing records
rather than inserting a second set.

Both passed on first run, so probed per `craft-tdd`/D14: saved a
pre-probe copy of `parent.py`, changed `_get_or_create_site`'s
`existing_by_location` lookup to `if False and ...` so it can never find
a match, and re-ran. Restored the pre-probe copy and confirmed a
byte-clean diff before re-running the suite.

Verified:
- Probe (broken): `poetry run pytest
  tests/test_ghfdb/test_importers.py::TestGHFDBTemplateRepeatImport -x -q`
  — 1 failed: `ValidationError(['A HeatFlowSite already exists at
  coordinate pair (11.00000, 48.00000).'])` on the second import — the
  disabled lookup no longer finds the first import's site, so the second
  import tries to create a second one at the same coordinates and the
  model's own uniqueness constraint refuses it. The right mechanism,
  failing for the right reason.
- Restore: `diff` against the pre-probe copy of `parent.py` — no
  differences.
- Restored green: `poetry run pytest
  tests/test_ghfdb/test_importers.py::TestGHFDBTemplateRepeatImport -q`
  — 2 passed.
- Lint, scoped: `poetry run ruff check tests/test_ghfdb/test_importers.py`
  and `poetry run ruff format --check tests/test_ghfdb/test_importers.py`
  — both clean.

No decisions.md entry: T032/T033 needed no production change and no
ambiguity resolution — the acceptance criteria already held, exactly as
D14 anticipated.

Next: T034 — a file identical except for a changed `q_top`/`q_bottom`
must update the determination in place rather than duplicating it.

## 2026-09-11 — US-6 · T034

Did: added
`test_a_changed_depth_interval_updates_the_determination_in_place` to
`TestGHFDBTemplateRepeatImport`. Imports the no-ID/no-ID_parent row once,
then re-imports it with `q_top`/`q_bottom` changed, and asserts exactly
one `HeatFlow` exists afterward, that its primary key is the same one
the first import created, and that its interval carries the corrected
values — deliberately `q_top`/`q_bottom`, per DR-003/the brief, since a
test that changed `qc` instead would pass over the top of the defect.

Ran and watched it fail for the right reason before any production
change:
`AssertionError: assert 2 == 1` — the second import wrote a second
`HeatFlow` rather than updating the first, because `_child_natural_key`
(child.py) includes `q_top`/`q_bottom`, so changing either changes the
row's lookup key and `get_or_init_instance` no longer finds the existing
record.

Verified:
- Red: `poetry run pytest
  "tests/test_ghfdb/test_importers.py::TestGHFDBTemplateRepeatImport::test_a_changed_depth_interval_updates_the_determination_in_place"
  -x -q` — 1 failed, `assert 2 == 1`, confirming the reported defect.
- Lint, scoped: `poetry run ruff check tests/test_ghfdb/test_importers.py`
  — clean; `poetry run ruff format --check` flagged one line-wrap, applied
  with `ruff format` (no assertion or fixture changed) and reviewed
  before committing.

No decisions.md entry yet: T034 is the reproduction only. The match
strategy decision belongs to T035.

Next: T035 — make T034 pass by changing the child match strategy without
letting two genuinely distinct determinations at one site collide.
