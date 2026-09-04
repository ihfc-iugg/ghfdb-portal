# Feature Specification: A published release read into the portal

**Feature Branch**: `003-ghfdb-release-import`

**Created**: 2026-04-15 (split from `002-ghfdb-proxy`)

**Rewritten**: 2026-08-24 — audited against the implementation, narrowed to the release import, and
rewritten in place. The adjudications behind every change are recorded in
[decisions.md](decisions.md).

**Status**: Draft

**Goals**: G2 — faithful translation between the published structure and the portal's own model ·
G3 — the complete database held as a collection of individual datasets, each mapped one-to-one to
its reviewed literature item

**Roadmap**: R3 · the capability R5 depends on

**References**: Fuchs et al. (2021); Fuchs et al. (2023); IHFC GHFDB v2024; [CONTEXT.md](../../CONTEXT.md);
constitution principles II, III, VI, IX; ADR-0003

**Depends on**: `002-ghfdb-proxy` — the published column definitions and the proxies that read them.

## Overview

A published release is distributed as one flat file: one row per determination, with the site's
columns repeated on every row belonging to it. The portal stores that same information as a
normalised graph of sites, the depth intervals within them, the gradient and conductivity measured
over each interval, and the determination that follows from the pair.

This feature reads such a file into that graph. It is the direction the portal has never had: the
published structure can already be read *out* of the model, but nothing can read a release *in*.

Two things make the reading more than a column mapping.

The first is that a release is not one dataset. It is the accumulated work of some sixteen hundred
publications, and the portal holds data as datasets that each trace to one reviewed publication.
So the file has to be taken apart along that seam as it is read, and each part attached to the
literature it came from.

The second is that a release is a scientific record, and a value the portal cannot interpret is
more likely to be a problem in the file than a problem in the reader. The import therefore checks
the whole file and writes nothing until every row of it passes, and reports what failed precisely
enough that a curator can correct the source and try again.

**Out of scope**: writing a release back out, the contributor upload template, any upload path
outside the administrative interface, and the assessment workflow. Each is named under
[Out of Scope](#out-of-scope) with the item that owns it.

## User Scenarios & Testing

### User Story 1 — A release file is checked in full before anything is written (Priority: P1)

A curator has a release file and needs to know whether the portal can read it. They start an
import and are shown what the portal made of the file, before a single record is created. If
anything failed, they are told which row and which column, what the value was, and why it was
refused — enough to correct the file and start again.

**Why this priority**: nothing else in this feature can be trusted without it. An import that
writes as it reads leaves a half-populated database that nobody can distinguish from a complete
one, and a rejection reported without its row and column cannot be acted on. This story is also
the one that makes the rest safe to develop, because it is what turns a bad file into a report
rather than into data.

**Independent Test**: give the importer a file with known faults in known cells and confirm that
every fault is reported with its row, column, value and reason, and that the database is unchanged
afterwards.

**Acceptance Scenarios**:

1. **Given** a file whose column names are all recognised, **When** the import is started, **Then**
   the column check passes and the values are read.
2. **Given** a file carrying a misspelled published column name, **When** the import is started,
   **Then** it is refused before any data row is read, and the error names the misspelled name, the
   correct name, and the fact that the file follows an outdated template.
3. **Given** a file carrying a column name the release format does not define, **When** the import
   is started, **Then** it is refused before any data row is read and the error names that column.
4. **Given** a file missing a column the release format requires, **When** the import is started,
   **Then** it is refused before any data row is read and the error names the missing column.
5. **Given** a file with faults in several different rows, **When** the values are checked, **Then**
   checking continues past the first fault and every fault in the file is reported together.
6. **Given** a reported fault, **When** the curator reads it, **Then** it carries the row number as
   it appears in the file, the column name as it appears in the header, the offending value, and the
   reason it was refused.
7. **Given** a file in which any value at all was refused, **When** the check finishes, **Then**
   nothing has been written and the portal holds exactly what it held before.
8. **Given** a file in which every value passed, **When** the curator confirms, **Then** the records
   are written.

---

### User Story 2 — The release lands as one dataset for each publication (Priority: P1)

The portal holds data as datasets, and one publication is always one dataset. A release carries the
work of many publications in one file, so reading it means separating it into those datasets and
attaching each to the publication it came from.

**Why this priority**: a release loaded as one undifferentiated pile would satisfy the letter of
"the data is in" and none of its purpose. Nothing downstream — public browsing, generated releases,
citation — can work from data whose provenance was flattened on the way in, and reconstructing the
seam afterwards is not possible.

**Independent Test**: import a file holding rows from several publications and confirm that one
dataset exists per publication reference, that each carries the title of its bibliographic record,
and that each record is attached to the right one.

**Acceptance Scenarios**:

1. **Given** a file whose rows carry several distinct publication references, **When** it is
   imported, **Then** one dataset exists for each distinct reference and no dataset spans two.
2. **Given** a publication reference matching exactly one bibliographic record the portal already
   holds, **When** its dataset is created, **Then** the dataset takes its title from that record and
   is linked to it.
3. **Given** a publication reference matching no bibliographic record, **When** its dataset is
   created, **Then** a bibliographic record is created carrying that citation key, and the dataset
   is linked to it.
4. **Given** a publication reference matching more than one bibliographic record, **When** the file
   is checked, **Then** the rows carrying it are refused with an error naming the reference and the
   records it matched, because the portal does not choose between them.
5. **Given** a dataset created by an import, **When** it is read afterwards, **Then** the
   publication reference it came from is recorded on it rather than left to be inferred.

---

### User Story 3 — Every row becomes the records the portal keeps (Priority: P1)

One row of a release describes a site, a depth interval within it, the gradient and the conductivity
measured over that interval, the determination that follows, the corrections applied to it, and,
where the measurement was made by probe, the probe's metadata. Reading the row means creating each
of those, related correctly.

**Why this priority**: this is the translation itself. Without it the previous two stories have
nothing to validate or to file.

**Independent Test**: import a file of known rows and confirm that each expected record exists with
the values the file gave, and that records the file did not describe do not exist.

**Acceptance Scenarios**:

1. **Given** a row, **When** it is imported, **Then** a site, a depth interval, a determination, and
   the gradient and conductivity measured over that interval exist and are related as the model
   defines.
2. **Given** several rows sharing one published site identifier, **When** they are imported,
   **Then** one site exists and every determination is attached to it.
3. **Given** several rows giving the same site and the same depth range, **When** they are imported,
   **Then** one interval exists and carries all of their determinations, each with its own gradient
   and conductivity — an interval is a sample that can be measured again by someone else.
4. **Given** several rows giving the same site and no depth range at all, **When** they are
   imported, **Then** they attach to one indeterminate interval for that site, taken to cover the
   whole borehole or probe deployment.
5. **Given** two rows sharing an interval but disagreeing about the probe that sampled it, **When**
   the file is checked, **Then** they are refused and the disagreement is reported, because the
   probe describes the interval rather than either determination.
6. **Given** a row whose site name is a number, a placeholder such as `?`, or empty, **When** it is
   imported, **Then** the name is stored exactly as the file gave it and the row is not refused,
   because a site is identified by its published identifier and not by its name.
7. **Given** a cell holding `[Unspecified]`, **When** it is imported, **Then** it is read as no
   value rather than as a fault, and no record is created that the file did not describe.
8. **Given** a controlled-vocabulary value that is bracketed, differently cased, or both, **When**
   it is imported, **Then** it is matched to the right term.
9. **Given** a controlled-vocabulary value matching no term, **When** it is imported, **Then** it is
   refused and reported, whether the column holds one value or several.
10. **Given** a row supplying some corrections and not others, **When** it is imported, **Then** a
   correction record exists for each one supplied and for none of the others.
11. **Given** a row supplying no probe metadata, **When** it is imported, **Then** no probe metadata
   record is created for it.
12. **Given** a row carrying a supplied quality code, **When** it is imported, **Then** that code is
   not stored, because the portal computes quality from what it holds.
13. **Given** a file carrying the assessment columns a release includes, **When** it is imported,
    **Then** those columns are recognised rather than refused, and their values are not stored.
14. **Given** a file of `n` data rows in which every row passes, **When** it is imported, **Then**
    `n` determinations exist — no row is dropped on the way in.

---

### User Story 4 — Importing the same file twice changes nothing the second time (Priority: P2)

A file is imported, and later imported again — because a run was interrupted, because a correction
was made to part of it, or because the same release was reloaded. The second run brings the portal
to the same state as the first rather than doubling what it holds.

**Why this priority**: below the first three because a first import can be verified without it, but
required, since a seeding is carried out in parts and a part that cannot be safely repeated cannot
be safely resumed.

**Independent Test**: import a file, import it again, and confirm the record counts and values are
identical after the second run.

**Acceptance Scenarios**:

1. **Given** a file already imported, **When** it is imported again unchanged, **Then** no record is
   duplicated and no count changes.
2. **Given** a file already imported, **When** a value in one row is corrected and the file is
   imported again, **Then** the corresponding record carries the new value and no second record is
   created.
3. **Given** a site whose determinations are cited to more than one publication, **When** the
   publication with the earlier year is imported after the later one, **Then** the site moves to the
   earlier publication's dataset, and its determinations stay with the datasets of the publications
   that reported them.
4. **Given** a site whose determinations are cited to more than one publication, **When** the
   publication with the later year is imported after the earlier one, **Then** the site stays where
   it is.

---

### Edge Cases

- A publication reference is blank. Every row of the current release carries one, so this has never
  been seen, but the reference is what decides the dataset — the row is refused rather than filed
  under a default.
- Two publication references differ only by case or surrounding whitespace. They are the same
  reference, and the dataset is created once.
- A file is imported whose publication references already have datasets from an earlier import. The
  existing datasets are used rather than duplicated.
- A numeric cell reaches a column that holds text, or a text cell reaches a column that holds a
  quantity. The value is refused with its row, column and value named, rather than failing in a way
  that names neither.
- Rows disagree about a record they share — two rows give one published site identifier but
  different coordinates, or one interval but different probe metadata. The portal does not choose
  between them or merge them; the file is refused and the disagreement reported, per the standing
  constraint that the portal does not guess at supplied data. In the current release 974 shared
  intervals disagree about the probe that sampled them, so this is the ordinary case rather than a
  remote one.
- A site has both rows giving a depth range and rows giving none. It holds an interval for each
  distinct range, plus the one indeterminate interval the depthless rows attach to. They are
  different samples and are not merged.
- A determination's published identifier repeats within one file. The second occurrence is refused
  rather than silently overwriting the first, because within a single file it means the file is
  wrong.

## Requirements

### Functional Requirements

**Reading the file**

- **FR-001**: The import MUST be reachable by a staff user holding the permission to add records,
  from the administrative interface, and MUST NOT be reachable by any other user.
- **FR-002**: The import MUST accept a release file in the format a published release is distributed
  in: one header row, one data row per determination.
- **FR-003**: The import MUST validate every column name in the header before reading any data row,
  and MUST refuse the file without writing anything if that validation fails.
- **FR-004**: The import MUST refuse a file carrying a misspelled published column name. The error
  MUST name the misspelled name, the correct name, and the fact that the file follows an outdated
  template.
- **FR-005**: The import MUST refuse a file carrying a column name the release format does not
  define, naming that column.
- **FR-006**: The import MUST refuse a file missing a column the release format requires, naming
  that column.
- **FR-007**: The set of column names the release format defines MUST be held in one place and MUST
  be what both the header check and the reading consult, so that the two cannot disagree.

**Checking the values**

- **FR-008**: The import MUST check every value in the file before writing any record.
- **FR-009**: Checking MUST continue past a failure so that every fault in the file is reported
  together rather than one per attempt.
- **FR-010**: Each refused value MUST be reported with the row number as it appears in the file, the
  column name as it appears in the header, the value itself, and the reason it was refused.
- **FR-011**: If any value in the file is refused, the import MUST write nothing and MUST leave the
  portal exactly as it was.
- **FR-012**: The import MUST read the published absent-value marker as no value rather than as a
  fault.
- **FR-013**: A controlled-vocabulary value MUST be normalised by removing surrounding square
  brackets and lowercasing before it is matched to a term.
- **FR-014**: A controlled-vocabulary value matching no term MUST be refused and reported, for
  columns holding one value and for columns holding several alike. No vocabulary failure may pass
  silently.
- **FR-015**: The import MUST NOT remove a data row from the file it was given. Every data row is
  either imported or reported as refused.

**Datasets and literature**

- **FR-016**: Each distinct publication reference in the file MUST become exactly one dataset, and
  no dataset may span two references.
- **FR-017**: Publication references MUST be compared ignoring case and surrounding whitespace.
- **FR-018**: Where exactly one bibliographic record matches a publication reference, the dataset
  MUST be linked to it and MUST take its title from that record's title.
- **FR-019**: Where no bibliographic record matches, the import MUST create one carrying the
  citation key, and link the dataset to it.
- **FR-020**: Where more than one bibliographic record matches, the import MUST refuse the rows
  carrying that reference, naming the reference and the records it matched.
- **FR-021**: The publication reference a dataset was created from MUST be stored on the dataset.
- **FR-022**: A row whose publication reference is empty MUST be refused.

**The records**

- **FR-023**: A site MUST be identified by its published site identifier, and rows sharing one MUST
  produce one site.
- **FR-024**: A depth interval MUST be identified by its site together with the depth range the row
  gives. An interval is a sample in its own right, so every determination reported over the same
  interval MUST attach to the one interval record rather than to a copy of it.
- **FR-025**: Where a row gives no depth range, its determination MUST attach to a single
  indeterminate interval for that site, understood as covering the full extent of the borehole or
  probe deployment. Exactly one such interval MUST exist per site.
- **FR-026**: A determination MUST be identified by its published determination identifier.
- **FR-027**: The thermal gradient and the interval conductivity a row reports MUST each be
  identified by that row's published determination identifier. A determination derived again over an
  existing interval reports its own gradient and conductivity, and the file gives no identifier that
  would let two rows be recognised as reporting one measurement.
- **FR-028**: The import MUST create, for each row, the determination it describes together with the
  gradient and the conductivity it was derived from, attached to the interval the row identifies.
- **FR-029**: A correction record MUST be created only for a correction the row supplies. A row that
  supplies none MUST produce none.
- **FR-030**: A correction flag MUST be normalised the same way as any other controlled-vocabulary
  value, so that a bracketed or differently cased flag is read rather than lost.
- **FR-031**: Probe metadata MUST belong to the depth interval, and at most one record MUST exist
  for an interval. It describes the deployment that sampled the interval and does not vary between
  the determinations reported over it.
- **FR-032**: A site's name MUST be stored exactly as the file gives it, including a numeric,
  placeholder or empty value, and MUST never cause a row to be refused.
- **FR-033**: A supplied quality code MUST NOT be stored. The portal computes quality from what it
  holds.
- **FR-034**: The assessment columns a release carries MUST be recognised by the header check and
  MUST NOT be stored.
- **FR-035**: Rows that share a site or an interval but disagree about that shared record's own
  values MUST be refused, with the disagreement reported. The portal MUST NOT choose between them
  or merge them.

**Repeating an import**

- **FR-036**: Importing a file the portal has already read MUST update the records it identifies
  rather than create second copies of them.
- **FR-037**: A site MUST belong to the dataset of the earliest publication year among the
  determinations reported for it.
- **FR-038**: Where a later import supplies an earlier publication year for a site the portal
  already holds, the site MUST move to that earlier publication's dataset.
- **FR-039**: Moving a site between datasets MUST NOT move its determinations. Each determination
  stays with the dataset of the publication that reported it.

### Key Entities

- **Release file**: one header row and one data row per determination, carrying the published
  parent and determination columns together with the identifiers, publication year, quality code and
  assessment columns a release adds to the contributor template.
- **Publication reference**: the citation key naming the publication a determination was reported
  in. The seam along which a release is divided into datasets.
- **Dataset**: the portal's unit of provenance. One publication, one dataset.
- **Bibliographic record**: the portal's record of a publication. May exist already, or be created
  from a citation key alone.
- **Site**: the place a determination was made, identified by its published site identifier, holding
  one or more depth intervals.
- **Determination**: one heat flow value, identified by its published determination identifier,
  attached to a depth interval and carrying its gradient, conductivity, corrections and, where
  applicable, probe metadata.

## Success Criteria

- **SC-001**: A file whose header carries a misspelled published column name is refused, and the
  portal is unchanged. Proven for each misspelled name the published format contains.
- **SC-002**: A file whose header carries an undefined column name, and a file missing a required
  column, are each refused with that column named, and the portal is unchanged.
- **SC-003**: A file containing faults in more than one row reports every fault, each carrying its
  row number, column name, value and reason. Proven by counting the reported faults against the
  faults planted.
- **SC-004**: After any refused file, every record count in the portal is what it was before.
- **SC-005**: A file of `n` valid rows drawn from `p` distinct publication references produces `p`
  datasets and `n` determinations, with every determination attached to the dataset of the reference
  its row carried.
- **SC-006**: A publication reference with no bibliographic record produces one carrying its
  citation key. A reference matching two is refused.
- **SC-007**: Every published column the release format defines is read into the field that holds
  it, proven column by column rather than in aggregate.
- **SC-008**: A row supplying `k` of the corrections produces exactly `k` correction records, for
  `k` of nought, some, and all.
- **SC-009**: Bracketed, differently cased and bracketed-and-cased vocabulary values all match their
  term, and an unmatched value is refused — proven for a column holding one value and for a column
  holding several.
- **SC-010**: A site whose name is numeric, `?`, or empty imports without being refused, and the
  stored name is what the file gave.
- **SC-011**: Importing the same file twice leaves every record count and every stored value
  identical to after the first import.
- **SC-012**: A site reported by two publications belongs to the dataset of the earlier publication
  year, proven with the earlier publication imported second as well as first, and its determinations
  remain with their own publications' datasets.
- **SC-013**: No supplied quality code is stored, proven by reading back a record whose row carried
  one.
- **SC-014**: Several rows giving one site and one depth range produce one interval carrying every
  one of their determinations, each with its own gradient and conductivity.
- **SC-015**: Rows giving a site and no depth range all attach to one interval for that site,
  however many of them there are, and that interval is distinct from any the same site has with a
  depth range.
- **SC-016**: Rows that share a site or an interval and disagree about that record's own values are
  refused with the disagreement named, proven for a site and for an interval's probe metadata.
- **SC-017**: No test in this feature's suite is expected to fail.

## Out of Scope

- **Writing a release out.** The export half of the original specification is now `004`, which also
  carries the unfinished published-column work the portal's own suite currently records as expected
  failures. Confirming that a release exported after an import matches the release that went in
  belongs there, since it cannot be demonstrated without a working export.
- **The contributor upload template.** A separate format with its own layout, read by its own path,
  specified as `005` under R6. This feature reads a published release and nothing else.
- **Any upload route outside the administrative interface.** R6 covers moving import into the
  portal's own pages; the views that once offered it were removed and wait on an upstream framework
  change.
- **Splitting a large file, and anything else that follows from its size.** How a file is divided
  and how many parts are run is decided by whoever runs the import, not by this feature.
- **The assessment workflow.** The assessment columns a release carries are recognised and not
  stored. Recording assessment in the portal is G13, and aspirational.
- **Computing quality.** Owned by R4. This feature only declines to store what the file supplies.
- **Choosing between near-duplicate sites.** The portal does not match on proximity or merge sites,
  by standing constraint. Disagreements are reported for a curator to resolve at source.
- **Deciding which determination is a site's parent.** A parent is designated, never calculated.

## Assumptions

- The portal is seeded into a database holding no heat flow records. Sam confirmed on 2026-08-24
  that anything currently held may be removed, so the import is not specified to reconcile against
  pre-existing records loaded by another route.
- A file is prepared before it is imported. Correcting an outdated header and dividing the file are
  the operator's steps, taken before the portal sees it.
- The publication year needed to decide a shared site's dataset is carried in the file, so it does
  not depend on the bibliographic record having been resolved first.
- Bibliographic citation keys are not guaranteed unique in the portal's own records, which is why
  matching more than one is a refusal rather than a choice.
- A release holds the current state of the published database and carries no release dimension of
  its own — one parent per site.

## Clarifications

### Session 2026-08-24

- Q: Should this feature cover both directions, or is the round trip better split? → A: Split.
  Import is the priority and export waits. Every open issue on the subject is export-side, so import
  is blocked by no outstanding decision.
- Q: Should the release import and the contributor upload be one specification or two? → A: Two.
  They share most of their reading, but they are different formats and the release is what matters
  now.
- Q: Should this rewrite replace the existing specification or start a new one? → A: Replace it in
  place, keeping the number and reusing the epic already raised for it.
- Q: What decides a dataset? → A: One dataset per publication reference, titled from the reference's
  title, with a stub bibliographic record created where the portal holds none.
- Q: A site's determinations are cited to more than one publication. Which dataset owns the site? →
  A: The earliest publication year. Ownership is compared as each import runs, and reassigned if an
  earlier publication arrives later.
- Q: Where is the import triggered? → A: The administrative interface, whose confirm step is the
  check that precedes writing.
- Q: What happens when a row is refused? → A: Nothing is written. A refused row means the data is
  probably wrong, and the file is corrected at source before a real run.
- Q: The published release carries misspelled column names. Should the import accept them? → A: No.
  They are refused, before the import begins, and the refusal is covered by tests.
- Q: Nothing in the file identifies the interval, the gradient or the conductivity. Should each
  determination own its own interval, so that re-importing can find them all? → A: No. An interval
  is a sample in its own right and can be measured again by someone else — a new determination
  derived from a fresh conductivity or gradient over an interval another team sampled must attach
  to that same interval, because it is measuring the same thing.
- Q: Then how is a re-derived determination told apart from a newly added one, and does the
  determination's identifier apply to the gradient and the conductivity too? → A: The file does not
  record the distinction, and does not need to — both arrive as a new row with a new identifier over
  an existing interval, and which publication reported each is what separates them. The gradient and
  the conductivity take that row's determination identifier, since a re-derivation reports its own.
- Q: Where a row gives no depth range, what interval does its determination attach to? → A: A single
  indeterminate interval for that site, taken to cover the whole borehole or probe deployment, with
  several determinations relating to it.
- Q: Probe metadata cannot be held once per interval if determinations over one interval disagree
  about it. Should it move to the determination? → A: No. For a marine measurement the probe
  describes the interval being sampled and would not change. Rows that disagree about it are
  refused, like any other disagreement about a shared record.
