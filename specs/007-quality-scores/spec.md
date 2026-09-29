# Feature Specification: Quality scores calculated with the current community scheme

**Feature Branch**: `007-quality-scores`

**Created**: 2026-09-29

**Status**: Draft

**Goals**: G6 — quality scores computed by the portal and authoritative over anything supplied

**Roadmap**: R9

**References**: Heat Flow Quality Analysis Toolbox (hfqa_tool) V0.2, Dergunova et al. (2026),
doi:10.5880/fidgeo.2026.032; Fuchs et al. (2023), Tectonophysics 863:229976; Neumann et al. (2026),
ESSD 18:4639–4668, section 4.1; ADR-0004; [CONTEXT.md](../../CONTEXT.md)

**Intake**: https://github.com/ihfc-iugg/ghfdb-portal/issues/232

## Overview

The heat flow community grades every heat flow determination with a quality scheme in three parts:

- a **U-score** for numerical uncertainty
- an **M-score** for methodological reliability
- seven **perturbation flags** recording which disturbing effects were recognised and whether they
  were corrected

The M-score is built from two sub-scores: a **T-score** for how the temperature gradient was
determined and a **TC-score** for how the thermal conductivity was determined. The product of the
two places the determination in one of four classes. A parent value inherits the poorest grades
among the children it rests on.

The portal already decided that it calculates these scores itself and that its values are
authoritative (ADR-0004). It holds a scoring module written against the 2023 paper, but nothing
calls it, it reads fields the data model no longer has, and the community has since moved on. The
2024 GHFDB release was scored with version 0.2 of the community's toolbox, which revises several of
the paper's rules. This feature makes the portal's scores real, and makes them follow that
version.

The scores are held where the data they describe is held. A thermal gradient carries its own
T-score and an interval conductivity its own TC-score, calculated only from the measurement, its
interval and its site. The same gradient or conductivity can be used by several children, and it
carries one score however many use it.

Three of the scheme's rules depend on something recorded on the child rather than on the
measurement:

- A probe gradient's tilt penalty is waived when the child records a tilt correction.
- A probe gradient's water depth penalty is waived when the child records a bottom-water
  temperature correction.
- A borehole conductivity's pT conditions only earn their score when the child's in-situ correction
  agrees with them.

So the score a measurement carries is its **uncorrected** score, and each child applies those three
rules to reach its own **corrected** T-score and TC-score. The child keeps both, so the effect of
its corrections is visible and a query on the corrected scores returns the right children. The
child's M-score comes from its corrected scores.

## User Scenarios & Testing

### User Story 1 — A gradient and a conductivity carry their own scores (Priority: P1)

When a thermal gradient or an interval conductivity is stored or changed, the portal scores it
against the probe-sensing or the borehole and mine rules. Which set applies is decided by its
site's exploration method. The score records whether any information it needed was missing, and it
is the same for every child that uses the measurement.

**Why this priority**: the sub-scores are the foundation everything else is built from. With these
alone, the assessment team can see where the methodological weaknesses in a dataset lie.

**Independent Test**: build gradients and conductivities at probe and borehole sites across the
scheme's criteria, and compare their scores with what toolbox version 0.2 gives for the same inputs.

**Acceptance Scenarios**:

1. **Given** a gradient at a site explored by probing, **When** it is scored, **Then** its T-score
   is the probe-sensing T-score for its probe penetration, number of temperature recordings, water
   depth and probe tilt, with no correction applied.
2. **Given** a gradient at a site explored by drilling, mining or tunnelling, **When** it is scored,
   **Then** its T-score is the borehole T-score for its temperature methods at top and bottom and
   its number of temperature recordings.
3. **Given** a conductivity at a probe or a borehole site, **When** it is scored, **Then** its
   TC-score is the matching scheme's TC-score for its location, source, method, saturation, number
   of measurements and pT conditions.
4. **Given** a borehole conductivity whose interval reports neither a top nor a bottom depth,
   **When** it is scored, **Then** its TC-score is the scheme's fixed minimum and is marked as
   reached with missing information.
5. **Given** a measurement where an input the scheme reads is empty, **When** it is scored, **Then**
   that criterion takes its largest penalty and the score is marked as reached with missing
   information.
6. **Given** a measurement where an input is explicitly recorded as unspecified, **When** it is
   scored, **Then** that criterion takes its largest penalty and the score is not marked as missing
   information.
7. **Given** a measurement at a site whose exploration method is empty, unspecified or neither
   probing nor drilling, mining, tunnelling or an indirect method, **When** it is scored, **Then**
   its score is recorded as not determined.
8. **Given** one gradient used by two children with different corrections, **When** both children
   are read, **Then** the gradient's own T-score is the same for both.

---

### User Story 2 — A child carries its quality code (Priority: P1)

Each child heat flow value carries a U-score from its value and uncertainty, a corrected T-score and
TC-score, an M-score, its seven perturbation flags and the quality code they make together.

**Why this priority**: the child is where the scheme grades a determination. Its quality code is
what a data user reads and what an export carries.

**Independent Test**: build children with known values, uncertainties, measurements and corrections,
and compare the code each carries with toolbox version 0.2's code for the same row, apart from the
documented split between uncorrected and corrected sub-scores.

**Acceptance Scenarios**:

1. **Given** a child with a value and a nonzero uncertainty, **When** it is scored, **Then** its
   U-score is the class the scheme assigns to its uncertainty as a percentage of its value.
2. **Given** a child whose value is empty or zero, or whose uncertainty is empty or zero, **When**
   it is scored, **Then** its U-score is not determined.
3. **Given** a probe child that records a tilt correction, **When** it is scored, **Then** its
   corrected T-score carries no tilt penalty, while its gradient's own T-score still does.
4. **Given** a probe child that records its surface and bottom-water correction as present and
   corrected, **When** it is scored, **Then** its corrected T-score carries no water depth penalty,
   while its gradient's own T-score still does.
5. **Given** a borehole child whose in-situ correction does not agree with its conductivity's pT
   conditions, **When** it is scored, **Then** its corrected TC-score takes the pT criterion's
   largest penalty.
6. **Given** a child with none of those three corrections, **When** it is scored, **Then** its
   corrected T-score and TC-score equal its measurements' own scores.
7. **Given** a child's corrected T-score and TC-score, **When** it is scored, **Then** its M-score
   is the class their product falls in, marked as reached with missing information if either
   corrected score was.
8. **Given** a child whose corrected scores' product is exactly on a class boundary, **When** it is
   scored, **Then** it takes the better of the two classes.
9. **Given** a child whose gradient or conductivity is absent, or whose score is not determined,
   **When** it is scored, **Then** its M-score is not determined.
10. **Given** a child's corrections, **When** it is scored, **Then** each of its seven perturbation
    flags records whether that effect was recognised, whether it was corrected, or that no
    information is held.
11. **Given** a scored child, **When** its record is read, **Then** it carries a quality code
    combining its U-score, its M-score and its seven perturbation flags.
12. **Given** children whose corrected T-scores differ from their gradients' own scores, **When**
    children are queried by corrected T-score or corrected TC-score, **Then** exactly the children
    whose own corrected score matches are returned.

---

### User Story 3 — A parent inherits its quality from its children (Priority: P2)

A parent heat flow value carries the poorest U-score and the poorest M-score among the children it
rests on, and the perturbation flags of its poorest child.

**Why this priority**: a parent is what a map plots and what most data users look at first. It
depends on children being scored, so it comes second.

**Independent Test**: build parents with one child, with several children all relevant, and with
several children only some relevant, and compare each parent's code with the rule.

**Acceptance Scenarios**:

1. **Given** a parent with exactly one child, **When** its quality is derived, **Then** it carries
   that child's quality code.
2. **Given** a parent with several children marked relevant, **When** its quality is derived,
   **Then** its U-score is the poorest U-score among them and its M-score the poorest M-score among
   them.
3. **Given** a parent with several children of which only some are marked relevant, **When** its
   quality is derived, **Then** the children not marked relevant play no part.
4. **Given** a parent with several children and none marked relevant, **When** its quality is
   derived, **Then** its quality is not determined.
5. **Given** a parent's relevant children, **When** its perturbation flags are derived, **Then**
   they are the flags of the child with the poorest U-score, with the poorest M-score deciding a tie.
6. **Given** relevant children with M-scores that are and are not marked as reached with missing
   information, **When** the poorest is chosen, **Then** any marked M-score counts as poorer than
   any unmarked one, and a not-determined M-score counts as poorest of all.
7. **Given** a parent whose quality is derived, **When** its value is read, **Then** it is unchanged.
   Quality is inherited and the value stays designated.

---

### User Story 4 — Scores stay current (Priority: P2)

Every score is recalculated whenever one of its inputs changes, wherever that change is made, and
records which revision of the scheme produced it. Records already in the portal are scored when
the feature ships.

**Why this priority**: a stored score that goes stale without anyone noticing is worse than none.
It is the objection ADR-0004 raises against supplied codes.

**Independent Test**: change each kind of input and assert that every score depending on it, and
only those, now reflects the change.

**Acceptance Scenarios**:

1. **Given** a gradient or a conductivity used by several children, **When** it is changed, **Then**
   its own score, every child using it and every parent above those children are recalculated.
2. **Given** a change to an interval's depths or probe metadata, or to a site's elevation or
   exploration method, **When** it is saved, **Then** every score reading it is recalculated.
3. **Given** a change to a child's value, uncertainty, corrections, relevance, gradient or
   conductivity, **When** it is saved, **Then** that child and its parent are recalculated.
4. **Given** a dataset imported from a file, **When** the import completes, **Then** every record it
   wrote carries its scores.
5. **Given** any stored score, **When** it is read, **Then** the revision of the scheme it was
   calculated under can be read with it.
6. **Given** records that existed before this feature, **When** the feature is deployed, **Then**
   every one of them carries its scores without anyone re-entering data.
7. **Given** the scores are recalculated for records whose inputs have not changed, **When** the
   results are compared with the stored ones, **Then** they are identical.

---

### User Story 5 — A reader sees how a child's quality was reached (Priority: P3)

A child's page shows its U-score, its gradient's and conductivity's own scores beside its corrected
scores, its M-score, its perturbation flags and its quality code. A gradient's and a conductivity's
pages show their own score.

**Why this priority**: the split between uncorrected and corrected scores exists so that the effect
of a correction can be seen. Until it is shown, only someone querying the database can see it.

**Independent Test**: render a child's page where a correction changed a sub-score, and assert that
both the uncorrected and the corrected value are present in the rendered page.

**Acceptance Scenarios**:

1. **Given** a child whose corrections changed its T-score, **When** its page is viewed, **Then**
   its gradient's own T-score and its corrected T-score are both present.
2. **Given** any scored child, **When** its page is viewed, **Then** its U-score, M-score,
   perturbation flags and quality code are present, and so is a mark on any score reached with
   missing information.
3. **Given** a gradient or a conductivity, **When** its page is viewed, **Then** its own score is
   present.

---

### Edge Cases

- A negative heat flow value is legitimate. Its uncertainty is taken as a percentage of the value's
  magnitude, never refused for being negative.
- A multi-valued vocabulary field that matches several of a criterion's classes takes the poorest
  of them.
- A value that is present but fits none of a criterion's classes takes the largest penalty without
  being marked as missing information, except where the scheme says otherwise (a borehole
  conductivity's location).
- A probe site whose elevation is zero or above sea level has no usable water depth and is treated
  as missing that information.
- A child that is the only child of its parent and is not marked relevant still passes its quality
  to the parent.
- Deleting a child recalculates its parent. Deleting the last child leaves the parent not
  determined.
- A quality code in an imported file is still refused, as ADR-0004 requires. Calculating scores
  never reads one.

## Requirements

### Functional Requirements

- **FR-001**: The portal MUST calculate the U-score, T-score, TC-score, M-score and perturbation
  flags as toolbox version 0.2 defines them, except where a decision recorded in this spec's
  decisions resolves a conflict between that version and its own documentation.
- **FR-002**: Every thermal gradient MUST carry its own T-score and every interval conductivity its
  own TC-score. Each MUST be calculated only from the measurement, its interval and its site, and
  MUST record whether it was reached with missing information.
- **FR-003**: The probe-sensing rules MUST apply to a measurement at a site whose exploration method
  is a form of probing. The borehole and mine rules MUST apply where it is drilling, mining,
  tunnelling or an indirect method. The score MUST be not determined where it is anything else.
- **FR-004**: Every child MUST carry a corrected T-score and a corrected TC-score. These are its
  measurements' own scores, adjusted by exactly three rules that read the child's corrections: the
  probe tilt correction, the probe bottom-water temperature correction, and the borehole in-situ pT
  agreement.
- **FR-005**: A child's corrected T-score and TC-score MUST be stored on the child, so that they
  can be queried directly.
- **FR-006**: Every child MUST carry a U-score, an M-score, seven perturbation flags and a quality
  code.
- **FR-007**: A child's M-score MUST be the class of the product of its corrected T-score and
  TC-score, rounded to three decimal places. The classes are M1 from 0.75, M2 from 0.50, M3 from
  0.25 and M4 below 0.25, and a product on a boundary takes the better class.
- **FR-008**: An M-score MUST be marked as reached with missing information when either corrected
  score was. An M-score MUST be not determined when either corrected score cannot be calculated.
- **FR-009**: A score MUST be marked as reached with missing information only where an input it
  needed is empty, or where the scheme names a specific case. An input explicitly recorded as
  unspecified MUST take the largest penalty without the mark.
- **FR-010**: The quality code MUST be written as the U-score, the M-score and the seven
  perturbation flags separated by full stops, for example `U1.M2.SxxxCxR` or `U2.M3x.-e-PX--`.
- **FR-011**: The perturbation flags MUST be, in order, sedimentation, erosion, topography,
  paleoclimate, surface and bottom-water temperature variation, convection, and heat refraction,
  written `S E T P V C R`. Each MUST be the upper-case letter when the effect is present and
  corrected, lower-case when present and not corrected, `X` when present and not significant, `x`
  when not recognised, and `-` when no information is held.
- **FR-012**: Every parent MUST carry a U-score, an M-score, perturbation flags and a quality code
  inherited from its children as User Story 3 describes. A parent's value MUST never be changed by
  this inheritance.
- **FR-013**: Every stored score MUST be recalculated whenever an input it reads changes, whether
  the change is made through a form, an import, the admin or code. This includes a change to a
  measurement shared by several children.
- **FR-014**: Every record carrying scores MUST record the revision of the scheme they were
  calculated under.
- **FR-015**: Every record already in the portal when the feature is deployed MUST be scored as part
  of that deployment.
- **FR-016**: Recalculating the scores of a record whose inputs have not changed MUST give the
  scores already stored.
- **FR-017**: The existing scoring module written against the 2023 paper, and the scoring methods on
  the models that conflict with it, MUST be replaced. The portal MUST end with one implementation of
  the scheme.
- **FR-018**: A child's page MUST show its U-score, its measurements' own scores beside its
  corrected scores, its M-score, its perturbation flags and its quality code. A gradient's and a
  conductivity's pages MUST show their own score.
- **FR-019**: The portal's glossary MUST define the T-score, the TC-score, uncorrected and corrected
  scores, the missing-information mark and the scheme revision, and its description of the quality
  code MUST match the code this feature writes.
- **FR-020**: The scheme as the portal implements it MUST be documented for a data user, including
  the toolbox version it follows, the decisions it takes where the sources conflict, and how the
  portal's uncorrected and corrected sub-scores relate to the toolbox's own.

### Story mapping

| Story | Requirements |
|---|---|
| US1 | FR-001, FR-002, FR-003, FR-009, FR-017, FR-019, FR-020 |
| US2 | FR-001, FR-004, FR-005, FR-006, FR-007, FR-008, FR-009, FR-010, FR-011, FR-017, FR-019 |
| US3 | FR-012, FR-019 |
| US4 | FR-013, FR-014, FR-015, FR-016 |
| US5 | FR-018 |

The glossary and documentation requirements (FR-019, FR-020) are met by the story that introduces
each term, not collected at the end.

### Key Entities

- **T-score**: a thermal gradient's score for how its temperature gradient was determined. Held
  uncorrected on the gradient and corrected on each child.
- **TC-score**: an interval conductivity's score for how its thermal conductivity was determined.
  Held uncorrected on the conductivity and corrected on each child.
- **U-score, M-score, perturbation flags**: a child's three graded components, each inherited by its
  parent.
- **Quality code**: the U-score, M-score and perturbation flags written as one string, held on
  children and parents.
- **Scheme revision**: the version of the community scheme a stored score was calculated under.

## Success Criteria

- **SC-001**: For every worked example the toolbox's test data provides, the portal gives the same
  U-score, M-score and perturbation flags, apart from the documented split between uncorrected and
  corrected sub-scores.
- **SC-002**: Every child and every parent in the portal carries a quality code, and none carries a
  code taken from an imported file.
- **SC-003**: A measurement used by several children carries one score, the same whichever child it
  is read through.
- **SC-004**: After any change to any input, no stored score differs from a fresh calculation over
  the same data.
- **SC-005**: Every stored score can be traced to the scheme revision that produced it.
- **SC-006**: The portal holds exactly one implementation of the quality scheme.

## Clarifications

### Session 2026-09-29

- **Q: Which version of the scheme does the portal follow: the 2023 paper or the toolbox that scored
  the 2024 release?**
  A: Toolbox version 0.2 (Dergunova et al., 2026). It is the version the 2024 GHFDB release was
  scored with, and the ESSD paper describing that release names it. The 2023 paper remains the
  scheme's conceptual reference. Where the two differ, the toolbox decides. The differences are
  listed in [decisions.md](decisions.md).

- **Q: What makes a stored score "uncorrected", and how can a corrected score be lower than it?**
  A: The uncorrected score reads nothing that belongs to a child. Two of the three child-dependent
  rules can only waive a penalty, so a corrected T-score is never below the uncorrected one. The
  third, the borehole pT agreement, can only impose one. The uncorrected TC-score scores the
  conductivity's pT conditions on their own terms, and the child's corrected TC-score applies the
  toolbox's requirement that its in-situ correction agrees. "Corrected" means "with the child's
  corrections taken into account", not "improved".

- **Q: Does a missing-information mark on an uncorrected score survive into the corrected one?**
  A: Only if the information is still missing once the child's corrections are applied. A probe
  gradient with no recorded tilt is marked missing information. A child recording a tilt
  correction waives the tilt criterion entirely, as the toolbox does, so that child's corrected
  T-score carries no mark from tilt.

- **Q: What does a parent inherit when it has one child that is not marked relevant?**
  A: That child's quality. The 2023 paper says a single child's score "is simply passed to the
  parent level", and a parent with one child rests on it whatever the flag says. With several
  children and none marked relevant there is nothing the parent rests on, so its quality is not
  determined.

- **Q: Where must the portal's scores agree with the toolbox's, given the uncorrected and corrected
  split?**
  A: On everything a data user compares: the U-score, the M-score, the perturbation flags and the
  quality code. The toolbox reports one T and one TC per row, and those equal the child's corrected
  scores, not its measurements' uncorrected ones. The documentation says so (FR-020).

## Assumptions

- The inputs the scheme reads already have fields in the portal's data model. Where the toolbox
  names a published column, the portal reads the field that column is imported into.
- Scores are recalculated when their inputs change, not on a schedule. There is no window in which a
  stored score is known to be stale.
- The published export and the published-structure API already read the stored quality code, so
  they carry the calculated code without a change of their own.
- Scores shown to a reader are those stored. A page never calculates a score of its own.
- A breakdown of every criterion's penalty is not part of this feature. Only the effect of the
  child's corrections is shown.
- Filters on the portal's own pages for the new scores are not part of this feature. The scores are
  stored so that queries return the right records, and a filter can be added on top later.
- A change to a parent's value, or the choice of which children are relevant, stays manual. This
  feature derives the parent's quality from that choice and never makes it.
- A later revision of the scheme is adopted as its own feature, which records the new revision and
  recalculates the database.
