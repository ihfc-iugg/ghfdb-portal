# Feature Specification: Import a completed upload template into a dataset

**Feature Branch**: `004-import-upload-template`

**Created**: 2026-09-11

**Status**: Draft

**Goals**: G4 (the assessment team can add datasets one at a time), with G3 and G2 behind it

**Roadmap**: R6, programmatic half

**Issue**: #199

**Input**: A completed copy of the official GHFDB upload template is read into the portal by calling
it from code: one file, into one dataset the caller names. The file is refused whole, before
anything is written, on failures the portal cannot absorb. The portal's own controlled vocabularies
decide what passes; the vocabulary sheet inside the template is guidance for whoever fills the
spreadsheet in, never the authority.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The reader reads the official template (Priority: P1)

The file the assessment team actually fills in is the published GHFDB upload template. Reading it is
what the existing importers have never been proven to do: the three committed fixtures are
hand-built hybrids rather than copies of the published file, and the column constants in the code
disagree with the template's seventy columns on ten names. This story makes the official file the
thing the reader is written and tested against, and reconciles every column name against it.

**Why this priority**: every other story is read through this one. A reader that agrees with a
fixture nobody uses proves nothing about a real upload.

**Independent Test**: point the reader at an unmodified copy of the published template and confirm
it recognises the header and resolves all seventy columns, with no column silently unmatched.

**Acceptance Scenarios**:

1. **Given** an unmodified copy of the official upload template, **When** the file is read, **Then**
   its header row is recognised and every one of its seventy columns resolves to either a stored
   field or an explicitly accepted-and-ignored column.
2. **Given** a file whose header row is not the official template's, **When** the file is read,
   **Then** it is refused whole with the header named as the reason and nothing is written.
3. **Given** a column present in the template but not resolvable in the code, **When** the test
   suite runs, **Then** it fails, so the disagreement cannot return unnoticed.

---

### User Story 2 - Sites and their parent values land in a named dataset (Priority: P1)

A caller names one dataset and one file. The rows group into sites by their coordinate pair, and the
parent heat flow value for each site comes from the file's P-columns.

**Why this priority**: this is the smallest slice that puts real data in the portal and is worth
running on its own.

**Independent Test**: import a file of several rows across two coordinate pairs into an empty
dataset and confirm two sites exist, each carrying its parent value, both belonging to the named
dataset.

**Acceptance Scenarios**:

1. **Given** an empty dataset and a file whose rows cover two coordinate pairs, **When** the file is
   imported into that dataset, **Then** two sites exist, each with the parent value its P-columns
   describe, and both belong to that dataset.
2. **Given** a file and no dataset named by the caller, **When** the import is called, **Then** it
   fails rather than choosing a dataset.
3. **Given** rows carrying geography columns, **When** they are imported, **Then** those values are
   stored as supplied rather than recomputed.
4. **Given** rows carrying the reviewer columns and `ID`, **When** they are imported, **Then** those
   columns are accepted without being stored, and their presence is not an error.

---

### User Story 3 - Child determinations land beneath their sites (Priority: P1)

Beneath each site sit the depth intervals and the heat flow determinations made over them, together
with the gradients, conductivities, corrections and probe metadata each determination carries.
`relevant_child` records which children fed the site's parent value.

**Why this priority**: without the children the import holds a headline number and none of the
evidence under it, which is not a usable dataset.

**Independent Test**: import a file whose rows describe two determinations at one site and confirm
both exist beneath that site with their intervals, gradients, conductivities, corrections and probe
metadata attached, and that `relevant_child` names the ones the parent value came from.

**Acceptance Scenarios**:

1. **Given** a file whose rows describe more than one determination at a single coordinate pair,
   **When** it is imported, **Then** each determination exists beneath that one site with its own
   depth interval.
2. **Given** determinations carrying gradient, conductivity, correction and probe columns, **When**
   they are imported, **Then** each of those values is stored against its own determination.
3. **Given** a site whose parent value derives from a subset of its children, **When** the file is
   imported, **Then** `relevant_child` names exactly that subset.

---

### User Story 4 - A file the portal cannot absorb is refused whole (Priority: P1)

The import either lands completely or changes nothing. A file is refused before anything is written
when it carries a failure the portal genuinely cannot absorb: a header that is not the official one,
a value the model cannot store, or a mandatory model field left empty. Every fault is reported by
row and column, all of them rather than only the first.

**Why this priority**: a partial import leaves a dataset nobody can trust and no record of what went
in, which is worse than a refusal.

**Independent Test**: import a file with faults on several distinct rows and confirm the dataset is
untouched afterwards and the report names every faulty row and column, not just the earliest.

**Acceptance Scenarios**:

1. **Given** a file with a fault on row 20 and another on row 400, **When** it is imported, **Then**
   both are reported, each naming its row and column.
2. **Given** a file with any such fault, **When** it is imported, **Then** the dataset holds exactly
   what it held before the import.
3. **Given** a file with no faults, **When** it is imported, **Then** nothing is reported and every
   row lands.

---

### User Story 5 - The portal's vocabularies decide what passes (Priority: P2)

Every controlled-vocabulary column is checked against the concepts the portal itself holds. The
vocabulary sheet inside the template is never consulted. A value that sheet permits but the portal
does not hold is a fault like any other, and refuses the file.

**Why this priority**: it is the rule most likely to be implemented the wrong way round, because the
allowed values are sitting right there in the file.

**Independent Test**: import a file whose vocabulary column carries a value the template's own sheet
lists but the portal holds no concept for, and confirm the file is refused.

**Acceptance Scenarios**:

1. **Given** a value the portal holds no concept for, **When** the file is imported, **Then** it is
   refused, naming the row, the column and the unrecognised value.
2. **Given** a value the template's vocabulary sheet lists but the portal does not hold, **When**
   the file is imported, **Then** it is still refused.
3. **Given** a value the portal holds but the template's sheet does not list, **When** the file is
   imported, **Then** it is accepted.

---

### User Story 6 - Importing the same file again updates what is there (Priority: P2)

Re-importing a file that has already been imported updates the existing records rather than adding a
second copy of everything.

**Why this priority**: corrections arrive as a fresh copy of the same spreadsheet, and the team
should not have to delete a dataset to apply one.

**Independent Test**: import a file, import it again unchanged, and confirm the record counts are
identical; then change one value, import a third time, and confirm the change lands without
duplicating anything.

**Acceptance Scenarios**:

1. **Given** a dataset already holding a file's contents, **When** the same file is imported again,
   **Then** the number of sites and determinations is unchanged.
2. **Given** that dataset, **When** a file identical except for one changed value is imported,
   **Then** that value is updated in place and nothing is duplicated.

---

### Edge Cases

- A row whose coordinate pair matches an existing site in the same dataset joins that site rather
  than creating a second one.
- A file with a recognised header and no data rows imports nothing and is not an error.
- A row missing its coordinate pair cannot be placed at a site, so it is a fault reported by row.
- Two rows with the same coordinates but conflicting site-level values are a fault, reported rather
  than resolved by picking one.
- A file whose obligation row or allowed-range row is violated still imports, provided the portal
  can store what it carries.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The import MUST be callable from code, taking one template file and one dataset named
  by the caller.
- **FR-002**: The import MUST refuse to run when no dataset is named rather than selecting one.
- **FR-003**: The reader MUST recognise the official template's header row and refuse any file whose
  header is not it.
- **FR-004**: Every column of the official template MUST resolve either to a stored field or to a
  column the reader explicitly accepts and does not store.
- **FR-005**: Rows MUST group into sites by their coordinate pair.
- **FR-006**: Each site's parent heat flow value MUST come from the file's P-columns, with
  `relevant_child` recording which child determinations fed it.
- **FR-007**: Depth intervals, determinations, gradients, conductivities, corrections and probe
  metadata MUST be stored against the determination they belong to.
- **FR-008**: Geography columns MUST be stored as supplied.
- **FR-009**: The reviewer columns and `ID` MUST be accepted without being stored.
- **FR-010**: The import MUST write nothing when the file carries any fault.
- **FR-011**: A fault MUST be one of: a header that is not the official one, a value the model
  cannot store, a controlled-vocabulary value the portal holds no concept for, or an empty mandatory
  model field.
- **FR-012**: Every fault in a file MUST be reported, each naming its row and column, rather than
  stopping at the first.
- **FR-013**: Controlled-vocabulary values MUST be validated against the concepts the portal holds.
- **FR-014**: The template's own vocabulary sheet MUST NOT be read or honoured by the import.
- **FR-015**: The template's obligation row and allowed-range row MUST NOT be enforced.
- **FR-016**: Re-importing a file MUST update the records it already created rather than duplicating
  them.
- **FR-017**: The test suite MUST read an unmodified copy of the official template, not a hand-built
  approximation of it.

### Key Entities

- **Upload template file**: the published GHFDB spreadsheet, seventy columns, header on its sixth
  row, filled in by the assessment team. Carries its own obligation row, allowed-range row and
  vocabulary sheet, none of which this feature enforces.
- **Dataset**: the container the caller names, which every site and determination from the file
  belongs to.
- **Site**: identified by its coordinate pair, carrying the parent heat flow value and the geography
  supplied for it.
- **Determination**: a heat flow value over a depth interval beneath a site, carrying the gradients,
  conductivities, corrections and probe metadata reported with it.
- **Concept**: a term in a controlled vocabulary the portal holds. The authority for whether a
  vocabulary value in the file is acceptable.
- **Fault**: something the portal cannot absorb, located at a row and a column, and reported.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An unmodified copy of the official upload template, filled in, imports into a named
  dataset in one call with nothing reported.
- **SC-002**: All seventy of the template's columns are accounted for, none silently unmatched.
- **SC-003**: A file carrying faults on any number of rows leaves the dataset exactly as it was, and
  every fault appears in the report with its row and column.
- **SC-004**: A vocabulary value the portal holds no concept for refuses the file, whether or not the
  template's own vocabulary sheet lists it.
- **SC-005**: Importing the same file twice produces the same record counts as importing it once.
- **SC-006**: A site whose parent value came from a subset of its children names exactly that subset
  in `relevant_child`.

## Clarifications

Questions raised by the ambiguity scan, answered from the agreed feature statement.

1. **Which vocabulary decides whether a value is acceptable, the portal's or the template's?**
   The portal's. The template's vocabulary sheet is guidance for whoever fills the spreadsheet in. A
   file that agrees with the sheet but names a concept the portal does not hold is still refused.
   Disagreements between the two are settled as real datasets are imported, not by code written
   here. (FR-013, FR-014, US-5.)
2. **Is a violated obligation or allowed-range row a fault?**
   No. Only failures the portal genuinely cannot absorb refuse a file. Those two rows become checks
   at a later point. (FR-015.)
3. **What happens when the caller names no dataset?**
   The import fails rather than guessing. (FR-002.)
4. **Are all faults reported, or does the import stop at the first?**
   All of them, each located by row and column, so one pass over the file tells the team everything
   to fix. (FR-012.)
5. **Does a repeat import add a second copy?**
   No, it updates in place. (FR-016.)

## Assumptions

- The file being read is a copy of the published template rather than a spreadsheet shaped like it.
  Detection is the header check, and that is enough for now.
- No revision marker exists inside the template, so a future revision of it is detected by a header
  that no longer matches rather than by a version.
- Until a completed real file is available, the empty official template at
  `docs/constitution/references/data_upload_template.xlsx` is what the work is built against.
- The all-or-nothing refusal depends on the rollback defect in #190 being fixed.
- Nothing in this feature has a person clicking anything. The upload page, the readable validation
  result and everything about who may import belong to R6's other half and to R7.
- Reading a published release in is not part of this or any feature. The data assessment team
  decided the direction is unnecessary, and PR #189 closes with its branch.
