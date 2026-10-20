# FS-008 decisions

Rationale too long to inline in the spec, and ambiguities resolved without asking.

## The FairDM pins move with this feature

When this feature was specified, `fairdm`, `fairdm-geo` and `fairdm-discussions` were pinned at
the head of their default branches. `fairdm-docs` was behind (`bead56e` against `847fee1`). The
build moves the `fairdm-docs` pin to the latest commit and re-checks every FairDM pin against its
default branch before it starts. It moves any pin that has fallen behind and confirms the
documentation build afterwards.

## Generated, not sampled

A sample of the published release would look more real, but it would bring the release's licence
and attribution with it. Its size would be capped at the release's size, and loading release rows
is the direction ADR-0010 closed. Generated data has none of those costs. FR-005 asks for
distributions that resemble the published database, which keeps it realistic.

## Size is counted in datasets

Sites, intervals and children vary too much per publication to make a good unit. A dataset is what
a person browses and what the assessment workflow acts on, so it is the number a developer can
reason about.

## D1. The command lives in `review`, the graph generator in `heat_flow`

**Decision:** `project/heat_flow/demo.py` builds the heat flow graph for a dataset, and
`project/review/management/commands/seed_demo_data.py` composes datasets, literature, assessments,
accounts and the graph.

**Why:** `heat_flow` owns the models it generates, and an assessment is the `review` app's. Putting
the command in `heat_flow` would make the core model app import the workflow app. The reverse,
`review` importing `heat_flow`, matches what an assessment is for. `ghfdb` stays out of it.

**ADR:** none — where one command lives; the app boundary it follows is already recorded in CONTEXT.md's standing constraints.

## D2. The smallest size is four datasets

**Decision:** `--size` accepts 4 to 200.

**Why:** FR-013 asks for every assessment state in demo data, and there are four. A smaller run could
not hold them all. 200 datasets of 50 children is the 10,000 Sam set as the target for one run.

**ADR:** none — a bound on one command's option, documented with the command.

## D3. Development accounts follow the fleet's `example.com` shape

**Decision:** besides FairDM's `create_dev_accounts`, the command creates `regular.user`,
`staff.user`, `super.user`, `data-assessor.user` and `data-curator.user` at `example.com`, all with
the password `password`.

**Why:** these are the sign-ins every development server of Sam's uses, so nobody has to look them up.
FairDM's `fairdm.org` accounts are kept because the spec names them.

**ADR:** none — local to the development accounts, documented on the demo data page.

## D4. An exported file is not re-imported in the tests

**Decision:** US1 scenario 2 ("every row passes the checks an import applies") is shown by
`full_clean()` on every multi-table record and by the correction-status check, not by exporting and
re-importing.

**Why:** the published-structure export is not the upload template. It lacks nine columns the import
requires and carries five it rejects, so a round trip cannot run. The instance checks are what the
import applies to each record.

**ADR:** none — a testing choice local to this feature.

## D5. "In bulk" covers the plain models

**Decision:** FR-015's "records MUST be written in bulk" is met by bulk-writing corrections, probe
metadata and the concept rows. Sites, intervals, parents, children, gradients and conductivities are
saved one at a time.

**Why:** those six are multi-table models, which Django cannot bulk-insert (research R1). To be
raised with Sam at the merge gate.

**ADR:** none — follows from Django's limits, recorded in research R1.

## D6. Demo accounts are not caught by the deploy check

**Decision:** documented, not built. The development docs say the demo accounts must be removed
before a copy of the database leaves development.

**Why:** FairDM's deploy check watches its own account lists, and `data-assessor.user` is not in
them. The command refuses to run outside development, so the accounts only reach production through
a copied database.

**ADR:** none — local to this feature.

## D7. The generator leaves temperatures and shut-in times that need an offset unit empty

**Decision:** `DemoGraph` sets no `surface_temperature`, `temperature_top` or `temperature_bottom`.
Shut-in time is set on borehole gradients only.

**Why:** a stored gradient holding a temperature in °C makes `full_clean()` raise `ValueError`
("Boolean value of PlainQuantity with offset unit is ambiguous") while Django validates the
gradient's check constraint, so US1 scenario 2 could not be shown. The quality scheme reads none of
these fields.

**Revisit if:** the framework's quantity fields handle offset units in constraint validation.

**ADR:** none — a limit of what this generator fills, local to this feature.

## D8. A stored conductivity is checked without `IntervalConductivity.clean()`

**Decision:** the generator's tests run `clean_fields`, `validate_constraints` and
`validate_unique` on conductivities, and assert the 0.1 to 50 range and the uncertainty rule directly.

**Why:** `IntervalConductivity.clean()` compares a pint quantity with a float and raises `ValueError`
on any record that has been saved and read back. The model is outside this story's scope, so the
defect is reported, not fixed.

**Revisit if:** `clean()` is fixed to compare magnitudes.

**ADR:** none — a testing workaround for an existing defect, reported separately.

## D9. The pin move was made without a dispatched implementer

**Decision:** T001, moving the `fairdm-docs` pin, was done by the orchestrator directly.

**Why:** a one-line change to `pyproject.toml` and a relock, with no design content.

**ADR:** none — a process note.

## D10. Demo assessments skip the file upload

**Decision:** demo assessments in every state carry no submitted file, and a described assessment's
dataset already holds heat flow records.

**Why:** the code review noted that the real workflow cannot reach those combinations. Demo data is
there to give every page and endpoint something to show, and an assessment's page reads its state,
not its files. Generating upload files would add a spreadsheet writer to the seed for no screen that
needs it.

**Revisit if:** a page or endpoint starts depending on an assessment's submitted files.

**ADR:** none — local to this feature.

## D11. Review findings left as they are

- An existing account whose names differ from the demo entry is reused unchanged rather than refused.
  The seed only adds groups to it, and a development database is the developer's own.
- The documented `DemoGraph` example labels records by dataset, so building twice into the same
  dataset repeats labels. The example builds once into a fresh dataset, which is the documented use.
- The demo assessor account is outside FairDM's deploy check, as D6 records.

**ADR:** none — local to this feature.
