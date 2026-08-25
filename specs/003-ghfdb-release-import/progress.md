# Progress — 003-ghfdb-release-import

## 2026-08-25T12:09:00Z · Implementer foundations · T001

Did: Created `tests/test_ghfdb/test_resources/test_release.py`, mirroring the
eventual `project/ghfdb/resources/release.py` (not yet created; lands in US-1,
T009). Carries `pytestmark = pytest.mark.ghfdb` and one test proving the
marker is genuinely applied at collection time, not just declared.

Verified: RED observed directly before creating the file — `poetry run pytest
tests/test_ghfdb/test_resources --collect-only -q` named nothing at this path
(confirmed empirically: a probe module with a docstring only and no test
function collects zero items under this repo's pytest config, `--collect-only`
included, so the module needed at least one real test to satisfy "collection
names it"). After: `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -v` → 1 passed.

Next: T002, the release format's column definitions.

Watch: none.

## 2026-08-25T12:20:00Z · Implementer foundations · T002

Did: Added `RELEASE_ONLY_COLUMNS`, `MISSPELLED_COLUMNS` and `RELEASE_COLUMNS` to
`project/ghfdb/constants.py`. `RELEASE_COLUMNS` is `PARENT_COLUMNS + CHILD_COLUMNS
+ RELEASE_ONLY_COLUMNS + list(MISSPELLED_COLUMNS)` — see decisions.md D19 for why
the misspelled names are folded in now, ahead of T003. Added `TestReleaseColumns`
to `test_release.py`.

Verified: RED confirmed — `git show HEAD:project/ghfdb/constants.py | grep -c
RELEASE_COLUMNS` → 0 before this commit. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -v` → 3 passed (T001's test plus
both new ones). `poetry run ruff check project/ghfdb/constants.py
tests/test_ghfdb/test_resources/test_release.py` → clean.

Next: T003, the read / recognised-and-discarded / refused split.

Watch: none.

## 2026-08-25T12:30:00Z · Implementer foundations · T003

Did: Added `DISCARDED_COLUMNS`, `REFUSED_COLUMNS` and `READ_COLUMNS` to
`project/ghfdb/constants.py` — three disjoint sets whose union is
`RELEASE_COLUMNS`. `REFUSED_COLUMNS` is the misspelled names; `DISCARDED_COLUMNS`
is the supplied quality code, the two legacy per-row quality names, and the four
assessment columns (see decisions.md D19 for why the legacy quality names are
included beyond FR-033's literal wording); `READ_COLUMNS` is everything else.
Added `TestReleaseColumnDisposition` to `test_release.py`.

Verified: RED confirmed by loading the T002 commit's constants.py in isolation
(`importlib` against `git show <T002 sha>:project/ghfdb/constants.py`) and
checking `hasattr` for all three names — all `False`. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 8 passed. `poetry run
ruff check project/ghfdb/constants.py tests/test_ghfdb/test_resources/test_release.py`
→ clean (ruff auto-fixed two yoda-condition findings in the new assertions,
re-verified green and re-linted clean after).

Next: T004, the base fixture cut from the published release archive.

Watch: none.

## 2026-08-25T12:45:00Z · Implementer foundations · T004

Did: Cut `tests/test_ghfdb/test_resources/fixtures/release/release_sample.csv`
byte-for-byte from `assets/ghfdb/IHFC_2024_GHFDB.zip` — the real header line
(both misspellings intact, see decisions.md D19 on why they stay for now), the
byte-order mark, and 7 real data rows, unzipped and located by scanning the
archive programmatically (not hand-picked) for a small set of rows satisfying
every shape T004 names in one place: 6 rows from site `R24-P003477` (rows
sharing a site; two, `R24-033563`/`R24-053075`, sharing a real interval and
agreeing on `probe_type`; three sharing the site's indeterminate no-depth
interval; four distinct publication references across the site) plus one row
from `R24-P004314` for a literal `[Unspecified]` cell, which no `R24-P003477`
row carries. Added `TestReleaseFixture` to `test_release.py`, one test per
shape T004's acceptance names plus the literal header-equality assertion.

Verified: the fixture file did not exist anywhere in this repository before
this task (confirmed: `git log --all --oneline -- 'tests/test_ghfdb/test_resources/fixtures/release/release_sample.csv'`
returns nothing before this commit). `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -v` → 15 passed. The header
match was also verified directly, independent of the test: extracted line 1 of
the archive's CSV member with `zipfile` + `readline()` in a throwaway script
and diffed it byte-for-byte against the fixture's first line before writing
the assertion. `poetry run ruff check tests/test_ghfdb/test_resources/test_release.py`
→ clean.

Next: T005, the fixture variants.

Watch: T004's fixture keeps both real misspellings in its header, so a reader
built against it directly (a later story, not this one) would refuse it per
D7 until a variant with both corrected exists — none of the Foundations
fixtures is "a clean file that passes," by design; that's what a later
story's own conftest will need to derive. Also: the fixture's line endings
are LF in the committed blob, not the archive's CRLF — the repository's own
pre-existing `.gitattributes` (`* text=auto`) normalises it on commit; see
decisions.md D19 for why this doesn't compromise "byte-for-byte."

## 2026-08-25T13:05:00Z · Implementer foundations · T005

Did: Added 8 fixture variants to `tests/test_ghfdb/test_resources/fixtures/release/`,
each derived from the T004 base by one deliberate change and verified
programmatically against it before being written: two isolate one misspelled
header at a time (`header_misspelled_only_ref_isgn.csv`,
`header_misspelled_only_tc_pt_fuction.csv`), one renames a column to an
unrecognised name (`header_undefined_column.csv`), one drops a required column
from the header line (`header_missing_required_column.csv`), and four change
one cell each (`bad_vocabulary_value.csv`, `numeric_value_in_text_column.csv`,
`disagreement_shared_site.csv`, `disagreement_shared_interval_probe.csv`).
Added `TestReleaseFixtureVariants` to `test_release.py`.

Verified: none of the 8 files existed anywhere in this repository before this
task. Each was diffed field-by-field against the base fixture with a
throwaway script before being written (row-keyed by `ID`, header-keyed by
name) to confirm exactly one field or header name differs — the same property
`test_single_row_variant_changes_exactly_one_cell` and the two header tests
now assert directly. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -v` → 23 passed. `poetry run
ruff check tests/test_ghfdb/test_resources/test_release.py` → clean.

Next: T007, the bibliographic fixtures (T006 is already closed).

Watch: none.

## 2026-08-25T13:15:00Z · Implementer foundations · T007

Did: Added `literature_with_known_citation_key` and
`literature_with_ambiguous_citation_key` fixtures to
`tests/test_ghfdb/test_resources/conftest.py`, built with
`LiteratureItemFactory` per tests/README.md (infrastructure, not the subject
under test). The ambiguous pair differs by case and a trailing space rather
than literally sharing a string — `LiteratureItem.citation_key` is unique at
the database level upstream, so two rows cannot hold the same string; see
decisions.md D19. Added `TestBibliographicFixtures` to `test_release.py`.

Verified: RED confirmed — `git diff HEAD -- tests/test_ghfdb/test_resources/conftest.py`
showed both fixtures as pure additions against the T005 commit, not present
before. `poetry run pytest tests/test_ghfdb/test_resources/test_release.py -v`
→ 25 passed (full module, all six tasks). `poetry run ruff check
tests/test_ghfdb/test_resources/test_release.py
tests/test_ghfdb/test_resources/conftest.py` → clean.

Next: none — Phase 1 Foundations (T001-T005, T007) is complete. T006 was
already closed before this run. The full `forge verify` runs once more at the
completion report, per the brief's rituals.

Watch: none.

## 2026-08-25T13:40:00Z · Implementer foundations · restructuring

Did: The mandatory full `forge verify` (§5) found what the narrow per-task
scopes could not: `forge verify --steps conformance` failed — "mirrors no
source module (expected .../project/ghfdb/resources/release.py)" —
because `tests/test_ghfdb/test_resources/test_release.py` mirrored a resource
module this phase correctly never creates (US-1's T009). Moved every class
unchanged into a new `tests/test_ghfdb/test_constants.py`, which mirrors the
existing `project/ghfdb/constants.py` that every constant this phase adds
actually lives in; deleted the old file. Moved T007's two fixtures from
`tests/test_ghfdb/test_resources/conftest.py` up to `tests/test_ghfdb/conftest.py`
so a test at the new location can still see them; reverted
`test_resources/conftest.py` to its pre-T007 state. See decisions.md D19's
final entry.

Verified: `poetry run pytest tests/test_ghfdb/test_constants.py -v` → 25
passed, same 25 tests as before the move. `forge verify --repo . --steps
conformance` → passed (0s), where it previously failed. Caught and reverted
one piece of collateral damage from this fix itself: `ruff check --fix` (run
manually, not the actual gate — `.pre-commit-config.yaml` excludes `tests/`
entirely, so this was extra caution) reordered import statements inside two
pre-existing functions in `tests/test_ghfdb/conftest.py`
(`load_concepts`, `sites_by_contribution`) that this task never touched;
reverted those two hunks by hand and kept only the intended diff (one changed
import line, two new fixtures at the end) — `git diff` confirms clean scope.
`poetry run pytest tests/test_ghfdb/test_constants.py
tests/test_ghfdb/test_resources/ -q` re-run in full to confirm the untouched
`test_resources/` suite (conftest.py reverted) is unaffected.

Next: none.

Watch: T009 (US-1) should reconsider whether the constants-only tests
gathered here belong beside the resource module once it exists — see
decisions.md's "Revisit if" on this entry.

## 2026-08-25T15:20:00Z · Implementer US-1 first part · T008, T009

Did: Created `project/ghfdb/resources/release.py` — `GHFDBReleaseCSVFormat`
(a comma-separated reader with a curator-facing title, "GHFDB Release
Format") and `GHFDBReleaseImportResource` (targets `HeatFlow`, two fields
wired for now — `qc`/`qc_uncertainty` via the existing `QuantityWidget`,
reused from `GHFDBChildImportResource`). Created
`tests/test_ghfdb/test_resources/test_release.py`, mirroring the new
module. Exported both classes from `project/ghfdb/resources/__init__.py`.

Verified: RED confirmed — `ModuleNotFoundError: No module named
'project.ghfdb.resources.release'` before the module existed. GREEN after:
`poetry run pytest tests/test_ghfdb/test_resources/test_release.py -v` → 3
passed. Discovered along the way and fixed before committing: the base
`CSV` format's `create_dataset` looks up tablib's format registry by
`get_title()`, so overriding it for a curator-facing name breaks dataset
creation (`UnsupportedFormat`) — see decisions.md D20. `poetry run ruff
check`/`ruff format --check` on both new files → clean.

Next: T011, the misspelled-column check.

Watch: none.

## 2026-08-25T15:35:00Z · Implementer US-1 first part · T011, T012

Did: `before_import` on `GHFDBReleaseImportResource` checks the file's
header against `MISSPELLED_COLUMNS`, `RELEASE_COLUMNS` and
`REQUIRED_COLUMNS` (all three checks — misspelled, undefined, missing —
landed together, since they share one pass over the header and one
collected-faults-then-raise-once shape; T013-T016 close on the same code,
proven by their own tests). Faults are collected into a list and raised as
one `ValueError` naming every one, so a file carrying more than one fault
reports all of them, not just the first the loop happens to reach. Added
`TestGHFDBReleaseImportResourceMisspelledColumns` — three tests: each of
the two misspelled names in isolation, and the published release header
(both misspellings together, D7) — plus one asserting no `HeatFlow` record
exists afterwards.

Verified: `poetry run pytest tests/test_ghfdb/test_resources/test_release.py -q`
→ 6 passed. Probed, not just read: temporarily mutated `misspelled_present`
to always be empty and re-ran the three misspelled-column tests — all
three failed for the expected reason (no fault reported), confirming they
exercise the real mechanism; reverted and re-ran green.

Next: T013, the undefined-column check.

Watch: none.

## 2026-08-25T15:45:00Z · Implementer US-1 first part · T013-T016

Did: Added `TestGHFDBReleaseImportResourceUndefinedColumn` and
`TestGHFDBReleaseImportResourceMissingColumn`, exercising the undefined-
and missing-column branches of the same `before_import` check T011/T012
already implemented. `header_missing_required_column.csv` (T005) drops
only the header cell for `environment`, leaving every data row one column
wider than the new header — reading it through
`tablib.Dataset(headers=...).append(...)`, or through the unmodified base
`CSVFormat.import_set`, raises `tablib.exceptions.InvalidDimensions`
before the resource is ever reached. Reworked `GHFDBReleaseCSVFormat.
create_dataset` to tolerate a row wider than the header (truncating the
excess), matching the padding tolerance the library's own reader already
applies to a row that is too short. See decisions.md D20.

Verified: `poetry run pytest tests/test_ghfdb/test_resources/test_release.py -q`
→ 8 passed. Probed: mutated `undefined`/`missing` to always resolve empty
— both new tests failed for the expected reason; reverted, re-ran green.

Next: T017, proving a header refusal stops the row loop.

Watch: none.

## 2026-08-25T15:55:00Z · Implementer US-1 first part · T017, T018

Did: Added `TestGHFDBReleaseImportResourceHeaderFailureStopsTheRowLoop` —
a dataset carrying both a header fault (a required column dropped) and a
row-level fault that would itself raise if read (`qc` set to a
non-numeric value). Asserts `result.invalid_rows == []` and `result.
error_rows == []` alongside the header-level `base_errors` entry,
proving the row was never reached rather than merely that it produced no
*additional* error. No new production code — `before_import`'s existing
`del dataset[:]` (landed with T011/T012) is what stops the row loop (R3).

Verified: `poetry run pytest tests/test_ghfdb/test_resources/test_release.py -q`
→ 9 passed. Probed: temporarily removed `del dataset[:]` from
`before_import`, keeping only the `raise` — the new test failed (the
"row that would itself have raised" was in fact read and reported),
confirming the assertion is anchored to the emptying, not the raise
alone; reverted, re-ran green.

Next: T019, every fault reported across several rows.

Watch: none.

## 2026-08-25T16:05:00Z · Implementer US-1 first part · T019-T024

Did: Added four test classes exercising properties the library already
provides by default or that landed incidentally with earlier tasks, each
closed here with its own test per the brief: `TestGHFDBReleaseImportResourceReportsEveryFault`
(two distinct faulty rows both surface — FR-009, already exhaustive in
the library's own row loop, per plan.md), `TestGHFDBReleaseImportResourceLineNumber`
(a fault in the first vs. third data row reports as file line 2 / 4 —
the `import_data` override from T009's own commit), `TestGHFDBReleaseImportResourceColumnName`
(a fault is keyed by `qc`/`qc_uncertainty`, never `value`/`uncertainty` —
the `import_instance` override, also already in place), and
`TestGHFDBReleaseImportResourceValueAndReason` (the offending value
appears in the message, and two different bad values produce two
different messages).

Verified: `poetry run pytest tests/test_ghfdb/test_resources/test_release.py -q`
→ 16 passed (full module). Probed the two corrections directly: reverting
`import_data`'s `+= 1` adjustment failed both line-number tests as
expected; reverting `import_instance`'s `field.column_name` back to
`field.attribute` failed both column-name tests as expected. Both
reverted, re-ran green. `poetry run ruff check`/`ruff format --check` →
clean.

Next: T033, the anonymous-request refusal.

Watch: decisions.md D20 records why `REQUIRED_COLUMNS`, `save_instance`
and `import_id_fields` are scoped the way they are, and flags the admin
registration plan.md describes as not done in this run.

## 2026-08-25T16:15:00Z · Implementer US-1 first part · T033

Did: Added `TestAnonymousRequestToTheImportRoute` to `tests/test_ghfdb/test_admin.py`
(mirrors `project/ghfdb/admin.py`, unchanged — T031/T032 already closed
the permission gate this task reuses). Two tests: an HTTP-level check that
an anonymous GET to the determination import route redirects to login
with `next` pointing at that exact URL, and a direct call to
`has_import_permission` with a `RequestFactory` request carrying
`AnonymousUser`, asserting it returns `False`. See decisions.md D20 for
why the second test is the one that actually proves T033's "distinguishably" —
every unauthenticated admin URL redirects to login identically, so the
HTTP-level test alone cannot tell a genuinely permission-gated route from
one with no check at all.

Verified: `poetry run pytest tests/test_ghfdb/test_admin.py -q` → 43
passed (full module, all pre-existing tests included). Probed: temporarily
hard-coded `GHFDBChildAdmin.has_import_permission` to always return `True`
— the direct-call test failed as expected; the HTTP-redirect test stayed
green under the same mutation, confirming empirically that it alone would
not have caught a broken permission gate. Reverted, re-ran green.

Next: none — all seventeen tasks in this run's brief are closed. The full
`forge verify` runs once more at the completion report.

Watch: the admin registration plan.md describes for the release format
and resource (attaching them to `GHFDBChildAdmin`'s existing import
machinery) was not done in this run — see decisions.md D20's last entry.
Three pre-existing tests not authored in this story assert
`get_import_resource_classes`/`get_import_formats` by exact equality
against today's state, and this story's own prohibition is against
modifying a test it did not author. Flagged as a concern in the
completion report rather than resolved here.
