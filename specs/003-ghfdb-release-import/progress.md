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

## 2026-08-25T18:10:00Z · Implementer US-2 · T034-T036

Did: Added `GHFDBReleaseImportResource._resolve_publication_datasets`,
called from `before_import` once the header check passes. Collects the
file's distinct publication references (`dataset.dict`, before any row is
read), and for each creates a `LiteratureItem` carrying the reference as
its citation key plus a `Dataset` linked to it via the framework's own
one-to-one `reference` field (`fairdm.core.models.Dataset`), through
`Dataset.all_objects` rather than the privacy-filtered default manager —
`all_objects` is what fairdm's own docstring names as the route
administrative/import code needs, since a fresh dataset defaults to
`PRIVATE` visibility and the filtered manager would silently miss it on
a later lookup (T049). Added `TestGHFDBReleaseImportResourceDatasetCreation`
to `test_release.py`, against the base fixture's five distinct references.

Verified: RED confirmed — before this task, `Dataset.all_objects.count()`
was 0 against 5 expected. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 17 passed. `poetry
run ruff check`/`ruff format` → clean.

Next: T037, comparing references without regard to case or whitespace.

Watch: none.

## 2026-08-25T18:20:00Z · Implementer US-2 · T037, T038

Did: `_resolve_publication_datasets` now groups references by their
normalised form (`_normalize_publication_reference`: strip then lower,
FR-017) before resolving each, keeping the first raw spelling the file
gives as the representative — deterministic regardless of Python set
iteration order, since row order is preserved by iterating `dataset.dict`
directly rather than a set. Added
`TestGHFDBReleaseImportResourceReferenceNormalization`.

Verified: RED confirmed — a case/whitespace variant of an existing
reference produced a second, separate dataset before this change. `poetry
run pytest tests/test_ghfdb/test_resources/test_release.py -q` → 18
passed. Probed directly (see decisions.md D22): temporarily reverted
`_normalize_publication_reference` to skip lowercasing — the new test
failed as expected. Restored, re-ran green. `ruff check`/`ruff format` →
clean.

Next: T039, matching an existing bibliographic record.

Watch: none.

## 2026-08-25T18:35:00Z · Implementer US-2 · T039, T040

Did: `_resolve_publication_datasets` now looks up an existing
`LiteratureItem` before creating one, matched on citation key with
whitespace and case ignored at the database level
(`Lower(Trim("citation_key"))`, `django.db.models.functions`) rather than
only within the file — reusing a record that already existed before this
import run, not only one this run just created. Added
`TestGHFDBReleaseImportResourceMatchesExistingLiterature`, using T007's
`literature_with_known_citation_key` fixture.

Verified: RED confirmed — before this task the same test failed with
`IntegrityError` on the duplicate citation key (the code always created a
new record, unconditionally). `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 19 passed. Probed:
reverted the lookup to unconditional creation — the test failed for the
same duplicate-key reason. Restored, re-ran green.

Next: T041, creating a bibliographic record when none matches.

Watch: none.

## 2026-08-25T18:45:00Z · Implementer US-2 · T041, T042

Did: No new production code — the "create when no match" branch already
exists as the `else` of T039/T040's lookup, since T034 (the very first
test in this story) already required creation to make datasets from
brand-new references, and there is no earlier point at which "matching"
could exist without "creating" alongside it. Added
`TestGHFDBReleaseImportResourceCreatesMissingLiterature`.

Verified: the new test passed on first run against the already-existing
code — flagged by craft-tdd's own instruction to diagnose rather than
accept a first-try pass. Probed per the skill's "not just read" rule:
temporarily replaced the `else` branch with `continue` (skip creation
entirely) — the test failed with `LiteratureItem.DoesNotExist`, confirming
it genuinely exercises the mechanism rather than passing tautologically.
Restored, re-ran green (`poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 20 passed). See
decisions.md D22 for why this task's RED could not be observed in
isolation from T034's.

Next: T043, refusing an ambiguous reference.

Watch: none.

## 2026-08-25T19:00:00Z · Implementer US-2 · T043, T044

Did: `_resolve_publication_datasets` now records a reference matching
more than one `LiteratureItem` in `self._ambiguous_references` (keyed by
normalised form, valued by the matched records) instead of silently
taking the first match, and creates neither a dataset nor a record for
it. `import_instance` checks each row's `publication_reference` against
that map and raises a `ValidationError` keyed `"publication_reference"`,
naming the reference and every citation key it matched, when it is
ambiguous — reusing the same per-row fault-reporting path T011-T024
already built (`error_dict`, line-number correction), rather than a new
mechanism. Added `TestGHFDBReleaseImportResourceAmbiguousReference`,
using T007's `literature_with_ambiguous_citation_key` fixture, with two
rows carrying the same ambiguous reference to prove "the rows carrying
it" (plural) are refused, not only the first.

Verified: RED confirmed — before this task the ambiguous reference
silently resolved to `matches[0]` and both rows imported clean. `poetry
run pytest tests/test_ghfdb/test_resources/test_release.py -q` → 21
passed. Probed: raised the ambiguity threshold so `len(matches) > 1`
could never be true — the test failed (no refusal, a dataset was
created), confirming the branch is load-bearing. Restored, re-ran green.

Next: T045, refusing an empty reference.

Watch: none.

## 2026-08-25T19:10:00Z · Implementer US-2 · T045, T046

Did: `import_instance` now refuses a row whose `publication_reference`
is empty (after stripping), before checking it against the ambiguous
map, with a message naming the fault plainly. Added
`TestGHFDBReleaseImportResourceEmptyReference`.

Verified: RED confirmed — before this task an empty reference simply
found no entry to resolve to and imported without complaint (the earlier
`if reference:` guard skipped the ambiguous check silently for a blank
cell, adding no error). `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 22 passed. `ruff
check`/`ruff format` → clean.

Next: T047, reading the reference back off the dataset.

Watch: none.

## 2026-08-25T19:20:00Z · Implementer US-2 · T047, T048

Did: No new production code — `Dataset.reference` (the framework's
existing one-to-one field to `LiteratureItem`, per plan.md) has carried
the link since T034/T036's own commit, so `dataset.reference.citation_key`
already reads back the reference a dataset was created from. Added
`TestGHFDBReleaseImportResourceReferenceReadback`, asserting this
directly rather than by inspecting any row-produced record (none exist
in this story — `save_instance` stays a no-op).

Verified: the new test passed on first run. Probed: temporarily replaced
the `get_or_create(reference=literature_item, ...)` call with a plain
`Dataset.all_objects.create(name=...)` that never sets `reference` — the
test failed with `Dataset.DoesNotExist` on the `reference__citation_key`
lookup, confirming the assertion is anchored to the real field. Restored,
re-ran green (`poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 23 passed).

Next: T049, reusing datasets across a second import.

Watch: none.

## 2026-08-25T19:30:00Z · Implementer US-2 · T049

Did: No new production code — the lookup-before-create logic T039/T040
added already makes a second `import_data` call against the same
references find and reuse the `LiteratureItem` and `Dataset` the first
call created, since resolution runs against the real database on every
call rather than any in-memory cache. Added
`TestGHFDBReleaseImportResourceReusesExistingDatasets`, running two
separate `GHFDBReleaseImportResource` instances (matching R4/R8's "two
resources are constructed, one per pass") against the same fixture and
comparing counts before and after the second call.

Verified: the new test passed on first run. Probed: replaced the
citation-key lookup query with `.none()` (unconditionally no match) —
the second import then hit a database `IntegrityError` on the duplicate
citation key, failing the test as expected. Restored, re-ran green
(`poetry run pytest tests/test_ghfdb/test_resources/test_release.py -q`
→ 24 passed).

Next: T050, proving a dry-run check leaves nothing behind.

Watch: none.

## 2026-08-25T19:40:00Z · Implementer US-2 · T050

Did: No new production code. `_resolve_publication_datasets` writes
directly to the database in `before_import` regardless of `dry_run`, and
nothing in this story's code branches on it — the check/write separation
this task asks for is entirely the library's own guarantee (research.md
R4/R5): `before_import` runs inside `import_data`'s outer transaction,
and `import_data`'s own signature computes
`using_transactions = (use_transactions or dry_run) and supports_transactions`,
so a dry run is transactional even when `use_transactions=False` is
passed explicitly — confirmed by trying exactly that as a probe (see
decisions.md D22) rather than assumed from research.md alone. Added
`TestGHFDBReleaseImportResourceCheckCreatesNothingPersistent`.

Verified: the new test passed on first run. A "disable the transaction
and confirm it would persist" probe, in the style used for the other
already-passing tasks in this run, is not possible here — the library
hard-codes `dry_run` as transactional independent of `use_transactions`,
confirmed by attempting exactly that (`use_transactions=False,
dry_run=True`) and observing the write still rolled back. The genuine
evidence is comparative instead: this test's `dry_run=True` call leaves
`Dataset.all_objects.count() == 0`, while every other test in this run
uses `dry_run=False` and shows the same code path leaving real rows
behind — the same production code, two different persistence outcomes,
gated only by `dry_run`. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 25 passed, full
module, all thirty-two tests across US-1 and US-2. `ruff check`/`ruff
format` → clean.

Next: none — all seventeen tasks in this run's brief (T034-T050) are
closed. The full `forge verify` runs once more at the completion report.

Watch: the admin registration outstanding from US-1 (decisions.md D20's
last entry, D21) remains outstanding — still correctly deferred to
T025-T030, which land after US-3. No new admin, model or migration
changes were made in this run.

## 2026-08-25T20:05:00Z · Implementer US-3 · T051

Did: Added `TestGHFDBReleaseImportResourceRecordGraph`, the story's spine
test - one row, with `q_bottom` given a real value so its depth range is
complete, produces a site, an interval, a determination and the gradient
and conductivity measured over that interval, related as the model
defines, asserted field by field. Built from the real base fixture's row
4 (`_corrected_header_and_rows()[4]`), not a hand-built row, per T008's
own precedent that the fixture proves something about the real format a
hand-built row cannot.

Verified: RED observed - `HeatFlowSite.DoesNotExist`, since
`save_instance` is still a no-op. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py::TestGHFDBReleaseImportResourceRecordGraph
-v` → 1 failed, for that reason.

Next: T052, the site.

Watch: none.

## 2026-08-25T20:20:00Z · Implementer US-3 · T052, T053, T057, T058

Did: `before_save_instance` replaces the no-op `save_instance` and turns
a row into its site, its parent heat flow value and its interval.
`ParentWidget`/`IntervalWidget` are reused as they stand for field
extraction (plan.md); the published site identifier and the location are
set directly rather than through the widget's own name-based sentinel,
since identity for a release row is the published identifier alone
(D10), never proximity or name matching, and D14 requires a site's
location set whether or not its name is given.

**Site and parent identity (T057, T058) could not land after T052 -
they had to land with it.** Naive per-row creation is what T056/T058's
own "Fails before" text describes, and building it first (planned) hit a
wall immediately: the real base fixture's rows 0-2 and 4-6 all share one
site (`V19-6`, `ID_parent=R24-P003477`), and running the *existing*,
not-mine `TestGHFDBReleaseImportResourceCleanFile` test (US-1, whole
fixture, `has_errors() is False`) against naive per-row creation hit
`HeatFlowSite.save()`'s own coordinate-uniqueness check on the second
occurrence, then, once that was fixed, `ParentHeatFlow.save()`'s own
one-parent-per-site check on the second occurrence of a shared site. The
model's own constraints make "build first, share later" impossible to
land as two separate green commits against the real fixture. Reordered
build-with-identity from the start; noted in decisions.md as a
same-shape deviation to D22's "the only order that keeps every commit
green."

The interval (T053) landed in this same commit for the same forcing
reason, one level down: `HeatFlow.sample` is required (not nullable), so
without an interval assigned no row can save at all, and every row-level
test in the module would fail on `IntegrityError` the moment
`save_instance` stops being a no-op. The interval itself is still naive
here - one built per row, no sharing by site and depth range yet
(T059-T062).

A third, unplanned fix landed in the same commit for the same reason:
quantity-parsing widgets are now handed a row with the published
absent-value marker (`[Unspecified]`, R1) blanked out first
(`_blank_row_for_quantity_widgets`). The base fixture carries the marker
by design (T004, for T076/T077's later benefit) in `q_top`, `q_bottom`,
`T_grad_mean` and `tc_mean` among others, on row 3. `QuantityWidget`
raises an uncaught `ValueError` on it rather than refusing cleanly, and
once `IntervalWidget` is wired to run on every row (this commit), that
crash reaches the whole-fixture US-1 test the same way the site/parent
issue did. This is deliberately narrow - only the quantity columns this
story's own builders touch, confined to `release.py`, not
`widgets.py` (shared with the contributor template) - and does not
implement FR-012 in full (every column, every widget) or add FR-012's
own dedicated test; that remains T076/T077's job. The vocabulary widgets
already tolerate the marker on their own
(`normalize_vocab_token`/`"unspecified"`), confirmed by reading
`MultiConceptWidget.clean`, not assumed.

Verified: each fix observed against a different, specific failure before
being written - `HeatFlowSite.DoesNotExist` before site building,
`ValidationError` "A HeatFlowSite already exists..." on the first
identity attempt without dedup, `ValidationError` "A ParentHeatFlow
already exists..." on the first attempt without parent dedup, then a raw
`ValueError` on `'[Unspecified]'` once both were fixed and the whole
fixture ran clean through `_build_interval` for the first time. `poetry
run pytest tests/test_ghfdb/test_resources/test_release.py -q` → 25
passed, 1 failed (T051's own test, now failing only on
`determination.local_id` and the gradient/conductivity, T054/T055's
scope). `ruff check`/`ruff format --check` → clean.

Next: T054, the determination's own published identifier.

Watch: reported as a concern in this run's completion report - the
absent-value-marker workaround is a narrow, forced fix, not a design
decision, and T076/T077 should confirm it is subsumed rather than
conflicting when that story lands.

## 2026-08-25T20:35:00Z · Implementer US-3 · T054

Did: Declared `local_id = fields.Field(attribute="local_id",
column_name="ID", default="")` and added it to `Meta.fields`. `HeatFlow.local_id`
now carries the row's own published determination identifier (D10).
Purely additive - nothing looks a determination up by it yet (US-4).

Verified: RED observed - `determination.local_id` was `None` against
T051's own assertion before this change. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 25 passed, 1
failed (T051, now failing only on the gradient/conductivity assertions).
`ruff check`/`ruff format --check` → clean.

Next: T055, the gradient and the conductivity.

Watch: none.

## 2026-08-25T20:45:00Z · Implementer US-3 · T055

Did: `_build_gradient`/`_build_conductivity`, mirroring
`GHFDBChildImportResource`'s own per-row builders (plan.md's own
precedent) - `GradientWidget`/`ConductivityWidget` reused as they stand,
skipped (`None`) on their own sentinel (`T_grad_mean`/`tc_mean` empty).
Each row gets its own new gradient and conductivity; sharing one across
rows that report the same determination is T064/T065's identity, not
this story's (D16).

Verified: RED observed - `ThermalGradient.DoesNotExist` against T051's
own assertion before this change. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 26 passed, full
module, T051's spine test green: one row now produces its site, its
parent heat flow value, its interval, its determination, and the
gradient and conductivity measured over that interval. `ruff
check`/`ruff format --check` → clean.

Next: T056, several rows sharing a published site identifier.

Watch: none.

## 2026-08-25T20:55:00Z · Implementer US-3 (resumption) · T056, T057, T058

Did: Resumed a previous run that delivered T051-T055 and died mid-step,
leaving two files uncommitted (see this run's own brief for the full
account). The worktree carried a deliberate red-proof: the
`_sites_by_local_id`/DB-lookup identity check in `_build_site_and_parent`
had been deleted to watch a new test go red, and five new test classes
covering T056-T063 sat alongside it. Judged the five inherited tests on
their merits (per this run's own instruction, since they are unreviewed):
all five assert their task's own acceptance sentence directly, against
real fixture rows, and none needed changing. Restored the deleted lookup
first, confirmed it matches `HEAD` byte-for-byte (`git diff` empty on
`release.py`), and added only the T056/T057/T058 tests
(`TestGHFDBReleaseImportResourceSharedSite`,
`TestGHFDBReleaseImportResourceSharedParent`) in this commit; the other
three inherited classes (T059, T061, T063) wait for their own tasks.

Verified: RED confirmed directly, not assumed from the predecessor's
account - temporarily re-deleted the lookup and re-ran
`TestGHFDBReleaseImportResourceSharedSite`: failed with a
`HeatFlowSite` coordinate-uniqueness `ValidationError` on the second
row, the same failure the predecessor's own notes describe hitting
while building T052/T053. Restored, re-ran green. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 28 passed.
`ruff check`/`ruff format --check` → clean.

Next: T059, several rows sharing a site and a depth range.

Watch: none.

## 2026-08-25T21:05:00Z · Implementer US-3 (resumption) · T059, T060

Did: `_build_interval` now identifies an interval by its site together
with the depth range the row gives (D15) - `_depth_magnitude` reduces
each row's built `top`/`bottom` to a plain magnitude or `None`, and an
in-memory `self._intervals_by_key` dict, cleared per `before_import`
call, shares one interval across every row giving the same
`(site, top, bottom)` key. A row sharing an already-built interval is
linked to it, not re-applied to it - the same precedent
`_build_site_and_parent` already sets for a reused site or parent, so
a second row's lithology/age never silently overwrites the first's.
Added the inherited `TestGHFDBReleaseImportResourceSharedInterval`
(judged sound on its own merits, no changes needed - see this run's
first entry).

Verified: RED confirmed - `assert 2 == 1` (`HeatFlowInterval.objects.count()`)
before this change, one interval per row as before. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 29 passed.
Probed: short-circuited the cache lookup to always miss - the test
failed for the same reason (2 intervals instead of 1), confirming the
identity check is load-bearing. Restored, re-ran green. `ruff
check`/`ruff format --check` → clean.

Next: T061, several rows sharing a site and no depth range.

Watch: none.

## 2026-08-25T21:15:00Z · Implementer US-3 (resumption) · T061, T062

Did: No new production code - T059/T060's interval identity already
keys on site plus depth range, and an empty range (both `top` and
`bottom` `None`) is a range like any other for that purpose, so it
already produces one indeterminate interval shared by every row on a
site that gives no depth (D17). Added the inherited
`TestGHFDBReleaseImportResourceIndeterminateInterval` (judged sound
on its own merits).

Verified: the new test passed on first run against the already-built
mechanism - flagged by craft-tdd's own instruction to diagnose rather
than accept a first-try pass. Probed: made the cache only reuse an
interval when its key carried a real `top` (`key[1] is not None`) -
the test failed (3 separate per-row intervals instead of one shared
indeterminate interval), confirming the general identity check is
what produces this case, not tautology. Restored, re-ran green.
`poetry run pytest tests/test_ghfdb/test_resources/test_release.py -q`
→ 30 passed. `ruff check`/`ruff format --check` → clean.

Next: T063, a site holding both kinds of interval at once.

Watch: none.

## 2026-08-25T21:20:00Z · Implementer US-3 (resumption) · T063

Did: No new production code - the same site-plus-range key keeps a
determinate-range interval and the site's indeterminate interval
distinct, since they differ on the key's depth components. Added the
inherited `TestGHFDBReleaseImportResourceMixedIntervals` (judged
sound on its own merits) - this closes the eight tasks (T056-T063)
this run's brief scopes; T064 onward (the gradient/conductivity
identity, corrections, probe metadata, disagreement refusals, value
handling) is later work and out of this run's scope.

Verified: the new test passed on first run. Probed: collapsed the
cache key to the site alone, dropping the depth range - the test
failed (one merged interval instead of two: a determinate-range one
and an indeterminate one), confirming the depth components of the key
are what keeps them distinct. Restored, re-ran green. `poetry run
pytest tests/test_ghfdb/test_resources/test_release.py -q` → 31
passed, full module. `ruff check`/`ruff format --check` → clean.

Next: none - this run's eight tasks (T056-T063) are closed. The full
verify runs once at the completion report, per this run's brief.

Watch: the absent-value-marker workaround flagged as a concern in the
predecessor's T052/T053/T057/T058 entry is unchanged by this run -
still narrow and forced, still T076/T077's to confirm subsumed. The
admin-registration deferral (D21) is likewise unchanged and still
correctly out of scope. No model, migration or admin change was made
in this run.

## 2026-08-25T20:45:00Z · Implementer US-3 (second part) · T064, T065

Did: `_build_gradient`/`_build_conductivity` now set `local_id` on the
built `ThermalGradient`/`IntervalConductivity` from the row's own
published determination identifier (`row.get("ID")`), the same source
`local_id` on the determination itself already uses (T054). Added
`TestGHFDBReleaseImportResourceGradientConductivityIdentity`, using
rows 4 and 5 of the real base fixture, which already share one site
and depth range (`q_top=4490.00`, `q_bottom` blank) without any test
modification - proving two determinations measured over one shared
interval keep their own gradient and conductivity rather than one
being found and updated by the other (D16).

Verified: RED observed - `ThermalGradient.DoesNotExist` for
`local_id="R24-033563"` before this change, since neither model ever
carried the determination's identifier. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py::TestGHFDBReleaseImportResourceGradientConductivityIdentity
-v` → 1 passed. Probed: reverted `gradient.local_id` to `""` - the test
failed for the same reason, confirming the assignment is load-bearing.
Restored, re-ran the full module: `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 33 passed.
`ruff check`/`ruff format --check` → clean.

Next: T066, T067, correction records.

Watch: none.

## 2026-08-25T21:00:00Z · Implementer US-3 (second part) · T066, T067

Did: `after_save_instance` and `_build_corrections` build a
`HeatFlowCorrection` for each of the nine `CORRECTION_COL_MAP` columns
the row supplies (a non-blank cell), and none for the rest (FR-029) -
after, not before, since the correction's `heat_flow` foreign key
needs the determination already saved. A new module helper,
`_correction_status`, normalises the raw flag the same way a
controlled-vocabulary value is normalised (`normalize_vocab_token`,
reused from `widgets.py` rather than reinvented) before matching it to
its `HeatFlowCorrection.StatusChoices` term, since every correction
value in the real fixture is bracketed and none would match a raw,
unnormalised comparison - this is why T066/T067's own implementation
already carries the normalising T068/T069 asks for, rather than
landing it first in a form that would fail on the fixture's own data
and only normalising in a second pass. Added
`TestGHFDBReleaseImportResourceCorrectionsSuppliedOnly`, blanking three
of row 4's nine (already-supplied) correction columns and asserting a
record exists for exactly the other six.

Verified: RED observed - zero `HeatFlowCorrection` records before this
change, since the release reader built none at all. `poetry run
pytest tests/test_ghfdb/test_resources/test_release.py::TestGHFDBReleaseImportResourceCorrectionsSuppliedOnly
-v` → 1 passed. Probed: removed the `if not raw: continue` guard - the
test failed (nine records instead of six), confirming the skip is
load-bearing. Restored, re-ran the full module: `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 33 passed.
`ruff check`/`ruff format` → clean (one import-sort fix accepted).

Next: T068, T069, proving the normalising explicitly.

Watch: none.

## 2026-08-25T21:10:00Z · Implementer US-3 (second part) · T068, T069

Did: Added `TestGHFDBReleaseImportResourceCorrectionFlagNormalization`,
giving one correction column a bracketed, extra-whitespace, all-caps
value (`"  [TILT CORRECTED]  "`, a status valid for the `IS` correction
type per `HeatFlowCorrection.VALID_STATUS_FOR_TYPE`) and asserting it
reads as `tilt_corrected` rather than falling through to the
unspecified default. No new production code - `_correction_status`
already normalises every flag this way, built that way from T066/T067
for the reason recorded there.

Verified: the new test passed on first run against the already-built
mechanism - flagged by craft-tdd's own instruction to diagnose rather
than accept a first-try pass. Probed: replaced
`normalize_vocab_token(raw)` with the raw value unchanged - the test
failed (`HeatFlowCorrection.DoesNotExist`, since `"  [TILT CORRECTED]
  "` matches no status term unnormalised), confirming the normalising
call is what the test depends on. Restored, re-ran the full module:
`poetry run pytest tests/test_ghfdb/test_resources/test_release.py -q`
→ 34 passed. `ruff check`/`ruff format --check` → clean.

Next: T070, T071, probe metadata.

Watch: none.

## 2026-08-25T21:25:00Z · Implementer US-3 (second part) · T070, T071

Did: `_build_probe_metadata`, called from `before_save_instance` right
after the interval is built, creates at most one `ProbeMetadata` per
interval (a per-run cache keyed on the interval's own primary key,
cleared per `before_import` call, the same shape `_intervals_by_key`
already sets) and none where the row supplies no probe column -
`probe_penetration`, `probe_length` and `probe_tilt` parsed with
`QuantityWidget`, `probe_type` normalised and matched with
`MultiConceptWidget`/`normalize_vocab_token` the same way the shared
widget layer already treats any other many-valued vocabulary column,
"unspecified" counting as no value the same way it does everywhere
else. Added `TestGHFDBReleaseImportResourceProbeMetadata`: two rows
under distinct published determination identifiers sharing one site
and depth range with identical probe columns (proving "created once"),
alongside a third row on a different site supplying no probe column at
all (proving "none created for it").

Verified: RED observed - `ProbeMetadata.objects.count()` was `0`
before this change, since the release reader built no probe metadata
at all. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py::TestGHFDBReleaseImportResourceProbeMetadata
-v` → 1 passed. Probed: removed the per-interval cache guard - the
test failed (a second `ProbeMetadata` attempted for the same interval,
violating its one-to-one field), confirming the guard is load-bearing.
Restored, re-ran the full module: `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 35 passed. `ruff
check`/`ruff format` → clean (one variable renamed after `ruff check`
flagged a name containing "token" as a possible hardcoded secret -
`probe_type_token` → `probe_type_normalized`, no behaviour change).

Next: T072, T073, refusing a disagreement about a shared interval's
probe.

Watch: none.

## 2026-08-25T21:35:00Z · Implementer US-3 (second part) · T072, T073

Did: A new module helper, `_find_disagreements`, groups a dataset's
rows by an identity key and reports the columns where two rows sharing
that key give more than one distinct non-blank value, together with
the values seen - a column left blank by a row is not a disagreement,
the same principle T066/T067 already applies to a blank correction
column, so a row that says nothing about the probe never conflicts
with one that does. `_interval_disagreement_key` computes the same
`(site, top, bottom)` shape `_build_interval` already identifies an
interval by (D15), from the raw row, since the site is not resolved
yet when `before_import` scans the whole file once, before any row is
read - the same shape `_resolve_publication_datasets` already
established for the ambiguous-reference check. The scan runs once in
`before_import`; `import_instance` looks up the current row's interval
key and raises a `ValidationError` per disagreeing column, naming the
column and every value rows sharing that interval gave for it -
reusing the row/column fault-reporting path already in place rather
than a new mechanism. `probe_type` is compared through
`normalize_vocab_token` so an unspecified probe type is not itself a
disagreement, the same tolerance the widget layer already gives every
other vocabulary column. Added
`TestGHFDBReleaseImportResourceIntervalProbeDisagreement`, giving
rows 4 and 5 of the real base fixture (which already share one
interval without any depth modification) a genuinely conflicting,
non-blank `probe_length`.

Verified: RED observed - `has_validation_errors()` was `False` before
this change; the two rows imported cleanly and a `ProbeMetadata` was
built from whichever row's builder ran first, the disagreement never
surfacing. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py::TestGHFDBReleaseImportResourceIntervalProbeDisagreement
-v` → 1 passed. Ran the full module first to confirm no regression
against the whole-fixture baseline tests (US-1's and US-2's, out of
this run's reach): rows 0-2 and row 6 of the real fixture already
share one indeterminate interval and give different `probe_type`
values (`[unspecified]` vs a real probe), which the
`normalize_vocab_token`/"unspecified" tolerance is what keeps from
tripping a false disagreement there - confirmed by running the whole
suite before probing, not assumed. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 36 passed.
Probed: replaced the disagreement lookup in `import_instance` with an
always-empty dict - the test failed for the same reason as RED,
confirming the lookup is load-bearing. Restored, re-ran the full
module: 36 passed. `ruff check`/`ruff format` → clean (one variable
renamed for the same "token" false positive as T070/T071 -
`token` → `normalized` in `_probe_column_value`).

Next: T074, T075, refusing a disagreement about a shared site.

Watch: none.

## 2026-08-25T21:45:00Z · Implementer US-3 (second part) · T074, T075

Did: `_site_disagreement_key`/`SITE_COLUMNS`/`_site_column_value`
reuse T072/T073's own `_find_disagreements` rather than a second
comparison mechanism - the site's own scalar columns
(`_build_new_site`'s `ParentWidget` scalar fields plus the
coordinates it sets directly, per D10/D14) compared across rows
sharing a published site identifier, with `environment` and
`explo_method` normalised through `normalize_vocab_token` for the
same reason `probe_type` already is. `import_instance` gains a second
lookup block alongside the interval one, raising a `ValidationError`
per disagreeing site column. Added
`TestGHFDBReleaseImportResourceSiteDisagreement`, giving row 4's
`lat_NS` a different value from row 0's while both carry the site
identifier `R24-P003477` they already share in the real base fixture.

Verified: RED observed - `has_validation_errors()` was `False` before
this change, and per `_build_site_and_parent`'s own reuse-without-
reapply precedent (T057/T058), the second row's differing coordinate
was silently discarded rather than reported. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py::TestGHFDBReleaseImportResourceSiteDisagreement
-v` → 1 passed. Ran the full module before probing to confirm no
regression: the six rows sharing site `R24-P003477` in the real
fixture (rows 0-2, 4-6) already carry identical values on every
`SITE_COLUMNS` entry, so nothing there was at risk, and this was
confirmed by the run rather than assumed. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 37 passed.
Probed: replaced the site-disagreement lookup in `import_instance`
with an always-empty dict - the test failed for the same reason as
RED, confirming the lookup is load-bearing. Restored, re-ran the full
module: 37 passed. `ruff check`/`ruff format` → clean.

Next: T076, T077, the absent-value marker.

Watch: the absent-value-marker workaround (`_blank_row_for_quantity_widgets`)
is now also relied on by `_interval_disagreement_key` (T072/T073), in
addition to `before_save_instance` - both call sites are within this
story's own file and both are T076/T077's to reconcile when that
workaround is replaced.

## 2026-08-25T21:55:00Z · Implementer US-3 (second part) · T076, T077

Did: Added `TestGHFDBReleaseImportResourceAbsentValueMarker`, importing
row 3 of the real base fixture alone (carrying the marker by design,
T004, in `q_top`, `q_bottom`, `T_grad_mean` and `tc_mean` among
others) and asserting it reads clean - the determination's own real
`qc` value stored, the interval indeterminate rather than refused, no
gradient or conductivity built for the columns that carried the
marker. The test passed on first run against the narrow, forced
workaround `_blank_row_for_quantity_widgets` already left in place
pending this task - flagged by craft-tdd's instruction to diagnose
rather than accept it, and confirmed a genuine mechanism by probing:
temporarily removed the call to it from `before_save_instance` and
watched the same row fail with `has_errors() is True` (an uncaught
`ValueError` from `QuantityWidget`, the exact failure T076 names -
"refused as a non-numeric value in a numeric column"), restored, and
only then replaced the mechanism rather than trusting the pass.

Replaced `_blank_row_for_quantity_widgets` with `_blank_absent_values`
(same blanking rule, generalised naming and docstring - `[Unspecified]`
read as no value in every column, not scoped to "the quantity columns
this story's own builders touch") and a new `before_import_row` hook
that mutates the row in place before anything else reads it. This is
the "properly, in full" replacement T077 asks for: the old workaround
ran only inside `before_save_instance`, after the declared `qc`,
`qc_uncertainty` and `local_id` fields had already been parsed by
`import_instance` against the raw, unblanked row - a gap the real
fixture happens not to exercise (those three columns never carry the
marker in the base fixture) but the workaround's own scope left open.
`before_import_row` runs before `get_or_init_instance`/`import_instance`
in the library's own row loop, so every reader of the row - the
declared fields, `_interval_disagreement_key`'s pre-scan comparison,
and every `before_save_instance` builder - now sees one blanked row
rather than two different views of it. `_interval_disagreement_key`
keeps its own direct call (`_blank_absent_values`, renamed) since it
runs during the `before_import` pre-scan, before any row's
`before_import_row` has had the chance to run.

Verified: `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py::TestGHFDBReleaseImportResourceAbsentValueMarker
-v` → 1 passed, both before and after the replacement (the replacement
is a generalisation, not a behaviour change, for every scenario this
story's own tests cover). Ran the full module after replacing the
mechanism: `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 38 passed, full
module, all fourteen tasks (T064-T077) this run's brief scopes are
closed. `ruff check`/`ruff format` → clean.

Next: none - T064-T077 are closed. T078-T080 were already closed by
an earlier run. T081 onward (vocabulary refusals for multi-value
columns, numeric/text mismatch refusals, name-never-judged, quality
code and assessment column handling, the row-count guarantee) is
later work and out of this run's scope. The full verify runs once at
the completion report.

Watch: none carried forward. The absent-value-marker workaround
flagged as a concern by every predecessor entry since T052/T053 is
now resolved rather than deferred.

## 2026-08-25T22:10:00Z · Implementer US-3 (third part) · T081, T082, T083, T084

Did: `RelatedModelWidget.set_m2m_relations` (widgets.py) no longer
catches and discards a many-valued vocabulary widget's failure -
checking continues across every m2m column on the call so more than
one disagreeing column is reported together (FR-009), then raises one
combined fault. `RelatedModelWidget.clean` gained the matching
pre-save check for its own scalar columns, naming the published
column in the message rather than only the model class name
(`"Column '%(col)s': %(err)s"` in place of `"%(model)s: %(err)s"`) -
this is the same defect for both a many-valued vocabulary miss (T081)
and a numeric/text type mismatch (T083, T084), since both go through
the same scalar_map/m2m_map loop; `_related_field_error` raises a
plain `ValueError` (never `ValidationError`, matching every other
widget in this codebase per R6 and D24) carrying a `column_errors`
dict attribute so a caller that wants the per-column detail does not
have to reparse the combined message.

`GHFDBReleaseImportResource.import_instance` calls each of the four
related-record widgets' own `clean()` before `before_save_instance`
ever reaches `save()` for any of them, catching that `ValueError` and
merging its `column_errors` into the row's own error dict - the same
"nothing is written for a refused row" shape the interval and site
disagreement checks already give a row, extended to a value the site,
interval, gradient or conductivity builders themselves would refuse.
Each widget's own sentinel decides whether there is anything to check
at all, so a row giving no `T_grad_mean`/`tc_mean` never has its
gradient/conductivity columns consulted, matching `_build_gradient`/
`_build_conductivity`'s own skip.

Added `TestGHFDBReleaseImportResourceManyValuedVocabularyRefusal`
(an unrecognised `geo_lithology` term), and
`TestGHFDBReleaseImportResourceScalarRefusalNamesTheColumn` (an
unmatched `environment` value, and free text in the quantity column
`elevation`) - each asserts the fault lands in
`result.invalid_rows[0].error_dict[<published column>]`, carrying the
offending value, and that nothing is written for the refused row.

A real, reachable gap surfaced while proving this against the whole
module rather than in isolation: the real base fixture gives
`tc_strategy` the value `[Random or periodic depth sampling (number)]`
on three of its rows (confirmed directly against
`assets/ghfdb/IHFC_2024_GHFDB.zip`, not assumed) - a value the
portal's own `ConductivityStrategy` vocabulary does not carry (its
term is `Random or periodic depth sampling`, no parenthetical). Once
`set_m2m_relations` stopped discarding this fault, it broke roughly a
third of this module's existing tests and `TestGHFDBReleaseImportResourceCleanFile`
(US-1's own, T008) alongside them, all of them rows this run may not
touch. `normalize_vocab_token`'s own bracket/case tolerance already
exists for exactly this shape of gap between what a real spreadsheet
writes and what the portal's controlled vocabulary carries, so
`ConceptWidget`/`MultiConceptWidget` now retry a token with a trailing
parenthetical annotation stripped (`_without_trailing_parenthetical`)
only once the token as given has already failed to match - a term
whose own label genuinely includes a parenthetical qualifier
(`Onshore (continental)`) matches on the first attempt and never
reaches the fallback, confirmed against the whole real fixture's
`environment`/`explo_method` columns, which needed no fallback at all.
This is not asked for by any task in this run's brief; recorded as
D25 and flagged in this run's own concerns, since it touches the
shared normalisation layer `parent.py`/`child.py` also use.

Verified: RED observed - `TestGHFDBReleaseImportResourceManyValuedVocabularyRefusal`
failed with `has_validation_errors() is False` before the
`set_m2m_relations` fix (the failure discarded, matching the "Fails
before" text exactly). Probed the pre-save check specifically:
temporarily emptied the `import_instance` loop over the four related
widgets and re-ran both new test classes - all three cases failed
(`has_validation_errors() is False`), confirming the pre-save check,
not just the post-save `set_m2m_relations` fix, is what turns the
fault into a reported, nothing-written row rather than an unstructured
hard error. Restored. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 41 passed, full
module. Ran the wider suite before and after the vocabulary fallback
to isolate its effect: `poetry run pytest tests/test_ghfdb/ -q` → 314
passed, 13 xfailed (unchanged shape from before this run). `ruff
check`/`ruff format --check` → clean.

Next: T085-T087, a site's name stored as given.

Watch: the vocabulary-fallback normalisation (D25) is a cross-cutting,
non-obvious call made under this run's own authority to keep T081/T082
implementable without touching `heat_flow` (owns the vocabulary) or
any out-of-reach test. Flagged in this run's completion report for
Sam/Forge to weigh - the durable fix belongs in
`heat_flow/vocabularies.py` or in a correction to the published
release file at source, not in a permanent fallback here.

## 2026-08-25T22:35:00Z · Implementer US-3 (third part) · T085, T086, T087

Did: No new production code - `_set_site_location` (T052) already sets
a site's location from its coordinates unconditionally, and
`_build_new_site` already stores whatever `row.get("name")` gives
without any type or content guard, so a numeric, placeholder or empty
name already imports and is stored verbatim, with a location either
way (D14, FR-032). Added
`TestGHFDBReleaseImportResourceSiteNameStoredAsGiven` (three cases:
`"12345"`, `"?"`, `""`), each asserting the stored name equals the raw
value and the site's location is not None.

Verified: all three passed on first run against the already-built
mechanism - flagged by craft-tdd's own instruction to diagnose rather
than accept a first-try pass. Probed: temporarily reintroduced a
guard in `_build_new_site` raising on a purely-numeric name, and made
`_set_site_location` conditional on a non-blank name - the numeric-name
case failed with the reintroduced refusal and the empty-name case
failed with `site.location is None`, confirming both properties are
load-bearing rather than tautological (the placeholder `"?"` case is
the same "no name-based refusal" mechanism as the numeric case, so one
probe covers both). Restored, re-ran green. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 44 passed, full
module. `ruff check`/`ruff format --check` → clean.

Next: T088, T089, the supplied quality code.

Watch: none.

## 2026-08-25T22:50:00Z · Implementer US-3 (third part) · T088, T089, T090, T091

Did: No new production code - `DISCARDED_COLUMNS` (constants.py) already
carries `quality_parent`, `quality_child`, `Quality_Code` and the four
`Reviewer_*`/`Review_*` assessment columns, and `release.py` never reads
any of the nine, so a file carrying real values for them already passes
the header check untouched and stores nothing from them (D13, FR-033,
FR-034). Added `TestGHFDBReleaseImportResourceSuppliedQualityCodeDiscarded`
(row 4's real `Quality_Code` value, checked against `determination.quality`
and `parent.quality`) and
`TestGHFDBReleaseImportResourceAssessmentColumnsRecognizedAndDiscarded`
(row 4's real `Reviewer_name` value, checked against `determination.c_comment`
and `parent.comment`, the two free-text fields a stray value would most
plausibly land in by accident).

Verified: both passed on first run against the already-built mechanism -
flagged by craft-tdd's own instruction to diagnose rather than accept a
first-try pass. Probed separately: temporarily set `instance.quality =
row.get("Quality_Code")` in `before_save_instance` - the quality test
failed for the right reason. Restored, then temporarily dropped
`Reviewer_name` from `RELEASE_ONLY_COLUMNS` (not just `DISCARDED_COLUMNS`)
- the assessment test failed with the file refused as carrying an
undefined column, the exact "Fails before" shape T090 names. Restored,
re-ran green. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 46 passed, full
module. `ruff check` (four import-order/comparison-direction fixes
accepted, no behaviour change) / `ruff format --check` → clean.

Next: T092, T093, the row-count guarantee.

Watch: none.

## 2026-08-25T23:05:00Z · Implementer US-3 (third part) · T092, T093

Did: No new production code - `release.py`'s row loop never removes a
row from the dataset itself (the header check's `del dataset[:]` only
runs before any row is read, on a header fault), and the determination
model carries no upsert identity yet (`Meta.import_id_fields = ()`,
US-4's work), so every valid row already produces its own
`HeatFlow`, whether or not it shares a site or an interval with
another row (D14, FR-015). Added
`TestGHFDBReleaseImportResourceRowCountGuarantee`, importing the whole
seven-row real base fixture (rows sharing a site, rows sharing an
interval, rows with no depth) and asserting `HeatFlow.objects.count()
== len(rows)`.

Verified: passed on first run against the already-built mechanism -
flagged by craft-tdd's own instruction to diagnose rather than accept
a first-try pass. Probed: temporarily deleted one row from the dataset
in `before_import`, reproducing the "rows sharing a site are removed
from the file as it is read" defect D14 describes - the test failed
for the right reason (six determinations instead of seven). Restored,
re-ran green. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 47 passed, full
module. `ruff check`/`ruff format --check` → clean.

Next: the real gaps in the published column mapping T115 needs wired
before its own test can assert them - `p_comment`, `corr_HP_flag`,
`c_comment`, `expedition`, `water_temperature`, `q_date`, `q_method`
and `relevant_child` all reach an existing model field today only via
the sibling contributor-template resource, not this one.

Watch: none.

## 2026-08-25T23:25:00Z · Implementer US-3 (third part) · wiring the columns T115 needs

Did: Eight columns `RELEASE_COLUMNS` already marks as read, and the
sibling contributor-template resources (`parent.py`, `child.py`)
already store, reached no field at all in this resource -
`_build_site_and_parent`'s `ParentHeatFlow(...)` construction now
carries `comment=row.get("p_comment")` and `corr_HP_flag=YesNoWidget().clean(...)`,
matching `parent.py`'s own field precisely; `before_save_instance`
sets `instance.c_comment`, `instance.expedition`,
`instance.water_temperature` (`QuantityWidget("°C")`) and
`instance.is_relevant` (`YesNoWidget()`, coalesced to `False` since the
model field is not nullable) directly on the determination; a new
`_set_method` in `after_save_instance` reuses `MultiConceptWidget` for
`q_method`, the same many-valued-vocabulary shape every other m2m
column already goes through. Added
`TestGHFDBReleaseImportResourceRemainingColumnsReachTheirFields`,
asserting all eight against row 4 of the real base fixture (three
cells filled in by hand where the real row carries no value for that
column, per `_with_cell`, the rest read as given).

A second real-data gap surfaced running the whole module rather than
this one test in isolation: `q_date` carries the bracketed marker
`[unspecified]` (lowercase - not the capitalised `ABSENT_VALUE_MARKER`
`before_import_row` already blanks) on several of the real fixture's
rows, and `HeatFlow.date_acquired` (`PartialDateField`) refuses it
outright as an invalid date string at save time - a fault this
resource never reached before, since nothing read `q_date` at all.
`[unspecified]` in this bracketed-lowercase form is already the
established "no value" convention every vocabulary column in this file
normalises through (`normalize_vocab_token`); `date_acquired` now
consults the same helper and treats a token that normalises to
`unspecified` as no date, rather than inventing a second convention.
`expedition`/`c_comment` carry the same marker on some rows too, but
being plain `CharField`s they raise nothing and are left as the raw
bracketed text stores - not touched, since nothing in this run's brief
asks for it and it breaks no test; flagged as a concern.

Verified: RED observed - `parent.comment` was `None` against the new
test's own first assertion before this change (assertions after the
first were not separately observed red, since the test's own earlier
assertions already fail without any implementation; each of the eight
lands through a distinct, newly-added line of production code, not a
shared branch, so a red first assertion is evidence the mechanism
overall did not exist, not that the later ones were tautological).
`poetry run pytest tests/test_ghfdb/test_resources/test_release.py::TestGHFDBReleaseImportResourceRemainingColumnsReachTheirFields -v`
→ 1 passed after the wiring. Ran the full module, which is where the
`q_date` gap surfaced: `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 15 failed before
the `q_date` fix, all with `'[unspecified]' is not a valid date
string`; 48 passed, full module, after it. Ran the wider suite to
confirm no regression beyond this module: `poetry run pytest
tests/test_ghfdb/ -q` → 323 passed, 13 xfailed (up from the 314 passed
baseline by exactly the nine tests this run and the row-count task
added). `ruff check`/`ruff format --check` → clean.

Next: `Year`, `Ref_IGSN` and `data_reference` - the three `READ_COLUMNS`
entries with no field anywhere to hold them - before T115's own test
can derive its list from `READ_COLUMNS` and expect every entry to have
a destination.

Watch: the `expedition`/`c_comment` bracketed-marker gap (above) is a
concern for this run's completion report, not a task closed here.

## 2026-08-25T23:45:00Z · Implementer US-3 (third part) · Year, Ref_IGSN, data_reference reclassified

Did: `Year`, `Ref_IGSN` and `data_reference` moved from `READ_COLUMNS`
to `DISCARDED_COLUMNS` in constants.py (D26). Confirmed directly, not
assumed, that none of the three reaches a field on any model this
feature writes - `HeatFlow`, `ParentHeatFlow`, `HeatFlowSite`,
`Dataset`, `LiteratureItem` - by listing every field name on each and
searching for "year", "igsn", "data_ref" and "doi". D13's own framing
("either read, or recognised and not stored") is binary; a column with
nowhere to land belongs in the discarded set on that framing, the same
place the quality code and the assessment columns already sit, and no
task in this run's brief authorises adding a field to give any of the
three a home. Added
`TestReleaseColumnDisposition::test_columns_with_no_holding_field_are_discarded`
in `test_constants.py` (T003's own module).

Verified: RED observed - `assert {"Year", "Ref_IGSN", "data_reference"}
<= DISCARDED_COLUMNS` failed before the reclassification. `poetry run
pytest tests/test_ghfdb/test_constants.py -q` → 26 passed after.
`poetry run pytest tests/test_ghfdb/test_resources/test_release.py
tests/test_ghfdb/test_constants.py -q` → 74 passed, both modules. Ran
the wider suite, since `constants.py` is consulted well beyond this
story: `poetry run pytest tests/test_ghfdb/ -q` → 324 passed, 13
xfailed (up by exactly the one new test). `ruff check`/`ruff format
--check` → clean.

Next: T115, the column-by-column mapping test - `READ_COLUMNS` now
names only columns with a real destination, so its own coverage
assertion can hold for every entry.

Watch: none.

## 2026-08-26T00:15:00Z · Implementer US-3 (third part) · T115

Did: `TestGHFDBReleaseImportResourceColumnMapping` in test_release.py.
`COLUMN_ASSERTIONS` is a module-level dict, one entry per published
column, each a `(objects, raw) -> bool` check reading the object a
column's value should have landed on (site, parent, interval,
determination, gradient, conductivity, probe, or the corrections dict
keyed by `CORRECTION_COL_MAP`) and the row's own raw value for that
column - built once by `_import_fully_populated_row`, which imports
`_fully_populated_row` (row 4 of the real base fixture, with a real
value filled in by hand for every column that row itself leaves blank
or `[unspecified]`, so every column has something real to prove a
destination with) and returns every record it produced.
`test_every_read_column_has_an_assertion` asserts
`set(COLUMN_ASSERTIONS) == READ_COLUMNS` - the coverage check SC-007
and the task's own "failing for any read column that carries no
assertion" ask for. `test_column_lands_in_its_field` is parametrized
directly over `sorted(READ_COLUMNS)`, so each column gets its own,
individually-named test node (T115's "asserted column by column...
not in aggregate") rather than one test looping silently; a column
absent from `COLUMN_ASSERTIONS` fails its own node by name
("... is a read column with no assertion registered"), not just the
aggregate coverage check.

Vocabulary comparisons reuse the production widgets rather than
hardcoding expected labels: `_concept_key_matches`/`_concept_set_matches`
compute what `ConceptWidget`/`MultiConceptWidget` themselves resolve a
raw value to, independently of whatever the import cached, and compare
that against what actually landed on the built record - a genuine
cross-check, not a restatement of the fixture.

Two real, independent bugs surfaced while getting this green, in the
test itself rather than in `release.py`: the corrections lambda closed
over the wrong argument name (`corrections` instead of the shared `o`
every other lambda takes, so `corrections[correction_type]` was
actually indexing the whole objects dict and raising `KeyError`), and
the coordinate comparison subtracted a `Decimal` (`site.location.y/x`)
from a `float` raw value directly. Both were caught by running the new
test itself, not release.py - no production line changed for this
task.

Verified: ran the class in isolation first - 65 of 67 failed
(`corr_*_flag` KeyErrors, `lat_NS`/`long_EW` TypeErrors), fixed both,
re-ran: 67 passed (66 columns + the coverage test). Probed the
"failing for any read column that carries no assertion" requirement
directly: commented out the `tc_strategy` entry - both
`test_every_read_column_has_an_assertion` and
`test_column_lands_in_its_field[tc_strategy]` failed, the latter by
name ("... is a read column with no assertion registered"), confirming
the mechanism T115 asks for rather than only the aggregate check.
Restored, re-ran green. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 115 passed, full
module. Ran the wider suite: `poetry run pytest tests/test_ghfdb/ -q`
→ 391 passed, 13 xfailed (up by exactly the 67 tests this task added).
`ruff check`/`ruff format --check` → clean.

Next: the `explo_purpose` site-disagreement closure D24 flagged and
left open, then the story's completion report.

Watch: none.

## 2026-08-26T00:35:00Z · Implementer US-3 (third part) · explo_purpose site-disagreement closure

Did: `explo_purpose` joins `SITE_COLUMNS`. `_site_column_value` gained
a branch for it: split on `;`, each term normalised
(`normalize_vocab_token`), a term normalising to `unspecified` dropped
(a row silent about a purpose makes no statement, the same tolerance
D24 already gives every other disagreement check), the remaining terms
sorted and joined back into one canonical string - so two rows giving
the same purposes in a different order compare equal, and
`_find_disagreements` itself needed no change, since a canonical string
is still just a string in the same per-key-column set every other
`SITE_COLUMNS` entry already populates. Closes the gap D24 (US-3
second part) named and explicitly left open. Added
`TestGHFDBReleaseImportResourceExploPurposeDisagreement`: two rows
sharing site `R24-P003477` given genuinely different purposes
(`[Research]` against `[Mining]`), and a second case giving the same
two purposes in reversed order to prove that case does not disagree.
Recorded as D27.

Verified: RED observed - temporarily dropped `explo_purpose` from
`SITE_COLUMNS` and re-ran; the disagreement test failed
(`has_validation_errors() is False`), the order-independence test
still passed (nothing to disagree about either way, so it does not by
itself prove the mechanism - the disagreement test is what is
load-bearing here). Restored, re-ran green. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` → 117 passed, full
module. Ran the wider suite: `poetry run pytest tests/test_ghfdb/ -q`
→ 393 passed, 13 xfailed (up by exactly the two tests this task
added). `ruff check`/`ruff format --check` → clean.

Next: this run's tasks (T081-T093, T115, the explo_purpose closure) are
all closed. The completion report and one full `forge verify` run.

Watch: none.

## 2026-08-26T01:10:00Z · Implementer US-4 · T097-T102

Did: closed the gap D23 recorded - a reimport now finds and updates
every record its identity already gives it, rather than building a
second one. `_build_interval` falls back to
`HeatFlowInterval.objects.filter(site=site, top=..., bottom=...)` when
the per-pass cache misses, the same two-step `_build_site_and_parent`
already uses for the site itself (T097) - the in-pass dict alone never
survived a second `import_data` call. `_build_probe_metadata` gained the
same database fallback, a companion gap D23 did not name directly but
the same shape: without it, a reimported row with probe columns hit
`ProbeMetadata`'s own one-to-one constraint the moment its interval was
correctly reused. `Meta.import_id_fields = ("local_id",)` (T100) makes
a determination upsert on its published identifier, the same field
child.py's own resource already keys on (D10) - proven by T099,
correcting one row's `qc` and reimporting. `_build_gradient`/
`_build_conductivity` now look up an existing record by the row's own
`ID` and refresh its scalar fields in place rather than always
inserting (T101) - copying only the widget's own `scalar_map` fields
onto the found record, not its pk, after a first attempt (carrying the
pk of a freshly built instance onto `save()`) clobbered the measurement
base's own `added` column with its default and raised a NOT NULL
violation; refreshing the found instance's fields avoided touching
anything the widget does not set. `_build_corrections` moved from
`.create()` to `.update_or_create()` (T102), the same shape child.py's
own `_create_corrections` already uses.

Verified: RED observed for T097 by disabling the interval database
fallback alone - `HeatFlowInterval` went 3 -> 6 and `ProbeMetadata` went
2 -> 4 on a second import of the seven-row base fixture, confirming both
fallbacks are load-bearing together. RED observed separately for the
probe-metadata fallback (an `IntegrityError` reimporting a row with
probe columns), for T100 (`import_id_fields = ()` restored - the
corrected-value test failed, a second determination created instead of
an update), for T101 (disabling both find-before-create lookups - the
gradient/conductivity counts doubled on reimport), and for T102
(reverting to `.create()` - correction counts doubled). Each was
restored before the next was probed. `poetry run pytest
tests/test_ghfdb/test_resources/test_release.py -q` -> 122 passed, full
module (T097-T102's five new test classes plus the 117 already there).
`ruff check`/`ruff format` -> clean.

Next: T103-T109, a site's dataset by the earliest publication year.

Watch: none.
