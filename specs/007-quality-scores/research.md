# Research — 007 quality scores

The evidence behind the plan. The conclusions are in [plan.md](plan.md) and
[decisions.md](decisions.md). This file records where they came from.

## R1 — The toolbox, as it scored the release

Heat Flow Quality Analysis Toolbox (hfqa_tool) V0.2, commit `e1688bf` of
github.com/viktoriadergunova/hfqa_tool. The rules live in two places, and both were read:

- `schemas/quality_score_schema.yaml`: the penalties, bins, cases and token lists
- `quality_score/*.py`: how those are applied, including what counts as missing

The Python decides wherever the two could be read differently. Its behaviour, as the portal
reproduces it:

**Evaluation primitives**

- **Numeric bins** are tried largest threshold first. Empty input gives the block's largest
  penalty with the mark. A value that fits no bin gives the largest penalty without it.
- **Flat mappings** (conductivity location) take the poorest matched token. Empty input gives the
  largest penalty with the mark. On the probe route, an unmatched value gives the largest penalty
  without the mark. On the borehole route it carries the mark.
- **Cases** (source, saturation, pT) first check every field any case names. If any is empty, the
  block takes its largest penalty with the mark. Otherwise every matching case counts and the
  poorest wins. With no match, a case with an empty condition is the fallback, and failing that the
  largest penalty applies without the mark.
- **Multi-valued fields** contribute every value. The poorest matching penalty wins (D8).

**Routing** (`apply_m_quality_score.py`): probe-sensing when the exploration method contains
"probing" and one of onshore, lake, river, offshore, ocean or clustering. Borehole when it contains
drilling, mining, tunneling or indirect. Otherwise not determined, and the M-score is `Mx`.

**Probe T-score**, starting at 1.0:

| Criterion | Input | Rule |
|---|---|---|
| Penetration | probe penetration (m) | >10: +0.1 · >3: 0 · >1: −0.1 · ≤1: −0.2 |
| Recordings | number of temperature recordings | >5: +0.1 · ≥3: 0 · =2: −0.1 · <2: −0.2 |
| Water depth | −elevation (m) | >2500: 0 · >1500: −0.1 · ≤1500: −0.2. Elevation ≥ 0 counts as empty. **Waived** (0, no mark) when the child's surface and bottom-water correction is "present and corrected". |
| Tilt | probe tilt (°) | >30: −0.2 · >10: −0.1 · ≥0: 0. **Waived** (0, no mark) when the child's temperature correction is "tilt corrected". |

**Probe TC-score**, starting at 1.0:

| Criterion | Input | Rule |
|---|---|---|
| Location | location | actual 0 · other −0.1 · literature −0.2 |
| Saturation | saturation, method, source, location | Cases; any of the four empty gives −0.2 with the mark. Pulse probe + in-situ probe source + saturated in-situ: +0.1. Pulse probe + in-situ probe source + recovered or saturated measured: 0. Lab method + recovered or saturated measured: 0. Lab + saturated calculated: −0.1. Lab + dry, unspecified or other: −0.2. Lithology or either well-log method + literature location: −0.1. Water content, mineral composition, chlorine content or unspecified method: −0.2. No match: −0.2. |
| Number | conductivity count | Not scored when location is literature. >3: 0 · ≥2: −0.1 · <2: −0.2 |
| pT | pT conditions, method | Cases; either empty gives −0.2 with the mark. Actual in-situ + pulse probe: +0.1. Replicated or corrected pT: 0. Replicated or corrected p or T: −0.1. Recorded or unrecorded ambient, unspecified: −0.2. No match: −0.2. |

The probe TC-score reads nothing from the child.

**Borehole T-score**, starting at 1.0. One case applies:

1. **Surface plus single point**, when the top method includes SUR. The bottom methods alone
   decide: cBHT, RTDeq, cRTD, ODTT-PC, ODTT-TP, cHT-FT, EGRT, GRT or cDST: −0.3. BHT, HT-FTpert,
   RTDpert, DST or RTD: −0.5. CPD, XEN, GTM, BSR, unspecified or other: −0.6.
2. **Continuous log**, when there are more than three recordings and every method at top and
   bottom is one of LOGeq, cLOG, DTSeq, cDTS or LOGpert. LOGpert: −0.1, otherwise +0.1.
3. **Multiple single points**, otherwise. LOGeq, cLOG, cBHT, HT-FTeq, cHT-FT, RTDeq, cRTD, ODTT-PC,
   ODTT-TP, EGRT, GRT, cDST or cDTS: −0.1. LOGpert, DTSpert, BHT, HT-FTpert, RTDpert, BLK, DST, DTS
   or RTD: −0.3. CPD, XEN, GTM, BSR, unspecified or other: −0.5.

Within a case the poorest matching group wins. When nothing matches, including when both method
fields are empty, the case's largest penalty applies with the mark (D16). HT-FTeq and HT-FTpert are
the vocabulary spellings of the toolbox's misspelled tokens (D15).

**Borehole TC-score**, starting at 1.0:

| Criterion | Input | Rule |
|---|---|---|
| Gate | interval top and bottom depth | Both empty: the TC-score is 0.1 with the mark, and nothing else is scored. |
| Location | location | actual 0 · other −0.1 · literature −0.2. Empty **or unmatched**: −0.2 with the mark. |
| Source | source | In-situ probe, core-log integration: +0.1 · core samples: 0 · cutting samples, outcrop samples, well-log interpretation: −0.1 · mineral computation, assumed from literature, unspecified, other: −0.2 |
| Number | conductivity count | Not scored when location is literature. >15: 0 · ≤15: −0.1 |
| Saturation | saturation | Saturated measured or measured in-situ: 0 · saturated calculated, recovered: −0.1 · dry measured, unspecified, other: −0.2 |
| pT, uncorrected (D3) | pT conditions alone | Actual, replicated or corrected in-situ pT: 0 · replicated or corrected p or T: −0.1 · recorded or unrecorded ambient, unspecified: −0.2 · anything else: −0.2 · empty: −0.2 with the mark. This is the toolbox's case list without its in-situ condition, and the paper's Table 3 ordering. |
| pT, corrected | pT conditions **and the child's in-situ correction** | In-situ pT (actual, replicated or corrected pT) with "considered – pT": 0. Replicated or corrected p or T with "considered – p" or "considered – T": −0.1. Ambient or unspecified with "not considered" or unspecified: −0.2. Anything else: −0.2. Either input empty: −0.2 with the mark. |

**M-score**: T × TC, rounded to three decimals. ≥0.75 M1, ≥0.50 M2, ≥0.25 M3, else M4. Suffix `x`
when either sub-score carried the mark.

**U-score**: |uncertainty| / |value| × 100, rounded to six decimals. <5 U1, 5–15 U2, >15–25 U3, >25
U4. Ux when the value is empty or zero, or the uncertainty is empty or zero.

**Perturbation flags**: seven positions from the child's corrections S, E, TOPO, PAL, SUR, CONV and
HR, written `S E T P V C R`. Present and corrected gives the upper-case letter, present and not
corrected gives lower case, present not significant gives `X`, not recognised gives `x`, and
anything else gives `-`.

**Inheritance** (the inheritance section of `combine_scores.py`, added after V0.2 in commit
`19022ed` and adopted by D9; the file itself exists at V0.2):
the poorest U (U1 < U2 < U3 < U4 < Ux), the poorest M (M1 < … < M4 < M1x < … < M4x < Mx), and the
flags of the child with the poorest U, with the poorest M deciding a tie.

## R2 — The toolbox's own tests at V0.2

`pytest testing/unit/quality_score_test` at `e1688bf`: 43 pass, 2 fail.

- `test_borehole_explicit_unspecified_does_not_force_x` expects no mark. The row has no in-situ
  correction column, and the code marks the pT criterion for it.
- `test_marine_mapping_multi_entry_uses_worst_penalty` reads a probe `source_type` mapping the
  schema does not have.

`testing/unit/testing_files/m_score_tests.xlsx` is referenced by no test. Its five expected
M-scores match the code's classes, and the code adds the mark to all five because no row carries an
in-situ correction (D12).

## R3 — Conformance cases

Produced by running the toolbox's own functions (`calculate_u_score`, `calculate_m_score` with
`return_debug=True`, `calculate_p_flags`) at `e1688bf` on these inputs. T and TC are the toolbox's
per-row values, which equal the child's **corrected** scores. The toolbox's worked examples are the
first five rows. The rest cover each criterion, the three child rules and the routing.

Column shorthand: exploration method (P12), value/uncertainty (C1/C2), penetration (C6),
recordings (C37), elevation (P6), tilt (C23), temperature correction (C12), surface/bottom-water
correction (C17), top/bottom methods (C31/C32), interval top/bottom (C4/C5), location (C42),
source (C41), method (C43), saturation (C44), pT conditions (C45), conductivity count (C47),
in-situ correction (C11), and corrections C13–C19 for the flags.

| Case | Inputs | U | T | TC | M | Flags |
|---|---|---|---|---|---|---|
| X1 CONTINUOUS_EQ + TC_FULL | drilling; LOGeq/LOGeq; 10 rec; 0–1000; actual, in-situ probe, 20, saturated measured, actual in-situ pT; no C11 | Ux | 1.1 | 0.9 | M1x | `-------` |
| X2 CONTINUOUS_PERT + TC_OK | drilling; LOGpert/LOGpert; 8; 0–800; actual, core samples, 10, saturated measured, actual in-situ pT; no C11 | Ux | 0.9 | 0.7 | M2x | `-------` |
| X3 MULTI_SINGLE + TC_MEDIUM | drilling; BHT/BHT; 2; 0–500; other, core samples, 5, recovered, replicated T; no C11 | Ux | 0.7 | 0.5 | M3x | `-------` |
| X4 SINGLE_PLUS_SURFACE + TC_WEAK | drilling; SUR/BHT; 1; 0–300; other, cutting samples, 1, dry measured, recorded ambient; no C11 | Ux | 0.5 | 0.3 | M4x | `-------` |
| X5 TC_GATE | drilling; LOGeq/LOGeq; 6; no depths; literature, assumed, –, unspecified, unspecified | Ux | 1.1 | 0.1 | M4x | `-------` |
| P1 | probing offshore; 80±4; pen 12; 6 rec; elev −3000; tilt 45; C12 tilt corrected; C17 present and corrected; actual, in-situ probe, sat. in-situ, pulse probe, 4, actual in-situ pT; C13–C16 present corr., present not corr., not significant, not recognised; C18 unspecified | U2 | 1.2 | 1.2 | M1 | `SeXxV--` |
| P2 | P1 without C12, C17 or C13–C18 | U2 | 1.0 | 1.2 | M1 | `-------` |
| P3 | probing onshore; 60±9; pen 2; 2 rec; elev +120; no tilt; other, core samples, sat. calculated, lab line source full, 2, recorded ambient | U2 | 0.4 | 0.5 | M4x | `-------` |
| P4 | probing clustering; −40±12; pen 0.8; 1 rec; elev −1600; tilt 12; literature, assumed, unspecified saturation, lithology estimation, no count, unspecified pT | U4 | 0.4 | 0.5 | M4 | `-------` |
| P5 | probing offshore; 100±30; pen 4; 3 rec; elev −2000; tilt 5; actual, in-situ probe, **no saturation**, unspecified method, 1, replicated p | U4 | 0.9 | 0.5 | M3x | `-------` |
| B1 | drilling; 65±3; LOGeq/cLOG; 40 rec; 100–900; actual, core samples, 30, saturated measured, corrected pT; C11 considered pT | U1 | 1.1 | 1.0 | M1 | `-------` |
| B2 | B1 with C11 not considered | U1 | 1.1 | 0.8 | M1 | `-------` |
| B3 | B1 with no C11 | U1 | 1.1 | 0.8 | M1x | `-------` |
| B4 | mining; B1 with recorded ambient pT and C11 unspecified | U1 | 1.1 | 0.8 | M1 | `-------` |
| B5 | drilling clustering; 50±10; BHT;cBHT / BHT; 3 rec; 0–2000; other, cutting samples, 12, recovered, replicated p; C11 considered p | U3 | 0.7 | 0.5 | M3 | `-------` |
| B6 | tunnelling; 90±20; SUR / cBHT; 2 rec; 0–1500; literature, assumed, dry measured, unspecified pT; C11 not considered | U3 | 0.7 | 0.2 | M4 | `-------` |
| B7 | drilling; 90±0; SUR / LOGeq; 2 rec; 0–1500; actual, mineral computation, 20, saturated calculated, actual in-situ pT; C11 considered pT | Ux | 0.4 | 0.7 | M3x | `-------` |
| B8 | indirect; 70, no uncertainty; no methods; 5 rec; no depths; (conductivity otherwise full) | Ux | 0.5 | 0.1 | M4x | `-------` |
| B9 | drilling; 70±7; unspecified/unspecified; 5; 100–200; literature, unspecified source, 1, unspecified saturation, unspecified pT; C11 unspecified | U2 | 0.5 | 0.2 | M4 | `-------` |
| N1 | exploration method other; 70±7 | U2 | – | – | Mx | `-------` |
| N2 | no exploration method; 70±7 | U2 | – | – | Mx | `-------` |

The **uncorrected** scores the portal stores on the measurement differ from these T and TC only
where a child rule changed them:

- P1's gradient carries 1.0 (P2's value, no waivers).
- B2's and B3's conductivity carries 1.0 (pT scored alone: corrected pT is 0).
- X1–X4's conductivities carry the TC with pT scored alone:
  - X1: 1.1, since actual in-situ pT is 0
  - X2: 0.9
  - X3: 0.6, since replicated T is −0.1
  - X4: 0.3, since recorded ambient is −0.2
  - X5 stops at the gate.

For B4 (recorded ambient, which is −0.2 on its own terms), B5, B6, B7 and B9, the uncorrected TC
equals the corrected.

The harness that produced this table (a thin wrapper that normalises published labels the way the
toolbox's ETL does and calls the three functions) is kept outside the repository. Nothing in the
portal depends on the toolbox or on pandas.

## R4 — Where each input lives in the portal

| Toolbox | Portal |
|---|---|
| P12 exploration method | `HeatFlowSite.explo_method` (single concept), reached as `measurement.sample.heatflowinterval.site` |
| P6 elevation | `HeatFlowSite.elevation` (quantity, m) |
| C4, C5 interval depths | `HeatFlowInterval.top`, `.bottom` of the conductivity's interval |
| C6, C23 penetration, tilt | `ProbeMetadata.penetration`, `.tilt` of the gradient's interval |
| C31, C32, C37 | `ThermalGradient.method_top`, `.method_bottom` (concepts), `.number` |
| C41–C45, C47 | `IntervalConductivity.source`, `.location`, `.method`, `.saturation`, `.pT_conditions` (concepts), `.number` |
| C1, C2 | `HeatFlow.value`, `.uncertainty` (quantities in mW/m²) |
| C9 relevant | `HeatFlow.is_relevant` |
| C11, C12, C13–C19 | `HeatFlowCorrection.status` for types IS, T, S, E, TOPO, PAL, SUR, CONV, HR |

Concept identifiers map one to one onto the toolbox's tokens by label:

- The location concept `literature` is the toolbox's `[Literature/unspecified]`.
- The `other` concepts are `[other (specify in comments)]`.
- The method `laboratoryOther` is `[Lab - other (specify in comments)]`.
- `waterContent` is `[Estimation - from water content/porosity]`.
- `probeContinuousHeating` has no toolbox token. It fits no case, so it takes the fallback.
- Temperature method `HT_FT` is HT-FTeq, and `HT_FTpert` is HT-FTpert (D15).

## R5 — The correction-status validation blocks two child rules

`HeatFlowCorrection.save()` refuses a status its type does not allow (FS-001 FR-028). As written,
the in-situ type accepts "tilt corrected" and "drift corrected" but not "considered – p/T/pT", and
the temperature type refuses "tilt corrected". The published structure (`C11`, `C12` in
`docs/validation/ghfdb-spec-v1.0.yaml`) and the portal's own `GenericFlagChoices` vocabulary have
it the other way round: C11 takes the three "considered" values, "not considered" and unspecified.
C12 takes tilt corrected, drift corrected, not corrected, corrected and unspecified.

So no child can currently record the tilt correction the probe waiver reads (D11), nor the
"considered" values the borehole pT agreement reads. Changing it changes a behaviour an existing
test pins (`test_correction_invalid_status_rejected` asserts that in-situ plus "considered – p" is
refused), so it waits on the maintainer's ruling. See plan.md, *Open items*.

## R6 — The measurement page

`/measurement/<uuid>/` is served by the framework's `MeasurementDetailView` with the template
`measurement/detail.html`, a placeholder showing name, UUID, dataset and sample. The framework's
measurement plugins module says measurements have no plugin surface. A project template of the same
name takes precedence, which is how `templates/fairdm_core/dataset_detail.html` already works.

## R7 — Deployment

`deploy/Dockerfile` starts the container with `python manage.py migrate --noinput && … && exec
gunicorn …`, so a command added after `migrate` runs on every deployment before the site serves.
