# Progress — 002-ghfdb-proxy

## 2026-08-23T23:40:00Z · Implementer foundations · T001

Did: Created `tests/test_ghfdb/test_columns.py` (empty module carrying the `ghfdb`
marker only — its test classes belong to the mapping tasks, out of this phase's
scope). Added `pytestmark = pytest.mark.ghfdb` to the three pre-existing modules
that lacked it: `test_models.py`, `test_managers.py`, `test_admin.py`. Left
`test_views.py` and `test_resources/` untouched, per the task's own carve-out.

Verified: Before, `poetry run pytest tests/test_ghfdb/test_columns.py --collect-only`
exited 4 with `ERROR: file or directory not found: tests/test_ghfdb/test_columns.py` —
the exact failure text T001 names. After creating the file, the same command exits 5
with `no tests collected` (file found, zero items — expected for a module whose tests
land in a later phase). `poetry run pytest tests/test_ghfdb/test_models.py
tests/test_ghfdb/test_managers.py tests/test_ghfdb/test_admin.py
tests/test_ghfdb/test_columns.py -q` → `23 passed, 1 xfailed`.

Next: T002, the autouse vocabulary-concept fixture's own contract test.

Watch: `test_columns.py` collects zero tests until the mapping-module tasks (T063+)
land test classes in it. That is expected, not a defect in this task.
