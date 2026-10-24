# The GHFDB parent table

The GHFDB parent table lists the parents of the Global Heat Flow Database, one row each, so a
visitor can scan them, sort them and open one. It is at `/ghfdb/parents/` and is open to anyone
reading the portal, signed in or not.

## Which parents it lists

The table lists the parents the portal serves to that visitor, and nothing else. It applies the
rule the [published structure API](published-structure-api.md) applies to its parent route, from
the same function, `served_parents()`, so the two never disagree:

- A parent is listed when its dataset is public and published, or the visitor holds a level on it.
- A parent is listed only when the site it describes is visible to the visitor too. A parent in
  a public dataset whose site sits in a private one is left out.
- A parent with no published identifier is not listed.

A signed-in contributor sees their private datasets' parents beside the public ones. The number
shown above the table is the number of parents listed for that visitor.

## The columns

A row holds the parent's published columns, under their published names: `ID_parent`, `q`,
`q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `explo_method`,
`explo_purpose`, `total_depth_MD`, `total_depth_TVD`, `corr_HP_flag`, `quality_parent` and
`p_comment`, with `children` after `q_uncertainty`.

- `ID_parent` links to the parent's page and `name` to the page of its site.
- `environment` and `explo_method` show the term's label, never the stored key.
- `explo_purpose` joins a site's purposes with semicolons.
- A value that is not recorded shows a dash, read out as "Not recorded". A recorded zero shows as
  `0`: the table never turns an empty value into a number.

## Children

The `children` column shows `n (m)`: `n` is the number of child heat flow values the parent has and
`m` how many of them are marked relevant. Both count only the children the visitor may open. A
child in a dataset that is not yet published is counted in neither number for a visitor outside
that dataset, and in both for a contributor on it.

Pressing the count opens a window over the table that lists the parent's children. The window
loads only then, so the table itself never reads a child. It lists every child the visitor may
open, the relevant ones first and each marked **Relevant**, then the others. Each child links to
its page and shows its quality code. The count in the row equals the children listed, and the
number in brackets the children marked. A child the visitor may not open is not named: the window
says how many more there are. Closing the window leaves the table, its page and its address as
they were.

The window is served at `/ghfdb/parents/<ID_parent>/children/`, which answers 404 for a parent
the visitor may not see and for an identifier that does not exist.

## Sorting

Every column sorts, ascending and then descending, by pressing its heading. `children` sorts on the
number of children, `name` on the site's name and `explo_purpose` on its alphabetically first purpose.

When rows tie on the chosen column, the table puts them in order of `ID_parent`. A parent therefore
appears on exactly one page of a sorted table, however many pages it has, and a page reached twice
shows the same rows.

## Paging

The table shows a fixed number of rows to a page and links to the others. The page is part of the
address (`?page=2`), as is the sort, so an address reopens the same page in the same order. The
number of queries the page makes does not grow with the number of rows on it.

## Filtering

The search box and the three quality and correction filters sit above the table. The rest are in
the filter panel, opened by the **Filters** button. Pressing a filter narrows the table, and
parents must match every filter that is set. The number above the table is the number of parents
that match.

| Filter | What it matches |
|---|---|
| `name` | Site names containing any of the words typed, in any case. |
| `corr_HP_flag` | Parents whose heat production correction is yes, no or not recorded. Choosing several lists parents in any of them. |
| `U_score`, `M_score` | Parents with any of the chosen quality grades. |
| `q`, `q_uncertainty`, `elevation`, `total_depth_MD`, `total_depth_TVD` | A range of values: a minimum, a maximum or both. |
| `lat_NS`, `long_EW` | A range of degrees, so two of each draw a box on the map. |
| `environment`, `explo_method`, `explo_purpose` | Parents whose site has any of the chosen terms of that vocabulary. A parent with several purposes is listed once, however many are chosen. |
| `project`, `dataset` | Parents in any of the chosen datasets, or in any dataset of the chosen projects. |

A range accepts negative values, and an empty side is open: a minimum alone lists everything at or
above it. A parent with no value in a ranged column is not listed once that range is set.
`project` and `dataset` offer the records the visitor may see: a signed-in contributor can pick
their private datasets, and a visitor cannot.

### Values the filters refuse

A value that cannot be used is reported on its own filter and narrows nothing, so the table stays
as it was:

- A bound that is not a number is refused with the code `invalid`.
- A maximum below the minimum is refused with the code `inverted`.
- A latitude beyond 90 degrees or a longitude beyond 180 is refused with the code `min_value` or
  `max_value`.
- A dataset or project the visitor may not see is refused with the code `invalid_choice`.

### The address

Every filter is a query parameter, so the address holds the table as it is shown. A range sends
its two ends as `<name>_min` and `<name>_max`, for example
`/ghfdb/parents/?q_min=-30&q_max=100`. Opening the address in another browser, signed in as the
same person or not, lists the same rows in the same order. The link to clear the filters, shown when nothing matches,
removes every filter.

## For developers

The page is `GHFDBParentTableView` in `project/ghfdb/views.py`, routed as `ghfdb-parent-table`. Its
rows come from `served_parents()` with the flat columns and the visible child counts added, and it
draws `GHFDBParentTable` from `project/ghfdb/tables.py`.

The table's building blocks:

- `NumberColumn` right-aligns a number in tabular figures and writes its unit into the heading's
  `title`.
- `TermColumn` shows a vocabulary concept's label.
- `not_recorded()` builds the dash an empty cell shows, translated for the request, and the
  `NOT_RECORDED` string it reads aloud. The mark carries `data-state="not-recorded"`.
- `TieBrokenQuerysetData` is the table's data class. It appends `ghfdb_id` to every ordering,
  because django-tables2 orders by the chosen column alone.

`GHFDBParentQuerySet.with_visible_child_counts(user)` adds the two counts, `total_children` and
`relevant_children`, over the children `HeatFlow.objects.visible_to(user)` returns, as one subquery.
`with_child_counts()` counts every child and serves the API, where visibility is applied
separately.

`GHFDBParentChildrenView` draws the window, from `ghfdb/parent_children.html`, routed as
`ghfdb-parent-children`. It looks the parent up in `served_parents()` and lists its children through
`HeatFlowPage.listing()`, relevant first.

The count's button carries `data-ghfdb="children-count"` with `data-total` and `data-relevant`, and
`hx-get` set to the window's address. In the window each child is a `data-heat-flow="child"` row
with `data-child` and `data-relevant`, and a relevant one holds a `data-ghfdb="relevant-badge"`.

Each row carries `data-ghfdb="parent-row"` and `data-parent`, the parent's published identifier,
so a script or a test can find a row without relying on the wording of a cell.

The filters are `GHFDBParentFilter` in `project/ghfdb/filters.py`, a django-filter filter set the
view names as its `filterset_class`. The view's `toolbar_filters` lists the four filters drawn above
the table and `filter_panel_attrs` places the panel at the end of the page at every width.

- `BoundsFilter` filters one number column by a minimum, a maximum or both. Its `end_field`
  argument names the form field that cleans each end, `LatitudeField` for `lat_NS` and
  `LongitudeField` for `long_EW`, which is what refuses 91.
- `BoundsField` is its form field. It raises `ValidationError` with the code `inverted` when the
  maximum is below the minimum.
- `BoundsInput` draws the two ends as one joined control, from `ghfdb/widgets/bounds.html`, and
  names them `<name>_min` and `<name>_max`.
- `explo_purpose` filters by `sample__in=<the sites with any chosen purpose>`, a subquery, so the
  query gains no join and each parent's child counts stay as they were.
