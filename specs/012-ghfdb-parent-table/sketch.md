# Sketch: A filterable table of GHFDB parents

## What exists

- `GHFDBParent` (`project/ghfdb/models.py`) is the proxy over `ParentHeatFlow`. Its manager
  already has `as_ghfdb_flat()`, which keys the scalar parent columns under their published
  names, and `with_child_counts()`, which annotates `total_children` and `relevant_children`.
- The table page is django-mvp's `table_view.html` behind FairDM's `FairDMTableView`, the same
  page the portal's sample and measurement listings use. It brings the search in the toolbar,
  the filter panel beside the table, sorting by column heading, the result count, the pager and
  the "nothing matches" state.
- The rows in the children window are the portal's own `c-heat_flow.child_row`, the row the
  parent's page lists its children with. `HeatFlowPage.for_parent()` already orders them
  relevant first and counts the ones the visitor may not open.
- The sidebar group is django-mvp's `MenuCollapse`, which opens itself on the page it holds.
- Every bound filter is django-mvp-forms' `RangeInput`, drawn as one join, [min][–][max], with
  the dash framed as the package frames text in a `Join` (planning note N2).
- Each select in the toolbar is a django-mvp-forms `Join` of a short label and the select,
  laid out with a crispy `FormHelper` on the view.
- Dataset and project are FairDM's `RecordMultipleFilter` over its dataset and project record
  fields, the filter FairDM's own measurement lists use (planning note N3).
- Children load into the window with htmx when the count is pressed (planning note N1).

## What the screens need from the code

1. The table needs every parent the visitor may see, where both the parent and its site pass
   FairDM's `visible_to`, with its published columns and its two child counts, in one query
   per page.
2. The vocabulary columns need each term's label, read from the concept the annotation returns.
3. The `explo_purpose` cell needs each parent's exploration purposes, prefetched for the page.
4. The dataset and project filters offer what FairDM's record fields offer at `view` scope:
   public records, and a signed-in person's own.
5. Each bound filter needs to reject an upper bound below its lower bound, and a value that is
   not a number, against that filter.
6. The children window needs one address per parent that returns its children, relevant first,
   and nothing for a parent the visitor may not see.
7. The sort by `children` and by `name` needs an order on the annotations, with the parent's ID
   as the tie-break.

## What the sketch faked

- No tests. Every filter, the visibility rule and the children window are unverified beyond
  loading them against the development database.
- The parent visibility rule is assembled in the view (`visible_parents`) rather than shared
  with the API's parent endpoint. FR-002 needs the two to be one rule.
- The `explo_purpose` filter matches on the concept's name and was checked against one term.
- The `children` column's sort and the `name` sort are written on the table and were only
  checked by eye on the first page.
- The window's open-on-arrival relies on htmx's `after-swap` event on the target, untested in a
  browser.
- No CONTEXT.md entry for the GHFDB parent table yet.
- Planning note N4 (the latest FairDM, django-mvp and django-mvp-forms) is not done. django-mvp
  0.31.0 and django-mvp-forms 0.8.0 are already the latest releases. The FairDM pin moves at the
  start of the build.
- The range template (`ghfdb/widgets/bounds.html`) is the portal's own. django-mvp-forms has a
  joined and a compact range but not [min][–][max]. It belongs upstream as a third layout.

## What was ruled by eye

- The column headings are the published names verbatim. A column's unit is hover text on its
  heading only.
- The `children` column sits straight after `q` and `q_uncertainty`, so the count that says how
  far to trust a value is read next to the value.
- The toolbar holds the site name search, then Environment, U-score and Dataset selects, each
  with its short label joined in front. Every range, `q` included, is in the panel.
- A range is [min][–][max].
- The page title is "GHFDB".
- The quality code filter is offered as the U-score and the M-score, the two grades the code
  starts with, rather than as the full code string.
- The window lists every child with the portal's own child row, and a relevant child carries a
  "Relevant" badge in place of the parent page's relevance text.
- The sidebar group is called GHFDB, with "Map Viewer" and "Parent Table" inside it.
- 50 rows to a page.
