# Research: A filterable table of GHFDB parents

**Input**: [spec.md](spec.md), [planning-notes.md](planning-notes.md), [sketch.md](sketch.md),
read against `main` on 2026-10-24.

## Planning notes

### N1. Load the children with htmx

**Adopted.** The count is a button carrying `hx-get` to one address per parent, which returns the
children's list as a fragment into a `<dialog>` on the table page. htmx ships with django-mvp, so
nothing is added. The table's own query never touches the children's rows (FR-021, SC-003): it
reads the two counts as annotations.

### N2. Display the filter fields with django-mvp-forms

**Adopted.** Going through the package's widgets field by field:

| Filter | django-mvp-forms piece | Why |
|---|---|---|
| Every bound (`q`, `q_uncertainty`, `elevation`, both depths) | `RangeInput`, as a join | The package's range widget. Its `joined` layout keeps both ends on one row |
| `lat_NS`, `long_EW` | `RangeInput`, with `LatitudeField` and `LongitudeField` as the two ends | The package's coordinate fields refuse a value outside the earth's range and more than six decimal places, so a box cannot be written that names no place |
| Environment, exploration method and purpose | `TomSelectMultiple(counted=True)` | The counted multiple choice. The standard multiple select is never used in these projects |
| `corr_HP_flag`, U-score, M-score | none: the toolbar's own checkbox dropdown | Sam chose the control FairDM's project list uses for status, which django-mvp draws for a plain `MultipleChoiceFilter` |

The sketch settled one layout the package does not have: [min][–][max], the dash framed as the
package frames text in a `Join`. `RangeInput` offers `joined` (two framed ends, each named) and
`compact` (one frame, a separator). The portal subclasses `RangeInput` and gives it its own
template, `ghfdb/widgets/bounds.html`. It belongs upstream as a third layout and is raised there
as a separate change. The portal does not wait for it.

### N3. Use FairDM's own fields for FairDM records

**Adopted.** Dataset and project are `fairdm.contrib.autocomplete.filters.RecordMultipleFilter`
over `DatasetMultipleChoiceField` and `ProjectMultipleChoiceField`, the filter FairDM's own
measurement and dataset lists use. At `scope="view"` the field offers public records and those the
signed-in person may view, and validates what it is sent against that, never against the page's
search (FR-013).

### N4. Start from the latest FairDM, django-mvp and django-mvp-forms

**Adopted, nothing to change.** `main` pins FairDM at `865964f`, which is the `v0.2.1` tag, the
latest release. django-mvp 0.31.0 and django-mvp-forms 0.8.0 in `uv.lock` are the latest releases
on PyPI. FairDM `main` is twelve commits past `v0.2.1`, unreleased, and a pin moves to a release,
not to a branch.

## The sketch's requirements

Each line of `sketch.md` "What the screens need from the code" and "What the sketch faked", and
where it is met:

| Requirement | Met by |
|---|---|
| Parents the visitor may see, parent and site both visible, one query per page | R1 |
| Vocabulary columns as term labels | R2 |
| Exploration purposes fetched once for the page | `prefetch_related` on the table's queryset, as `GHFDBParentQuerySet.with_children()` already does for the API |
| Dataset and project filters at view scope | N3 |
| Range filters refusing inverted and non-numeric bounds, against the filter | R3 |
| One address per parent returning its children, nothing for a hidden parent | R4 |
| Sorting by `children` and `name`, ID breaking ties | R2 |
| Visibility rule written in the view, not shared | R1 |
| Exploration purpose filter tried against few rows | tested in US-2 |
| The window opening when its content arrives, untested | R4 |
| No glossary entry | CONTEXT.md, US-1 |
| The range layout written in the portal | N2 |

## R1. One visibility rule for the API and the table

`project/ghfdb/viewsets.py` already holds the rule as `served_parents_for(request, view)`: FairDM's
`FairDMVisibilityFilter` applied to the parents and to the sites, and a parent kept only when its
site is among the visible sites (ADR 0021). The filter's `filter_queryset` never reads `view`.

**Decision:** move it to `project/ghfdb/visibility.py` as `served_parents(request)` and call it
from both the viewsets and the table. One function, so the table and the API cannot disagree about
which parents exist (FR-002, spec clarification). The sketch's `visible_parents(user)` used
`visible_to`, a second spelling of nearly the same rule, and is dropped.

## R2. The table

`FairDMTableView` (FairDM) over django-mvp's `MVPTableView`, with a django-tables2 table, is what
the portal's sample and measurement listings use. It brings the toolbar, the filter panel, sorting
by heading, the count, the pager and the empty state.

- **Columns**: the scalar published columns come from `GHFDBParentQuerySet.as_ghfdb_flat()`,
  keyed under their published names. `with_child_counts()` adds `total_children` and
  `relevant_children`. Both exist and are tested (FS-002).
- **Labels**: `environment` and `explo_method` annotate the concept, whose `label` is the term.
  `explo_purpose` is many-valued and is prefetched.
- **Missing values**: the table's `default` is the em dash with "Not recorded" for screen readers,
  FR-005.
- **Sorting**: every scalar column sorts on its annotation. `children` and `name` need an
  `order_<column>` method, and every order adds `ghfdb_id` so ties are stable across pages.
  `explo_purpose` and `p_comment` do not sort.
- **Units**: hover text on the heading, a `title` on the `<th>`.
- **Page size**: `paginate_by = 100`.

## R3. Range filters

django-filter's `RangeFilter` cleans a `slice`. Its field does not compare the two ends, so an
upper bound below the lower one matches nothing in silence. A `RangeField` subclass raises
`ValidationError(code="inverted")` in `compress`. django-mvp drops an invalid filter from the query
and reports it against the field (`MVPListViewMixin.get_filterset`), which is FR-016. The ends are
sent as `<name>_min` and `<name>_max` (`widgets_names`), so an address reads as the bounds it
holds.

## R4. The children window

A `TemplateView` at `ghfdb/parents/<ghfdb_id>/children/` looks the parent up inside
`served_parents(request)` and answers 404 for anything else. Its list is
`HeatFlowPage.for_parent()["children"]` with `show_all`, which already orders relevant children
first, splits off those the visitor may not open and counts them (FS-011). The fragment uses the
portal's `c-heat_flow.child_row` with a new `relevance_badge` attribute.

The dialog opens on htmx's `htmx:afterSwap` on its target. That is script behaviour, so it is
checked in headless Chrome against the served page: press a count, read that the dialog is open
and lists that parent's children, close it, read that the table's address is unchanged (FR-022).

## R5. The sidebar group

django-mvp's `MenuCollapse` is a group that opens on any page it holds. `ghfdb/menus.py` replaces
the single map viewer entry with it, at the same position.

## What already exists

| Piece | Where the search stopped |
|---|---|
| Parent visibility rule | this repo: `served_parents_for` in `ghfdb/viewsets.py`, moved |
| Published parent columns and child counts | this repo: `GHFDBParentQuerySet.as_ghfdb_flat()`, `with_child_counts()` |
| Table page, toolbar, filter panel, pager, empty state | installed package: `FairDMTableView`, django-mvp `table_view.html` |
| Site name search | installed package: `mvp.filters.SearchFilter` |
| Range widget | installed package: django-mvp-forms `RangeInput`, subclassed for its template |
| Coordinate ends | installed package: django-mvp-forms `LatitudeField`, `LongitudeField` |
| Counted multiple choice | installed package: django-mvp-forms `TomSelectMultiple` |
| Dataset and project filters | installed package: FairDM `RecordMultipleFilter` |
| Children ordered relevant first, hidden ones counted | this repo: `HeatFlowPage.for_parent()` |
| Child row | this repo: `c-heat_flow.child_row`, one attribute added |
| Collapsible sidebar group | installed package: django-mvp `MenuCollapse` |
| Dialog and its open/close | the browser: `<dialog>` and `showModal()`, htmx bundled with django-mvp |
| Inverted range check | new code: a `RangeField.compress` override, three lines |
| Corrections filter matching "not recorded" | new code: one filter method |
