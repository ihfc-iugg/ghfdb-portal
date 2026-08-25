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
