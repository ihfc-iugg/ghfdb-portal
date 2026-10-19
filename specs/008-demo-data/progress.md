
## 2026-10-19T23:11:22Z · Implementer US1-US3 · T002

Did: added project/heat_flow/demo.py (Region, REGIONS, SITES_PER_DATASET, CHILDREN_CYCLE, DemoGraph) and tests/test_heat_flow/test_demo.py.
Verified: uv run pytest tests/test_heat_flow/test_demo.py -n0 -> 56 passed; pre-commit on both files and mypy project green.
Next: T003 the seed_demo_data command.
Watch: temperatures omitted (D7); IntervalConductivity.clean() raises on stored records (D8).

## 2026-10-19T23:18:55Z · Implementer US1-US3 · T003

Did: added the seed_demo_data command (refusal outside development, preload and licences, per-dataset transaction with deferred recalculation, literature, contributors, assessment, graph) and its tests.
Verified: uv run pytest tests/test_review/test_management -n0 -> 11 passed; pre-commit on the changed files and mypy project green.
Next: T004 documentation.
Watch: DEFAULT_SIZE is patched to 4 in the tests; accounts and the state plan wait for T006, so one demo user uploads and decides every assessment for now.
