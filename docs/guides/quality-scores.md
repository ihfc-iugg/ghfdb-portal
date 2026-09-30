# Quality scores

The portal scores the heat flow data it holds. This page explains the scores a temperature gradient,
a thermal conductivity, a child heat flow value and a parent heat flow value carry, and how they are
reached, so that a data user can tell why a value scored what it did.

## Which scheme

The scores follow version 0.2 of the Heat Flow Quality Analysis Toolbox (`hfqa_tool`, Dergunova et
al. 2026), the version that scored the 2024 release of the Global Heat Flow Database. The toolbox
refines the scheme of Fuchs et al. (2023). The paper remains the place the scheme's intent is
explained. Where the paper and the toolbox differ, the toolbox decides (see
*Where the sources disagree*, below).

The portal calculates these scores itself and treats its own value as authoritative, as
[ADR 0004](../adr/0004-quality-scores-are-computed-by-the-portal.md) records. A quality code in an
imported file is rejected, not stored.

Every stored score records the revision of the scheme that calculated it, currently `hfqa_tool 0.2`.
When the scheme changes, the revision tells you which records were scored under which.

## The T-score and the TC-score

A score starts at 1.0, each criterion adds or subtracts a penalty, and the scores found in
practice lie between 0.1 and 1.2.

- A **thermal gradient** carries a **T-score**, for how well the temperature gradient was
  determined.
- An **interval conductivity** carries a **TC-score**, for how well the thermal conductivity was
  determined.

Both are the measurement's **uncorrected score**. A gradient or conductivity can be used by several
child heat flow values, and each child may record different corrections. So the score stored on the
measurement reads nothing from any child, and it is the same whichever child uses it.

Each measurement stores three values:

| Field | Meaning |
| --- | --- |
| `score` | The T-score or TC-score. Empty when the score is not determined (below). |
| `score_missing` | The missing-information mark (below). |
| `quality_scheme` | The scheme revision the score was calculated under. |

They are recalculated when the measurement is saved, when a vocabulary value it reads is added,
removed or cleared, and when its interval, its probe metadata or its site changes, so the stored
value matches the record (see *How scores stay current*). The fields are listed in
[GHFDB Fields](../ghfdb_fields.md).

## Which rules apply

A measurement is scored by the rules its own site's exploration method selects. The gradient's site
decides its T-score and the conductivity's site decides its TC-score.

| Exploration method | Rules |
| --- | --- |
| Probing (onshore, lake, river and similar), probing (offshore, ocean), probing-clustering | Probe sensing |
| Drilling, drilling-clustering, mining, tunnelling, indirect | Borehole and mine |
| Other, unspecified, or not recorded | Not determined (see *Not determined*, below) |

## Probe-sensing rules

Both scores start at 1.0.

### Probe T-score

| Criterion | Input | Penalty |
| --- | --- | --- |
| Penetration | Probe penetration | More than 10 m: +0.1. More than 3 m: 0. More than 1 m: −0.1. Otherwise −0.2. |
| Recordings | Number of temperature recordings | More than 5: +0.1. 3 to 5: 0. Exactly 2: −0.1. Fewer than 2: −0.2. |
| Water depth | The site's depth below sea level | More than 2500 m: 0. More than 1500 m: −0.1. Otherwise −0.2. An elevation of zero or above has no water depth, so the criterion is treated as missing. |
| Tilt | Probe tilt | More than 30°: −0.2. More than 10°: −0.1. 10° or less: 0. |

The probe penetration and the tilt are read from the probe metadata of the gradient's interval. A
gradient with no probe metadata has both inputs empty.

### Probe TC-score

| Criterion | Input | Penalty |
| --- | --- | --- |
| Location | Where the conductivity was determined | Actual heat-flow location: 0. Other location: −0.1. Literature: −0.2. |
| Saturation | Saturation, method, source and location together | In-situ probe source, pulse-probe method, saturated measured in situ: +0.1. The same source and method with a recovered or saturated measured rock: 0. A laboratory method with a recovered or saturated measured rock: 0. A laboratory method with a saturated calculated rock: −0.1. A laboratory method with a dry, unspecified or other saturation: −0.2. A lithology or well-log method at a literature location: −0.1. Water content, mineral composition, chlorine content or an unspecified method: −0.2. Anything else: −0.2. |
| Number | Number of conductivity determinations | Not scored when the location is literature. More than 3: 0. 2 or 3: −0.1. Fewer than 2: −0.2. |
| pT conditions | Pressure and temperature conditions, with the method | Actual in-situ conditions with a pulse probe: +0.1. Replicated or corrected in-situ pT: 0. Replicated or corrected in-situ p or T alone: −0.1. Recorded or unrecorded ambient conditions, or unspecified: −0.2. Anything else: −0.2. |

## Borehole and mine rules

Both scores start at 1.0.

### Borehole T-score

The gradient's temperature methods at the top and the bottom of its interval select one of three
cases. Within a case, the poorest matching group decides.

| Case | When | Methods and penalty |
| --- | --- | --- |
| One point plus surface | The top method includes SUR | Decided by the bottom methods alone. cBHT, RTDeq, cRTD, ODTT-PC, ODTT-TP, cHT-FT, EGRT, GRT: −0.3. BHT, HT-FTpert, RTDpert: −0.5. CPD, XEN, GTM, BSR, unspecified, other: −0.6. |
| Continuous log | More than 3 recordings, and every method at top and bottom is LOGeq, cLOG, DTSeq, cDTS or LOGpert | LOGpert: −0.1. Otherwise +0.1. |
| Multiple single points | Every other gradient | LOGeq, cLOG, cBHT, HT-FTeq, cHT-FT, RTDeq, cRTD, ODTT-PC, ODTT-TP, EGRT, GRT, cDTS: −0.1. LOGpert, DTSpert, BHT, HT-FTpert, RTDpert, BLK: −0.3. CPD, XEN, GTM, BSR, unspecified, other: −0.5. |

### Borehole TC-score

A conductivity whose interval reports neither a top nor a bottom depth takes a fixed TC-score of
0.1 with the missing-information mark, and nothing else is scored. Otherwise:

| Criterion | Input | Penalty |
| --- | --- | --- |
| Location | Where the conductivity was determined | Actual: 0. Other: −0.1. Literature: −0.2. |
| Source | Nature of the samples | In-situ probe, core-log integration: +0.1. Core samples: 0. Cutting samples, outcrop samples, well-log interpretation: −0.1. Mineral computation, assumed from literature, unspecified, other: −0.2. |
| Number | Number of conductivity determinations | Not scored when the location is literature. More than 15: 0. 15 or fewer: −0.1. |
| Saturation | Saturation state | Saturated measured, or measured in situ: 0. Saturated calculated, recovered: −0.1. Dry measured, unspecified, other: −0.2. |
| pT conditions | Pressure and temperature conditions | Actual, replicated or corrected in-situ pT: 0. Replicated or corrected in-situ p or T alone: −0.1. Recorded or unrecorded ambient conditions, or unspecified: −0.2. |

A location that is empty takes −0.2 with the mark.

## Several values in one field

Some inputs are vocabulary fields that can hold more than one value, such as a gradient with two
temperature methods at its top. Every value is scored and the poorest penalty applies.

## The missing-information mark

A score is marked as reached with missing information when an input the scheme needed was **empty**.
That criterion then takes its largest penalty, so the score is a floor for what the measurement
might deserve, and the mark says that the record could be improved by adding the missing
information.

An input recorded as **unspecified** is a value, not an empty one. It takes the same largest
penalty and carries no mark, because nothing is missing: the contributor stated that it is not
known. The file import keeps the two apart. A cell reading `[unspecified]` is stored as the
vocabulary's `unspecified` concept, and a blank cell is stored as nothing (see
[Importing data](importing-data.md)).

Two cases beyond an empty input also carry the mark, because the scheme names them: a borehole
conductivity whose interval reports no depth, and a borehole gradient whose temperature methods fit
none of the three cases (empty methods, or only methods the case's lists do not name).

## Not determined

A measurement whose site has an exploration method that is empty, unspecified or other has no rules
to be scored by. Its `score` is stored empty, which means not determined, and it is not marked:
nothing was scored, so no input was missing. It is never stored as 0.

## The child's scores

A child heat flow value (a determination) carries its own scores. They are the **U-score**, for its
uncertainty, the **corrected T-score** and **corrected TC-score** of the gradient and the
conductivity it was calculated from, the **M-score**, made from those two, the seven
**perturbation flags**, and the **quality code** that joins them. The code is stored on the child as
`quality`, and each part is stored on its own so that children can be found by it:

| Field | Meaning |
| --- | --- |
| `U_score` | The grade for the uncertainty of the value. |
| `T_score`, `T_score_missing` | The child's corrected T-score and its missing-information mark. Indexed. |
| `TC_score`, `TC_score_missing` | The child's corrected TC-score and its mark. Indexed. |
| `M_score` | The grade for the methodology. |
| `quality` | The quality code. The seven flags are its last seven characters and are not stored apart. |
| `quality_scheme` | The scheme revision the scores were calculated under. |

None of these can be edited. A child is rescored when it is saved, and when one of its corrections
is saved or deleted. A deletion is rescored once the transaction that made it commits, so deleting a
whole dataset does not rescore each child once per correction. The fields are listed in
[GHFDB Fields](../ghfdb_fields.md).

## The U-score

The U-score grades the uncertainty of the heat flow value, from the coefficient of variation: the
uncertainty as a percentage of the value, rounded to six decimal places.

| Coefficient of variation | U-score |
| --- | --- |
| Below 5 % | U1 |
| 5 % up to and including 15 % | U2 |
| Above 15 % up to and including 25 % | U3 |
| Above 25 % | U4 |

A value or an uncertainty that is empty or zero cannot be graded, and the U-score is `Ux`. The sign
is ignored, because a heat flow can be negative: a value of −40 mW/m² with an uncertainty of 12
mW/m² is a coefficient of 30 % and scores U4.

## Corrected scores and the three child rules

The T-score and TC-score stored on a gradient or a conductivity are its **uncorrected scores**, and
they read nothing from any child. A child takes each of them through its own corrections to reach
its **corrected score**, which is the value the M-score is made from. A corrected score can be lower
than the uncorrected one as well as higher. Each of the child's two measurements is scored by the
rules of its own site, so a child whose gradient and conductivity sit at sites with different
exploration methods is scored by two different rule sets.

Three rules read the child's corrections:

- **Tilt.** When the child's temperature correction is recorded as tilt corrected, the probe tilt
  criterion of the gradient is waived: it takes no penalty and no mark, even when the tilt is empty.
  This applies to a probe gradient only.
- **Bottom-water temperature.** When the child's surface and bottom-water correction (`SUR`) is
  present and corrected, the water depth criterion of the gradient is waived in the same way. This
  applies to a probe gradient only.
- **In-situ agreement.** The toolbox scores a borehole conductivity's pT conditions only when the
  child's in-situ correction agrees with them. In-situ pT, or replicated or corrected pT, agrees
  with "considered, pT" and scores 0. Replicated or corrected p or T alone agrees with "considered,
  p" or "considered, T" and scores −0.1. Ambient or unspecified conditions agree with "not
  considered" or an unspecified correction and score −0.2. Anything else scores −0.2. The
  uncorrected TC-score cannot read the child, so it scores the pT conditions on their own terms, and
  the two can differ.

A borehole child that records no in-situ correction at all takes −0.2 and the missing-information
mark on the pT criterion, as the toolbox does. A correction whose status is `-` is recorded as
unspecified, and it takes the same −0.2 without the mark. The file import writes every correction
row, with `-` for an empty cell, so an imported child is never without one. The probe route reads
nothing from the in-situ correction.

## The M-score

The M-score grades the methodology from the product of the corrected T-score and TC-score, rounded
to three decimal places.

| Product | M-score |
| --- | --- |
| 0.75 or more | M1 |
| 0.50 or more, below 0.75 | M2 |
| 0.25 or more, below 0.50 | M3 |
| Below 0.25 | M4 |

A product exactly on a boundary takes the better class. When either corrected score was reached
with missing information, an `x` follows the grade (`M1x` to `M4x`). When either cannot be
calculated, because the child has no gradient or no conductivity, or the measurement's site selects
no rules, the M-score is `Mx`.

## The perturbation flags

Seven characters record how the child's environmental corrections stand, one for each of the
corrections `S`, `E`, `TOPO`, `PAL`, `SUR`, `CONV` and `HR`, in that order. They are written as the
letters `S E T P V C R`:

| Letter | Correction |
| --- | --- |
| `S` | Sedimentation or subsidence |
| `E` | Erosion |
| `T` | Topography |
| `P` | Paleoclimate |
| `V` | Surface-temperature variation |
| `C` | Convection |
| `R` | Heat refraction |

An upper-case letter means the effect is present and corrected, and a lower-case letter means it is
present and not corrected. `X` means present and not significant, and `x` means not recognised.
Anything else, including an unspecified status or no recorded correction, is `-`. The in-situ and
temperature corrections write no flag.

A status on the file import may be written as its label. See [Importing data](importing-data.md).

## The quality code

The code joins the three parts with full stops: the U-score, the M-score and the seven flags. It is
at most fourteen characters:

- `U1.M2.SxxxCxR`
- `U2.M3x.-e-PX--`
- `Ux.Mx.-------`

The paper writes the code without the first full stop. The toolbox writes both, and the portal
follows the toolbox.

## What a parent inherits

A parent heat flow value is designated by a curator, not calculated, but its quality is not chosen.
It is inherited from the children it rests on, as Fuchs et al. (2023, section 3.4) describe, using
the toolbox's ranking for the two points the paper leaves open.

**Which children count.**

- A parent with exactly one child rests on it, whether or not the child is marked relevant. The
  paper's single-child case does not depend on the flag, so the portal's does not either.
- A parent with several children rests on those marked relevant. The children not marked take no
  part, which is how a poor determination stays in the record without lowering the site's quality.
- A parent with several children of which none is marked relevant, or with no children, is not
  determined: `Ux`, `Mx` and `-------`, which is the code `Ux.Mx.-------`.

**What it takes from them.**

- The U-score is the poorest among them, ranked `U1`, `U2`, `U3`, `U4`, then `Ux` as the poorest.
- The M-score is the poorest among them, ranked `M1` to `M4`, then `M1x` to `M4x`, then `Mx`. Any
  grade marked as reached with missing information is poorer than any unmarked grade, so `M1x` is
  poorer than `M4`.
- The perturbation flags are taken whole from the child with the poorest U-score, the child with
  the poorest M-score deciding a tie. They are not merged flag by flag. When two children tie on both
  scores, the one with the lower primary key wins, so recalculating gives the same flags every time.

For example, a parent with two relevant children coded `U1.M4.S------` and `U3.M1x.-E-----`
inherits `U3.M1x.-E-----`. `U3` is the poorer U-score, `M1x` is the poorer M-score because a marked
grade is poorer than `M4`, and the flags are those of the child with the poorer U-score.

A parent's **value** is never changed by inheritance. Only `U_score`, `M_score`, `quality` and
`quality_scheme` are written.

**When it is recalculated.** A parent is refreshed only when something on the child side changes,
never by saving the parent. Saving a child, changing whether it is relevant, moving it to another
parent (which refreshes both parents), deleting it, and saving or deleting one of its corrections
each refresh the parent. Saving the parent itself does not, because its inputs are its children and
the choice of which are relevant stays with the curator. A deleted child's parent is refreshed
once the deleting transaction commits, and only if it still exists.

A queryset `update` or `bulk_create` sends no signal, so it leaves the parent as it was. See *How
scores stay current* for the repair.

## How scores stay current

A score is stored, never worked out when it is read, so the portal recalculates it when something
it reads changes. A change reaches every score that depends on it and no other.

| What changes | What is recalculated |
|---|---|
| A gradient or a conductivity is saved, or a vocabulary value it reads is added, removed or cleared | its own score, the children that use it, and those children's parents |
| An interval is saved (its depths) | the gradients and conductivities on it, and onward |
| Probe metadata is saved or deleted | the gradients on its interval, and onward |
| A site is saved (its elevation or exploration method) | every gradient and conductivity on its intervals, and onward |
| A child is saved | the child and its parent, and the parent it left if it moved |
| A correction is saved or deleted | the child it belongs to, and that child's parent |
| A child is deleted | the parent it belonged to |

"Onward" means the children that use those measurements, and then their parents. The levels are
recalculated from the bottom up, gradients and conductivities first, then children, then parents,
so each level reads the fresh scores of the level below it. A parent is never recalculated by its
own save.

**A delete waits for the commit.** Deleting a dataset removes every child and correction in it, so
recalculating after each one would rescore a parent once per row, and a parent that is about to go
too would be scored for nothing. A delete instead notes what it touched, and the portal
recalculates once when the transaction commits, and only the records that still exist. If the
transaction is rolled back, nothing is recalculated and the next one is not affected.

**An import recalculates once, when it ends.** Importing a file saves each row's interval,
gradient, conductivity, child and corrections one after another. Recalculating at every save would
score the same child many times over, so the import collects what it wrote and recalculates each
record once, inside the import's own transaction. A check and a dry run therefore store no
scores, since they store no rows, and an import that fails is rolled back with its scores and
leaves recalculation switched on for the next write. The parent pass of a full-file import saves
its sites outside this, so a re-import recalculates the measurements on each site as it saves it.
A quality code in the file is still rejected (see *Which scheme*).

**Writes that skip the portal's code skip the scores.** A queryset `update`, a `bulk_create` and a
change made in the database directly send no signal, so they leave the scores as they were. Repair
them by running the command that recalculates every record:

```console
python manage.py refresh_quality --all
```

Without `--all`, `refresh_quality` recalculates only the records whose stored revision is not the
current one (see *Which scheme*), which is every record written before scoring existed and every
record scored under an earlier revision. It reports how many of each it covered. Running it twice
changes nothing, and `--all` over unchanged inputs stores the same values it found. The portal's
container runs it on start, after the migrations, as `deploy/README.md` describes.

A record imported before scoring existed keeps what was stored then. The command cannot recover a
value that was never stored, so importing that file again is the repair for a missing input.

## How these match the toolbox

For every row the toolbox scores, the T-score and TC-score it reports are the child's corrected
scores here, not the uncorrected scores of the gradient and the conductivity. The portal's
`T_score` and `TC_score` on a child equal the toolbox's per-row T and TC, and so do its U-score,
M-score and flags. Filtering children by `T_score` or `TC_score` therefore finds the children the
toolbox would, including where a correction changed the score. The portal is checked against the
toolbox's own output for a set of cases covering each criterion, each child rule and the routing.

The two child rules that need a correction the model cannot yet record (a tilt-corrected
temperature, and the in-situ statuses "considered, p", "considered, t" and "considered, pT") are
applied by the scheme whenever it is given them. Until the model accepts them, a stored child cannot
hold those statuses.

## Where the sources disagree

The paper, the toolbox's schema, the toolbox's code and the toolbox's own tests do not always
agree. The portal's choices are recorded in `specs/007-quality-scores/decisions.md`. The ones that
bear on the T-score and TC-score are these.

**The toolbox decides, not the paper (D1).** The toolbox scored the release, so following it keeps
the portal's scores comparable with the scores data users already hold. The rules that differ from
a literal reading of the paper are the ones set out above: routing by exploration method, the
continuous-log condition, the estimate grouping for unspecified methods, the fixed TC-score of 0.1
without depths, the unscored number for literature locations and the water depth at or above sea
level.

**Several values take the poorest (D8).** The paper does not say how to score a field holding more
than one value. The toolbox scores every matching value and takes the largest penalty, and so does
the portal.

**The paper's worked examples are not the test (D10).** The paper's Table 5 contradicts its own
inputs or its own rules in five places. The portal is checked against the toolbox's own output for
each case, and uses the paper's examples only where they agree with it.

**The toolbox's code is the oracle (D12).** Two of the toolbox's own tests fail against its code,
and its worked-example spreadsheet differs from the code by the missing-information mark and
nothing else. The code is what scored the release, so the code decides.

**Misspelled method names are read as the methods they name (D15).** The toolbox's borehole lists
spell three temperature methods in ways that match nothing in the published vocabulary: `[HFT-FTeq]`
(for HT-FTeq) and `[HF-FTpert]` and `[HFT-FTpert]` (for HT-FTpert). The portal reads them as the
vocabulary's HT-FTeq and HT-FTpert. The other gaps in the lists are kept as the toolbox has them:
DTSeq appears only in the continuous-log case, and the surface case has no HT-FTeq.

**A method that fits no case is marked (D16).** When none of a borehole gradient's methods fits its
case, the toolbox takes the case's largest penalty and sets the mark. The portal does the same.

**The quality code is written with two full stops (D5).** The paper writes `U1M2.SxxxCxR` and the
toolbox's code writes `U1.M2.SxxxCxR`, so the portal does.

**Heat refraction is R, and the flags follow the paper's figure order (D6).** The paper's Table 5 is
the outlier in both the letter and the order of the fifth and sixth flags.

**A product on a class boundary takes the better class (D7).** The toolbox rounds the product to
three places and compares with "at least".

**The tilt correction is read from the temperature correction (D11).** The paper conditions the
tilt rule on the in-situ correction. The toolbox, and the portal's own vocabulary, use the
temperature correction.

**A borehole child with no in-situ correction takes the agreement penalty (D13).** It takes −0.2
with the mark, as the toolbox does.

**A correction recorded as `-` is unspecified, and a missing one is empty (D14).** The flags write
`-` for both.

**Routing follows the site's exploration method (D17).** The vocabulary's concepts map onto the
toolbox's routing words as the table under *Which rules apply* shows. Whether a
child carries probe metadata is not how the scheme routes.

## In the code

The scheme lives in `project/heat_flow/quality.py`, and nothing else in the portal implements it.

- `ProbeRules` and `BoreholeRules` hold one route's tables and score a gradient or a
  conductivity. `route(site)` returns the one that applies to a site, or `None` when neither does.
- `Criterion` holds the three ways a criterion is evaluated: numeric bins, a mapping of values to
  penalties, and cases that combine several fields.
- `Reading` reads what the scheme needs from a measurement, its interval and its site: concept
  identifiers, quantities in a given unit, the site and the probe metadata.
- `SubScore` is a T-score or TC-score with its missing-information mark. A `value` of `None` means
  not determined.
- `QualityScheme` does the arithmetic of a child's code: `QualityScheme.u_score(value,
  uncertainty)`, `QualityScheme.m_score(t, tc)`, `QualityScheme.perturbation_flags(statuses)` and
  `QualityScheme.code(u, m, flags)`. It also does a parent's: `QualityScheme.inherit(children)`
  returns the inherited U-score, M-score and flags. `QualityScheme.U_RANK` and
  `QualityScheme.M_RANK` list the grades from best to poorest, and `QualityScheme.NOT_DETERMINED`
  is the `Ux`, `Mx`, `-------` it returns for no children.
- `SCHEME_REVISION` is the revision every stored score records.

`ScoredMeasurement`, in `project/heat_flow/models/child.py`, is what a thermal gradient and an
interval conductivity share to store their own score. `refresh_score()` recalculates and stores the
score, the mark and the revision. `HeatFlow.refresh_quality()` does the same for a child: it reads
the child's corrections, scores the gradient and the conductivity by the child rules, and stores
the corrected scores, the M-score, the U-score, the code and the revision.
`ParentHeatFlow.refresh_quality()`, in `project/heat_flow/models/parent.py`, does it for a parent:
it picks the children the parent rests on, calls `QualityScheme.inherit()`, and stores `U_score`,
`M_score`, `quality` and `quality_scheme`. Like the others it writes with a queryset `update`.

The receivers in `project/heat_flow/signals.py` call them through `Recalculation`, which holds the
cascade. `Recalculation.request()` names the records that changed and recalculates them and
everything that reads them, in that order, or collects them: a request made with
`when_committed=True` (every delete) waits for the transaction to commit, and one made inside
`Recalculation.deferred()` waits for the end of the block. `Recalculation.flush()` recalculates what
was collected, once each. `Recalculation.measurement()` names a gradient or a conductivity, and
`Recalculation.measurements_on()` names those on some intervals. The receivers are
`refresh_measurement_on_save`, `refresh_measurement_on_concepts`,
`refresh_measurements_on_interval_save`, `refresh_measurements_on_probe_save`,
`refresh_measurements_on_probe_delete`, `refresh_measurements_on_site_save`,
`remember_parent_before_save`, `refresh_child_on_save`, `refresh_child_on_correction_save`,
`refresh_parent_on_child_delete` and `refresh_child_on_correction_delete`, connected in the app's
`ready()`. `remember_parent_before_save` notes the parent a child is leaving, which
`refresh_child_on_save` then refreshes along with the new one.

`GHFDBChildImportResource` enters `Recalculation.deferred()` in `before_import` and flushes it in
`after_import`. Its `import_data` ends the deferral if the import fails.

The command is `refresh_quality`, in `project/heat_flow/management/commands/refresh_quality.py`.
`Command.levels()` returns the four levels in cascade order with what each refresh reads
prefetched, and `Command.refresh()` walks one level in chunks of `Command.CHUNK_SIZE` records.

## Not covered here

This page covers the scores of a gradient, a conductivity, a child and a parent, and how they are
kept current. How a measurement's page shows them is documented as it is built.
