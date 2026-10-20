# Tasks: Heat flow content on the site and measurement overview pages

**Input**: `specs/011-heat-flow-overview-pages/` — spec.md, sketch.md, research.md, plan.md,
decisions.md

**Tests**: required. The sketch's templates exist and are kept, so a page test written now could
pass on its first run. Every task therefore shows its tests red against the code with the piece
under test removed or broken (the template block, the method, the hook), then restores it and
shows them green, and records the command and the failure in the task's evidence. Tests find
elements by `data-` hooks and record URLs, never wording (testing standard §1). Records come from
`tests/factories.py`; vocabulary values a test reads are set explicitly.

**Docs**: each story documents the public names it introduces in `docs/guides/record-pages.md`,
in its own task, never batched into the last story.

## Format: `[ID] [Story] Description`

---

## Phase 1: User Story 1 — A visitor reads a child's heat flow and how it was reached (P1)

**Goal**: a child's page shows its value and method, the gradient and conductivity it was
calculated from, its corrections, its quality card, its parent and relevance, and its interval
and site, each linked and limited to what the visitor may open.

**Independent test**: render a child with a gradient, a conductivity, corrections, a parent and
stored scores, and find each of them, linked.

- [ ] T001 [US1] Rebuild `project/heat_flow/overview.py` as the `HeatFlowPage` class of plan.md
      › *What each page gathers*: `__init__`, `context`, `opens`, `split`, `is_stale`,
      `site_location` and `for_child`. Delete the sketch's module functions. Tests first in
      `tests/test_heat_flow/test_overview.py`, class per method: `split` returns the records the
      visitor may open and counts the rest, with one query for any number of records; `opens`
      for anonymous visitors, a dataset member and a published dataset; `is_stale` for the
      current revision, an older one and an empty one; `for_child` with each related record
      present, absent, and in an unpublished dataset.
- [ ] T002 [US1] Rebuild `project/heat_flow/templatetags/heat_flow_overview.py` per plan.md ›
      *The template tag*: `heat_flow_page` (cached in the render context), `labels`,
      `plus_minus`; drop `quantity` and change the templates that used it to a quantity's own
      text with `default_if_none:''`. Tests first in
      `tests/test_heat_flow/test_templatetags/test_heat_flow_overview.py` (create the
      subpackage with `__init__.py`): `labels` for a graph concept, a many-to-many of two, an
      empty manager and `None`; `plus_minus` with and without an uncertainty and for an empty
      value; `heat_flow_page` gathers once when two blocks of one render ask (query count).
- [ ] T003 [US1] Child page: add the data hooks of plan.md › *Hooks* to
      `heatflow_overview.html`, `measured_on.html`, `child_row.html`, `code.html` and
      `stale.html`. Tests first in `tests/test_templates/test_heatflow_overview.py`,
      `TestChildPage`: spec US-1 scenarios 1–7 (scenario 5 by a stale revision); edge cases: no
      gradient, no conductivity, no corrections against a correction recorded as not
      recognised, no parent, an unscored child, a gradient, conductivity or parent in an
      unpublished dataset (shown as hidden, never named or linked); FairDM's shared page is kept
      (FR-009: the identifiers and citation cards are present, and the Manage menu for a dataset
      manager); the same query count for one and for three corrections. Move FS-007's `TestChildCard` from
      `tests/test_templates/test_measurement_detail.py` into this module unskipped, its fixtures
      pointed at the child's overview page and unchanged otherwise.
- [ ] T004 [US1] Docs: create `docs/guides/record-pages.md` with the child page section and the
      developer section (`HeatFlowPage`, `heat_flow_page`, `labels`, `plus_minus`, the template
      names, one example of a type template filling a block), add it to the guides toctree; in
      `docs/guides/quality-scores.md` say where the scores are shown; edit
      `specs/007-quality-scores/spec.md` US-5 and FR-018 to point at FS-011 as current text
      (decision D4). Verify with the Sphinx build.

---

## Phase 2: User Story 2 — A visitor reads a site's heat flow (P1)

**Goal**: a site's page shows its parent value and quality, its own description, and its
intervals from shallowest to deepest with each interval's children.

**Independent test**: a site with a parent and two intervals, one carrying two children: the
parent, both intervals in order and the three children are found, linked.

- [ ] T005 [US2] `HeatFlowPage.for_site`: the parent, the intervals ordered by top then bottom,
      each with its children, the cut at `intervals_shown` lifted by `show_all`, and the hidden
      counts. Tests first in `tests/test_heat_flow/test_overview.py`, `TestForSite`.
- [ ] T006 [US2] Site page: data hooks in `heatflowsite_overview.html`; the "Show all" link to
      `?show=all#intervals`. Tests first in `tests/test_templates/test_heatflowsite_overview.py`,
      `TestSitePage`: spec US-2 scenarios 1–5; a site with more than twenty intervals shows
      twenty and the remainder, and shows all with `show=all`; an interval and a child in an
      unpublished dataset are counted, never linked; a parent in an unpublished dataset is
      hidden; the same query count for a site with one interval and with three, each carrying
      children.
- [ ] T007 [US2] Development data: the page-state step of plan.md › *Development data* in
      `project/heat_flow/demo.py`, called from `seed_demo_data` on the first dataset of a run.
      Tests first in `tests/test_heat_flow/test_demo.py` and the command's tests: after a run,
      each state of research R4 exists. Document it in `docs/development/demo-data.md`.
- [ ] T008 [US2] Docs: the site section of `docs/guides/record-pages.md`, including the
      "Show all" behaviour.

---

## Phase 3: User Story 3 — A visitor reads a gradient's or a conductivity's own record (P2)

**Goal**: a gradient's or conductivity's page shows its own fields and score, its interval and
site, and the children that use it.

**Independent test**: a gradient and a conductivity, each used by two children: their fields,
their score and both children are found, linked.

- [ ] T009 [US3] `HeatFlowPage.for_source`: the interval, the site, the children that use the
      measurement with the cut and hidden count. Tests first in
      `tests/test_heat_flow/test_overview.py`, `TestForSource`.
- [ ] T010 [US3] Gradient and conductivity pages: data hooks in `thermalgradient_overview.html`,
      `intervalconductivity_overview.html` and `children.html`; the "Show all" link replacing
      the disabled placeholder. Tests first in
      `tests/test_templates/test_thermalgradient_overview.py` and
      `test_intervalconductivity_overview.py`: spec US-3 scenarios 1–5 (scenario 2 by the
      concepts set on the conductivity); a score not determined is never zero; more than twenty
      children cut and shown in full with `show=all`; the same query count for one child and
      three. Move FS-007's `TestMeasurementCard` in, unskipped, and delete
      `tests/test_templates/test_measurement_detail.py`.
- [ ] T011 [US3] Docs: the gradient and conductivity sections of `docs/guides/record-pages.md`.

---

## Phase 4: User Story 4 — A visitor reads how a parent's value and quality were reached (P2)

**Goal**: a parent's page shows its designation, its inherited quality and the children it rests
on, every child with its relevance, and its site.

**Independent test**: a parent with three children, two relevant: all three listed with their
relevance, the two relevant marked as what its quality rests on, the site linked.

- [ ] T012 [US4] `ParentHeatFlow.quality_basis()` per plan.md, and `refresh_quality` rewritten to
      call it. Tests first in `tests/test_heat_flow/test_models/test_parent.py`,
      `TestQualityBasis`: one child (relevant or not), several with some relevant, several with
      none, no children. The existing `refresh_quality` tests stay unchanged and green.
- [ ] T013 [US4] `HeatFlowPage.for_parent`: the children (relevant first) with the cut and hidden
      count, the basis and the ids it rests on, the site. Tests first in
      `tests/test_heat_flow/test_overview.py`, `TestForParent`.
- [ ] T014 [US4] Parent page: data hooks in `parentheatflow_overview.html` and
      `card/quality/parent.html` (`data-quality="basis"` carries the basis). Tests first in
      `tests/test_templates/test_parentheatflow_overview.py`: spec US-4 scenarios 1–5; the
      quality card's stored grades and flags; a stale revision; more than twenty children cut
      and shown in full; a child in an unpublished dataset counted; the same query count for one
      child and three.
- [ ] T015 [US4] Docs: the parent section of `docs/guides/record-pages.md`, and
      `ParentHeatFlow.quality_basis` in its developer section.

---

## Phase 5: User Story 5 — A visitor reads a depth interval and where it lies (P3)

**Goal**: an interval's page shows its depth, rock and probe, its site, and the site's location;
every measurement page on an interval shows the site's location too.

**Independent test**: an interval with probe metadata at a site with a location: depth range,
probe, site link and coordinates found; a child on it shows the same coordinates.

- [ ] T016 [US5] `HeatFlowPage.for_interval`. Tests first in
      `tests/test_heat_flow/test_overview.py`, `TestForInterval` and `TestSiteLocation` (a
      site with a location, without one, and in an unpublished dataset).
- [ ] T017 [US5] Interval page and the location card on every page: data hooks in
      `heatflowinterval_overview.html` and `site_location.html`. Tests first in
      `tests/test_templates/test_heatflowinterval_overview.py`: spec US-5 scenarios 1–4; the
      site's coordinates on the child, gradient, conductivity and parent pages, and the
      no-location state on each.
- [ ] T018 [US5] Docs: the interval section and the location paragraph of
      `docs/guides/record-pages.md`; ADR for research R1 under `docs/adr/` with the index
      updated; the `CHANGELOG.md` entry.
