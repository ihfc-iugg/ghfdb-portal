# Feature Specification: The published structure reachable through the API

**Feature Branch**: `006-published-structure-api`

**Created**: 2026-09-18

**Status**: Draft

**Goals**: G8 — the GHFDB structure reachable through the API, alongside the relational model's own
endpoints

**Roadmap**: R10

**References**: Fuchs et al. (2021); Fuchs et al. (2023); constitution principles II, III, VII, IX;
ADR-0002, ADR-0003; [CONTEXT.md](../../CONTEXT.md)

## Overview

The framework already generates and documents an API over the portal's own models. What it does not
offer is the database in the shape the published product has, which is what a consumer outside the
portal expects: a researcher pulling heat flow data into their own analysis, and the map viewer,
which reads the portal's API and carries no data of its own.

This feature adds that shape as three read-only endpoints over the two proxy models that already
present the stored graph in published columns:

- **parents** — one record per representative site value, carrying the published parent columns plus
  how many determinations the site holds and how many of them contributed to that value.
- **children** — one record per determination, carrying the published child columns, the site's
  coordinates, and a link to the parent it belongs to.
- **flat** — the released row exactly: every published parent column followed by every published
  child column, under the published names, in the published order.

The three are not three views of one thing. Parents and children are the published structure's own
two levels, navigable from one to the other. Flat is the release file as a stream of rows, for the
consumer who wants what the published download gives them without the download.

All three are registered on the framework's router, so they appear in the API index and in the
generated schema beside the portal's own endpoints, and all three are scoped by the proxies to
records that belong to the published database.

The canonical column definitions live in the extraction app's constants module (ADR-0002, with the
two spelling corrections of ADR-0003). This feature treats that module as the single authority for
what the columns are called and what order they come in, exactly as the proxy feature does. Nothing
here restates a column list that module already holds.

Writing is out of scope: the routes into the portal are the import paths, and these endpoints never
create, change or delete a record.

## User Scenarios & Testing

### User Story 1 — Parents read through the API (Priority: P1)

A consumer outside the portal asks the API for heat flow sites in the published parent shape and
receives them a page at a time, each record carrying the published parent columns under their
published names, a link to its own record, and the two determination counts. Following that link
returns the same record with its determinations attached.

**Why this priority**: the parent level is what a map plots. A consumer that can read parents has
the database's spatial layer and the representative value at every point, which is the smallest
useful thing this feature can deliver.

**Independent Test**: build sites with representative values, request the list endpoint
unauthenticated, and assert the published column set, the published order, the counts, and that the
number of queries behind a page does not change when more sites exist.

**Acceptance Scenarios**:

1. **Given** parents in the published database, **When** the parent list endpoint is requested,
   **Then** each record carries every published parent column, under its published name, in
   published order.
2. **Given** the same request, **When** the number of stored parents is increased, **Then** the
   number of database queries behind one page is unchanged.
3. **Given** a parent whose site holds determinations of which only some contributed to its value,
   **When** its record is read, **Then** it carries the total number of determinations and the
   number that contributed.
4. **Given** a parent whose site holds no determinations, **When** its record is read, **Then** both
   counts are zero.
5. **Given** a parent record in a list response, **When** the link it carries to itself is followed,
   **Then** the same parent is returned, with its determinations attached.
6. **Given** a record that does not belong to the published database, **When** either parent route
   is requested for it, **Then** it is absent from the list and its own route reports that it does
   not exist.
7. **Given** no credentials at all, **When** either parent route is requested, **Then** the records
   are returned rather than refused.
8. **Given** a request that would create, change or delete a parent, **When** it is sent to either
   parent route, **Then** it is refused and nothing in the database changes.
9. **Given** the API index, **When** it is read, **Then** the parent endpoint is listed there, and
   the generated schema describes it.

---

### User Story 2 — Determinations read through the API, and navigable to their site (Priority: P1)

A consumer asks the API for determinations and receives them a page at a time, each carrying the
published child columns, the coordinates of the site it was made at, and a link to its parent.
Following that link, or reading a single determination, gives the parent's full record without a
second request.

**Why this priority**: the determination is the unit of the published database, and the coordinates
are what make one usable on its own — a determination with no position can be neither plotted nor
joined to anything else.

**Independent Test**: build complete record chains, request the list endpoint, and assert the
published child column set, the presence of coordinates and a parent link on every record, the
nested parent on the single-record route, and a query count per page that does not grow with the
number of determinations.

**Acceptance Scenarios**:

1. **Given** determinations in the published database, **When** the child list endpoint is
   requested, **Then** each record carries every published child column, under its published name,
   in published order.
2. **Given** the same records, **When** the list is read, **Then** each record carries the latitude
   and longitude of the site it was made at, and carries no other parent column.
3. **Given** a determination in a list response, **When** the link it carries to its parent is
   followed, **Then** the parent that determination belongs to is returned.
4. **Given** a single determination is requested by its own route, **When** it is read, **Then** the
   parent it belongs to is present as a complete record rather than a link.
5. **Given** the same request, **When** the number of stored determinations is increased, **Then**
   the number of database queries behind one page is unchanged.
6. **Given** a determination whose gradient, conductivity, probe metadata or a particular correction
   is absent, **When** it is read, **Then** those columns are present and empty rather than missing
   or the record being dropped.
7. **Given** a record that does not belong to the published database, **When** either child route is
   requested for it, **Then** it is absent from the list and its own route reports that it does not
   exist.
8. **Given** a determination whose method, lithology or conductivity metadata holds several values,
   **When** it is read, **Then** each such column carries the values as a list rather than as one
   joined string.
9. **Given** a request that would create, change or delete a determination, **When** it is sent to
   either child route, **Then** it is refused and nothing in the database changes.
10. **Given** the API index, **When** it is read, **Then** the determination endpoint is listed
    there, and the generated schema describes both of its shapes.

---

### User Story 3 — The released row served as it is published (Priority: P1)

A consumer who knows the published file asks the API for the database in that file's own shape and
receives rows a page at a time: every published parent column, then every published child column,
one row per determination, with the site's values repeated on every row that mentions it. Nothing
else appears in the row.

**Why this priority**: this is what "extract the database and run my own analysis" means in
practice. A consumer who has ever opened the published file can use this endpoint without learning
anything about the portal, and the rows it emits are the rows an export writes.

**Independent Test**: build complete record chains, request the endpoint, and assert the row against
the canonical column order held in the extraction app's constants module — same names, same
sequence, nothing added.

**Acceptance Scenarios**:

1. **Given** determinations in the published database, **When** the flat endpoint is requested,
   **Then** each row carries every published parent column followed by every published child column,
   under the published names, in the canonical published order.
2. **Given** the same rows, **When** they are read, **Then** they carry no key that is not a
   published column — no links, no counts, no identifier belonging to the portal's own model.
3. **Given** several determinations belonging to one parent, **When** the rows are read, **Then**
   each row repeats that parent's values.
4. **Given** the same request, **When** the number of stored determinations is increased, **Then**
   the number of database queries behind one page is unchanged.
5. **Given** a single row is requested by its determination's published identifier, **When** it is
   read, **Then** the same row is returned as the list would carry.
6. **Given** a record that does not belong to the published database, **When** the endpoint is
   requested, **Then** no row for it appears.
7. **Given** a released column carrying one of the two names the published file misspells, **When**
   any row is read, **Then** the corrected spelling is the name emitted and the misspelled form
   appears nowhere in the response.
8. **Given** no credentials at all, **When** either flat route is requested, **Then** the rows are
   returned rather than refused, and a request that would change a record is refused.
9. **Given** the API index, **When** it is read, **Then** the flat endpoint is listed there, and the
   generated schema describes it.

---

### Edge Cases

- A page requested beyond the last one reports that it does not exist rather than returning an empty
  page as though it were data.
- A page size larger than the maximum the framework allows is served at the maximum rather than
  refused.
- A many-valued column with no related records is an empty list, which is distinct from a scalar
  column with no value.
- A published column the portal holds no value for at all is present and empty on every record,
  never absent, so a consumer's column set is identical on every row.
- A determination whose site has no coordinates is still returned, with the coordinates empty.
- A request for a record by an identifier that is not a number at all is refused as not found rather
  than raising.

## Requirements

### Functional Requirements

- **FR-001**: The API MUST expose three endpoints over the published database — one for parents, one
  for determinations, one for the released row — each offering a paged list and a route to a single
  record.
- **FR-002**: Every field name a record carries that is a published column MUST be the published
  name exactly, including its casing, as held in the extraction app's constants module.
- **FR-003**: Published columns MUST appear in the canonical published order held in that module.
  Keys that are not published columns MUST be grouped ahead of them, so the published sequence is
  never interrupted.
- **FR-004**: The two spelling corrections of ADR-0003 MUST be honoured: the corrected names are
  emitted and the misspelled forms appear nowhere in a response.
- **FR-005**: A parent record MUST carry the number of determinations at its site and the number of
  those that contributed to its value, on both the list and the single-record route.
- **FR-006**: A parent's single-record route MUST carry the determinations belonging to it.
- **FR-007**: A determination record MUST carry the latitude and longitude of its site, and no other
  parent column.
- **FR-008**: A determination record MUST carry a link to its parent on the list route, and the
  parent's complete record on its own route.
- **FR-009**: Every record on a list route MUST carry a link to its own route.
- **FR-010**: A flat row MUST carry published columns and nothing else.
- **FR-011**: A column that holds several values MUST be emitted as a list of values rather than as
  the joined string the published file's cell carries.
- **FR-012**: A column with no value MUST be emitted as empty, with the key present.
- **FR-013**: Records MUST be addressed by their published identifier on every single-record route.
- **FR-014**: All three endpoints MUST be read-only. A request to create, change or delete through
  them MUST be refused.
- **FR-015**: All three endpoints MUST serve a request that carries no credentials.
- **FR-016**: All three endpoints MUST show only records that belong to the published database, on
  every route, including a request for one record by its identifier.
- **FR-017**: All three endpoints MUST be registered on the framework's router, appear in the API
  index, and appear in the generated schema and its documentation pages.
- **FR-018**: The number of database queries behind one page MUST NOT grow with the number of
  records on it, on any of the three endpoints.
- **FR-019**: Each endpoint MUST be documented for a consumer outside the portal, with at least one
  worked request and the response it returns.

### Key Entities

- **Parent record**: one representative heat flow value for a site, in the published parent columns,
  with its two determination counts.
- **Determination record**: one heat flow determination, in the published child columns, with the
  coordinates of its site and its link to its parent.
- **Released row**: one determination, in every published parent and child column, in published
  order — the row a published release file carries.

## Success Criteria

- **SC-001**: A consumer with no account and no knowledge of the portal's internal model can read
  every record in the published database through the API, in published columns.
- **SC-002**: The column names and their order on the flat endpoint match the canonical published
  column list exactly, verified against that list rather than against a copy of it.
- **SC-003**: The number of database queries behind one page is the same for a page of one record
  and a page of the maximum size, on all three endpoints.
- **SC-004**: A consumer holding a row from a published release file can reach that row's record on
  all three endpoints using only the identifiers the file carries.
- **SC-005**: Every one of the three endpoints is listed in the API index and described in the
  generated schema, with no endpoint reachable but undocumented.
- **SC-006**: No response from any of the three endpoints carries a field name that is neither a
  published column nor one of the four named additions — the self link, the parent link, and the two
  counts.

## Clarifications

### Session 2026-09-18

- **Q: Which of the three spreadsheets does the flat endpoint mirror — the upload template, the
  management spreadsheet, or the release format?**
  A: The release format. It is the format exports are always written in, and it is what a consumer
  of the published product recognises. The management spreadsheet is never imported or exported, and
  the upload template is a contributor's input rather than a published product.

- **Q: Does the flat endpoint carry the columns a release file adds to the template — the review
  status, the year, the quality code and the parent identifier?**
  A: The parent identifier is already a published parent column and is carried. The other three are
  not: the portal computes quality itself rather than storing a supplied code, and the review status
  and year have no field in the portal's schema to be read from. A release file is assembled from
  the portal's data plus the assessment team's own columns, and assembling one is R17's work. This
  endpoint serves the portal's data in the released row's shape.

- **Q: What identifies a determination on its own route?**
  A: Its published identifier — the one a published file carries as the row's own id, stored on the
  record as its GHFDB identifier.

- **Q: Do the two determination counts belong on the parent list route, given they are not published
  columns?**
  A: Yes. The proxy computes both in the page query already, so carrying them costs no additional
  query, and the map viewer needs them to show whether a site's representative value rests on one
  determination or several. If the aggregate proves expensive against a full-size database, the
  answer is to hold the counts on the record rather than to drop them from the response.

- **Q: A determination's list record links to its parent while its own record nests the parent
  whole. Is one name for two shapes a problem for a consumer?**
  A: No. It means the schema describes two shapes for a determination, one for the list and one for
  the single record, which the generated documentation shows plainly. The alternative — every list
  record dragging a complete parent behind it — makes the common request much heavier in order to
  serve the rarer one.

## Assumptions

- The published identifier a consumer holds from a release file is the identifier these endpoints
  are addressed by, rather than the portal's own internal identifier. A consumer never needs to see
  the portal's identifiers at all.
- The framework's paging behaviour — its page parameter, its page size parameter, its default and
  its maximum — is inherited rather than redefined, so these endpoints page like every other
  endpoint the portal serves.
- Records are scoped to the published database by the proxy models, which already refuse anything
  without a published identifier. This feature adds no scoping rule of its own.
- Two published child columns resolve to nothing in the portal today, because no field holds them.
  They are emitted as empty rather than omitted, and filling them is the work of whichever feature
  gives them a field.
- Serving these rows in a format other than the one the API's own content negotiation offers — a
  comma-separated download of the whole database, in particular — is not part of this feature. The
  flat endpoint is where such a format would later attach.
- Filtering and searching these endpoints beyond what the framework offers by default is not part of
  this feature.
- The static download of the 2024 release, and the column-metadata route beside it, stay where they
  are. Retiring them belongs to R8, which replaces the static download with the portal's own data.
