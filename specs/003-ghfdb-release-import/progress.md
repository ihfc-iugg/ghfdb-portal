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
