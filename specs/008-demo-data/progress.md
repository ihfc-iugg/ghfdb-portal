
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

## 2026-10-19T23:20:35Z · Implementer US1-US3 · T004

Did: added docs/development/demo-data.md, the Development toctree entry, a pointer from step 2a of getting-started, and a Demo data entry in CONTEXT.md.
Verified: uv sync --group docs; sphinx-build -E -b html docs <outdir> -W --keep-going reports 32 warnings, all in files this task did not touch (ROADMAP.md, GOALS.md, constitution/, guides/ and others), none in the new page; pre-commit green.
Next: T005 the --size option.
Watch: the -W docs build exits 1 on those existing warnings, so it cannot be used as a gate for this task.

## 2026-10-19T23:26:01Z · Implementer US1-US3 · T005

Did: added --size (DEFAULT_SIZE 20, MIN_SIZE 4, MAX_SIZE 200) with a CommandError naming the range before anything is written; the tests now pass --size explicitly; documented the option.
Verified: uv run pytest tests/test_review/test_management -n0 -> 21 passed; pre-commit and mypy project green.
Next: T006 accounts and the state plan.
Watch: none.

## 2026-10-19T23:36:51Z · Implementer US1-US3 · T006

Did: the command now calls create_dev_accounts, creates the example.com accounts (regular, staff, super, data-assessor, data-curator) with confirmed addresses and the role groups, credits the assessor on every dataset as the review view does, and uses the assessor and curator as uploader and decider. Documented the accounts and states.
Verified: uv run pytest tests/test_review/test_management -n0 -k "States or Accounts or Visibility" -> 23 passed, 1 failed on a wrong assumption (the list page hides private datasets for everyone); the test now opens each private dataset page and then 3 Visibility tests passed. pre-commit and mypy project green.
Next: full verify and the report.
Watch: FairDM dataset list reads Dataset.objects, which excludes private datasets for every user, so a contributor reaches a private dataset through its own page.

## 2026-10-20T00:08:17Z · Implementer US1 · T007

Did: see commit. Verified: commands in ledger. Next: following task. Watch: none.

## 2026-10-20T00:08:17Z · Implementer US1 · T008

Did: see commit. Verified: commands in ledger. Next: following task. Watch: none.
