# Feature Specification: A filterable table of GHFDB parents

**Feature Branch**: `012-ghfdb-parent-table`

**Created**: 2026-10-23

**Status**: Draft

**Goals**: G7, the published GHFDB freely reachable by anyone with no account, because the table
lets a reader browse and narrow the parent values themselves rather than only download them. G2,
faithful translation to the GHFDB structure, because the table presents parents in the published
column names a reader of a GHFDB release already knows.

**Roadmap**: R8, public access to the database itself. This feature is one slice of it. The
download of the current database and the removal of the static download stay with R8.

**References**: FS-002 (the GHFDB proxy models), FS-006 (the published-structure API, whose parent
endpoint sets the visibility rule this table follows), FS-011 (the parent, child and site overview
pages the table links to); [CONTEXT.md](../../CONTEXT.md)

## Overview

The portal holds every parent heat flow value in the GHFDB, but the only ways to read them in bulk
are the API and the map viewer. Neither lets a reader ask an ordinary question of the data, such
as "which continental sites above 100 mW/m² have a quality code of A", and see the answer as rows.

This feature adds a public table of parents. Each row is one parent, shown in the published GHFDB
column names. Every column can be filtered and sorted, and the table can be paged through. A count
column shows how many children each parent has and how many of them are marked relevant. Selecting
the count opens a window over the table that lists those children, relevant ones first.

The table sits in the sidebar beside the map viewer. The single map viewer entry becomes a group
that holds both, so a reader finds the two ways of browsing the GHFDB in one place.

## User Scenarios & Testing

A **visitor** in these stories is anyone reading the portal, signed in or not. A parent appears in
the table when the visitor may see both the parent and its site, by the same rule the API's parent
endpoint applies (FS-006).

### User Story 1 — A visitor browses the parents in a table (Priority: P1)

A visitor opens the table from the sidebar. They see one row per parent they may see, with the
parent's published columns: its heat flow value and uncertainty, its site's name, coordinates and
elevation, its geographic environment, its comment, whether a heat production correction was
applied, its site's total measured and vertical depths, its exploration method and purpose, and its
quality code. They can sort by any column and page through the rows. Each row links to the
parent's page and to its site's page.

**Why this priority**: without the table nothing else in this feature has anywhere to be.

**Independent Test**: create parents in a public dataset and in a private one, open the table
without signing in, and assert that only the public parents are listed, each with its published
columns and links to its parent and site pages.

**Acceptance Scenarios**:

1. **Given** parents in a public dataset, **When** a visitor who is not signed in opens the table,
   **Then** every one of them is listed, one row each.
2. **Given** a parent whose dataset or site the visitor may not see, **When** the visitor opens the
   table, **Then** that parent is not listed.
3. **Given** the table, **When** a visitor sorts by a column, **Then** the rows are ordered by that
   column, and sorting again reverses the order.
4. **Given** more parents than fit on one page, **When** a visitor moves to the next page, **Then**
   the next rows are shown and the visitor can tell how many parents match in total.
5. **Given** a row, **When** a visitor follows its links, **Then** they reach the parent's page and
   its site's page.
6. **Given** a field with no value, **When** the row is shown, **Then** the cell reads as not
   recorded and never as zero.

---

### User Story 2 — A visitor narrows the table with filters (Priority: P1)

A visitor narrows the table to the parents they care about. They can set a lower and an upper bound
on heat flow, its uncertainty, elevation and either total depth. They can restrict latitude and
longitude to a box. They can choose one or more values of the geographic environment, the
exploration method, the exploration purpose, the heat production correction and the quality code.
They can search the site name. They can restrict the table to one or more datasets or projects.
Filters combine, and the table shows how many parents match. The filtered table has its own
address, so the visitor can bookmark it or send it to a colleague.

**Why this priority**: the request names comprehensive filtering as a requirement, and a table of
tens of thousands of rows that cannot be narrowed is of little use.

**Independent Test**: create parents that differ in heat flow, latitude, environment, quality code,
dataset and project, apply each filter in turn and then several together, and assert that exactly
the matching parents are listed each time.

**Acceptance Scenarios**:

1. **Given** parents with heat flow values of -20, 60 and 140, **When** a visitor sets a lower
   bound of -30 and an upper bound of 100, **Then** the first two are listed and the third is not.
2. **Given** a bound set on one side only, **When** the table is shown, **Then** the other side is
   open.
3. **Given** parents at several coordinates, **When** a visitor sets a latitude and longitude box,
   **Then** only the parents whose site lies inside it are listed.
4. **Given** parents in different geographic environments, **When** a visitor chooses two
   environments, **Then** parents in either of them are listed.
5. **Given** parents in several datasets, **When** a visitor restricts the table to one dataset,
   **Then** only that dataset's parents are listed.
6. **Given** parents in several projects, **When** a visitor restricts the table to one project,
   **Then** only parents in that project's datasets are listed.
7. **Given** a site name fragment, **When** a visitor searches for it, **Then** parents whose
   site's name contains it are listed, regardless of case.
8. **Given** several filters set at once, **When** the table is shown, **Then** only parents
   matching all of them are listed, and the count of matches is shown.
9. **Given** a filtered and sorted table, **When** a visitor opens its address in a new browser,
   **Then** the same filters and order are applied.
10. **Given** a dataset or project the visitor may not see, **When** the visitor chooses a dataset
    or project to filter by, **Then** it is not offered.
11. **Given** filters that match no parents, **When** the table is shown, **Then** the visitor is
    told that nothing matches and can clear the filters.

---

### User Story 3 — A visitor sees a parent's children from its row (Priority: P1)

Each row shows how many children the parent has, followed in brackets by how many of them are
marked relevant: "4 (2)". The visitor selects the count and a window opens over the table listing
the parent's children. Relevant children come first, each carrying a badge that marks it relevant.
Each child shows its heat flow value with its uncertainty and its quality code, and links to its
own page. The visitor closes the window and is back at the table where they left it.

**Why this priority**: the request makes the count and its list a requirement. Whether a parent
rests on one child or several, and which of them were used, is what tells a reader how far to trust
the parent's value.

**Independent Test**: create a parent with three children, two marked relevant, open the table and
assert that its row shows "3 (2)". Open the list of children and assert that it shows all three,
the two relevant ones first and badged, the third last and unbadged, each linked to its page.

**Acceptance Scenarios**:

1. **Given** a parent with three children of which two are marked relevant, **When** a visitor
   opens the table, **Then** its row shows 3 (2).
2. **Given** a parent with children none of which is marked relevant, **When** a visitor opens the
   table, **Then** its row shows the number of children followed by (0).
3. **Given** a row, **When** a visitor selects its count, **Then** a window opens over the table
   listing every child of that parent.
4. **Given** the list of children, **When** it is shown, **Then** every relevant child comes before
   every child that is not relevant, and only the relevant ones carry the relevant badge.
5. **Given** the list of children, **When** it is shown, **Then** each child shows its heat flow
   value with its uncertainty and unit and its quality code, and links to its page.
6. **Given** an open list of children, **When** the visitor closes it, **Then** the table is shown
   with the same filters, order and page as before.
7. **Given** a table of many parents, **When** the visitor opens it, **Then** no child is loaded
   until the visitor asks for a parent's children.

---

### User Story 4 — A visitor finds the table beside the map viewer (Priority: P2)

A visitor opens the sidebar. Where the map viewer entry used to be there is now a group for the
GHFDB, which they can expand and collapse. Inside it are the map viewer, first, and the table.

**Why this priority**: the table needs a way in, but the address works without it, and the move of
the map viewer into the group is a rearrangement rather than something new a visitor can do.

**Independent Test**: render any page and assert that the sidebar has a collapsible group in the
place the map viewer entry held, containing the map viewer link followed by the table link, and
that the map viewer is no longer a top-level entry.

**Acceptance Scenarios**:

1. **Given** any page, **When** a visitor opens the sidebar, **Then** a collapsible group is shown
   in the position the map viewer entry held.
2. **Given** the group, **When** the visitor expands it, **Then** it holds the map viewer link
   followed by the table link, and each leads to its page.
3. **Given** the sidebar, **When** it is shown, **Then** the map viewer appears only inside the
   group.
4. **Given** a visitor on the table or the map viewer, **When** the sidebar is shown, **Then** the
   group is expanded and the current page's entry is marked as current.

### Edge Cases

- A negative heat flow value. Negative values are legitimate (CONTEXT.md), so they are listed,
  sorted and filtered like any other value, and a bound can be negative.
- A parent with no value in a filtered field. A bound on that field leaves it out, and with no bound
  set it is listed.
- Every parent has at least one child the visitor may see. A parent with no children is not a state
  the table has to present.
- A parent with many children. The list of children shows them all and stays usable.
- A filter value that is not valid, such as text in a numeric bound or an upper bound below the
  lower bound. The visitor is told which filter is wrong, and the table is not narrowed by it.

## Requirements

### Functional Requirements

**The table**

- **FR-001**: The portal MUST serve a table of parents that a visitor can open without signing in.
- **FR-002**: The table MUST list a parent only when the visitor may see both the parent and its
  site, by the rule the API's parent endpoint applies.
- **FR-003**: Each row MUST show the parent's published GHFDB columns, under the published column
  names, for heat flow, its uncertainty, site name, latitude, longitude, elevation, geographic
  environment, comment, heat production correction, total measured depth, total vertical depth,
  exploration method, exploration purpose and quality code.
- **FR-004**: Vocabulary-backed columns MUST show their vocabulary terms, never stored identifiers.
- **FR-005**: An empty cell MUST read as not recorded, distinguishable from zero.
- **FR-006**: Each row MUST link to the parent's page and to its site's page.
- **FR-007**: A visitor MUST be able to sort by any column in either direction.
- **FR-008**: The table MUST be paged, and MUST show how many parents match.

**Filtering**

- **FR-009**: A visitor MUST be able to set a lower bound, an upper bound or both on heat flow, heat
  flow uncertainty, elevation, total measured depth and total vertical depth.
- **FR-010**: A visitor MUST be able to restrict latitude and longitude to a box.
- **FR-011**: A visitor MUST be able to choose one or more values of geographic environment,
  exploration method, exploration purpose, heat production correction and quality code, and a
  parent matching any chosen value of a field passes that filter.
- **FR-012**: A visitor MUST be able to search the site name, ignoring case.
- **FR-013**: A visitor MUST be able to restrict the table to one or more datasets and to one or
  more projects, and MUST be offered only datasets and projects they may see.
- **FR-014**: Filters MUST combine, so a row is listed only when it passes every filter set.
- **FR-015**: The filters, sort order and page MUST be held in the table's address.
- **FR-016**: A filter value that is not valid MUST be reported to the visitor against that filter,
  and MUST not narrow the table.

**Children**

- **FR-017**: Each row MUST show the parent's number of children followed in brackets by the number
  of them marked relevant.
- **FR-018**: Selecting the count MUST open a window over the table that lists every child of the
  parent.
- **FR-019**: The list MUST put every relevant child before every child that is not relevant, and
  MUST mark each relevant child with a badge.
- **FR-020**: Each child in the list MUST show its heat flow value with its uncertainty and unit and
  its quality code, and MUST link to its page.
- **FR-021**: A parent's children MUST be fetched only when the visitor opens its list, never with
  the table.
- **FR-022**: Closing the list MUST return the visitor to the table unchanged.

**Navigation**

- **FR-023**: The sidebar MUST hold a collapsible GHFDB group in the position the map viewer entry
  holds today, containing the map viewer link and then the table link.
- **FR-024**: The map viewer MUST no longer appear as a top-level sidebar entry.

### Story mapping

| Story | Requirements |
|---|---|
| US-1 | FR-001 – FR-008 |
| US-2 | FR-009 – FR-016 |
| US-3 | FR-017 – FR-022 |
| US-4 | FR-023, FR-024 |

### Key Entities

No new entities. The table reads the existing parent records through the GHFDB parent proxy
(FS-002), with their sites, children, datasets and projects.

- **GHFDB parent table**: the page this feature adds. Needs a CONTEXT.md entry so that it is not
  called "the database" and is not confused with the map viewer.

## Success Criteria

- **SC-001**: Every parent a visitor may see can be found in the table, and no parent they may not
  see is listed or counted.
- **SC-002**: For any combination of filters, the rows listed are exactly the parents that match all
  of them.
- **SC-003**: Opening the table does not load any child records, whatever the number of parents.
- **SC-004**: Every count shown on a row equals the number of children in that parent's list, and
  the bracketed number equals the number of badged children in it.

## Clarifications

### Session 2026-10-23

- Q: Can a parent have no visible children? → A: No. A parent always has at least one child the
  visitor may see, so the table never presents an empty list of children.
- Q: What does the count show? → A: The number of children, then the number marked relevant in
  brackets: "n (m)".
- Q: Which children does the list show, and in what order? → A: All of the parent's children.
  Relevant children come first and carry a badge marking them relevant.
- Q: Which parents does the table list? → A: Those whose dataset and site the visitor may both see,
  the rule FS-006 applies to the API's parent endpoint, so the table and the API never disagree.
- Q: Are the columns the published GHFDB names or the data model's names? → A: The published names.
  The table is a GHFDB view of the parents, built on the GHFDB parent proxy.
- Q: Which FairDM records can the table be filtered by? → A: Dataset and project, the two a parent
  belongs to. Filtering by contributor is not part of this feature.
- Q: Is a row linked anywhere? → A: Yes, to the parent's page and to its site's page, which FS-011
  fills with heat flow content.

## Assumptions

- The portal is on the latest FairDM, django-mvp and django-mvp-forms before the build starts. That
  upgrade is its own change and lands first.
- Downloading the filtered rows is not part of this feature. The download of the database stays
  with R8.
- The map viewer itself is unchanged. Only its place in the sidebar moves. Bringing it into the
  portal is R12.
- The table lists parents only. A table of children, sites or datasets is not part of this feature.
- The heat flow determination list and its empty columns (#248) are a separate table and are not
  touched.
