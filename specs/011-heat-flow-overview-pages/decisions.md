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

**ADR:** none — scope of this feature, recorded in the spec.

## D2. Interval and measurement pages show the site's location

A site holds the location, and an interval and its measurements hold none (ADR 0023). FairDM's
measurement page falls back to the sample's location, and the sample of a child, gradient or
conductivity is an interval, which has none, so every one of those pages would say no location is
recorded. The pages show the site's location and say it is the site's, as FairDM does when it falls
back to a sample.

**ADR:** none — what the pages show; ADR 0023 already decides the site holds the location.

## D3. "How it was reached" means what FS-007's quality card showed

For a child, the request asks for "its quality code with how it was reached". FS-007 built a card
for exactly this: the own scores beside the corrected scores, the U-score, the M-score, the flags
and the revision (FS-007 US-5, FR-018). It is the reading the portal already settled on. Showing
each criterion and penalty would be a second feature, and the quality scores guide already explains
them.

For a parent, its quality is inherited from its children, so the explanation is which children it
rests on. Its value is designated by curators, and the page does not try to explain a designation
beyond the curator's comment and the children listed.

**ADR:** none — a reading of the request, recorded in the spec.

## D4. This feature takes over FS-007's page story

FS-007 US-5 and FR-018 describe a child's page, and a gradient's and conductivity's page, showing
their scores. That page was removed when FairDM replaced its measurement page with the overview, and
the card has been on no page since (#263). FS-011 US-1 and US-3 now carry that behaviour. The build
edits FS-007's spec so US-5 and FR-018 point at FS-011 and read as current, in this feature's pull
request, without strike-through. The tests FS-007 wrote for the card, skipped since #263, are either
brought back against the new pages or replaced by this feature's own.

**ADR:** none — a hand-over between two specs.

## D5. A list of related records shows only what the visitor may open

FairDM already applies this rule to the records its shared pages list: a record in a dataset the
viewer may not see is counted and never named. The heat flow lists follow the same rule, decided
for each listed record by whether its own page would open. A site and its records normally sit in
one dataset, so this rarely shows, but nothing enforces that.

**ADR:** none — FairDM's existing visibility rule, applied.

## D6. Long lists are cut and counted, not paged in place

A site can carry hundreds of intervals. The spec asks that a page show part of a long list, say how
many more there are and offer a way to see them, and leaves the cut-off and the route to planning.
FairDM's own lists do the same (ten measurements on a sample, eight siblings on a measurement).

**ADR:** none — superseded in detail by D10, a page detail.

## D7. Who the stories are about

"Visitor" is anyone reading the portal, signed in or not, limited by FairDM's visibility rules. It
is the request's "most people outside the assessment team", and G7's "anyone, no account required".
It is a word for this spec, not a role, so CONTEXT.md gains no entry.

**ADR:** none — vocabulary of this spec only.

## D8. Success criteria come from the request's last sentence

"It should answer their questions without a trip to the API or a download" is the measure. SC-001
makes it checkable: every value in a release row is readable on one of the pages involved, with the
publication's own columns on the dataset page FairDM already provides.

**ADR:** none — how the success criteria were derived.

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

## Build decisions (2026-10-20)

Made while planning and building, after the sketch was passed.

## D9. Each type's content reaches FairDM's page through a template tag

FairDM's overview has one plugin per base model and no hook for a type's own context, and its
plugin registry cannot replace a registration (research R1). A type template is the one route
that reaches the page, so the visitor-dependent lists are gathered by a template tag that hands
the record and the visitor to `HeatFlowPage`, cached once per render.

**ADR:** graduates at convergence (durable, cross-cutting, not visible in the code).

## D10. Long lists show twenty and a "Show all" link

Intervals on a site and children on a gradient, conductivity or parent are cut at twenty, say
how many more there are, and link to the same page with `?show=all`, which lifts the cut. The cut
of twenty was ruled by eye at the sketch. The link replaces FairDM's disabled placeholder, which
would not meet FR-007. A site's children are listed under their interval and are not cut.

**ADR:** none — a page detail, set by the sketch, that nothing else inherits.

## D11. The parent's inheritance rule moves onto the model

Which children a parent's quality rests on was worked out inside `refresh_quality`. The page has
to name them (FR-019), and a second copy of the rule could disagree with the score, so it becomes
`ParentHeatFlow.quality_basis()`, called by both.

**ADR:** none — the rule is FS-007's (ADR 0004 covers the portal computing the scores); this
moves it, it does not change it.

## D12. The walkthrough states come from the demo data command

The sketch's states were seeded by hand. The development seeding path makes them, on the first
dataset of a run, so anyone with a development database can reach every state the pages answer
for.

**ADR:** none — development data only.

## D13. FS-007's card tests move to the pages that now carry the card

`tests/test_templates/test_measurement_detail.py` has been skipped since #263. Its child-card
tests move to the child page's module and its measurement-card tests to the gradient and
conductivity modules, unskipped, with fixtures pointed at the overview pages and assertions
unchanged. The old module is deleted.

**ADR:** none — test placement.

## D14. Design review: approved, findings carried into the plan

The design review approved the plan with no critical or high finding. Each medium and low
finding was a small edit and was made in `plan.md`, `tasks.md` and `research.md` rather than
carried as a watch item:

- The child's quality card reads its gradient's and conductivity's scores from the records the
  visitor may open, so a hidden one shows no score (SEC-001, FR-006).
- `<c-heat_flow.field>` carries `data-field` and a `not-recorded` state, and every page test
  asserts its story's fields by it (SPEC-003).
- Interval lithology and child methods are prefetched on every list (ARCH-001).
- The stale notice, the interval and site links, and FairDM's shared page are tested on every
  page that carries them (SPEC-002, SPEC-005, SPEC-006).
- Cut-list tests set the cut small instead of pinning twenty (SPEC-007), and the parent's
  relevant-first order is not asserted (SPEC-008).
- A record's site is read from the existing `site` properties, with no helper (ARCH-002).
- `for_source` is named `for_gradient_or_conductivity`, since `IntervalConductivity` already has
  a `source` field.
- T007 stays (D12) and the review app's command is named in the plan (SPEC-009).

The stories build in order on the feature branch, one at a time, because all five extend one
class and one guide page (SPEC-004).

**ADR:** none — plan corrections local to this feature.

## D15. SC-001 reads "on the child's page or a record it links to"

SC-001 names the child's, parent's, site's and dataset's pages, while the spec's own stories put
the gradient's, conductivity's and interval's release columns on those records' pages. The plan
takes the reading the stories imply: every release column is shown on the child's page or on a
record it links to, and a test reads the columns from the export resource and finds each one on
its page. The spec's wording is the orchestrator's to settle under the open spec gate.

**ADR:** none — reading of a success criterion.

## D16. US1 ports the other pages onto `HeatFlowPage` unchanged

The sketch's module functions are deleted with the module, but the other five pages still need
their content until their own stories rebuild them test-first. `HeatFlowPage` therefore carries
`for_site`, `for_interval`, `for_gradient_or_conductivity` and `for_parent` with the sketch's
logic, now reading the shared `opens`, `split` and `listing`. One test asserts that `context()`
reaches a method for every type. The tag still reads `?intervals=all` so the site template's
link keeps working; the site story moves it to `?show=all` with its template. The four methods
are documented in `docs/guides/record-pages.md` so the docs check is clean, and each story that
rebuilds one updates that row.

**ADR:** none — a stage in building the feature.

## D17. Repairs to the pages and fixtures the sketch and FS-007 left behind

- `heatflowinterval_overview.html` named the icons `arrow-up` and `arrow-down`; the registry has
  `arrow_up` and `arrow_down`, and the page raised `IconNotFoundError` when rendered. Fixed in
  passing, since the page could not otherwise be rendered by the smoke test of the tag library.
- FS-007's card fixtures could not run against the page: they built records in datasets that
  are not published, and the `conductivity` fixture passed `location=[]`, a field since renamed
  `conductivity_location`. The `page` and `query_count` fixtures now read the page signed in as a
  superuser, who may open every record; the field name is corrected. No test body changed.
- The `field` component's `data-field` and `not-recorded` state moved from T002 to T003, because
  the page test that drives them is a child-page test.

**ADR:** none — repairs to test support and a sketch template.

## D18. US1's changes to existing tests are formatting and fixture repairs

The test-change check flagged seven existing test modules after US1. Four (`test_demo`,
`test_refresh_quality`, `test_child`, `test_quality`) parse to the same syntax tree before and
after: formatter output only. `test_signals` carries the linter's automatic fixes (nested `with`
blocks joined, one unused import removed) with no assertion changed. `tests/test_templates/
conftest.py` and `test_measurement_detail.py` are the fixture repairs and test moves of D13 and
D17. Accepted.

**ADR:** none — test housekeeping.

## D19. The page states are made on the first complete dataset, from records moved, not added

**Decision:** with `--page-states` (D20), `seed_demo_data` calls `DemoGraph.vary_page_states` on the first dataset of the run
whose assessment is complete (public and published), and passes the run's first dataset, which is
private and unpublished, as the place hidden records go. The step moves existing records into
that dataset and adds only empty intervals, so a run still makes the same number of datasets,
sites and children.

**Why:** the first dataset of a run is only described, so it is private. A visitor cannot open
its sites, and a state such as "an interval in a dataset the visitor may not open" needs a site
the visitor can open. Moving records leaves the counts that the command's size tests assert
(four datasets, eighty sites, two hundred children) as they were.

**Revisit if:** the order of assessment states in `STATE_PLAN` changes, or the command is asked
to make more children to show a cut list with children in every interval.

**ADR:** none — development data only.

## D20. The page states are made only when `seed_demo_data --page-states` asks for them

FS-008's command tests promise that a default run scores every record under the current scheme
revision, matches a fresh recalculation and gives every site its own coordinates. The page
states need the opposite: a stale score, an unscored child and a site with no location. Those
promises stay true for a default run, and the states are made only when `--page-states` is
passed. A test asserts a default run varies nothing. The orchestrator made this change directly
to finish T007: one option, one guard and the tests' fixture.

**ADR:** none — development data only.

## D21. Two of FS-007's measurement card tests could not move unchanged

**Decision:** `TestMeasurementCard` moved into the gradient and conductivity page modules,
unskipped. Two things changed to let it run:

- The `child`, `gradient`, `conductivity` and `probe_interval` fixtures in
  `tests/test_templates/conftest.py` now build their records in the published dataset. The
  child page showed FairDM's "only people with access can see this" notice for a record in an
  unpublished dataset, and `test_the_placeholder_alert_is_gone` counts every alert. No test
  body changed for this one.
- `test_a_measurement_of_another_type_shows_no_card` asserted `card.cards == []` for a parent.
  The parent's page now carries its own quality card (`data-quality-card="parent"`), so the test
  is renamed and asserts `["parent"]`: another type shows its own card and not the gradient's
  or the conductivity's. This is a changed assertion in a test written for FS-007, made because
  the premise (no other type has a card) stopped being true when the parent card was added.

**Why:** the first is a fixture repair of the kind D17 made. The second cannot be satisfied
without removing the parent's card, which US4 and plan.md › Templates and components require.

**Revisit if:** Forge triage prefers the test dropped, or a measurement type with no card is
added.

**ADR:** none — test placement.

## D22. The release columns the page test reads are the ones the export resource writes

**Decision:** the SC-001 test takes the names in `GHFDBExportResource.Meta.export_order` that
the resource also carries a field for, compared ignoring case. That is 63 columns. It does not
take the resource's own field list, which includes every model field (`uuid`, `measurement_ptr`
and so on), and it does not take the order's names alone, which list nine columns the resource
has no field for (`ID_parent`, `quality_parent`, `quality_child`, `Quality_Code_Child`,
`Quality_Score_Parent`, `Reviewer_name`, `Reviewer_comment`, `Review_date`, and `ID` as a
published column). The model's `id` field matches `ID` by name, so `id` is mapped to the
child's `ghfdb_id`, the child's own identifier.

**Why:** the brief asks for the columns the resource writes, read from the resource. Neither list
on its own is that, and a hand list is not allowed.

**Revisit if:** the half-landed column work behind the xfailed tests in
`tests/test_ghfdb/test_resources/test_export.py` is finished, and the resource declares the nine
columns it lacks. The test then fails on each until the table names a page for it.

**ADR:** none — test method.

## D23. The release columns with no page of ours got a field on the page that could hold them

**Decision:** `ref_igsn` is shown on the interval page (`for_interval` returns `igsn`).
`data_reference` and `publication_reference` are shown on the child's determination card from the
dataset's data reference and related literature. The child's corrections and its relevance carry
`data-field`, as does the parent's value.

**Why:** the table must name a page for every column. FairDM's shared page shows the identifiers
and the citation but marks nothing a test can find. The two reference columns are always empty in
the export, so the child's fields read the dataset's own references, the nearest stored source.

**Revisit if:** the export fills those two columns from a stored value, or Forge triage prefers
them named under the dataset page.

**ADR:** none — placement of fields.
