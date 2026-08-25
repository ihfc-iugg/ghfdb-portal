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
