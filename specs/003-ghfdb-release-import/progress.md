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
