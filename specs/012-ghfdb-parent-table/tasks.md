# Tasks: A filterable table of GHFDB parents

**Input**: `specs/012-ghfdb-parent-table/` — spec.md, sketch.md, research.md, plan.md,
decisions.md

**Tests**: required. The sketch's code exists on the branch, so a test written now could pass on
its first run. Every task therefore shows its tests red against the code with the piece under test
removed or broken (the filter, the method, the column, the route), then restores it and shows them
green, and records the command and the failure in the task's evidence. Tests find elements by
`data-` hooks, record URLs and query parameters, never wording (testing standard §1). Records come
from `tests/factories.py`; vocabulary values a test reads are set explicitly.

**Order**: US1 first, then US2, US3 and US4. US1 owns `visibility.py`, the table and the view every
later story uses.

**Kept from the sketch**: the templates, markup and copy (sketch.md "What was ruled by eye").
Behind them, every piece is rebuilt or confirmed under a test.

## Format: `[ID] [Story] Description`

---

## Phase 1: User Story 1 — A visitor browses the parents in a table (P1)

**Goal**: the table lists exactly the parents the visitor may see, in their published columns,
sorted and paged, each row linked to its parent and its site.

**Independent test**: parents in a public dataset and in a private one, and a public parent whose
site is private. A visitor who is not signed in sees only the first set.

- [ ] T001 [US1] Move the parent visibility rule to `project/ghfdb/visibility.py` as
      `served_parents(request)` and call it from `GHFDBParentViewSet` and `GHFDBFlatViewSet`
      (plan.md › Visibility). Tests in `tests/test_ghfdb/test_visibility.py`: a public parent with
      a public site is served, a parent in a private dataset is not, a public parent whose site is
      private is not, a signed-in contributor on the private dataset is served it. The existing API
      tests in `tests/test_ghfdb/` stay green unchanged.
- [ ] T002 [US1] `GHFDBParentTable` in `project/ghfdb/tables.py` (plan.md › The table). Tests in
      `tests/test_ghfdb/test_tables.py`: each published column renders its value under its
      published name; a vocabulary column renders the term's label, never the stored key; a
      missing value renders the not-recorded mark and never `0`, and a value of zero renders `0`;
      `ID_parent` links to the parent's page and `name` to the site's page; `explo_purpose` joins
      several purposes; sorting by `children` and by `name` orders on them, both directions, with
      `ghfdb_id` breaking ties; every number column's heading carries its unit as `title`.
- [ ] T003 [US1] `GHFDBParentTableView`, its route `ghfdb-parent-table` and the template
      `ghfdb/parent_table.html` (plan.md › The views). Tests in
      `tests/test_ghfdb/test_parent_table_view.py`: a visitor who is not signed in gets 200 and
      the rows `served_parents` gives, by `data-parent`; the count shown matches the number served;
      101 parents give two pages of 100 and 1; the page's query count is the same for 3 parents and
      for 30.
- [ ] T004 [US1] Add **GHFDB parent table** to `CONTEXT.md` and write
      `docs/guides/parent-table.md` for US1 (what it lists, which parents, sorting, paging), linked
      from the guides index. The docs build passes.

## Phase 2: User Story 2 — A visitor narrows the table with filters (P1)

**Goal**: every filter in the spec narrows the table, filters combine, the address holds them, and
an invalid value is reported against its filter without narrowing.

**Independent test**: parents differing in heat flow, latitude, environment, quality, dataset and
project; each filter alone, then several together.

- [ ] T005 [US2] `BoundsInput`, `BoundsField` and `BoundsFilter` in `project/ghfdb/filters.py`,
      with `ghfdb/widgets/bounds.html` kept. Tests in `tests/test_ghfdb/test_filters.py`: the
      spec's -30/100 example lists -20 and 60 and not 140; a lower bound alone leaves the upper side
      open and the reverse; a negative bound works; `q_min=abc` and an upper bound below the lower
      are errors on that filter with codes `invalid` and `inverted`, and the table is not narrowed
      by them; the widget sends `<name>_min` and `<name>_max`.
- [ ] T006 [US2] Coordinate bounds: `lat_NS` and `long_EW` with django-mvp-forms `LatitudeField`
      and `LongitudeField` as their ends (research.md N2). Tests: a box lists only the parents whose
      site lies inside it; a latitude of 91 is refused with `max_value` on `lat_NS`.
- [ ] T007 [US2] The choice filters: `environment`, `explo_method`, `explo_purpose` (vocabulary
      choices, counted Tom Select), `corr_HP_flag` (yes, no, not recorded), `U_score`, `M_score`.
      Tests: two environments list parents in either; a purpose matches a parent with that purpose
      among several, listed once; `corr_HP_flag=unknown` lists only parents with no recorded flag;
      U-score and M-score each narrow; the vocabulary filters offer the vocabulary's terms.
- [ ] T008 [US2] `name` search, `project` and `dataset` (`RecordMultipleFilter`, `scope="view"`).
      Tests: a fragment matches the site name in any case; a dataset narrows to its parents and a
      project to the parents of its datasets; a private dataset is refused for a visitor and
      accepted for a contributor on it.
- [ ] T009 [US2] The view's filter layout: `toolbar_filters`, `filter_panel_attrs` and the
      combined behaviour. Tests in `test_parent_table_view.py`: several filters together list only
      parents matching all of them, with the count; the same address in a fresh client gives the
      same rows and order (FR-015); filters that match nothing give the empty state with a clear
      link; the toolbar holds `name`, `corr_HP_flag`, `U_score` and `M_score` and the panel the
      rest.
- [ ] T010 [US2] Document the filters in `docs/guides/parent-table.md`.

## Phase 3: User Story 3 — A visitor sees a parent's children from its row (P1)

**Goal**: each row shows `n (m)`; pressing it opens a dialog listing every child, relevant first
and badged, loaded only then; closing it leaves the table as it was.

**Independent test**: a parent with three children, two relevant.

- [ ] T011 [US3] The `children` column's button and its hooks. Tests in `test_tables.py`: three
      children with two relevant render `data-total="3"` and `data-relevant="2"`; none relevant
      renders `0`; the button's `hx-get` is the parent's children address.
- [ ] T012 [US3] `GHFDBParentChildrenView`, route `ghfdb-parent-children`, fragment
      `ghfdb/parent_children.html`, and `relevance_badge` on `c-heat_flow.child_row`. Tests in
      `tests/test_ghfdb/test_parent_children_view.py`: every child is listed, each relevant child
      before every other and only relevant ones badged; each child links to its page and shows its
      quality code; a child in an unpublished dataset is counted, not named; a parent the visitor
      may not see answers 404, as does an unknown id; the fragment's query count does not grow with
      the number of children; the table page's queries touch no child row (SC-003: the table
      page's query count is unchanged by adding children). The parent overview page, which uses the
      same row without the new attribute, stays green.
- [ ] T013 [US3] Browser test (`e2e`, the repo's Playwright fixture): on the served table, press a
      parent's count; the dialog opens listing that parent's children; close it; the table's address
      and page are unchanged (FR-022).
- [ ] T014 [US3] Document the children window in `docs/guides/parent-table.md`.

## Phase 4: User Story 4 — A visitor finds the table beside the map viewer (P2)

- [ ] T015 [US4] The collapsible GHFDB group in `project/ghfdb/menus.py`. Tests in
      `tests/test_ghfdb/test_menus.py`: the group sits where the map viewer entry was; it holds the
      map viewer link then the table link; the map viewer is no longer a top-level entry; on either
      page the group is open and the current entry is marked current.

## Phase 5: Close

- [ ] T016 Squash nothing (no migration). Run the full suite, lint, types, templates and the docs
      build. Remove `.devserver.env` if one was added.
