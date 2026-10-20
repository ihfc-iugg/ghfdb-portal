# FS-011 sketch: heat flow content on the overview pages

The prototype of the six record pages, built on the feature's branch against the pinned FairDM
(f69c9cb). Nothing in it is tested. The build plans from this file.

## What exists

**The records the pages read.**

- `HeatFlowSite` is a sample. It holds the location, its elevation, the site type, geographic
  environment, exploration method and purpose (vocabulary fields), the access geometry (top,
  bottom, length, vertical depth, inclination, azimuth) and where it lies (country, region,
  continent, domain). Its intervals are `site.intervals`.
- `HeatFlowInterval` is a sample with a `site` foreign key, a top and bottom depth, a vertical
  depth and datum, lithology, stratigraphy and age, and an optional `probe_metadata` (probe type,
  length, penetration, tilt). It holds no location (ADR 0023).
- `HeatFlow` (the child) is a measurement on an interval. It points at one `thermal_gradient`, one
  `thermal_conductivity` and one `parent`, carries `is_relevant`, its `corrections` (type and
  status), and the stored U-score, corrected T- and TC-scores with their missing marks, M-score,
  quality code and scheme revision.
- `ThermalGradient` and `IntervalConductivity` are measurements on an interval, each with its own
  stored score, missing mark and scheme revision, and `heat_flow_children` for the children that
  use it.
- `ParentHeatFlow` is a measurement on the site, with the inherited U-score, M-score, quality code
  and scheme revision, the heat production flag, the curator's comment and the GHFDB id.

What they cannot supply directly: the set of children a parent's quality rests on is worked out
inside `ParentHeatFlow.refresh_quality` and not stored, and the current scheme revision is the
constant `SCHEME_REVISION` in `heat_flow.quality`.

**What FairDM gives.** A type gets its own page from `<app_label>/<model_name>_overview.html`,
extending `sample/sample_overview.html` or `measurement/measurement_overview.html` and filling
blocks. There is one `Overview` plugin per base model (`Sample`, `Measurement`), so a type has no
plugin of its own to add context through. `visible_to(user)` on the sample and measurement
querysets is the rule for who may open a record. A measurement's `effective_location_for` falls
back to its sample's location, and an interval has none, so without this feature every interval,
child, gradient and conductivity page says no location is recorded.

**Components.** `c-mvp.card`, `c-mvp.data_field`, `c-stats`, `c-card.location`,
`c-actions.pending` and FairDM's list rows. FS-007's quality card components sit in
`templates/cotton/card/quality/`. They called `<c-data_field>`, which no longer exists, so the card
could not render on any page. The sketch moves them to `<c-mvp.data_field>`.

**Planning notes.** None for this feature.

## What the screens need from the code

1. Each page's heat flow content gathered once per request. The sketch gathers it again in every
   block that reads it, so a page makes 70 to 300 queries.
2. A way for each heat flow type to add its own content to FairDM's page, given that FairDM has
   one overview plugin per base model.
3. Every listed or linked record checked with `visible_to` for the visitor, with the ones left out
   counted: a site's parent, intervals and children; an interval's site; a child's gradient,
   conductivity, parent, interval and site; a gradient's or conductivity's children; a parent's
   children and site.
4. A site's intervals ordered by top depth, with each interval's children, without a query per
   interval.
5. The children a parent's quality rests on, by the same rule `ParentHeatFlow.refresh_quality`
   applies, and why there are none when there are none (no children, or several and none marked
   relevant). The rule lives in one place.
6. Whether a stored score is stale: a non-empty scheme revision that is not the current one.
7. The site's location, elevation and uncertainty for the interval, child, gradient, conductivity
   and parent pages, or why it is not shown.
8. Quantities written with their unit, a value and its uncertainty as "17.63 ± 0.91 K/km", and
   vocabulary fields written as their labels, whether the field holds one concept or several.
9. A site page that shows every interval on request (`?intervals=all` in the sketch).
10. A real way to see every child when a list of children is cut at twenty (FR-007).

## What the sketch faked

- The context reaches the templates through a template tag, `heat_flow_page`, called in each
  block. Where it lives and how it reaches the page is the plan's to decide.
- The "All heat flow values" button under a long list of children is FairDM's disabled
  placeholder. FR-007 needs a route that works.
- The walkthrough states were seeded by a throwaway script into the development database: the
  datasets "Walkthrough: heat flow page states" (public, published) and "Walkthrough: unpublished
  heat flow records" (private). The build needs a development seeding path that makes the same
  states.
- No tests. FS-007's skipped card tests in `tests/test_templates/test_measurement_detail.py` are
  untouched.
- FS-007's spec still describes its own page story (decision D4). Not edited yet.

## What was ruled by eye

Taste calls, made without a rule to decide them. The orchestrator passed the sketch for Sam under
an open gate, so none of these was changed in review.

- The site's figures strip shows the parent heat flow (with its quality code), the number of
  depth intervals and the number of heat flow values, in place of FairDM's measurements, related
  samples and people counts.
- A site's intervals are an ordered list, shallowest first, with each interval's children nested
  under it, not a table.
- Long lists are cut at twenty intervals and twenty children.
- A child's page reads, in order: the value and method, what it was calculated from, the
  corrections, the quality card, the parent, then the determination details. FairDM's "How it was
  measured" follows.
- The quality code sits in the page header as a badge beside the type, on the child and parent.
- A gradient's result shows the measured and corrected gradients side by side, and its
  temperatures, methods, corrections and shut-in times as a top-and-bottom table.
- An interval's figures strip shows its top, bottom and the number of measurements.
- On a child, gradient and conductivity, a "Measured over" card names the interval and site in
  place of FairDM's "Measured on" sample card.
- The parent page's sample card is titled "Site".

Decisions with a right answer, kept to their rule:

- Every table has a caption and header cells with `scope` (WCAG 2.2, 1.3.1 Info and
  Relationships).
- An empty field reads "Not recorded" and an empty score "Not determined", never a dash or a zero
  (FR-004).
- Numbers use tabular figures so values line up down a list.
- The wording for records left out ("… belongs to a dataset that hasn't been published yet") and
  for cut lists ("and N more") is FairDM's own, from its related-samples and measurements cards.
