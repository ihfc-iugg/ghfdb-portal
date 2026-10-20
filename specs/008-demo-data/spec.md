# Feature Specification: Demo data for development

**Feature Branch**: `008-demo-data`

**Created**: 2026-10-19

**Status**: Draft

**Goals**: G8, which puts the GHFDB structure in the API, and G10, the map viewer reading that
API. Both are built by people outside the portal who need data to build against.

**Roadmap**: none. No roadmap item covers development data.

**References**: ADR-0006 (a site is its coordinates), ADR-0010 (the release import direction ends),
FS-001, FS-005, FS-006, FS-007; [CONTEXT.md](../../CONTEXT.md); FairDM's development accounts
guide (`docs/portal-development/development_accounts.md` in FairDM)

**Intake**: https://github.com/ihfc-iugg/ghfdb-portal/issues/278

## Overview

A fresh development database is empty. Nothing appears on the map, the explore page or the dataset
lists, and every API endpoint returns an empty list. Anyone working on the portal has to make their
own records first, and so does anyone building something that reads the portal's API, like the map
viewer or a researcher's analysis scripts. Today that means using the admin or uploading a
spreadsheet. The project's `create_fixtures` and `savedemo` invoke tasks point at a command and a
compose file that no longer exist (#255).

This feature adds one command that fills a development database with **demo data**: generated
records shaped like real heat flow data, marked so nobody mistakes them for real ones. The
developer chooses how much they get, from a handful of datasets up to about 10,000 children in one
run, and can run it again to add more. The data covers every state a person
working on the portal needs to see, and it reads through the site and through both families of API
endpoints exactly as imported data would.

It is generated, not copied from a published release. The portal no longer loads releases
(ADR-0010), and generated data can be produced at any size, with no licence or attribution to carry
along.

## User Scenarios & Testing

### User Story 1 — A developer fills an empty database with demo data (Priority: P1)

A developer with a migrated, empty development database runs one command. When it finishes, the
database holds heat flow sites, depth intervals, parents and children, thermal gradients,
conductivities, corrections and probe metadata. These sit in datasets, each tied to its own
literature item and credited to contributors. The values fall in ranges a heat flow scientist would
recognise. Every record is valid by the same rules an import applies, and the portal has computed
every quality score.

**Why this priority**: this is the feature. Everything else adjusts how much data there is, or which
data.

**Independent Test**: run the command against an empty test database with a small size, then assert
the following:

- every heat flow model holds records
- every record passes model validation
- every child and parent carries a computed quality score
- every vocabulary-backed field holds a concept from its vocabulary

**Acceptance Scenarios**:

1. **Given** a migrated database with no data, **When** the developer runs the command with no
   options, **Then** it completes and the database holds records of every heat flow model at the
   default size.
2. **Given** demo data was loaded, **When** a GHFDB export of it is produced, **Then** every row
   passes the same checks an import of that file would apply.
3. **Given** demo data was loaded, **When** each site is inspected, **Then** it has its own
   coordinate pair and exactly one designated parent.
4. **Given** demo data was loaded, **When** the quality scores are read, **Then** each matches what
   the portal computes from that record's own data.
5. **Given** the controlled vocabularies have not been loaded, **When** the command runs, **Then**
   it loads them first and then proceeds.
6. **Given** the environment is production, **When** the command runs, **Then** it refuses and
   writes nothing.

---

### User Story 2 — A developer chooses how much data they get (Priority: P1)

A developer passes a size to the command. A small size gives a few datasets, enough to page through
a list by hand. A large one gives around 10,000 children, enough to see how a page, a filter or an
API endpoint behaves with a realistic amount of data. A developer who needs more runs the command
again, and each run adds to the demo data already there. One number sets the scale. Everything
else, from sites per dataset to children per parent, grows with it in realistic proportion.

**Why this priority**: a larger database is where slow queries and oversized responses show up.

**Independent Test**: run the command at two sizes and assert that the record counts scale with the
size and keep the same proportions between models.

**Acceptance Scenarios**:

1. **Given** an empty database, **When** the developer runs the command with a small size,
   **Then** the number of datasets matches that size.
2. **Given** demo data is already loaded, **When** the developer runs the command again, **Then**
   the new demo data is added beside the old, and every site still has its own coordinate pair.
3. **Given** a size of zero or a negative number, **When** the command runs, **Then** it refuses
   with a message naming the accepted range and writes nothing.

---

### User Story 3 — A developer sees the portal in every state (Priority: P2)

A developer signs in and finds the portal the way it looks in use, with every state present:

- public datasets anyone can see
- private datasets only their contributors can see
- assessments at each stage, from described through awaiting a decision and changes requested to
  complete
- contributors holding each role in the assessment workflow

The developer signs in as any of FairDM's development accounts and as the portal's Data Assessor
and Data Curator, and sees what each of those people sees.

**Why this priority**: most pages behave differently by state and by who is looking. A feature
tested only against public data, viewed by a superuser, has not been tested.

**Independent Test**: load demo data and assert that every assessment state, both visibilities and
every workflow role are present. Then assert that each development account can sign in.

**Acceptance Scenarios**:

1. **Given** demo data is loaded, **When** the datasets are counted by visibility, **Then** both
   public and private datasets exist.
2. **Given** demo data is loaded, **When** the assessments are counted by state, **Then** every
   state in the assessment workflow is present.
3. **Given** demo data is loaded, **When** the developer signs in as the development Data Curator,
   **Then** at least one assessment is waiting for their decision.
4. **Given** demo data is loaded, **When** an anonymous visitor lists datasets on the site or
   through the API, **Then** only public datasets appear.

---

### Edge Cases

- **A database already holding real data.** The command adds demo data beside it and never changes
  or deletes anything that is not demo data. Demo literature uses identifiers that cannot collide
  with a real publication.
- **Very large sizes.** Memory use stays bounded however large the size is. The command never holds
  the whole database in memory at once.
- **A size that does not divide evenly.** Proportions round, and the dataset count is exact.
- **Coordinates.** Every site gets a distinct coordinate pair, on land and at sea, in the
  proportions the real database has. No two demo sites share a coordinate pair, at any size or across repeated runs.
- **Quality scores.** The portal computes them after the records are written. Supplied quality is
  never generated.

## Requirements

### Functional Requirements

- **FR-001**: The portal MUST provide a management command that fills the configured database with
  demo data.
- **FR-002**: Demo data MUST include records of every model in the heat flow data model:
  - sites
  - depth intervals
  - parents
  - children
  - thermal gradients
  - interval conductivities
  - corrections
  - probe metadata
- **FR-003**: Demo data MUST be grouped into datasets, one per literature item, each with
  contributors credited.
- **FR-004**: Every demo record MUST pass the validation an import of the same data would apply.
- **FR-005**: Generated values MUST fall within the ranges the GHFDB documents for each field, and
  their distributions MUST resemble those of the published database.
- **FR-006**: Every vocabulary-backed field MUST hold concepts from its controlled vocabulary. The
  command MUST load the vocabularies first if they are absent.
- **FR-007**: Each demo site MUST have its own coordinate pair and exactly one designated parent.
- **FR-008**: Quality scores MUST be computed by the portal after the demo records are written, and
  never generated.
- **FR-009**: The command MUST accept a size that sets the number of datasets. The counts of every
  other model MUST scale from it in fixed proportions.
- **FR-010**: The command MUST refuse a size outside its documented range and write nothing.
- **FR-011**: Every demo record MUST be identifiable as demo data, and demo literature MUST use
  identifiers that cannot belong to a real publication.
- **FR-012**: The command MUST never change or delete a record that is not demo data.
- **FR-013**: Demo data MUST include public and private datasets, and assessments in every state of
  the assessment workflow.
- **FR-014**: Demo data MUST include contributors in every workflow role. FairDM's development
  accounts, plus a Data Assessor and a Data Curator account, MUST exist and be able to sign in.
- **FR-015**: Records MUST be written in bulk, and memory use MUST stay bounded as the size grows.
- **FR-016**: Running the command again MUST add demo data beside what earlier runs made, without
  colliding with it.
- **FR-017**: Demo data MUST include public projects, each holding several demo datasets, and
  demo datasets that belong to no project.

### Story mapping

| Story | Requirements |
|---|---|
| US-1 | FR-001 – FR-008, FR-011, FR-012 |
| US-2 | FR-009, FR-010, FR-015, FR-016 |
| US-3 | FR-013, FR-014, FR-017 |

### Key Entities

- **Demo data**: generated records shaped like real heat flow data, identifiable as generated, and
  never published as real. New term for CONTEXT.md.
- **Size**: the one number a developer sets, counted in datasets.

## Success Criteria

- **SC-001**: A developer with an empty, migrated database has browsable demo data after running one
  command with no options.
- **SC-002**: The largest documented size produces about 10,000 children in one run.
- **SC-003**: Running the command never changes the count of non-demo records.

## Clarifications

### Session 2026-10-19

- Q: Generated data or a sample of the published release? → A: Generated. The portal no longer
  loads releases (ADR-0010), generated data can be produced at any size, and nothing needs to carry
  the release's licence or attribution.
- Q: What does the size count? → A: Datasets, because one publication is one dataset and that is
  the unit a person browses. Every other count follows from it.
- Q: How large must the largest size be? → A: About 10,000 children in one run. A developer who
  needs more runs the command several times, and each run adds to the last. No run time is set.
- Q: Do the generic records belong in FairDM? → A: Not in this feature. It builds on FairDM's
  existing development-account commands and keeps its own generation in the portal. Whether
  FairDM should generate generic projects, datasets and contributors for every portal is a
  separate question.

## Assumptions

- The database has been migrated before the command runs. The command does not migrate.
- FairDM's development-account commands stay available at the pinned FairDM version.
