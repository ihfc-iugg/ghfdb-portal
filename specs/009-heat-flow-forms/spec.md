# Feature Specification: Forms designed for heat flow sites and measurements

**Feature Branch**: `009-heat-flow-forms`

**Created**: 2026-10-20

**Status**: Draft

**Goals**: G4, the assessment team adding datasets to the portal one at a time, and G5, people
outside the team adding their own. Both need a record to be correctable in the portal once it is
there. The work also moves toward G13, record keeping in the portal rather than on spreadsheets,
but nothing in it exists for G13 alone.

**Roadmap**: none. No roadmap item covers the record forms.

**References**: ADR-0006 (a site is its coordinates), ADR-0011 (the portal concepts decide a
vocabulary value), ADR-0022 (stored quality scores are recalculated when their inputs are written),
ADR-0023 (a site holds the location and its own elevation); FairDM ADR 0026 (a record's editing
pages are six shared pages); [CONTEXT.md](../../CONTEXT.md);
[the field mapping table](../../docs/ghfdb_fields.md)

**Intake**: https://github.com/ihfc-iugg/ghfdb-portal/issues/286

## Overview

Every heat flow site and measurement in the portal can be edited through FairDM's "Edit details"
page. The form on that page is generated from a short list of field names per model. Only the
site's location input has been changed by hand, so that it takes a latitude and a longitude and
nothing else (ADR-0023).

The generated forms leave a lot out. A site's form has no elevation and no true vertical depth. A
child heat flow's form has no surface temperature, no date, no way to say which thermal gradient
and interval conductivity it was calculated from, and none of its nine corrections. An interval
conductivity's form has no location and no count of measurements, and an interval's form has no
probe metadata. A
Data Curator cannot say on any form which children a parent rests on. Today every one of these
can only be fixed in the admin or by uploading a corrected template.

This feature redesigns the form for each of the six records: a heat flow site, a depth interval, a
child heat flow, a thermal gradient, an interval conductivity and a parent heat flow. Each one
covers everything the upload template records about that record. Fields are grouped and ordered the
way an assessor reads a publication, a field that takes a term offers that field's own controlled
vocabulary, and values the portal works out for itself, like quality scores and GHFDB ids, are left
out.

The people filling these forms in are a Data Assessor or Data Curator entering or correcting one
record at a time, and later a researcher from outside the team adding their own data. Who may open
a form does not change. That is FairDM's access rule for the editing pages.

## Clarifications

### Session 2026-10-20

- Q: Which fields does each form cover? → A: every field that holds a column of the upload template
  for that record, as the field mapping table maps it, and nothing the portal calculates or assigns.
  A model field with no published column (a site's FairDM type, for example) stays off the form
  unless it is already there.
- Q: Where is relevance marked, on the child or on the parent? → A: on the parent. Marking which
  children a parent rests on is the act of designating it, and a curator makes that choice looking
  at all the children at the site together. The child's form does not repeat it.
- Q: Does the child's form offer every gradient and conductivity in the dataset? → A: no. It offers
  only the ones on the child's own depth interval, because a child is calculated from measurements
  over its own depth range.
- Q: Does a correction left untouched on the child's form get stored? → A: a correction the
  assessor never sets reads back as unspecified, which is what an import or an export already gives
  an empty correction column. Whether a row is stored for it is a planning question.
- Q: Does this feature add pages for creating a site or measurement? → A: no. FairDM decides which
  pages exist. A site or measurement is added today by upload, and a page that adds one through the
  portal is FairDM's to provide. These forms are the ones the registry hands to any page, so such a
  page uses them with no further work.

## User Scenarios & Testing

### User Story 1 — A Data Assessor corrects a heat flow site (Priority: P1)

A Data Assessor opens the edit page of a site from a dataset they are assessing, and corrects what
the publication reports about it: its name, its coordinates, its elevation and the datum it is
measured from, its geographic environment, the exploration method and purpose, the borehole's
measured and true vertical depth, its azimuth and inclination, and the rock it was drilled into.
The country, region, continent and domain are offered for correction as well. Where a field takes
a term, the assessor chooses from that field's vocabulary.

**Why this priority**: the site is the record every other one hangs from, and its elevation and
true vertical depth cannot be corrected anywhere in the portal front end today.

**Independent Test**: open the site's edit page as a Data Assessor allowed to change it, change the
elevation, its datum and the true vertical depth, save, and read the stored site back.

**Acceptance Scenarios**:

1. **Given** a site the assessor may change, **When** they open its edit page, **Then** the form
   offers every site field the field mapping table maps a published column to.
2. **Given** the site's form, **When** the assessor enters an elevation with its unit and a datum
   and saves, **Then** the site's own elevation and datum hold those values, and FairDM's location
   elevation stays empty (ADR-0023).
3. **Given** the site's form, **When** the assessor looks at the location input, **Then** it takes
   a latitude and a longitude and nothing else.
4. **Given** the site's form, **When** the assessor sets the coordinates to those of another site,
   **Then** the save is refused with an error against the location and nothing is written
   (ADR-0006).
5. **Given** the site's form, **When** the assessor opens the geographic environment, exploration
   method or exploration purpose, **Then** the only choices are the concepts of that field's
   vocabulary, and exploration purpose accepts several.

---

### User Story 2 — A Data Assessor corrects a child heat flow and its corrections (Priority: P1)

A Data Assessor opens a child heat flow's edit page and corrects what the publication reports
about the determination: its value and uncertainty, the method, the surface temperature, the date
it was acquired, the expedition, and the comment. They choose the thermal gradient and interval
conductivity the child was calculated from, out of those on the child's own depth interval. On the
same form they set the status of each of the nine corrections, with a comment where the paper
gives one, and each correction offers only the statuses valid for its type.

**Why this priority**: the child is the determination itself. Its corrections and the gradient and
conductivity behind it decide its quality score, and none of them can be corrected through the
portal front end today.

**Independent Test**: open a child's edit page as a Data Assessor allowed to change it, pick a
gradient on its interval, set the topographic correction to present and corrected, save, and check
that the child, its link and its correction are stored and its quality score has been recalculated.

**Acceptance Scenarios**:

1. **Given** a child the assessor may change, **When** they open its edit page, **Then** the form
   offers every child field the field mapping table maps a published column to, except relevance,
   which the parent's form carries.
2. **Given** a child on an interval with two thermal gradients and another interval in the same
   dataset with a third, **When** the assessor chooses the child's gradient, **Then** the two on its
   own interval are offered and the third is not. The same holds for interval conductivities.
3. **Given** the child's form, **When** the assessor sets a correction's status, **Then** only the
   statuses valid for that correction type are offered.
4. **Given** a child with no corrections recorded, **When** the assessor sets one correction and
   saves, **Then** that correction holds the chosen status and comment, and every correction left
   untouched reads back as unspecified.
5. **Given** a child whose corrections change, **When** the form is saved, **Then** the child's
   stored quality score is the one the portal calculates from its new data (ADR-0022).
6. **Given** the child's form, **When** the assessor opens the method, **Then** the only choices are
   the concepts of the heat flow method vocabulary, and several can be chosen.

---

### User Story 3 — A Data Assessor corrects a thermal gradient or an interval conductivity (Priority: P2)

A Data Assessor opens the edit page of a thermal gradient and corrects its measured and corrected
values with their uncertainties, the temperature methods and corrections at each end of the
interval, the shut-in times and the number of temperature recordings. On an interval conductivity they correct its value and
uncertainty, its method, source, location, strategy, saturation, pressure and temperature
conditions and function, and the number of measurements it averages. Each term field offers its own
vocabulary.

**Why this priority**: these measurements feed a child's quality score, but a child can be
corrected without them. The gradient's form already holds every column it should, so for the
gradient this story is its arrangement and vocabularies, and for the conductivity it adds its
location and count.

**Independent Test**: open a conductivity's edit page, choose a location and enter the number of
measurements, save, and read the conductivity back with its score recalculated.

**Acceptance Scenarios**:

1. **Given** a thermal gradient the assessor may change, **When** they open its edit page, **Then**
   the form offers every gradient field the field mapping table maps a published column to.
2. **Given** an interval conductivity the assessor may change, **When** they open its edit page,
   **Then** the form offers every conductivity field the field mapping table maps a published column
   to.
3. **Given** either form, **When** the assessor opens any term field, **Then** the only choices are
   the concepts of that field's vocabulary.
4. **Given** a gradient or conductivity whose scored inputs change, **When** the form is saved,
   **Then** its stored score, and the score of every child calculated from it, are the ones the
   portal calculates from the new data (ADR-0022).

---

### User Story 4 — A Data Assessor corrects a depth interval and its probe metadata (Priority: P2)

A Data Assessor opens a depth interval's edit page and corrects its top and bottom depth, its
vertical depth and datum, and the lithology, age and stratigraphy of the rock in it. For a marine
probe deployment they also enter or correct the probe type, length, penetration and tilt on the
same form.

**Why this priority**: the interval's depth range is already on its form. The probe metadata is
the part that is missing, and it matters only to marine sites.

**Independent Test**: open an interval's edit page, enter a probe type and a tilt, save, and read
the interval's probe metadata back.

**Acceptance Scenarios**:

1. **Given** an interval the assessor may change, **When** they open its edit page, **Then** the
   form offers every interval and probe metadata field the field mapping table maps a published
   column to.
2. **Given** an interval with no probe metadata, **When** the assessor saves the form without
   entering any, **Then** the interval still has no probe metadata.
3. **Given** an interval with no probe metadata, **When** the assessor enters a probe type and a
   tilt and saves, **Then** the interval has probe metadata holding them.
4. **Given** the interval's form, **When** the assessor enters a bottom depth that is not below the
   top depth, **Then** the save is refused with an error and nothing is written.

---

### User Story 5 — A Data Curator designates a parent and the children it rests on (Priority: P2)

A Data Curator opens a parent's edit page and sets the representative value for the site: its
value and uncertainty, whether heat production was corrected for, and a comment. On the same form
they mark which of the site's children the value rests on.

**Why this priority**: designating a parent is the curatorial decision the published structure
records, and marking its relevant children is today possible only in the admin or by upload.

**Independent Test**: open a parent's edit page for a site with three children, mark two as
relevant, save, and read back which children are relevant and the parent's inherited quality.

**Acceptance Scenarios**:

1. **Given** a parent the curator may change, **When** they open its edit page, **Then** the form
   offers its value, uncertainty, heat production correction and comment, and the children at its
   site to mark as relevant.
2. **Given** a site with three children, **When** the curator marks two of them relevant and saves,
   **Then** exactly those two are relevant, and the parent's stored quality is the one the portal
   inherits from them.
3. **Given** a parent whose value the curator does not touch, **When** they change which children
   are relevant and save, **Then** the parent's value is unchanged. A parent's value is never
   calculated.
4. **Given** the parent's form, **When** the curator looks for the children to mark, **Then** only
   the children at the parent's own site are offered.

---

### Edge Cases

- A child whose interval has no thermal gradient or no interval conductivity: the choice is empty
  and the child saves without that link.
- A site with no parent yet: the children at the site have no parent form to be marked on. This
  feature does not create parents.
- A record in a dataset the viewer may not change: FairDM's access rule on the editing pages
  decides, unchanged.
- A vocabulary value stored on a record that the vocabulary no longer holds (an import or an older
  version): the form shows the stored value so that saving an unrelated change does not silently
  drop it.
- A quantity entered in a unit the field accepts other than its base unit (an elevation in feet):
  it is stored with that unit, as an import stores it.

## Requirements

### Functional Requirements

**Coverage**

- **FR-001**: Each of the six forms MUST offer every field of its record that the field mapping
  table maps a column of the upload template to, apart from the exceptions FR-003 and FR-011 name and the interval's IGSN, which is an identifier
and is edited on FairDM's identifiers page.
  (US1, US2, US3, US4, US5)
- **FR-002**: The site's form MUST offer the site's own elevation with its unit and its elevation
  datum, and its location input MUST take a latitude and a longitude and nothing more (ADR-0023).
  (US1)
- **FR-003**: A form MUST NOT offer a value the portal calculates or assigns: the U-score, M-score,
  T-score, TC-score, their missing-information marks, the quality code, the scheme revision, and
  the GHFDB ids of children and parents. (US1, US2, US3, US4, US5)

**Arrangement**

- **FR-004**: Each form MUST group its fields by what they describe and present the groups in the
  order the upload template presents its columns for that record, so that an assessor working down
  a publication works down the form. (US1, US2, US3, US4, US5)
- **FR-005**: The forms MUST be the forms the registry gives for these models, so that every page
  that edits or adds one of these records uses them. (US1, US2, US3, US4, US5)

**Vocabulary**

- **FR-006**: Every field that takes a term MUST offer only the concepts of that field's own
  controlled vocabulary, and a field that holds several terms MUST accept several. (US1, US2, US3,
  US4)
- **FR-007**: A stored term that is no longer among the vocabulary's choices MUST be kept when the
  form is saved without touching that field. (US1, US2, US3, US4)

**Related records**

- **FR-008**: The child's form MUST let the assessor choose its thermal gradient and its interval
  conductivity, offering only the measurements on the child's own depth interval. (US2)
- **FR-009**: The child's form MUST let the assessor set the status and comment of each of the nine
  correction types, offering for each only the statuses valid for that type. A correction never set
  MUST read back as unspecified. (US2)
- **FR-010**: The interval's form MUST let the assessor enter or correct its probe metadata. An
  interval saved with no probe metadata entered MUST gain none. (US4)
- **FR-011**: The parent's form MUST let the curator mark which children at its own site the
  parent rests on, offering only those children. Relevance MUST NOT be offered on the child's form.
  (US2, US5)

**What saving does**

- **FR-012**: A form MUST refuse whatever the record's own validation refuses (a duplicate site
  location, an interval whose bottom is not below its top, a correction status invalid for its type),
  show the error against the field it concerns where there is one, and write nothing. (US1, US2, US4)
- **FR-013**: Saving a form MUST leave every stored quality score equal to what the portal
  calculates from the data after the save, for the record saved and every record whose score reads
  from it (ADR-0022). (US2, US3, US5)
- **FR-014**: Saving a parent's form MUST NOT change the parent's value except where the curator
  changed it. (US5)
- **FR-015**: Every label, help text, group title and error message the forms add MUST be
  translatable (Constitution Article VIII). (US1, US2, US3, US4, US5)

### Key Entities

- **Heat flow site, depth interval, child heat flow, thermal gradient, interval conductivity,
  parent heat flow**: the six records with a form, as CONTEXT.md defines them. No model changes.
- **Correction**: one status per correction type on a child. Edited on the child's form.
- **Probe metadata**: the marine probe parameters of an interval. Edited on the interval's form.

## Success Criteria

### Measurable Outcomes

- **SC-001**: For each of the six records, every upload template column the field mapping table
  maps to it can be entered or corrected on its form, apart from the calculated and assigned values
  of FR-003. None of them requires the admin or an upload.
- **SC-002**: No form offers a quality score, a scheme revision or a GHFDB id.
- **SC-003**: Every term field on every form offers exactly the concepts of its own vocabulary.
- **SC-004**: A record corrected through its form exports the same release-format row as the same
  correction made in a re-uploaded template.

## Assumptions

- Who may open each form is FairDM's access rule for its editing pages (FairDM ADR 0026), and this
  feature changes nothing about it.
- A record is moved to another dataset, sample or site by no form here. FairDM leaves the fields
  that move a record off the edit page, and an interval's site is treated the same way.
- Imports, exports and uploads are untouched. A form and an import store the same record the same
  way.
- The API representations of these records are FS-010's (#287), and their overview pages are
  FS-011's (#288). The published structure in the API is FS-006's.
- A child's link to its parent follows its site. This feature does not add a way to attach a child
  to a parent at another site.
