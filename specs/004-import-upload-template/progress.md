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
