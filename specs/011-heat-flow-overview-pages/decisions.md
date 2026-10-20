# FS-011 decisions

Rationale too long to inline in the spec, and the ambiguities resolved without asking. Nobody was
interviewed for this specification, so every reading below was made from the request, the
repository and FairDM, and is recorded here so it can be overruled.

## Why this is a feature

After this work, a visitor can read on a heat flow record's own page what makes it a heat flow
record: a site's parent value, quality and intervals, a child's gradient, conductivity, corrections
and quality, and the same for the gradient, conductivity, parent and interval. Today that needs the
API or a download. That is several new ways for a user to work with the site, and no existing spec
describes the record pages, so it is a feature.

## The agreed reading

Every heat flow site, depth interval and heat flow measurement page shows the heat flow content
that belongs to its record, on top of what FairDM's shared overview page already shows. A site
shows its parent value and quality and the intervals and children beneath it. A child shows the
gradient and conductivity it was calculated from, its corrections and how its quality code was
reached. A gradient, a conductivity and a parent show their own records, the children they relate
to, and their own quality. An interval shows its depth range, its rock and its probe metadata. Every
page links to the records it names and shows only the ones the visitor may open. Forms (#286), API
representations (#287) and the published-structure API (FS-006) stay outside it.

## D1. The interval's page is in scope, at P3

The request lists the site, child, gradient, conductivity and parent pages, and opens with "every
site and measurement in the portal has an overview page". An interval is a sample with a page of its
own. Leaving it out would leave one page in the record without heat flow content, and would leave
the location problem in D2 unsolved for the interval itself. It is the lowest priority because a
reader usually reaches it from a page that already names its depth range.

## D2. Interval and measurement pages show the site's location

A site holds the location, and an interval and its measurements hold none (ADR 0023). FairDM's
measurement page falls back to the sample's location, and the sample of a child, gradient or
conductivity is an interval, which has none, so every one of those pages would say no location is
recorded. The pages show the site's location and say it is the site's, as FairDM does when it falls
back to a sample.

## D3. "How it was reached" means what FS-007's quality card showed

For a child, the request asks for "its quality code with how it was reached". FS-007 built a card
for exactly this: the own scores beside the corrected scores, the U-score, the M-score, the flags
and the revision (FS-007 US-5, FR-018). It is the reading the portal already settled on. Showing
each criterion and penalty would be a second feature, and the quality scores guide already explains
them.

For a parent, its quality is inherited from its children, so the explanation is which children it
rests on. Its value is designated by curators, and the page does not try to explain a designation
beyond the curator's comment and the children listed.

## D4. This feature takes over FS-007's page story

FS-007 US-5 and FR-018 describe a child's page, and a gradient's and conductivity's page, showing
their scores. That page was removed when FairDM replaced its measurement page with the overview, and
the card has been on no page since (#263). FS-011 US-1 and US-3 now carry that behaviour. The build
edits FS-007's spec so US-5 and FR-018 point at FS-011 and read as current, in this feature's pull
request, without strike-through. The tests FS-007 wrote for the card, skipped since #263, are either
brought back against the new pages or replaced by this feature's own.

## D5. A list of related records shows only what the visitor may open

FairDM already applies this rule to the records its shared pages list: a record in a dataset the
viewer may not see is counted and never named. The heat flow lists follow the same rule, decided
for each listed record by whether its own page would open. A site and its records normally sit in
one dataset, so this rarely shows, but nothing enforces that.

## D6. Long lists are cut and counted, not paged in place

A site can carry hundreds of intervals. The spec asks that a page show part of a long list, say how
many more there are and offer a way to see them, and leaves the cut-off and the route to planning.
FairDM's own lists do the same (ten measurements on a sample, eight siblings on a measurement).

## D7. Who the stories are about

"Visitor" is anyone reading the portal, signed in or not, limited by FairDM's visibility rules. It
is the request's "most people outside the assessment team", and G7's "anyone, no account required".
It is a word for this spec, not a role, so CONTEXT.md gains no entry.

## D8. Success criteria come from the request's last sentence

"It should answer their questions without a trip to the API or a download" is the measure. SC-001
makes it checkable: every value in a release row is readable on one of the pages involved, with the
publication's own columns on the dataset page FairDM already provides.

## FairDM

The spec is written against the pinned FairDM, f69c9cb. FairDM's default branch is at 2bebf29b, two
commits ahead (Django 6.0, and development accounts moved to example.com). Neither touches the
overview pages, their plugins or their guide, so this feature needs nothing from a newer FairDM.

What the build extends, at f69c9cb:

- `<app_label>/<model_name>_overview.html` gives a type its own page, extending
  `sample/sample_overview.html` or `measurement/measurement_overview.html` and filling
  `overview.properties`, `overview.result`, `overview.badges`, `overview.location` and the rest.
- `fairdm.core.sample.plugins.Overview` and `fairdm.core.measurement.plugins.Overview`, both
  `TypedOverviewPlugin` subclasses, hold what a page computes, as methods a portal can override.
- `docs/portal-development/overview-pages.md` in FairDM describes both.

The quality card components FS-007 built are still in `templates/cotton/card/quality/`, and
`tests/test_templates/test_measurement_detail.py` holds their skipped tests.

## Dependencies

None open. FS-007 (quality scores) is delivered. The sibling requests #286 and #287 touch other
surfaces and neither waits on this one.
