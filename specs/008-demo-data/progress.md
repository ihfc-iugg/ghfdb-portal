
## 2026-10-19T23:11:22Z · Implementer US1-US3 · T002

Did: added project/heat_flow/demo.py (Region, REGIONS, SITES_PER_DATASET, CHILDREN_CYCLE, DemoGraph) and tests/test_heat_flow/test_demo.py.
Verified: uv run pytest tests/test_heat_flow/test_demo.py -n0 -> 56 passed; pre-commit on both files and mypy project green.
Next: T003 the seed_demo_data command.
Watch: temperatures omitted (D7); IntervalConductivity.clean() raises on stored records (D8).
