# Feature Specification: API representations of heat flow sites and measurements

**Feature Branch**: `010-heat-flow-api`

**Created**: 2026-10-20

**Status**: Draft

**Goals**: G8 (the relational model's own endpoints, alongside the published structure) and G10
(the map viewer reads the portal's API and holds no data of its own)

**Roadmap**: none. The issue cites no roadmap item. R10 delivered the published structure through
the API (FS-006), and R12 brings the map viewer into the portal. This feature sits between them.

**Issue**: [#287](https://github.com/ihfc-iugg/ghfdb-portal/issues/287)

**References**: Fuchs et al. (2021); Fuchs et al. (2023); constitution articles XI, XII and XIII;
ADR 0021, ADR 0022, ADR 0023; [CONTEXT.md](../../CONTEXT.md);
[FS-006](../006-published-structure-api/spec.md)

## Overview

The portal's API serves two different things. One is the published GHFDB structure, the flat parent
and child shape a consumer of the released file expects (FS-006). The other is the portal's own
relational model: heat flow sites, depth intervals, child heat flow values, thermal gradients,
interval conductivities and parents. This feature is about the second.

Today the framework generates those endpoints from each model's field list, with no knowledge of
heat flow. A record arrives without the records it can't be understood without. A child heat flow
value does not carry the gradient and conductivity it was calculated from. A site does not carry its
parent value or its intervals. Vocabulary terms and units can't be read from the response, and the
quality scores the portal calculates are not there at all. Anyone working with the data through the
API has to make one request per related record and already know what the portal stores behind each
field.

After this feature, each of the six record types is served in a shape designed for heat flow data:

- **Related records come with the record.** Reading one site gives its parent, its intervals and
  the children made over them. Reading one child gives the gradient and conductivity behind it, its
  corrections, and where it was made.
- **Vocabulary terms are readable.** Every term carries its label and the identifier that defines
  it, so a consumer needs no lookup to know what it means.
- **Units are stated.** Every value with a unit says which unit it is in.
- **Quality is present.** Every record the portal scores carries its stored scores and the scheme
  revision they were calculated under.

Two consumers are in view. The **map viewer** reads this API and holds no data of its own. A
**researcher scripting against the portal** reads records into their own analysis.

The published-structure endpoints of FS-006 do not change. This feature follows the way they list,
page and decide who may see what, so a consumer meets one set of rules across the API.

## User Scenarios & Testing

### User Story 1 — A researcher reads a heat flow site with what belongs to it (Priority: P1)

A researcher asks the API for a heat flow site and gets back, in one response, the site's own
description, its position, its parent value with that value's quality, and the depth intervals at
the site with the child heat flow values made over each. Listing sites a page at a time gives each
site's position, its parent value and its quality code, which is what a map plots.

**Why this priority**: every other record hangs off the site. A site that arrives with its parent
and its children is the smallest useful thing this feature delivers, and it is what the map viewer
needs to show a point and explain it.

**Independent Test**: build a public site with a parent, two intervals and several children,
request it with no credentials, and assert that the parent, the intervals and the children all come
back in that one response. Then request the site list and assert that the number of queries behind
one page does not grow as sites are added.

**Acceptance Scenarios**:

1. **Given** a public site with a parent, intervals and children, **When** its single record is
   requested, **Then** the response carries the site's parent, every interval at the site, and the
   children made over each interval.
2. **Given** a public site with a parent, **When** the site list is requested, **Then** each site
   carries its position, its parent's value and uncertainty, and its parent's quality code.
3. **Given** a site with no parent, **When** it is read in the list or on its own, **Then** the
   parent is present and empty, and the site is not dropped.
4. **Given** the site list, **When** the number of stored sites, intervals and children grows,
   **Then** the number of database queries behind one page is unchanged.
5. **Given** a parent requested on its own, **When** it is read, **Then** it carries its value, its
   uncertainty, its quality scores, its GHFDB identifier where it has one, the site it describes,
   and the children it was derived from, each with whether it was marked relevant.
6. **Given** an interval or a child at the site that sits in a dataset the requester may not see,
   **When** the site is read, **Then** that record is absent from the response.
7. **Given** a request with no credentials, **When** a public site is requested, **Then** it is
   served rather than refused.

---

### User Story 2 — A researcher reads a child heat flow value with how it was reached (Priority: P1)

A researcher asks the API for a child heat flow value and gets back, in one response, the value and
its uncertainty, the thermal gradient and interval conductivity it was calculated from, the
corrections recorded against it with the status of each, its quality scores, the interval it was
made over and the site that interval belongs to.

**Why this priority**: the child is the unit of the heat flow database. Nobody can judge its value
without the gradient, conductivity and corrections behind it, and its quality scores are the
portal's own contribution to that judgement.

**Independent Test**: build a child with a gradient, a conductivity and several corrections,
request it with no credentials, and assert that all of them and its quality scores come back in one
response. Request the child list and assert that the query count behind a page does not grow with
the number of children.

**Acceptance Scenarios**:

1. **Given** a child with a gradient, a conductivity and corrections, **When** its single record is
   requested, **Then** the response carries the gradient, the conductivity and every correction with
   its status.
2. **Given** a scored child, **When** it is read, **Then** it carries its U-score, its M-score, its
   corrected T-score and TC-score with their missing-information marks, its quality code and the
   scheme revision they were calculated under, each equal to the stored value.
3. **Given** a child whose scores have not been determined, **When** it is read, **Then** each
   undetermined score is present and empty rather than zero or missing.
4. **Given** a child, **When** it is read in the list or on its own, **Then** it carries the
   coordinates of the site it was made at, and a reference to its interval and its parent.
5. **Given** a child with no gradient, no conductivity or no corrections, **When** it is read,
   **Then** those parts are present and empty, and the child is not dropped.
6. **Given** the child list, **When** the number of stored children grows, **Then** the number of
   database queries behind one page is unchanged.
7. **Given** a request that creates or changes a child and supplies quality scores, a quality code
   or a GHFDB identifier, **When** it is accepted, **Then** none of the supplied values is stored, and
   the record holds the scores the portal calculates.

---

### User Story 3 — A researcher reads a gradient, a conductivity or an interval on its own (Priority: P2)

A researcher asks the API for a thermal gradient, an interval conductivity or a depth interval. The
record comes back with its own measurements, its scores where it is scored, and the records that use
it: the children calculated from a gradient or conductivity, and for an interval, its probe metadata
and the children, gradients and conductivities made over it.

**Why this priority**: every child calculated from a gradient or conductivity shares it, and an
interval is what several measurements are made on. These are the second questions a researcher
asks, once they have a site or a child in hand.

**Independent Test**: build a gradient used by two children and an interval with probe metadata,
request each, and assert that the gradient's uncorrected score and missing-information mark, the
children using it, and the interval's measurements and probe metadata are all present.

**Acceptance Scenarios**:

1. **Given** a scored gradient or conductivity, **When** it is read, **Then** it carries its
   uncorrected score, its missing-information mark and its scheme revision, each equal to the
   stored value.
2. **Given** a gradient used by several children, **When** its single record is requested, **Then**
   it carries a reference to each child calculated from it.
3. **Given** an interval with probe metadata, **When** its single record is requested, **Then** it
   carries the probe metadata and a reference to each child, gradient and conductivity made over it.
4. **Given** a gradient, conductivity or interval, **When** it is read, **Then** it carries the
   coordinates of the site it is placed at.
5. **Given** the gradient, conductivity or interval list, **When** the number of stored records
   grows, **Then** the number of database queries behind one page is unchanged.

---

### User Story 4 — A researcher reads vocabulary terms and units without looking anything up (Priority: P2)

A researcher reading any of the six record types finds that every field holding a vocabulary term
gives the term's label and the identifier that defines it, and every value with a unit says which
unit it is in. They can interpret a record without knowing what the portal stores behind each
field.

**Why this priority**: it applies to every record the other stories serve, and it is what makes a
response usable by someone outside the assessment team. It comes after the first two stories
because those decide which records arrive together.

**Independent Test**: read one record of each type with every vocabulary field and every quantity
filled, and assert that each term carries a label and an identifier, and each quantity a unit that
matches the unit the portal stores it in.

**Acceptance Scenarios**:

1. **Given** a record whose field holds a vocabulary term, **When** it is read, **Then** the term
   comes with its label and its identifier, and never as a bare internal number.
2. **Given** a field that holds several vocabulary terms, **When** it is read, **Then** each term is
   its own entry, each with a label and an identifier.
3. **Given** a record with a value that has a unit, **When** it is read, **Then** the record states
   the unit that value is in, and the unit is the canonical one the portal stores it in.
4. **Given** an empty value that has a unit, **When** it is read, **Then** the value is present and
   empty, and no number is invented for it.
5. **Given** the generated API schema, **When** it is read, **Then** it describes the vocabulary
   term and the unit of each field that has one.

### Edge Cases

- A site has at most one parent, but a site with **no** parent can exist. It is served with the
  parent empty.
- One interval can carry **several children**, each calculated differently. All of them are served,
  never one picked from among them.
- A child that is **not marked relevant** is still served, on its own route and under its parent,
  with its relevance stated.
- A heat flow value can be **negative**. It is served as stored.
- A **stale** score, calculated under an earlier scheme revision, is served with the revision it was
  calculated under, so a consumer can tell.
- A coordinate's digits are not its precision (CONTEXT.md). The API serves the stored coordinate and
  claims nothing more about it.
- A related record the requester may **not see** is left out. It is never shown as a placeholder
  that gives away that it exists.
- A correction recorded as not applied is different from a correction with no record at all, and
  the response tells the two apart.

## Requirements

### Functional Requirements

- **FR-001**: A site's single record MUST carry its parent, every interval at the site, and the
  children made over each interval. *(US1)*
- **FR-002**: A site in a list MUST carry its position, its parent's value and uncertainty, and its
  parent's quality code. *(US1)*
- **FR-003**: A parent's record MUST carry its value, its uncertainty, its quality scores, its GHFDB
  identifier where it has one, a reference to the site it describes, and a reference to each of its
  children with whether that child is marked relevant. *(US1)*
- **FR-004**: A child's single record MUST carry its gradient, its conductivity, every correction
  recorded against it with that correction's status, a reference to its interval and its parent,
  and its GHFDB identifier where it has one. *(US2)*
- **FR-005**: A child MUST carry its U-score, its M-score, its corrected T-score and TC-score with
  their missing-information marks, its quality code and its scheme revision, each as stored. *(US2)*
- **FR-006**: A gradient and a conductivity MUST carry their uncorrected score, its
  missing-information mark and its scheme revision, each as stored. *(US3)*
- **FR-007**: A gradient's or conductivity's single record MUST carry a reference to each child
  calculated from it. *(US3)*
- **FR-008**: An interval's single record MUST carry its probe metadata, and a reference to each
  child, gradient and conductivity made over it. *(US3)*
- **FR-009**: Every interval, child, gradient, conductivity and parent MUST carry the coordinates of
  the site it is placed at. The site stays the one record that holds them (ADR 0023). *(US2, US3)*
- **FR-010**: Every field holding a vocabulary term MUST give each term with its label and the
  identifier that defines it. *(US4)*
- **FR-011**: Every value with a unit MUST be served in the canonical unit the portal stores it in,
  and the record MUST state that unit. *(US4)*
- **FR-012**: A field with no value MUST be present and empty. An undetermined score is empty, never
  zero. *(US2, US4)*
- **FR-013**: A related record MUST be served only where the requester may see it on its own route.
  *(US1)*
- **FR-014**: The six record types MUST keep their current addresses, and each record MUST keep the
  identifier it is addressed by today. *(US1, US2, US3)*
- **FR-015**: Lists MUST be paged, ordered and permitted the same way the published-structure
  endpoints are, and a request with no credentials MUST be served the public records. *(US1)*
- **FR-016**: The number of database queries behind one page of any list MUST NOT grow with the
  number of records stored. *(US1, US2, US3)*
- **FR-017**: Quality scores, quality codes, scheme revisions and GHFDB identifiers MUST NOT be
  stored from a value supplied through the API. A record the API accepts today MUST still be
  accepted. *(US2)*
- **FR-018**: The generated API schema MUST describe each record's shape, including the vocabulary
  term and unit of each field that has one. *(US4)*
- **FR-019**: The shape of each record type MUST be documented for a consumer outside the portal,
  with at least one example request and response. *(US1)*

### Key Entities

- **Heat flow site**: a location, the one record holding coordinates and elevation. Carries its
  parent and its intervals on its own route.
- **Depth interval**: a depth range at a site, with its lithology, stratigraphy, age and probe
  metadata, and the measurements made over it.
- **Child heat flow value**: one determination over an interval, from one gradient and one
  conductivity, with its corrections and its scores.
- **Thermal gradient** and **interval conductivity**: the measurements a child is calculated from,
  each with its own uncorrected score.
- **Parent heat flow value**: the representative value for a site, designated by curators, with
  quality inherited from its children.
- **Correction**: one recognised disturbance on a child, and what was done about it.

## Success Criteria

- **SC-001**: A researcher with no account reads a public site with its parent, its intervals and
  their children in one request.
- **SC-002**: A researcher reads a child with its gradient, conductivity, corrections and quality
  scores in one request.
- **SC-003**: The number of database queries behind one page of each list is the same for a page of
  one record as for a full page.
- **SC-004**: No response for any of the six record types gives a vocabulary term without its label
  and identifier, or a value with a unit without stating the unit.
- **SC-005**: Every quality score served equals the score stored on the record, and no score sent
  through the API changes what is stored.
- **SC-006**: No response reveals a record the requester could not read on that record's own route.

## Clarifications

### Session 2026-10-20

- Q: How deep do related records nest, and is a list shaped like a single record? → A: A single
  record carries its related records whole, one level down, and records further away as references.
  A list carries what a page of that type is read for (for a site, its position, parent value and
  quality code) and references for the rest. This follows FS-006, where a determination links to
  its parent in a list and nests it on its own route. Integrated into FR-001 to FR-008.
- Q: Does the new shape change what can be written through the API? → A: No. Writing stays as it is
  today. The related records, labels, units and scores added here are for reading, and the values
  the portal calculates are never taken from a request. Integrated into FR-017 and US2 scenario 7.
- Q: In what form is a unit given? → A: Each value is served in the canonical unit the portal stores
  it in, and the record states that unit beside it. Converting units on request is out of scope.
  Integrated into FR-011.
- Q: Who may see a related record nested inside another? → A: Exactly whoever may see it on its own
  route. A record the requester may not see is left out, which is the rule the published-structure
  endpoints already apply to a determination and its parent (ADR 0021). Integrated into FR-013 and
  US1 scenario 6.
- Q: Do intervals and measurements carry a location, given that only a site holds one? → A: They
  carry the coordinates of the site they are placed at, read from the site and not stored again, so
  a consumer can place any record without a second request. Integrated into FR-009.

## Assumptions

- The six record types are the ones issue #287 names: sites, intervals, children, gradients,
  conductivities and parents. Corrections and probe metadata are served inside the child and the
  interval, not as types of their own.
- Filtering a list stays as the framework provides it today. New filters are out of scope.
- The published-structure endpoints (FS-006), the forms for these records (#286) and their overview
  pages (#288) are outside this feature.
- Nothing here needs a FairDM release newer than the one the portal is pinned to.
