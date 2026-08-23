# Implementation Plan — 002 the published structure read from the model

**Branch**: `002-ghfdb-proxy` · **Specification**: [spec.md](spec.md) ·
**Research**: [research.md](research.md) · **Reconciliation**: [reconciliation.md](reconciliation.md) ·
**Decisions**: [decisions.md](decisions.md)

## Context

This is an audit of a feature built in April 2026, not new construction. Both proxies, both
managers, all five queryset methods and both changelists exist and work. `reconciliation.md` records
the split: 6 of 121 tasks satisfied with a code citation and a passing test, 115 open.

The plan covers the 115. It does not rebuild what reconciled, and it does not rebuild working code
whose only fault is that nothing tests it.

**The split's shape is the plan's shape.** Forty-one of the open tasks have their production code
already written and cited — the work there is a test, and in a handful of cases a small correction
the test forces. Seventy-four are genuinely absent, and more than half of those are one structural
change and the fixtures that make the rest provable.

## Technical context

- Python 3.13, Django ≥ 5.0, the FairDM framework with `fairdm-geo` and `research_vocabs`.
- `django-import-export` 4.x for the resource attachment points. The resources themselves are
  `003-ghfdb-import-export`'s and are not touched.
- `pytest` with `pytest-django`, Ruff and mypy, Sphinx with MyST.
- SQLite in development, PostgreSQL in production.
- The `ghfdb` suite is 154 passing tests in 208 seconds, and the chain fixture dominates that. Suite
  runtime is the main cost this plan can accidentally multiply — see US-1 below.

## The one structural change

Everything in US-3 turns on a published-column mapping that does not exist in any form.

Today a published column name appears in four places: `constants.py`, each changelist's
`list_display`, and a literal copy inside the changelist's own test. Three of the names have already
drifted apart across those copies (D2), and the drift went unnoticed because the test compares one
copy against another rather than either against the canonical definitions.

The mapping is one entry per published column, naming which of R1's four groups it belongs to and
how its value is reached. A builder turns a canonical column list into display callables in that
list's order and refuses, at import time, a column the mapping does not hold. After it, the order is
never restated: the changelists ask for `CHILD_COLUMNS` and `PARENT_COLUMNS`, and a column added to
the canonical definitions and not to the mapping is a startup failure rather than a silently missing
column.

That refusal is what SC-007 means by a test that fails when the canonical definitions change and the
changelist does not, and T064 proves the gate against the defect rather than only against the
passing case.

**Deliberately not extended to the resources.** They declare the same names a third and fourth time
and would be served by the same mapping (R1). That is `003-ghfdb-import-export`'s work. The mapping
is written so it can be adopted there unchanged, and this run does not touch those files.

## Approach, by story

### US-1 — determinations read in the published shape (41 tasks, 1 closed)

Almost entirely test work. The annotation blocks, the export queryset and the correction subqueries
are written and correct; what is missing is any test that would notice if they stopped being.

Four things drive it:

- **Fixtures first.** The counted chain fixture, the unpublished chain, and the four partial chains.
  Nothing in the story can be proven without them, and their absence is why the existing tests
  assert `hasattr` rather than values.
- **Constancy measured at two row counts, through one helper.** R2 settles the shape: build *n*,
  count, build more, count again, assert the two counts are equal to each other rather than to a
  literal. The helper is itself gated — T010 requires it proven against a deliberately linear
  callable, because a helper that cannot fail is worse than no helper.
- **The complete row, not the annotated one.** R3 records that seventeen published child columns are
  many-valued and cannot be annotated, so SC-001 is proven after the export method rather than after
  the flattening one. A reader who takes SC-001 to mean the flattening method alone writes a test
  that cannot pass.
- **The `xfail` comes off.** `test_as_ghfdb_flat_scalar_columns` expects a prefixed elevation key.
  D6 rules the published name correct and the test wrong, so the assertion is corrected rather than
  the queryset. FR-011 states the rule the prefixes follow, so the collision list stops being an
  escape hatch: each name on it is checked to be a field the base class actually declares.

**Risk: suite runtime.** Every constancy test builds chains twice, and the chain fixture is the
expensive thing in this suite. The mitigation is in R2's decision — the correctness tests take the
cheap single chain, only the constancy tests take the counted one, and the counted one runs at two
and four rather than at two and two hundred. Four rows prove the same property as two hundred and
cost one hundred and ninety-six fewer.

### US-2 — sites read in the published shape (21 tasks, 1 closed)

The same shape, plus one method brought into use.

The parent flattening method has no caller. R5 records what stands in its place: fifteen display
methods on the site changelist that walk `sample → heatflowsite → field` per column, guarded by
nested `getattr` calls. It is not an N+1 — the changelist does `select_related` on those paths — but
it is the same data reached twice as expensively as it needs to be, in fifteen near-identical
methods, and it is why the flattening method is untested.

Wiring the changelist to read the flattening method deletes all fifteen, makes the method reachable
and testable, and makes both changelists the same shape, which is what lets one mapping serve both.
That wiring is US-3's task; US-2's is that the method annotates every published parent column and
does so at a constant query cost.

The counts need the four contribution shapes SC-004 names — all contributing, some, none, and a site
with no determinations at all. The existing test covers one site with one contributing
determination, which is the case least likely to be wrong. The distinction between a count of zero
and a null is its own assertion.

### US-3 — the assessment team reads the database in the terms they know (59 tasks, 4 closed)

The mapping and the builder come first, then both registrations are rebuilt on them.

After that the two changelists differ only in their column list, their lookup paths and the four
geography columns the site changelist adds. Six near-identical filter classes collapse to one taking
a vocabulary and a lookup path — six callers, which is what earns the generalisation. The read-only
guarantees stay written out on each class rather than shared through a base: two classes is not
enough to justify an abstraction whose only purpose is to avoid repeating three one-line methods.

Three findings in this story are defects rather than absences.

**The site changelist exposes an export it was specified not to have.** FR-021 gives the export
resource to the determination changelist and to nothing else. `GHFDBParentAdmin` inherits
`ImportExportMixin` and overrides only the import side, so the framework's default export path is
live on it with a generated resource — which would emit the site model's own fields, not the
published structure. The test that was meant to prove the requirement asserts the import classes and
stops, so it passes over the half that is wrong. The fix is to close the export path on that
registration, and T110 asserts exclusivity in both directions rather than in one.

**The search test cannot fail.** Both of its assertions are `status_code == 200`, and a search
matching nothing returns 200. Both changelists get a search test that asserts the row is found and
that a non-matching query returns none.

**Exploration purpose is unproven on the site changelist.** The filter class exists; nothing
exercises it. SC-009 requires each vocabulary filter proven on both changelists, and this is the one
gap in that grid.

**Risk: the column corrections are visible to users.** Three headings change — `tc_pT_fuction` to
`tc_pT_function`, `Ref_ISGN` to `Ref_IGSN`, and `quality` to `quality_child` and `quality_parent` —
and the last two columns of the determination changelist swap order. That is a deliberate,
adjudicated change (D2) and it is exactly the kind of change the people who read these changelists
notice. It belongs in the pull request's description in the terms they use, not only in a decision
record.

### Feature-wide (2 tasks)

`SC-011` is a statement about the suite, so it needs an assertion about the suite. Fourteen tests
under `tests/test_ghfdb/` are expected to fail. Thirteen belong to `003-ghfdb-import-export` and
stay, by D5. The fourteenth is this feature's and comes off. So the assertion covers this feature's
own modules and names the exclusion, rather than asserting across the package and being wrong about
what it owns. One conditional skip that can no longer fire comes out at the same time.

Documentation covers the query surface the feature presents: the two proxies, the scoping rule, the
five queryset methods and the two changelists.

## Sequencing

The fixtures block everything, and the mapping blocks US-3. Beyond that the three stories are
independent: US-1 and US-2 touch the queryset module, US-3 touches the admin, and only the site
changelist's queryset spans both.

1. **Fixtures** — T001 to T010. Blocking for all three stories.
2. **US-1 and US-2 in parallel** — different queryset classes, no shared edit.
3. **The mapping** — T063 to T077. Depends on nothing above, so it can run alongside step 2.
4. **Both changelists** — depends on the mapping, and the site changelist's queryset depends on
   US-2's flattening method being proven.
5. **Feature-wide** — last, because the suite-health assertion is only meaningful once the run's own
   `xfail` has come off.

## Convergence

- The full suite passes, run once, at the end. The expected count is 154 passing plus what this run
  adds, 13 expected-to-fail, and none of the 13 in this feature's own modules.
- Lint, formatting and type checks pass on every changed file, at CI's scope rather than the
  pre-commit gate's.
- `manage.py check` reports no errors and no warnings with both registrations live.
- Migrations squashed to one change set on the branch, applying cleanly to an empty database, with
  no operation that touches data.
- No column list, in code or in a test, is a copy of one `constants.py` already holds. This is the
  condition the whole run exists to establish, so it is checked at the end as well as asserted in
  the suite.
