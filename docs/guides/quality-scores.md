# Quality scores

The portal scores the heat flow data it holds. This page explains the scores a single temperature
gradient and a single thermal conductivity carry, and how they are reached, so that a data user can
tell why a measurement scored what it did.

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

They are recalculated when the measurement is saved and when a vocabulary value it reads is added,
removed or cleared, so the stored value always matches the record. The fields are listed in
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

**Routing follows the site's exploration method (D17).** The vocabulary's concepts map onto the
toolbox's routing words as the table under *Which rules apply* shows. Whether a
child carries probe metadata is not how the scheme routes.

## Not covered here

This page covers the scores of a single gradient or conductivity. The scores a child heat flow
value and a parent carry are documented as they are built.
