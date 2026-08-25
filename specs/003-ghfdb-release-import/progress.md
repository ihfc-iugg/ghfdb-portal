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
