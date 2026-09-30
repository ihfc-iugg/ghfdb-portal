# Decisions — 007 quality scores

These are the decisions taken during this feature, and why. Rationale too detailed for
[spec.md](spec.md) lives here. The gate-level trail lives on the feature's issue.

## Sources

The scheme is described in four places, and they do not agree everywhere:

| Short name | Source |
|---|---|
| **Paper** | Fuchs et al. (2023), "Quality-assurance of heat-flow data: The new structure and evaluation scheme of the IHFC Global Heat Flow Database", Tectonophysics 863:229976. Tables 1–5, Figs. 3–5. |
| **Toolbox** | Heat Flow Quality Analysis Toolbox (hfqa_tool) V0.2, Dergunova et al. (2026), doi:10.5880/fidgeo.2026.032. The release matches commit `e1688bf` of github.com/viktoriadergunova/hfqa_tool. |
| **Release paper** | Neumann et al. (2026), "The 2024 release of the GHFDB", ESSD 18:4639–4668, section 4.1. It names the toolbox as the version the release was scored with. |
| **Website** | heatflow.world, data quality scheme page, and the walkthrough video "Quality standards for the IHFC Global Heat Flow Database" (2024). |

The toolbox's earlier version (v0.1, Chishti et al. 2025, the `ihfc-iugg/hfqa_tool` repository) is
superseded by V0.2 and is not followed.

## D1 — The toolbox, not the paper, is the definition

Where the paper and the toolbox differ, the toolbox decides. The toolbox scored the published
release, so following it keeps the portal's scores comparable with the scores data users already
have. The paper remains the conceptual reference and the place the scheme's intent is explained.

The rule changes this brings in, relative to the paper:

- A U-score with an uncertainty of zero is not determined, where a literal reading of the paper
  gives U1.
- A measurement is routed to the probe-sensing or the borehole and mine rules by its site's
  exploration method. An exploration method that is empty, unspecified, "other" or neither routes
  to nothing, and the M-score is not determined.
- A borehole gradient counts as a continuous log only when it has more than three temperature
  recordings and every temperature method at top and bottom is a logging or distributed-sensing
  method. Otherwise it is scored as multiple single points, with no condition on the count.
- A borehole temperature method recorded as unspecified or other is scored as an estimate.
- A borehole conductivity with neither interval top nor bottom depth gets a fixed TC-score of 0.1
  and the missing-information mark.
- A borehole conductivity's number of measurements is not scored when its location is literature
  or unspecified.
- A borehole conductivity's pT conditions earn their score only when the child's in-situ correction
  agrees with them (see D3).
- The probe estimation methods include the two well-log methods in the −0.1 group, and chlorine
  content, unspecified and other in the −0.2 group.
- The probe bin edges are the toolbox's own: penetration above 10 m is +0.1, above 3 m is 0, above
  1 m is −0.1, otherwise −0.2. Temperature recordings above 5 are +0.1, 3 or more are 0, exactly 2
  is −0.1, otherwise −0.2.
- A probe site with an elevation of zero or above has no water depth, and that criterion is
  treated as missing.
- The missing-information mark is set by an empty input only. An input recorded as unspecified
  takes the largest penalty without the mark. The paper sets the mark for both. The toolbox's own
  test documentation states the narrower rule explicitly.

**ADR:** none. Choosing which published scheme to follow is the feature's own subject, and ADR-0004
already records that the portal computes quality itself.

## D2 — Uncorrected scores on the measurement, corrected scores on the child

The scheme reads three things from the child when scoring a gradient or a conductivity:

- the tilt correction (the child's temperature correction recorded as tilt corrected)
- the bottom-water temperature correction (its surface and climatic correction recorded as present
  and corrected)
- the in-situ correction, which must agree with a borehole conductivity's pT conditions

A gradient or conductivity can be used by several children, and it must carry the same score
whichever child uses it. So the score stored on the measurement reads nothing from any child. Each
child applies those three rules to reach its own corrected T-score and TC-score, and its M-score is
calculated from those.

The alternative was to move the three corrections onto the gradient and the conductivity, on the
grounds that a correction to the temperature data physically belongs to the gradient. It was
rejected for three reasons:

- It changes a data model already settled.
- The published structure keeps all three as child columns.
- The bottom-water correction is also one of the child's perturbation flags, so it would have to be
  read from two places.

Decided by the maintainer while the feature was being specified, 2026-09-29.

**ADR:** none. The spec records it, and it is local to how this feature stores scores.

## D3 — The uncorrected TC-score scores pT conditions alone

The toolbox scores a borehole conductivity's pT conditions only when the in-situ correction on the
same row agrees: in-situ pT with "considered – pT", p- or T-only with "considered – p" or
"considered – T", ambient with "not considered" or unspecified. Anything else takes −0.2.

The uncorrected TC-score cannot read the child, so it scores the pT conditions as the paper's
Table 3 does, on their own terms. The child's corrected TC-score applies the agreement
requirement. A corrected TC-score can therefore be lower than the uncorrected one, which is why the
spec defines "corrected" as "with the child's corrections taken into account" rather than
"improved".

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D4 — The corrected scores are stored, not calculated when read

A calculated property would avoid a second stored copy, but a query filtering children by T-score
or TC-score could then only reach the measurement's uncorrected score through the relation. Where
a correction applied, it would return the wrong children without any sign of it. The corrected
scores have exactly the same inputs as the stored M-score, so they are recalculated at the same
moment and add no risk of going stale beyond what the M-score already carries.

Decided by the maintainer while the feature was being specified, 2026-09-29.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D5 — The quality code is written with two full stops

The paper, the website's flowchart and the toolbox's README write `U1M2.SxxxCxR`. The toolbox's code
writes `U1.M2.SxxxCxR`, and its own unit test asserts that form. The portal already writes the
dotted form (`Ux.Mx.-------` is the current default), and the toolbox is the definition (D1), so
the dotted form stays.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D6 — Heat refraction is R, and the flags follow the paper's figure order

The paper's text, its Fig. 4, the website, the release paper and the toolbox's code all write heat
refraction as R and put surface-temperature variation fifth and convection sixth. The paper's
Table 5 writes heat refraction as h/H and swaps the fifth and sixth positions, and the toolbox's
README copies one of its examples. Table 5 is the outlier, so the portal follows everything else.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D7 — A product on a class boundary takes the better class

The paper's Fig. 3 legend gives the classes as ranges that share their end points. Its worked
example I, and some grid cells, place an exact 0.25 or 0.50 in the poorer class. That is consistent
with floating-point sums such as 1 − 0.1 − 0.2 − 0.2 = 0.4999…, not with an intended strict
inequality. The toolbox rounds the product to three decimal places and compares with "at least",
and the portal does the same.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D8 — Multi-valued fields take the poorest matching class

Several inputs are vocabulary fields that can hold more than one concept. The paper does not say
how to score them. The toolbox scores every concept that matches and takes the largest penalty,
and the portal does the same.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D9 — Parent inheritance follows the toolbox, with one addition

The paper says a parent inherits the poorest U-score and M-score among its relevant children, and
that a single child's score passes straight up. It does not say how the parent's perturbation
flags are chosen, or how an M-score marked as missing information ranks against one that is not.
The toolbox's inheritance, added after V0.2 in the same repository, answers both:

- U ranks U1, U2, U3, U4, then Ux as poorest.
- M ranks M1 to M4, then M1x to M4x, then Mx as poorest. Any marked M-score is poorer than any
  unmarked one.
- The perturbation flags are taken whole from the child with the poorest U-score, with the poorest
  M-score deciding a tie.

The portal adds one rule. A parent with exactly one child inherits it whether or not that child is
marked relevant, because the paper's single-child case does not depend on the flag. A parent with
several children and none marked relevant is not determined.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D10 — The paper's worked examples are not the conformance oracle

The paper's Table 5 contradicts its own inputs or its own rules in five places:

- example F's temperature penalty
- example J's U-score, whose uncertainty ratio gives U2 while the table says U3
- the U-score labelled on location 2
- location 1's inherited code, which ignores the relevance flags
- example I's M4x at exactly 0.25 (see D7)

The toolbox's own tests and test documentation are the reference the implementation is checked
against. The paper's examples are used only where they agree with the toolbox.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D11 — The probe tilt correction is read from the temperature correction

The paper conditions the tilt rule on the in-situ correction column. The toolbox reads the
temperature correction column, whose vocabulary is the one that holds "tilt corrected". The
portal's own vocabulary agrees with the toolbox, so the portal reads the child's temperature
correction.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D12 — The toolbox's code is the oracle where its own tests disagree with it

Running the toolbox's scoring tests against its V0.2 code shows two failures. A borehole test
expects no missing-information mark on a row that records "unspecified" everywhere, but the row
leaves the in-situ correction empty, and the code marks that. A probe test reads a `source_type`
block the probe schema does not have. Its worked-example spreadsheet (`m_score_tests.xlsx`) also
gives `M1`, `M2`, `M3` and `M4` where the code gives `M1x`, `M2x`, `M3x` and `M4x`, for the same
reason: none of its rows carries an in-situ correction. The classes agree. Only the mark differs.

The code is what scored the 2024 release, so the portal's conformance cases are the code's output
for each input, recorded in [research.md](research.md) R3. Where the spreadsheet's expected column
differs, it differs by that mark and nothing else.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D13 — A borehole child with no in-situ correction takes the agreement penalty

The toolbox's pT rule for a borehole conductivity needs the child's in-situ correction. When the
child records none, the code applies the criterion's largest penalty (−0.2) and the
missing-information mark. The portal does the same, because the corrected TC-score applies the
toolbox's agreement requirement (D3, and the spec's second clarification). An empty input the
score needed carries the mark (FR-009).

This narrows US2 scenario 6 for borehole children. A child "with none of those three
corrections" keeps its conductivity's own TC-score only if it is a probe child, or if its in-situ
correction is recorded and agrees. The alternative reading, where no in-situ correction means no
agreement rule, contradicts the toolbox and its worked example "CONTINUOUS_PERT + TC_OK": that
example reaches its expected M2 only with the −0.2. Put to the maintainer with the plan.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D14 — A correction recorded as `-` is unspecified, a missing one is empty

The scheme tells an empty input (largest penalty, marked) from one recorded as unspecified
(largest penalty, not marked). A child's corrections are stored one row per disturbance type, and
the file import writes an empty cell as a row with status `-`, whose label is "unspecified". So the
portal cannot tell those two apart for a correction. It reads `-` as recorded unspecified and a
missing row as empty. Only the in-situ correction's pT agreement is affected. The perturbation
flags write `-` for both, as the toolbox does.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D15 — Four misspelled method tokens in the toolbox are read as the methods they name

The toolbox's borehole temperature lists spell three methods in ways that match no value of the
published vocabulary: `[HFT-FTeq]` (for HT-FTeq), and `[HF-FTpert]` and `[HFT-FTpert]` (for
HT-FTpert). One entry also carries a leading space (`" [cHT-FT]"`, listed correctly beside it).
Read literally, a gradient measured with either method matches nothing and is scored as
unresolvable. The lists place them in the equilibrium and perturbed groups by name, and that is
what the portal does.

Other gaps in the lists are kept as the toolbox has them. DTSeq appears only in the continuous-log
case, and the surface-plus-single-point case has no HT-FTeq. The toolbox decides (D1), and nothing
in its documentation says otherwise.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D16 — A borehole temperature method that fits no case is marked

When none of a borehole gradient's temperature methods fits its case's groups, the toolbox takes
the case's largest penalty and sets the missing-information mark. Its schema names this as
"apply max penalty for unresolvable case and flag x". FR-009 allows the mark "where the scheme
names a specific case", so the portal marks it too. It is the second such case, beside a borehole
conductivity's location.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D17 — Measurements are routed by the site's exploration method

The portal's exploration-method vocabulary maps onto the toolbox's routing words as follows.
Probe-sensing: probing onshore, probing offshore, probing clustering. Borehole and mine: drilling,
drilling clustering, mining, tunnelling, indirect. Not determined: other, unspecified, empty. The
`is_probe` property on the child, which tested for probe metadata, is not how the scheme routes and
is no longer used for scoring.

**ADR:** none. It settles how this feature reads the scheme, and the spec records it.

## D18 — What is stored, and which fields are indexed

- **Thermal gradient, interval conductivity:** the existing `score` becomes nullable, and null
  means not determined. It loses its 0–1 bounds, because the scheme's scores run from 0.1 to 1.2.
  New `score_missing` (boolean) and `quality_scheme` (the revision). `score` is indexed on both,
  since the assessment team filters measurements by it. The conductivity has no index on it today.
  `score_missing` and `quality_scheme` are not indexed: no page or query filters on them, and the
  refresh command's stale check (D20) is a single scan at deploy time.
- **Child:** new `T_score` and `TC_score` (the corrected scores, nullable floats, indexed, per
  FR-005 and D4), `T_score_missing`, `TC_score_missing` and `quality_scheme`. `M_score` widens to
  three characters for `M1x`–`M4x`. `quality` widens to fourteen for the longest code,
  `Ux.M4x.SETPVCR`. `U_score` and `M_score` keep their indexes.
- **Parent:** new `U_score` and `M_score` (indexed, like the child's) and `quality_scheme`.
  `quality` widens to fourteen.
- **Perturbation flags are not stored separately.** They are the last seven characters of the
  quality code. A second copy would be a second thing to keep current.

The choice lists keep their names (`UScoreOptions`, `MScoreOptions`), and `MScoreOptions` gains the
four marked classes.

**ADR:** none. Field-level storage for this feature, recorded in `docs/ghfdb_fields.md`.

## D19 — Scores are recalculated when their inputs are written

Signal receivers recalculate a score when one of its inputs is saved, deleted or has a vocabulary
value added or removed. They recalculate the measurement's own score, then every child using the
measurement, then each of those children's parents. Each refresh writes with a queryset `update`,
so it does not fire the receivers again. Saving a parent does not recalculate it: its inputs are
its children, and the choice of which are relevant stays manual.

A file import writes one child with a dozen saves and vocabulary additions. Recalculating after
each would score every record many times over. So the child import holds recalculation back while
it runs and scores everything it wrote once, at the end and inside the import's own transaction,
so a dry run leaves nothing behind.

A queryset `update` or `bulk_create` bypasses the receivers, as it does every Django signal. The
refresh command (D20) is the repair for that, and the documentation says so.

**ADR:** decided at convergence.

## D20 — Records are scored at deployment by a refresh that runs on start

FR-015 asks for every existing record to be scored as part of the deployment. A data migration
would have to call the scoring code through historical models, which do not carry it, or through
the live ones, which breaks the moment a later migration changes a field. Instead a management
command, `refresh_quality`, recalculates every record whose stored scheme revision is not the
current one. The container runs it after `migrate` on every start. Once everything is current it is
a count and nothing else. The same command adopts a later scheme revision (the spec's last
assumption), and `--all` recalculates regardless.

**ADR:** decided at convergence.

## D21 — Measurement pages show quality through a template override

The framework's measurement page is a placeholder. It shows no fields at all and has no extension
point. The portal overrides that one template (`templates/measurement/detail.html`, as it already
overrides the dataset page). It keeps the placeholder's content and adds a quality section for a
child, a gradient and a conductivity, which reads only stored values.

**ADR:** none. Local to how this feature shows its scores.
