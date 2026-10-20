# Feature Specification: Heat flow content on the site and measurement overview pages

**Feature Branch**: `011-heat-flow-overview-pages`

**Created**: 2026-10-20

**Status**: Draft

**Goals**: G7, the published GHFDB freely reachable by anyone with no account, because this page is
what most people outside the assessment team read. G1, the normalised relational model, because the
page is where that model's relationships between site, interval, child, gradient, conductivity and
parent become visible to a reader.

**Roadmap**: none. No roadmap item covers the record pages.

**References**: FS-001 (the heat flow data model), FS-007 (quality scores), ADR 0023 (a site holds
the location and its own elevation); FairDM's overview pages guide
(`docs/portal-development/overview-pages.md` in FairDM) and FairDM ADR 0023 (an overview page is
extended through blocks, plugin methods and type templates); [CONTEXT.md](../../CONTEXT.md)

**Intake**: https://github.com/ihfc-iugg/ghfdb-portal/issues/288

## Overview

Every heat flow site, depth interval and heat flow measurement in the portal has an overview page.
FairDM draws that page from its base `Sample` or `Measurement` model, so today it shows what any
sample or measurement in any FairDM portal would show: a name, a dataset, a timeline, people, a
citation, and a value with its uncertainty where the type has one. None of what makes the record a
heat flow record is on it. A site page does not show the site's parent value or how its heat flow
was determined. A child page does not show the gradient and conductivity it was calculated from,
the corrections recorded for it, or its quality code. The quality card FS-007 built is on no page
at all, because the measurement page it sat on was replaced by FairDM's overview.

This feature puts the heat flow content on those pages. A visitor reading a site sees its parent
value and quality, and the intervals and children beneath it. A visitor reading a child sees what
it was calculated from, the corrections applied and how its quality code was reached. The gradient,
conductivity, parent and interval pages show their own records in the same way, and every page
links to the records it names, so a reader can walk the whole record from any point in it.

Most people who open these pages are not on the assessment team. They are researchers deciding
whether a value is comparable with theirs, and the page should answer that without sending them to
the API or a download.

The pages keep everything FairDM already gives them: the header, the people, the citation, the
identifiers, who may open the page and the Manage menu. The heat flow content is added to them.

## User Scenarios & Testing

A **visitor** in these stories is anyone reading the portal, signed in or not. They see a record
when FairDM's rules let them open its page: once its dataset is public and published, or when they
hold a level on the record, its dataset or its project.

### User Story 1 — A visitor reads a child's heat flow and how it was reached (Priority: P1)

A visitor opens a child heat flow value's page. They see the value and its uncertainty, the method
used, and the depth interval and site it was determined over. They see the thermal gradient and
interval conductivity it was calculated from, each with its value, and can follow either to its own
page. They see every correction recorded for the child, each with its status, so they can tell a
correction that was applied from one that was needed and not applied. They see the child's quality
code, its U-score and M-score, the gradient's and conductivity's own scores beside the corrected
scores this child reached, the missing-information mark where it applies, the seven perturbation
flags and the scheme revision. They see the parent the child belongs to and whether it was used in
deriving that parent's value.

**Why this priority**: the child is the heat flow determination itself, and judging whether its
value is comparable is the question most readers bring.

**Independent Test**: render the page of a child that has a gradient, a conductivity, corrections,
a parent and stored quality scores, and assert that each of them is present and that the gradient,
conductivity, interval, site and parent are linked.

**Acceptance Scenarios**:

1. **Given** a child with a gradient and a conductivity, **When** a visitor opens its page,
   **Then** the page shows the gradient's value and the conductivity's value, each with its unit,
   and links to each one's page.
2. **Given** a child with corrections recorded, **When** a visitor opens its page, **Then** every
   recorded correction is shown with its correction type and its status.
3. **Given** a child whose corrections changed its T-score, **When** a visitor opens its page,
   **Then** the gradient's own T-score and the child's corrected T-score are both shown.
4. **Given** any scored child, **When** a visitor opens its page, **Then** its quality code,
   U-score, M-score, perturbation flags and scheme revision are shown as stored.
5. **Given** a child scored under a scheme revision that is not the current one, **When** a visitor
   opens its page, **Then** the page says the score is stale.
6. **Given** a child that belongs to a parent, **When** a visitor opens its page, **Then** the page
   links to the parent and shows whether the child is marked relevant to it.
7. **Given** a child, **When** a visitor opens its page, **Then** the page names its depth interval
   with its depth range and its site, and links to both.

---

### User Story 2 — A visitor reads a site's heat flow (Priority: P1)

A visitor opens a site's page. They see the site's parent heat flow value, its uncertainty and its
quality code, and can follow it to the parent's page. They see the site's own heat flow description:
its geographic environment, its exploration method and purpose, its access geometry and where it
lies. They see the site's depth intervals in depth order, each with its depth range, and the children
determined over each interval with each child's value and quality code, so they can see the whole
site at once and follow any record to its page.

**Why this priority**: the site is where most readers arrive from the map, and the parent value is
the number the published database gives for it.

**Independent Test**: render the page of a site with a parent and two intervals, one carrying two
children, and assert that the parent value and quality code, both intervals in depth order and all
three children are present and linked.

**Acceptance Scenarios**:

1. **Given** a site with a parent, **When** a visitor opens its page, **Then** the page shows the
   parent's value with its uncertainty and unit and its quality code, and links to the parent's
   page.
2. **Given** a site with no parent, **When** a visitor opens its page, **Then** the page says no
   parent value has been designated.
3. **Given** a site with several intervals, **When** a visitor opens its page, **Then** the
   intervals are listed from shallowest to deepest, each with its depth range.
4. **Given** an interval carrying several children, **When** a visitor opens the site's page,
   **Then** each child is listed under that interval with its value and quality code, and links to
   its page.
5. **Given** a site, **When** a visitor opens its page, **Then** its geographic environment,
   exploration method and exploration purpose are shown with their vocabulary terms.

---

### User Story 3 — A visitor reads a gradient's or a conductivity's own record (Priority: P2)

A visitor opens a thermal gradient's page and sees its measured and corrected values with their
uncertainties, the temperature methods and corrections at the top and bottom of the interval, the
shut-in times, the temperatures and the number of recordings. A visitor opens an interval
conductivity's page and sees its value and uncertainty, its source, method, strategy, saturation,
pT conditions and pT function, and the number of measurements. On either page they see the
measurement's own score with its missing-information mark and scheme revision, the depth interval
and site it was measured over, and the children that use it, each linked.

**Why this priority**: a reader following a child to what it was calculated from needs these pages
to answer the next question, but few readers start here.

**Independent Test**: render a gradient's page and a conductivity's page, each used by two children,
and assert that the measurement's own fields, its score and both children are present and linked.

**Acceptance Scenarios**:

1. **Given** a gradient with measured and corrected values, **When** a visitor opens its page,
   **Then** both are shown with their uncertainties and units.
2. **Given** a conductivity, **When** a visitor opens its page, **Then** each of its
   vocabulary-backed fields is shown with its vocabulary terms.
3. **Given** a gradient or a conductivity with a stored score, **When** a visitor opens its page,
   **Then** its own score, its missing-information mark where set, and its scheme revision are
   shown.
4. **Given** a gradient or a conductivity whose score is not determined, **When** a visitor opens
   its page, **Then** the page says the score is not determined and never shows it as zero.
5. **Given** a gradient used by two children, **When** a visitor opens its page, **Then** both
   children are listed and linked.

---

### User Story 4 — A visitor reads how a parent's value and quality were reached (Priority: P2)

A visitor opens a parent heat flow value's page. They see its value and uncertainty, whether a
heat production correction was applied, the curator's comment and its GHFDB id. They see its
quality code, U-score, M-score, flags and scheme revision, and which children that quality rests on.
They see every child of the parent, each with its value and quality code and whether it is marked
relevant, and the site the parent represents.

**Why this priority**: a parent is designated by curators, not calculated, so a reader needs to
see which children stand behind it to trust it. It follows the site and child stories because both
already show the parent's value.

**Independent Test**: render the page of a parent with three children, two marked relevant, and
assert that all three children are listed with their relevance, that the two relevant ones are the
ones its quality is said to rest on, and that the site is linked.

**Acceptance Scenarios**:

1. **Given** a parent with several children, **When** a visitor opens its page, **Then** every
   child is listed with its value, its quality code and whether it is marked relevant, and links to
   its page.
2. **Given** a parent with several children and some marked relevant, **When** a visitor opens its
   page, **Then** the page identifies the relevant children as those its quality rests on.
3. **Given** a parent with exactly one child, **When** a visitor opens its page, **Then** the page
   identifies that child as the one its quality rests on, whether or not it is marked relevant.
4. **Given** a parent with several children and none marked relevant, or with no children, **When**
   a visitor opens its page, **Then** the page says why its quality could not be determined.
5. **Given** a parent, **When** a visitor opens its page, **Then** the page links to its site.

---

### User Story 5 — A visitor reads a depth interval and where it lies (Priority: P3)

A visitor opens a depth interval's page. They see its depth range, its vertical depth and datum,
the lithology, stratigraphy and age of the rock in it, and the probe metadata where a marine probe
was used. They see the site it belongs to, linked, and the site's location, because an interval
holds no location of its own. The measurements made on it are listed as FairDM already lists them.

On a child's, gradient's or conductivity's page, the location shown is likewise the site's.

**Why this priority**: the interval is the physical thing the measurements were made on, but a
reader usually reaches it from a site or a child that already names its depth range.

**Independent Test**: render the page of an interval with probe metadata at a site with a location,
and assert that the depth range, the probe metadata, the link to the site and the site's coordinates
are present. Render a child on that interval and assert that its page shows the same coordinates.

**Acceptance Scenarios**:

1. **Given** an interval, **When** a visitor opens its page, **Then** its depth range and the
   lithology, stratigraphy and age recorded for it are shown, and its site is linked.
2. **Given** an interval with probe metadata, **When** a visitor opens its page, **Then** the probe
   type, length, penetration and tilt are shown with their units.
3. **Given** an interval at a site with a location, **When** a visitor opens the interval's page or
   the page of a measurement made on it, **Then** the page shows the site's location and says it is
   the site's.
4. **Given** an interval whose site has no location, **When** a visitor opens its page, **Then** the
   page says no location is recorded.

### Edge Cases

- A field with no value. An empty field is shown as not recorded, and is never shown as zero or
  left looking like a value. This matters most for scores, where empty means not determined.
- A child with no gradient or no conductivity. The page says which one is not recorded and still
  shows everything else.
- A child with no corrections recorded. The page says none are recorded. This is different from
  a correction recorded with the status "not recognised", which is shown as recorded.
- A child with no parent. The page says the child belongs to no parent.
- Records the visitor may not see. A page lists and links only the records the visitor may open,
  by the same rules FairDM applies to the record's own page. Records they may not see are never named
  or linked. Where a list leaves records out for this reason, it says how many.
- A site with many intervals or children. A borehole can have hundreds of intervals. The page
  stays usable: where it shows only some of a list, it says how many more there are and offers a
  way to see them.
- A record with no quality score yet. A child or parent whose scores are empty shows them as not
  determined, never as the poorest grade.

## Requirements

### Functional Requirements

**Every heat flow page**

- **FR-001**: Each heat flow site, depth interval, child, thermal gradient, interval conductivity and
  parent page MUST show the record's own heat flow fields in addition to what FairDM's shared page
  shows. The fields shown for each type are those its stories name.
- **FR-002**: Every quantity MUST be shown with its unit.
- **FR-003**: Every vocabulary-backed field MUST be shown as its vocabulary terms, never as stored
  identifiers.
- **FR-004**: An empty field MUST be shown as not recorded, distinguishable from a zero. An empty
  score MUST be shown as not determined.
- **FR-005**: Every record a page names (site, interval, child, gradient, conductivity, parent) MUST
  link to that record's page.
- **FR-006**: A page MUST name and link only the records the visitor may open, by FairDM's rules for
  opening that record's page, and MUST say how many it leaves out.
- **FR-007**: Where a page shows only part of a list, it MUST say how many records it does not show
  and give the visitor a way to see them.
- **FR-008**: Scores and quality codes MUST be shown as stored. A page MUST never calculate a score.
- **FR-009**: The pages MUST keep everything FairDM's shared page provides: the header and its
  Manage menu, people, identifiers, citation, timeline and who may open the page.

**Child**

- **FR-010**: A child's page MUST show its thermal gradient and interval conductivity, each with its
  value and unit.
- **FR-011**: A child's page MUST show every correction recorded for it, with its correction type and
  status, and MUST say when none is recorded.
- **FR-012**: A child's page MUST show its quality code, U-score, M-score, the gradient's and
  conductivity's own scores beside its corrected scores, the missing-information marks, the seven
  perturbation flags and the scheme revision.
- **FR-013**: A child's page MUST show its depth interval with its depth range, its site, and its
  parent with whether the child is marked relevant to it.

**Site**

- **FR-014**: A site's page MUST show its parent's value, uncertainty and quality code, or say that
  no parent has been designated.
- **FR-015**: A site's page MUST list its depth intervals from shallowest to deepest, each with its
  depth range and the children determined over it, each child with its value and quality code.

**Gradient and conductivity**

- **FR-016**: A gradient's or conductivity's page MUST show its own score with its
  missing-information mark and scheme revision.
- **FR-017**: A gradient's or conductivity's page MUST show its depth interval, its site, and the
  children that use it.

**Parent**

- **FR-018**: A parent's page MUST list every child with its value, quality code and whether it is
  marked relevant.
- **FR-019**: A parent's page MUST identify the children its quality rests on, by the inheritance
  rule in CONTEXT.md, and say why its quality was not determined when it rests on none.
- **FR-020**: A parent's page MUST show its heat production correction, its comment and its GHFDB
  id, and link to its site.

**Interval and location**

- **FR-021**: An interval's page MUST show its depth range, vertical depth and datum, lithology,
  stratigraphy and age, its probe metadata where it has any, and its site.
- **FR-022**: The page of an interval, and of a child, gradient or conductivity made on one, MUST
  show its site's location as the site's, or say that no location is recorded.

**Staleness**

- **FR-023**: Where a stored score's scheme revision is not the current one, the page MUST say the
  score is stale.

### Story mapping

| Story | Requirements |
|---|---|
| US-1 | FR-001 – FR-013, FR-023 |
| US-2 | FR-001 – FR-009, FR-014, FR-015 |
| US-3 | FR-001 – FR-009, FR-016, FR-017, FR-023 |
| US-4 | FR-001 – FR-009, FR-018 – FR-020, FR-023 |
| US-5 | FR-001 – FR-009, FR-021, FR-022 |

### Key Entities

No new entities. The pages read the existing heat flow site, depth interval, child, thermal
gradient, interval conductivity, correction, probe metadata and parent records, and the quality
scores FS-007 stores on them.

- **Visitor**: anyone reading the portal, signed in or not, limited to the records FairDM lets them
  open. Used in this spec only. It is not a role and needs no CONTEXT.md entry.

## Success Criteria

- **SC-001**: Every value the release format carries for a child and its parent and site can be
  read on the page of the child, its parent, its site or the dataset they belong to, so a visitor
  needs no download to see a published row.
- **SC-002**: From any heat flow record's page, a visitor can reach every other record of the same
  site that they may open by following links alone.
- **SC-003**: Every quality score a page shows equals the score stored on the record.

## Clarifications

### Session 2026-10-20

- Q: Is the depth interval's page in scope, when the request names the site, child, gradient,
  conductivity and parent pages? → A: Yes, at the lowest priority. The request opens with "every
  site and measurement", an interval is a sample with a page of its own, and without this feature
  that page and every measurement page on an interval would say no location is recorded, because
  the site holds the location (ADR 0023).
- Q: Which location do the interval and measurement pages show? → A: The site's, said to be the
  site's. FairDM falls back to the sample's location, and an interval has none.
- Q: What does "how it was reached" mean for a child's quality code? → A: What FS-007's quality card
  showed: the gradient's and conductivity's own scores beside the corrected scores the child's
  corrections produced, the U-score and M-score built from them, the flags and the scheme revision.
  Showing the criteria and penalties behind each score is not part of this feature. The quality
  scores guide explains them.
- Q: What does "how it was reached" mean for a parent? → A: Which children its quality rests on, by
  the inheritance rule. A parent's value is designated by curators and is not explained by the page
  beyond its comment and its children.
- Q: Does a visitor see records from datasets they may not open? → A: No. Each listed record is
  shown only when its own page would open for the visitor, the same rule FairDM applies to the
  records it already lists, and hidden records are counted, never named.

## Assumptions

- FairDM's overview pages at the pinned version are what these pages extend. Nothing in this feature
  needs a newer FairDM.
- Editing and adding records is not part of this feature. The forms are #286, and the Manage menu
  FairDM provides is kept as it is.
- The API representation of these records is #287 and the published-structure API is FS-006.
  Neither is part of this feature.
- Search, filters and the map are not part of this feature. A page is reached the way it is reached
  today.
- Scores are those FS-007 stores. When a score is stale the page says so and does not recalculate
  it.
