# Reconciliation — 001 heat flow data model

`tasks.md` was written from `spec.md` as though the repository were empty. This file records what
walking that list against the code proved was already there.

**45 of 87 tasks are satisfied. 42 are open.**

A task counts as satisfied only where both a code citation and a passing test that covers it exist.
Code with no test does not close a task — the task stays open and the remaining work is the test.
The evidence for each satisfied task is in `feature-state.json`, which is what the implementation
work is dispatched from.

The original `tasks.md` recorded 67 of 67 complete. Those ticks were not consulted.

| Story | Satisfied | Open |
|---|---|---|
| US-1 — a complete record stores and reads back | 27 | 11 |
| US-2 — a site is its coordinates | 0 | 8 |
| US-3 — one parent per site | 7 | 3 |
| US-4 — marine instrument metadata | 6 | 1 |
| US-5 — every model served by the framework | 3 | 7 |
| US-6 — test data for every model | 2 | 4 |
| US-7 — a published column reaches its field | 0 | 8 |

## What that says about the feature

The models are genuinely built and genuinely tested. Twenty-seven of US-1's thirty-eight tasks are
satisfied, and the tests behind them are real: they assert on persisted values, reject wrong sample
types, and cover the deletion behaviours. This is not a feature that was claimed and not written.

The gaps are of three kinds, and they cluster rather than scatter.

**Whole stories nothing was ever written for.** US-2 and US-7 are at zero. Site identity was decided
in ADR-0006 after this feature was built and no specification ever carried it, so nothing enforces
it. The documentation was out of scope for the original specification, so the field map drifted
untested and the diagram never rendered.

**Behaviour built and never exercised.** Thirteen tasks describe something the code does, with no
test that would notice if it stopped. The pattern is that the primary path is tested and its
neighbours are not: several determinations sharing one gradient is tested, sharing one conductivity
is not. The child's link to its parent clearing on deletion is tested, the interval's
deletion cascading from its site is not. The correction type and status combinations are validated
and tested, the one-correction-per-type constraint beside them is not.

**Configuration that reads as deliberate and does nothing.** Two tasks are open because what exists
is wrong rather than missing, and this is the finding the audit turned up that nobody was looking
for. The registry configurations declare the commission's authority, its citation, keywords, a
repository link and a description for every model. None of it is read. Every model registers with
`authority=None` and `citation=None`, verified at runtime, because those attributes belong on a
metadata object the registry reads and are declared as bare class attributes instead. The tests
pass because they only ever asked whether a configuration exists and whether its field list is
non-empty — neither question can fail on a configuration that is silently ignored.

## Open tasks by reason

**Never built (25)** — T036, T038–T046, T051, T070, T074, T075, T078, T079, T081, T082–T089.

**Built, untested (13)** — T017, T018, T022, T023, T026, T029, T037, T054, T057, T059, T065, T069,
T072.

T037 deserves its own note: the migrations exist, and nothing anywhere applies them. The suite runs
with `--nomigrations`, and the one migration test checks only that no model change is unrecorded.
"Migrations apply cleanly to an empty database" has never been true or false in this repository,
because it has never been asked.

**Partially built (2)** — T056, the one-published-value-per-site guarantee, holds through the model
and is unproven through the import path. T080, factories, exist for seven of the eight models;
corrections have none.

**Built differently, and ruled wrong (2)** — T068 and T073, the registry metadata described above.

## Two tasks the design review reopened

The reconciliation closed both and was wrong about both, which is what the review exists to catch.

**T001** was closed citing `pyproject.toml:200` and, as its test, a directory rather than a test
node — the only such citation in the ledger. That configuration is the one setting `--nomigrations`,
so the evidence offered for "a test database that applies every migration" is the line that stops it
happening. Reopened, and its remaining work merged into T037.

**T005** was closed on a test asserting five of the fourteen fields FR-001 lists. "Every field is
persisted and reads back" was recorded as proven while eight fields would regress unnoticed.
Reopened, naming them.

Both are the same error: reading the evidence as confirming the task rather than asking what the
task claims and whether the evidence reaches it.

## Things this reconciliation deliberately did not open

The scoring interface on the models is not a task. It is unreachable and superseded by
`heat_flow/quality.py`, and both are a deferred interface belonging to the roadmap's quality items
rather than dead code. See `decisions.md`, D1.
