# Feature Specification: Forms designed for heat flow sites and measurements

**Feature Branch**: `009-heat-flow-forms`

**Created**: 2026-10-20

**Status**: Draft

**Goals**: G5, community members outside the assessment team adding their own datasets, with
nothing becoming public until the team has reviewed it. A researcher with their own heat flow data
has to be able to correct what is in their dataset without the admin or a re-uploaded spreadsheet.
The same forms serve G4, since the assessment team edits records through them too. The work also
moves toward G13, record keeping in the portal rather than on spreadsheets, but nothing in it
exists for G13 alone.

**Roadmap**: R7 (contribution from outside the assessment team, approved before it goes public),
loosely. R7 is the route a researcher's data takes into the portal. This feature is how they
correct it once it is there.

**References**: ADR-0006 (a site is its coordinates), ADR-0011 (the portal concepts decide a
vocabulary value), ADR-0017 (a role carries the trust that decides publication), ADR-0022 (stored
quality scores are recalculated when their inputs are written), ADR-0023 (a site holds the location
and its own elevation); FairDM ADR 0026 (a record's editing pages are six shared pages);
[CONTEXT.md](../../CONTEXT.md); [the field mapping table](../../docs/ghfdb_fields.md)

**Intake**: https://github.com/ihfc-iugg/ghfdb-portal/issues/286

## Overview

The portal is built for researchers who hold heat flow data of their own, not only for the
assessment team. A researcher in no team role adds a dataset for their publication, and from then
on its sites and measurements are theirs to keep correct. When they find a wrong elevation, a
missing correction or a measurement linked to the wrong gradient, they should be able to fix it on
the record itself, the way they would fix a typo in a document they own.

Every heat flow site and measurement already has FairDM's "Edit details" page. The form on it is
generated from a short list of field names per model, and only the site's location input has been
changed by hand, so that it takes a latitude and a longitude and nothing else (ADR-0023).

The generated forms leave a lot out. A site's form has no elevation and no true vertical depth. A
child heat flow's form has no surface temperature, no date, no way to say which thermal gradient and
interval conductivity it was calculated from, and none of its nine corrections. An interval
conductivity's form has no location and no count of measurements, an interval's form has no probe
metadata, and no form says which children a parent value rests on. Today a researcher can fix none
of these without the admin, which is closed to them, or a corrected spreadsheet.

This feature redesigns the form for each of the six records: a heat flow site, a depth interval, a
child heat flow, a thermal gradient, an interval conductivity and a parent heat flow. Each one
covers everything the upload template asks a contributor for about that record. Fields are grouped
and ordered the way the template presents them, so a researcher who filled the template in finds
the same things in the same order. A field that takes a term offers that field's own controlled
vocabulary, and values the portal works out for itself, like quality scores and GHFDB ids, are left
out.

Who may open a form, and when a researcher's records become public, do not change. A researcher's
dataset stays private until a Data Curator approves it, and a correction made through these forms
follows the same rule as everything else in that dataset.

## Clarifications

### Session 2026-10-20

- Q: Who is the person filling these forms in? → A: first, a researcher with their own heat flow
  data and no team role, correcting the records in their own dataset. The assessment team uses the
  same forms for the datasets they assess, with nothing different on them.
- Q: Which fields does each form cover? → A: every field that holds a column of the upload template
  for that record, as the field mapping table maps it, and nothing the portal calculates or assigns.
  A model field with no published column (a site's FairDM type, for example) stays off the form
  unless it is already there.
- Q: Who marks which children a parent value rests on? → A: the researcher, on the parent's form,
  for their own data. The upload template a contributor fills in already asks for the parent value
  and for which children are relevant, so stating it is part of contributing. A Data Curator's
  approval of the dataset is the check on it, as it is for every other value. The child's form does
  not repeat the choice.
- Q: Does the child's form offer every gradient and conductivity in the dataset? → A: no. It offers
  only the ones on the child's own depth interval, because a child is calculated from measurements
  over its own depth range.
- Q: Does a correction left untouched on the child's form get stored? → A: a correction the
  researcher never sets reads back as unspecified, which is what an import or an export already
  gives an empty correction column. Whether a row is stored for it is a planning question.
- Q: Does this feature add pages for creating a site or measurement? → A: no. FairDM decides which
  pages exist, and at the version the portal uses, a sample or measurement has an edit page but no
  page that creates one. These forms are the ones the registry hands to any page, so a create page
  uses them once FairDM provides one.

## User Scenarios & Testing

### User Story 1 — A researcher corrects a heat flow site in their dataset (Priority: P1)

A researcher with no team role opens the edit page of a site in their own dataset and corrects what
their publication reports about it: its name, its coordinates, its elevation and the datum it is
measured from, its geographic environment, the exploration method and purpose, the borehole's
measured and true vertical depth, its azimuth and inclination, and the rock it was drilled into. The
country, region, continent and domain are offered for correction as well. Where a field takes a
term, they choose from that field's vocabulary.

**Why this priority**: the site is the record every other one hangs from, and its elevation and
true vertical depth cannot be corrected anywhere a researcher can reach today.

**Independent Test**: open the site's edit page as a researcher in no team role who may change the
dataset, change the elevation, its datum and the true vertical depth, save, and read the stored site
back.

**Acceptance Scenarios**:

1. **Given** a site in a dataset the researcher may change, **When** they open its edit page,
   **Then** the form offers every site field the field mapping table maps a published column to.
2. **Given** the site's form, **When** the researcher enters an elevation with its unit and a datum
   and saves, **Then** the site's own elevation and datum hold those values, and FairDM's location
   elevation stays empty (ADR-0023).
3. **Given** the site's form, **When** the researcher looks at the location input, **Then** it takes
   a latitude and a longitude and nothing else.
4. **Given** the site's form, **When** the researcher sets the coordinates to those of another site,
   in their dataset or any other, **Then** the save is refused with an error against the location
   and nothing is written (ADR-0006).
5. **Given** the site's form, **When** the researcher opens the geographic environment, exploration
   method or exploration purpose, **Then** the only choices are the concepts of that field's
   vocabulary, and exploration purpose accepts several.
6. **Given** a researcher's dataset waiting for a Data Curator's decision, **When** the researcher
   corrects a site in it, **Then** the corrected site is no more visible to others than it was
   before the save.

---

### User Story 2 — A researcher corrects a child heat flow and its corrections (Priority: P1)

A researcher opens the edit page of a child heat flow in their dataset and corrects what their
publication reports about the determination: its value and uncertainty, the method, the surface
temperature, the date it was acquired, the expedition, and the comment. They choose the thermal
gradient and interval conductivity the child was calculated from, out of those on the child's own
depth interval. On the same form they set the status of each of the nine corrections, with a comment
where they have one, and each correction offers only the statuses valid for its type.

**Why this priority**: the child is the determination itself. Its corrections and the gradient and
conductivity behind it decide its quality score, and a researcher can correct none of them today.

**Independent Test**: open a child's edit page as a researcher who may change the dataset, pick a
gradient on its interval, set the topographic correction to present and corrected, save, and check
that the child, its link and its correction are stored and its quality score has been recalculated.

**Acceptance Scenarios**:

1. **Given** a child in a dataset the researcher may change, **When** they open its edit page,
   **Then** the form offers every child field the field mapping table maps a published column to,
   except relevance, which the parent's form carries.
2. **Given** a child on an interval with two thermal gradients and another interval in the same
   dataset with a third, **When** the researcher chooses the child's gradient, **Then** the two on
   its own interval are offered and the third is not. The same holds for interval conductivities.
3. **Given** the child's form, **When** the researcher sets a correction's status, **Then** only the
   statuses valid for that correction type are offered.
4. **Given** a child with no corrections recorded, **When** the researcher sets one correction and
   saves, **Then** that correction holds the chosen status and comment, and every correction left
   untouched reads back as unspecified.
5. **Given** a child whose corrections change, **When** the form is saved, **Then** the child's
   stored quality score is the one the portal calculates from its new data (ADR-0022).
6. **Given** the child's form, **When** the researcher opens the method, **Then** the only choices
   are the concepts of the heat flow method vocabulary, and several can be chosen.

---

### User Story 3 — A researcher corrects a thermal gradient or an interval conductivity (Priority: P2)

A researcher opens the edit page of a thermal gradient in their dataset and corrects its measured
and corrected values with their uncertainties, the temperature methods and corrections at each end
of the interval, the shut-in times and the number of temperature recordings. On an interval
conductivity they correct its value and uncertainty, its method, source, location, strategy,
saturation, pressure and temperature conditions and function, and the number of measurements it
averages. Each term field offers its own vocabulary.

**Why this priority**: these measurements feed a child's quality score, but a child can be
corrected without them. The gradient's form already holds every column it should, so for the
gradient this story is its arrangement and vocabularies, and for the conductivity it adds its
location and count.

**Independent Test**: open a conductivity's edit page as a researcher who may change the dataset,
choose a location and enter the number of measurements, save, and read the conductivity back with
its score recalculated.

**Acceptance Scenarios**:

1. **Given** a thermal gradient in a dataset the researcher may change, **When** they open its edit
   page, **Then** the form offers every gradient field the field mapping table maps a published
   column to.
2. **Given** an interval conductivity in a dataset the researcher may change, **When** they open its
   edit page, **Then** the form offers every conductivity field the field mapping table maps a
   published column to.
3. **Given** either form, **When** the researcher opens any term field, **Then** the only choices
   are the concepts of that field's vocabulary.
4. **Given** a gradient or conductivity whose scored inputs change, **When** the form is saved,
   **Then** its stored score, and the score of every child calculated from it, are the ones the
   portal calculates from the new data (ADR-0022).

---

### User Story 4 — A researcher corrects a depth interval and its probe metadata (Priority: P2)

A researcher opens the edit page of a depth interval in their dataset and corrects its top and
bottom depth, its vertical depth and datum, and the lithology, age and stratigraphy of the rock in
it. For a marine probe deployment they also enter or correct the probe type, length, penetration and
tilt on the same form.

**Why this priority**: the interval's depth range is already on its form. The probe metadata is the
part that is missing, and it matters only to marine data.

**Independent Test**: open an interval's edit page as a researcher who may change the dataset, enter
a probe type and a tilt, save, and read the interval's probe metadata back.

**Acceptance Scenarios**:

1. **Given** an interval in a dataset the researcher may change, **When** they open its edit page,
   **Then** the form offers every interval and probe metadata field the field mapping table maps a
   published column to.
2. **Given** an interval with no probe metadata, **When** the researcher saves the form without
   entering any, **Then** the interval still has no probe metadata.
3. **Given** an interval with no probe metadata, **When** the researcher enters a probe type and a
   tilt and saves, **Then** the interval has probe metadata holding them.
4. **Given** the interval's form, **When** the researcher enters a bottom depth that is not below
   the top depth, **Then** the save is refused with an error and nothing is written.

---

### User Story 5 — A researcher states a site's parent value and the children it rests on (Priority: P2)

A researcher opens the edit page of the parent heat flow in their dataset and corrects the
representative value their publication gives for the site: its value and uncertainty, whether heat
production was corrected for, and a comment. On the same form they mark which of the site's
children the value rests on.

**Why this priority**: the parent value is what most people reading the published database use, and
which children it rests on decides its quality. A researcher can state neither on a form today, only
in a re-uploaded spreadsheet.

**Independent Test**: open a parent's edit page as a researcher who may change the dataset, for a
site with three children, mark two as relevant, save, and read back which children are relevant and
the parent's inherited quality.

**Acceptance Scenarios**:

1. **Given** a parent in a dataset the researcher may change, **When** they open its edit page,
   **Then** the form offers its value, uncertainty, heat production correction and comment, and the
   children at its site to mark as relevant.
2. **Given** a site with three children, **When** the researcher marks two of them relevant and
   saves, **Then** exactly those two are relevant, and the parent's stored quality is the one the
   portal inherits from them.
3. **Given** a parent whose value the researcher does not touch, **When** they change which children
   are relevant and save, **Then** the parent's value is unchanged. A parent's value is never
   calculated.
4. **Given** the parent's form, **When** the researcher looks for the children to mark, **Then**
   only the children at the parent's own site are offered.

---

### Edge Cases

- A child whose interval has no thermal gradient or no interval conductivity: the choice is empty
  and the child saves without that link.
- A site with no parent yet: the children at the site have no parent form to be marked on. This
  feature does not create parents.
- A record in a dataset the researcher may not change: FairDM's access rule on the editing pages
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
  table maps a column of the upload template to, apart from the exceptions FR-003 and FR-011 name
  and the interval's IGSN, which is an identifier and is edited on FairDM's identifiers page. (US1,
  US2, US3, US4, US5)
- **FR-002**: The site's form MUST offer the site's own elevation with its unit and its elevation
  datum, and its location input MUST take a latitude and a longitude and nothing more (ADR-0023).
  (US1)
- **FR-003**: A form MUST NOT offer a value the portal calculates or assigns: the U-score, M-score,
  T-score, TC-score, their missing-information marks, the quality code, the scheme revision, and
  the GHFDB ids of children and parents. (US1, US2, US3, US4, US5)

**Arrangement**

- **FR-004**: Each form MUST group its fields by what they describe and present the groups in the
  order the upload template presents its columns for that record, so that a researcher who filled
  the template in finds the same things in the same order. (US1, US2, US3, US4, US5)
- **FR-005**: The forms MUST be the forms the registry gives for these models, so that every page
  that edits or adds one of these records uses them. (US1, US2, US3, US4, US5)

**Vocabulary**

- **FR-006**: Every field that takes a term MUST offer only the concepts of that field's own
  controlled vocabulary, and a field that holds several terms MUST accept several. (US1, US2, US3,
  US4)
- **FR-007**: A stored term that is no longer among the vocabulary's choices MUST be kept when the
  form is saved without touching that field. (US1, US2, US3, US4)

**Related records**

- **FR-008**: The child's form MUST let the researcher choose its thermal gradient and its interval
  conductivity, offering only the measurements on the child's own depth interval. (US2)
- **FR-009**: The child's form MUST let the researcher set the status and comment of each of the
  nine correction types, offering for each only the statuses valid for that type. A correction never
  set MUST read back as unspecified. (US2)
- **FR-010**: The interval's form MUST let the researcher enter or correct its probe metadata. An
  interval saved with no probe metadata entered MUST gain none. (US4)
- **FR-011**: The parent's form MUST let the researcher mark which children at its own site the
  parent rests on, offering only those children. Relevance MUST NOT be offered on the child's form.
  (US2, US5)

**What saving does**

- **FR-012**: A form MUST refuse whatever the record's own validation refuses (a duplicate site
  location, an interval whose bottom is not below its top, a correction status invalid for its type),
  show the error against the field it concerns where there is one, and write nothing. (US1, US2, US4)
- **FR-013**: Saving a form MUST leave every stored quality score equal to what the portal
  calculates from the data after the save, for the record saved and every record whose score reads
  from it (ADR-0022). (US2, US3, US5)
- **FR-014**: Saving a parent's form MUST NOT change the parent's value except where the researcher
  changed it. (US5)
- **FR-015**: Saving a form MUST NOT change who can see the record or its dataset. A record in a
  dataset waiting for a Data Curator's decision stays as private as the dataset (ADR-0017). (US1,
  US2, US3, US4, US5)
- **FR-016**: Every label, help text, group title and error message the forms add MUST be
  translatable (Constitution Article VIII). (US1, US2, US3, US4, US5)

### Key Entities

- **Heat flow site, depth interval, child heat flow, thermal gradient, interval conductivity,
  parent heat flow**: the six records with a form, as CONTEXT.md defines them. No model changes.
- **Correction**: one status per correction type on a child. Edited on the child's form.
- **Probe metadata**: the marine probe parameters of an interval. Edited on the interval's form.

## Success Criteria

### Measurable Outcomes

- **SC-001**: For each of the six records, a researcher in no team role can enter or correct every
  upload template column the field mapping table maps to it on its form, apart from the calculated
  and assigned values of FR-003. None of them requires the admin or a re-uploaded spreadsheet.
- **SC-002**: No form offers a quality score, a scheme revision or a GHFDB id.
- **SC-003**: Every term field on every form offers exactly the concepts of its own vocabulary.
- **SC-004**: A record corrected through its form exports the same release-format row as the same
  correction made in a re-uploaded template.
- **SC-005**: No save through these forms makes a record visible to anyone who could not see it
  before.

## Assumptions

- Who may open each form is FairDM's access rule for its editing pages (FairDM ADR 0026), and this
  feature changes nothing about it. A researcher reaches the forms for the datasets FairDM lets them
  change.
- When a researcher's dataset becomes public is decided by the assessment workflow, unchanged: it is
  private until a Data Curator approves it (ADR-0017, R7). This feature does not redesign it.
- How a researcher's records first reach their dataset is R7's route into the assessment workflow,
  and is not part of this feature.
- A record is moved to another dataset, sample or site by no form here. FairDM leaves the fields
  that move a record off the edit page, and an interval's site is treated the same way.
- Imports, exports and uploads are untouched. A form and an import store the same record the same
  way.
- The API representations of these records are FS-010's (#287), and their overview pages are
  FS-011's (#288). The published structure in the API is FS-006's.
- A child's link to its parent follows its site. This feature does not add a way to attach a child
  to a parent at another site.
