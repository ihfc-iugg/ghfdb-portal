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

**ADR:** pending S5 verdict.

## D2. The smallest size is four datasets

**Decision:** `--size` accepts 4 to 200.

**Why:** FR-013 asks for every assessment state in demo data, and there are four. A smaller run could
not hold them all. 200 datasets of 50 children is the 10,000 Sam set as the target for one run.

**ADR:** pending S5 verdict.

## D3. Development accounts follow the fleet's `example.com` shape

**Decision:** besides FairDM's `create_dev_accounts`, the command creates `regular.user`,
`staff.user`, `super.user`, `data-assessor.user` and `data-curator.user` at `example.com`, all with
the password `password`.

**Why:** these are the sign-ins every development server of Sam's uses, so nobody has to look them up.
FairDM's `fairdm.org` accounts are kept because the spec names them.

**ADR:** pending S5 verdict.

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
