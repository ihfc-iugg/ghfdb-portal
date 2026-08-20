# Implementation Plan — 001 heat flow data model

**Branch**: `001-heat-flow-data-model` · **Specification**: [spec.md](spec.md) ·
**Research**: [research.md](research.md) · **Reconciliation**: [reconciliation.md](reconciliation.md)

## Context

This is an audit of a feature built in April 2026, not new construction. The models exist and are
largely tested. `reconciliation.md` records the split: 45 of 87 tasks satisfied with a code citation
and a passing test, 42 open. Two of those closures were reopened by the design review, which is
recorded there.

The plan covers the 42. It does not rebuild what reconciled.

## Technical context

- Python 3.13, Django ≥ 5.0, the FairDM framework with `fairdm-geo` and `research_vocabs`.
- SQLite in development, PostgreSQL in production. No constraint that only one of them can express.
- `pytest` with `pytest-django`, `factory_boy` for fixtures, Ruff and mypy, Sphinx with MyST for
  documentation.
- The suite runs `--nomigrations`, which is why one open task is that nothing applies the
  migrations.

## Approach, by story

### US-2 — a site is its coordinates (8 tasks, nothing built)

Enforce in `save()` and in `clean()`, per R1. `save()` is the guarantee and covers
`objects.create()` and the factories, neither of which calls `full_clean()`. `clean()` is what turns
a duplicate entered through the admin into a field error rather than a server error. The rule binds
only where a location is set, and never constrains a site against itself.

The `save()` half mirrors the parent's one-per-site guard in the same package. The `clean()` half
does not: that guard has none, and adding one would change behaviour this feature was not asked to
change. So the two rules are alike in their guarantee and differ in how the admin reports a breach,
and that asymmetry is deliberate rather than an oversight.

The import's two notions of site identity are reconciled in the same story: it resolves by borrowed
identifier when a row carries one and by coordinates otherwise, so the paths can disagree and the
first contradicts the rule.

**Risk**: the guard makes previously-accepted writes fail. There is no heat flow data in production,
so the cost of finding a violation is a test failure rather than a migration. The import tests are
the place a regression would surface, and the story requires one.

### US-5 — registration (7 open, two of them wrong rather than missing)

Move the authority, citation, keywords and repository link onto the `ModelMetadata` object the
registry reads, and delete the three attributes it ignores — taking care not to remove
`admin_list_display` or the class-level `description`, which look equally unfamiliar and are read. Verified at runtime that every model
currently registers with `authority=None` and `citation=None`.

Supply a component class only where the generated one will not serve, per constitution principle IX
— the opposite of what the approved specification asked for, and the reason for D8.

The test that would have caught this compares each configuration's declared attributes against
those the registry reads, so the class of defect is closed rather than the four instances of it.

### US-6 — test data (4 tasks)

Preload concepts for the `heat_flow` tests the way the extraction tests already do, then populate
vocabulary many-to-many fields through `post_generation` hooks. Per R2, the reason every such
declaration is commented out is that no concept rows exist in these tests, not that the factories
are wrong.

Factories stay one level deep. Multi-model graphs are assembled by fixtures.

### US-7 — documentation (8 tasks, nothing built)

Add the Mermaid renderer, rewrite the diagram against the current model, bring the field map current
and test it against the canonical column definitions, and delete the Graphviz toolchain the diagram
supersedes.

The rendering test asserts against built output, because the failure it guards against is a source
file that is valid and never rendered.

**Not touched**: the manuscript figure and its caption, which depict a junction table the code does
not have. That is a publication artefact rather than a stale copy of this diagram, and it is #147.

### US-1, US-3, US-4 — closing test gaps

Mostly tests for behaviour that exists. The pattern across all three is that a primary path is
tested and its neighbour is not: sharing a gradient is tested and sharing a conductivity is not,
the child's link clearing on deletion is tested and the interval cascading from its site is not.

Two are more than a test. The valid correction status combinations are enforced in code and
documented nowhere. And nothing applies the migrations to an empty database, which needs a test that
runs them rather than the existing check for unrecorded model changes.

## Constitution check

| Principle | How this plan stands |
|---|---|
| I — FAIR-first | Improved. Registering models currently credit nobody; the authority and citation start reaching the registry. |
| II — schema fidelity | Improved. The field map becomes checkable rather than aspirational, and its first proven staleness is already known. |
| III — FairDM-first | Improved, and the reason for D8: generated components are preferred over hand-written ones, reversing what the approved specification asked for. |
| VI — test-first | The whole shape of the work. Thirteen open tasks exist because behaviour was built without a test, and the reconciliation refused to close them on the code alone. |
| VII — documentation | US-7 exists for this. The field map obligation was already constitutional and unenforced. |
| IX — simplicity | Two ways: no component class where the framework generates one, and the Graphviz toolchain deleted rather than maintained beside its replacement. |
| X — WHDB mission | One site per coordinate pair is a stated hard requirement of the assessment team. |

**No entry in complexity tracking.** Nothing in this plan adds an abstraction, a dependency beyond
the Mermaid renderer, or an extension point. The two application-level guarantees are constrained
by the framework's polymorphic inheritance rather than chosen, and both are recorded in
`decisions.md`.

## Sequence

The test module split comes first, in the foundational phase. Four stories add tests to
`tests/test_heat_flow/test_models.py`, and in separate worktrees they would collide on it. The
constitution already requires the mirrored layout it moves to.

US-2 and US-5 next: both are behaviour changes rather than test additions, and both touch files the
other stories' tests read.

US-6 next, because vocabulary coverage in the factories is what several US-1 test gaps need.

US-1, US-3 and US-4 then close their test gaps.

US-7 last. The diagram has to describe the model as it finishes, not as it started.

## Out of scope

Everything `spec.md` lists, and in particular the scoring interface, which is deferred rather than
dead. The 14 quarantined extraction tests belong to #122 and are not touched.
