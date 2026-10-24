# Implementation Plan: A filterable table of GHFDB parents

**Branch**: `012-ghfdb-parent-table` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: the approved spec, the approved sketch ([sketch.md](sketch.md)) and
[research.md](research.md).

## Summary

A table page on FairDM's `FairDMTableView` lists the GHFDB parents a visitor may see, in their
published columns, with a filter set built from django-mvp-forms widgets and FairDM's record
filters. The parent visibility rule moves out of the API viewsets into one function both call. A
second view returns a parent's children as a fragment that htmx loads into a dialog. The sidebar's
map viewer entry becomes a collapsible group. The sketch's templates, markup and copy are kept.
The code behind them is rebuilt test-first.

## Technical Context

**Language/Version**: Python 3.13, Django 6.0

**Primary Dependencies**: FairDM v0.2.1, django-mvp 0.31.0, django-mvp-forms 0.8.0,
django-tables2, django-filter, research-vocabs. No new dependency.

**Storage**: PostgreSQL with PostGIS. No migration.

**Testing**: pytest, pytest-django, factory-boy, `django_assert_num_queries`, headless Chrome for
the dialog script.

**Performance Goals**: the table page and the children fragment each make a fixed number of
queries, whatever the number of rows or children (testing standard §5).

**Constraints**: the table and the API apply one visibility rule (FR-002). The table loads no child
record (FR-021, SC-003).

## Design

### Visibility: `ghfdb/visibility.py`

```python
def served_parents(request) -> GHFDBParentQuerySet:
    """GHFDB parents the request may see: the parent and its site both visible (ADR 0021)."""
```

Moved from `viewsets.served_parents_for`. `GHFDBParentViewSet.get_queryset` and
`GHFDBChildViewSet.get_queryset` call it (`GHFDBFlatViewSet` reuses the child viewset's), and so
do both new views. `docs/guides/published-structure-api.md` names the old function and is updated.

### The table: `ghfdb/tables.py`

`GHFDBParentTable(django_tables2.Table)`, columns in published order with `children` after
`q_uncertainty`. `NumberColumn` right-aligns in tabular figures and puts the unit in its heading's
`title`. `TermColumn` shows a concept's label. The default is the not-recorded mark.
`render_ID_parent` and `render_name` link to the parent's and the site's page. `render_children`
draws the `n (m)` button with `hx-get` to the children address. Every column sorts (FR-007):
`order_children` and `order_name` order on their annotations, `p_comment` on its own, and
`explo_purpose` on a subquery reading the alphabetically first purpose of the site (D6), never a
join. **Every sort ends in `ghfdb_id` (D7)**, including the default and the plain column sorts:
the table overrides django-tables2's ordering hook so the tie-break is appended whatever column
was chosen. `TermColumn` holds one vocabulary instance for the column, not one per cell. The
empty-cell mark carries `data-state="not-recorded"`, built lazily so it is translated per
request.

### The filters: `ghfdb/filters.py`

`GHFDBParentFilter(FilterSet)`:

| Name | Filter | Where |
|---|---|---|
| `name` | `SearchFilter(fields=["sample__name"])` | toolbar |
| `corr_HP_flag` | `MultipleChoiceFilter`, yes, no, not recorded | toolbar |
| `U_score`, `M_score` | `MultipleChoiceFilter` over the score choices | toolbar |
| `q`, `q_uncertainty`, `elevation`, `total_depth_MD`, `total_depth_TVD` | `BoundsFilter` | panel |
| `lat_NS`, `long_EW` | `BoundsFilter` with coordinate ends | panel |
| `environment`, `explo_method` | `MultipleChoiceFilter`, counted Tom Select, vocabulary choices | panel |
| `explo_purpose` | the same, filtering by `sample__in=<sites with any chosen purpose>`, a subquery, so the counted query gains no join (design review SPEC-001) | panel |
| `project`, `dataset` | `RecordMultipleFilter`, `scope="view"` | panel |

`BoundsInput(RangeInput)` draws `ghfdb/widgets/bounds.html` and sends `_min` and `_max`.
`BoundsField(RangeField)` raises `inverted`. A coordinate bound uses `LatitudeField` or
`LongitudeField` for its two ends.

### The views: `ghfdb/views.py`

- `GHFDBParentTableView(FairDMTableView)`: `served_parents(request)` with the flat columns, the
  purposes prefetched, and **the two counts taken over the children the visitor may see (D5)**:
  `Count("children", filter=Q(children__in=<visible children>))` and the same with
  `children__is_relevant=True`, where the visible children are FairDM's `visible_to` for the
  request's user, as a subquery. `toolbar_filters = ["name", "corr_HP_flag", "U_score",
  "M_score"]`, `filter_panel_attrs = {"position": "end", "breakpoint": False}`,
  `paginate_by = 100`, `page_title` "GHFDB".
- `GHFDBParentChildrenView(TemplateView)`: 404 unless the parent is in `served_parents(request)`.
  Context: the parent and `HeatFlowPage(parent, user).listing(<its children, relevant first>)`,
  which splits off and counts those the visitor may not open without the rest of `for_parent()`'s
  work.

Routes: `ghfdb/parents/` (`ghfdb-parent-table`) and `ghfdb/parents/<int:ghfdb_id>/children/`
(`ghfdb-parent-children`).

### Templates (kept from the sketch)

- `ghfdb/parent_table.html` extends `table_view.html` and adds the `<dialog id="children-dialog">`
  with its target `#children-window`.
- `ghfdb/parent_children.html`, the fragment.
- `ghfdb/widgets/bounds.html`, the range.
- `cotton/heat_flow/child_row.html` gains `relevance_badge`.

### Hooks the tests find elements by

`data-ghfdb="parent-row"` with `data-parent="<ghfdb_id>"` on each row, `data-state="not-recorded"`
on an empty cell, `data-ghfdb="children-count"`
with `data-total` and `data-relevant` on the button, the existing `data-heat-flow="child"`,
`data-relevant` on child rows, and `data-ghfdb="relevant-badge"` on the badge.

### Menu: `ghfdb/menus.py`

`MenuCollapse("ghfdb")` with the map viewer then the table, inserted where the map viewer entry
was.

### Documentation

- `CONTEXT.md`: **GHFDB parent table**, under the spreadsheet section, so it is not called "the
  database" and is not confused with the map viewer.
- `docs/guides/parent-table.md`: what the table lists, the filters, the children window, its
  address. Added to the guides index.

## Constitution Check

- Development standards, testing standard: tests first for every behaviour the spec names,
  hooks not wording, query counts on the list and the fragment.
- No new dependency, no migration.
- The `[min][–][max]` range is written in the portal and raised upstream separately, so the
  portal carries no workaround for a package defect: it is a layout the package lacks, not a fault.

## Project Structure

```text
project/ghfdb/
├── visibility.py          # new: served_parents
├── viewsets.py            # calls served_parents
├── filters.py             # new
├── tables.py              # new
├── views.py               # two views added
├── urls.py                # two routes
├── menus.py               # the collapsible group
└── templates/ghfdb/
    ├── parent_table.html
    ├── parent_children.html
    └── widgets/bounds.html
templates/cotton/heat_flow/child_row.html
tests/test_ghfdb/
├── test_visibility.py
├── test_tables.py
├── test_filters.py
├── test_views.py          # TestGHFDBParentTableView, TestGHFDBParentChildrenView,
│                          # and the dialog's browser test (requires_browser)
└── test_menus.py
CONTEXT.md, docs/guides/parent-table.md
```

## Complexity Tracking

None.
