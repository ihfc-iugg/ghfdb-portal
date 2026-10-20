# Implementation Plan: Heat flow content on the site and measurement overview pages

**Branch**: `011-heat-flow-overview-pages` | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: the approved spec, the passed sketch ([sketch.md](sketch.md)) and [research.md](research.md).

## Summary

Each heat flow type gets a page template extending FairDM's shared sample or measurement overview,
filling its blocks with the record's heat flow content. The sketch's templates and copy are kept.
What sits behind them is rebuilt test-first: a class, `HeatFlowPage`, gathers what a page lists
for the visitor, a template tag hands it to the templates once per render, and one model method,
`ParentHeatFlow.quality_basis()`, holds the inheritance rule the parent's score and its page both
read. FS-007's quality card, broken since its component was renamed, is repaired and returns on
the child, gradient and conductivity pages, with a new card for the parent.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2

**Primary Dependencies**: FairDM f69c9cb (overview pages, `visible_to`), django-cotton, django-mvp
components, research-vocabs, pint. No new dependency.

**Storage**: PostgreSQL with PostGIS. No migration.

**Testing**: pytest, pytest-django, factory-boy, `django_assert_num_queries`

**Target Platform**: the portal's server-rendered pages

**Project Type**: web application (Django project)

**Performance Goals**: a page's query count does not grow with the number of intervals, children
or corrections it lists (testing standard §5).

**Constraints**: FairDM's overview pages are extended, never replaced (FR-009, Article XIII). Every
listed record passes `visible_to` for the visitor (FR-006).

**Scale/Scope**: six page templates, one module, one tag library, one model method, eleven Cotton
components (seven new, four touched).

## Design

### What each page gathers: `heat_flow/overview.py`

```python
class HeatFlowPage:
    """What a heat flow record's overview page lists, for one visitor."""

    intervals_shown = 20
    children_shown = 20

    def __init__(self, record, user, show_all=False): ...

    def context(self) -> dict: ...         # dispatches on the record's type
    def for_site(self) -> dict: ...        # parent, intervals with their children, counts
    def for_interval(self) -> dict: ...    # site, probe metadata, site location
    def for_child(self) -> dict: ...       # gradient, conductivity, corrections, parent, interval, site
    def for_source(self) -> dict: ...      # a gradient's or conductivity's children, interval, site
    def for_parent(self) -> dict: ...      # children, the ones its quality rests on, site

    def opens(self, record) -> bool: ...         # would the record's own page open for the visitor
    def split(self, records) -> tuple: ...       # (the visitor may open, how many they may not)
    def site_location(self) -> dict: ...
    @staticmethod
    def is_stale(record) -> bool: ...
```

- `split` makes one `visible_to` query per list (`Sample.objects` for samples,
  `Measurement.objects` for measurements), so a list costs the same for one record or many.
- A list longer than its cut shows the first rows, says how many more, and links to the same page
  with `?show=all`. `show_all` lifts the cut.
- A site's children are fetched for all shown intervals at once, `prefetch_related("method")`,
  and grouped in Python.
- Ordering: intervals by `top`, then `bottom`, then `pk` (FR-015). A parent's children with the
  relevant ones first.

### The template tag: `heat_flow/templatetags/heat_flow_overview.py`

- `{% heat_flow_page record as hf %}` builds `HeatFlowPage(record, request.user,
  show_all=request.GET.get("show") == "all").context()` the first time a render asks for that
  record, and keeps it in `context.render_context`, so the second block asking reads the same
  dict without a query.
- `{{ concepts|labels }}`: the labels of one concept or a many-to-many manager, joined by commas,
  each in the request's language where the concept is a graph concept.
- `{{ value|plus_minus:uncertainty }}`: pint's `plus_minus`, written as text; the value alone
  when the uncertainty is empty; an empty string when the value is.

Each `*_overview.html` calls the tag in each block that reads it, as the sketch does.

### The parent's inheritance rule: `ParentHeatFlow.quality_basis()`

Returns `(basis, children)`: `single` and the one child, `relevant` and the relevant children,
`none` (several, none relevant) or `empty` (no children) with no children. `refresh_quality` is
rewritten to call it, with its tests unchanged and still green.

### Templates and components (kept from the sketch)

- `project/heat_flow/templates/heat_flow/{heatflowsite,heatflowinterval,heatflow,
  thermalgradient,intervalconductivity,parentheatflow}_overview.html`.
- `templates/cotton/heat_flow/`: `field`, `code`, `stale`, `child_row`, `children`,
  `measured_on`, `site_location`.
- `templates/cotton/card/quality/`: `index` and `own` moved to `<c-mvp.data_field>`; `grades`,
  `flags` and `parent` added.
- The disabled "All heat flow values" placeholder becomes a "Show all" link (sketch need 10).
- The `quantity` filter the sketch added is dropped: a quantity's own `str()` already writes its
  unit, and empty values use `default_if_none:''`.

### Hooks the tests find elements by

Tests find elements by `data-` attributes and by the records' URLs, never by wording
(testing standard §1). The plan adds: `data-heat-flow="<what>"` on each card or list a test reads
(`gradient`, `conductivity`, `corrections`, `parent`, `intervals`, `children`, `interval`,
`site`, `probe`, `location`), `data-state` on its empty, hidden and stale states, `data-hidden`
carrying a hidden count, and `data-more` carrying a cut list's remainder. FS-007's existing
`data-quality*` hooks stay.

### Development data

`DemoGraph` gains a step, run by `seed_demo_data` on the first dataset it builds, that varies a
few of that dataset's sites so every state the walkthrough lists is reachable (research R4).
Records in an unpublished dataset are added to a published site by the command, which already
makes private datasets. Documented in `docs/development/demo-data.md`.

### Documentation

- `docs/guides/record-pages.md`, new, in the guides navigation: what each record's page shows a
  reader, written per story, with a closing section for developers naming `HeatFlowPage`,
  `heat_flow_page`, `labels`, `plus_minus`, `ParentHeatFlow.quality_basis` and the template
  names, with a minimal example of adding a block (Article VI).
- `docs/guides/quality-scores.md`: where the scores now appear.
- FS-007's spec: US-5 and FR-018 point at FS-011 (decision D4).
- `docs/adr/0024-…`: research R1, numbered at the push for the merge gate.
- `CHANGELOG.md`: one entry.

## Constitution Check

| Article | Check |
|---|---|
| I Testing | Every story test-first; page tests by data hooks; query counts on the three list pages |
| II Simplicity | One class, one tag library, one model method; no dependency |
| III Anti-abstraction | No base class; `HeatFlowPage` is one class with one method per page |
| V Security | All output through the template layer; listed records filtered by `visible_to` |
| VI Documentation | Guide page, developer section with an example, CHANGELOG, ADR |
| VIII i18n | Every string wrapped; labels read in the request's language |
| X Cohesion | The sketch's module functions become `HeatFlowPage` methods; the parent rule moves onto the model |
| XIII FairDM-first | FairDM's pages extended through type templates and blocks; `visible_to` reused |

## Project Structure

```text
project/heat_flow/
├── overview.py                         # HeatFlowPage
├── models/parent.py                    # ParentHeatFlow.quality_basis()
├── demo.py                             # page-state variation
├── templatetags/heat_flow_overview.py  # heat_flow_page, labels, plus_minus
└── templates/heat_flow/*_overview.html
templates/cotton/heat_flow/*.html
templates/cotton/card/quality/*.html
tests/test_heat_flow/test_overview.py
tests/test_heat_flow/test_templatetags/test_heat_flow_overview.py
tests/test_heat_flow/test_models/test_parent.py
tests/test_heat_flow/test_demo.py
tests/test_templates/test_{heatflow,heatflowsite,heatflowinterval,thermalgradient,
                          intervalconductivity,parentheatflow}_overview.py
docs/guides/record-pages.md
```

`tests/test_templates/test_measurement_detail.py` (FS-007, skipped) is split into the child,
gradient and conductivity page modules and unskipped.

## Complexity Tracking

| Choice | Why | Simpler option rejected |
|---|---|---|
| A template tag gathers page context | FairDM has one plugin per base model and no hook (research R1) | Swapping FairDM's registration: private state |
| `labels` filter | Two concept kinds with different `label` shapes | `i18n_label` reads one kind only |
