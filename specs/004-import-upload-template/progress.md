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
