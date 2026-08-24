# Reconciliation — 002 the published structure read from the model

`tasks.md` was written as though the repository held no implementation of this feature. This file
walks that list against the code and records, per task, whether the code already satisfies it.

**A task is closed only where a `file.py:line` citation and a passing test both exist, and the test
genuinely exercises what the task describes.** Code with no test does not close a task — the task
stays open and its remaining work is the test. Neither does a test that asserts something weaker
than the task states. The original `tasks.md` recorded 74 of 74 complete. Not one of those ticks was
consulted.

Baseline the reconciliation was measured against: `poetry run pytest tests/test_ghfdb -q` →
**154 passed, 14 xfailed**, on `002-ghfdb-proxy` @ fd2fe52.

## The split

Revised after the design review, which challenged every closure. Three of the six survived.

| | Tasks |
|---|---|
| Closed — code cited and a passing test that covers it | **3** |
| Open — built, but the test does not reach the task's claim | **37** |
| Open — never built | **76** |
| **Total** | **116** |

The total moved from 121 because the review collapsed seven tasks that split a single dictionary
literal into one task per block, and added two the audit had missed.

The shape of that split is the finding. Most of this feature's production code exists and works.
What is missing is a test suite that would notice if it stopped working, and one structural change —
the published-column mapping — that nothing in the repository has any form of.

Five open tasks are defects rather than absences. Two were found by writing the list greenfield
rather than by reading the code, and three more by the design review that challenged it:

- **The site changelist exposes an export it was specified not to have.** FR-021 gives the export
  resource to the determination changelist and to nothing else. `GHFDBParentAdmin` inherits
  `ImportExportMixin` (`project/ghfdb/admin.py:512`) and overrides only
  `get_import_resource_classes`, so the framework's default export path is live on it with a
  generated resource. The test that was meant to prove the requirement asserts the import classes
  and stops (`tests/test_ghfdb/test_admin.py:399`), so it passes over the half that is wrong. T109,
  T110 and T119.
- **The site flattening method returns one row per exploration purpose.** `explo_purpose` is a
  many-to-many field on the site, and the parent queryset annotates it with `F()`
  (`project/ghfdb/managers.py:263`), contradicting its own docstring five lines above. Measured: a
  site carrying two exploration purposes comes back as two rows, and chaining the counts onto it does
  not collapse them. Nothing catches it today because the method has no caller, and T115 gives it
  one. T059 now excludes the column and T062 prefetches it instead, which is what R3 already says
  many-valued columns get.
- **Four changelist headings are already wrong, for a reason the plan would have reproduced.** Django
  resolves a `list_display` entry against the model's fields before the admin's attributes, and reads
  `short_description` only when no field matches. So a column named after a model field takes the
  field's `verbose_name`: `expedition` renders as "expedition/platform/ship", `c_comment` as
  "comment", `water_temperature` as "bottom water temperature", and the leading identifier as "ID
  Child". All four measured. The mapping would have inherited the fault, because it binds callables
  under published names. T077 now requires the entries to be named differently from the columns they
  render, and T070, T079 and T099 assert rendered headings rather than entry names.
- **The import route writes without consulting any read-only guarantee.** Both registrations declare
  no add, no change and no delete, and both inherit an import action that `django-import-export`
  grants to any staff user whenever `IMPORT_EXPORT_IMPORT_PERMISSION_CODE` is unset — verified unset
  in this project. T085 and T105 prove read-only by asserting three hooks the import path never
  reaches. T123 covers it.
- **The search test cannot fail.** `test_ghfdb_admin_search_by_name_and_id_parent`
  (`tests/test_ghfdb/test_admin.py:127`) issues two search requests and asserts `status_code == 200`
  on each. A search matching nothing returns 200. Neither assertion can distinguish working search
  from broken search. T082 and T102.

## Closed

| Task | Code | Test |
|---|---|---|
| T013 — the determination manager hides unpublished rows | `project/ghfdb/managers.py:178` | `tests/test_ghfdb/test_managers.py:215` |
| T044 — the site manager hides unpublished rows | `project/ghfdb/managers.py:278` | `tests/test_ghfdb/test_managers.py:240` |
| T089 — it carries the determination import resource and the export resource | `project/ghfdb/admin.py:231` | `tests/test_ghfdb/test_admin.py:110` |

Both scoping closures are genuine: each builds an unpublished record, proves it exists through the
underlying model's own manager, and asserts it is absent from the proxy's. T089's test covers the
import attachment and the export attachment, which is the whole of what the task claims.

### Three closures the design review reversed

Reconciliation is the stage most likely to be wrong, and it fails quietly, which is why the review
went looking here at all. It found three, and all three stand.

- **T049 was closed on the wrong model.** It is a parent-flattening task, and both citations were
  child-side: `managers.py:102` is the determination queryset's elevation annotation, and the cited
  test asserts a key on `GHFDBChild.objects.none()`. The same test class is disqualified as
  insufficient for T016 a few rows below, for exactly the reason that should have disqualified it
  here — it checks that a key exists, never that a value resolves on a row.
- **T078 and T098 were closed on a superuser**, while T009 is held open on the grounds that a
  superuser is not the staff user the tasks name. The same evidence cannot be sufficient in one row
  and insufficient in another. A superuser bypasses view-permission checks entirely, so neither test
  can detect a registration unreachable for the audience the specification names. The remaining work
  on each is one line once T009's fixture exists.

## Open — built, but the test does not reach the task's claim

The production code is cited. The work is the test, and in a few cases a small correction the test
will force.

### Phase 1 — fixtures

| Task | Built at | What remains |
|---|---|---|
| T002 vocabulary preload | `tests/test_ghfdb/conftest.py:17` | nothing asserts the fixture's contract, and every other test depends on it silently |
| T003 dataset fixture | `tests/test_ghfdb/conftest.py:30` | the same |
| T004 one complete chain | `tests/test_ghfdb/conftest.py:36` | the fixture builds the full graph with both published identifiers set. No test asserts it is complete, so a silently truncated fixture would weaken every test that takes it |
| T009 staff client | pytest-django's `admin_client`, used throughout | a superuser is not the staff user with view permission the task names, so no test proves the changelists are reachable on view permission alone |

### Phase 2 — determinations

| Task | Built at | What remains |
|---|---|---|
| T011 the proxy adds no table | `project/ghfdb/models.py:57` | `tests/test_ghfdb/test_models.py:11` asserts `Meta.proxy`, and does not assert the table is `HeatFlow`'s or that no local field is declared |
| T012 translated verbose names | `project/ghfdb/models.py:59` | the names are asserted as strings. The lazy wrapper is not |
| T014 scoping survives chaining | `project/ghfdb/managers.py:178` | proven on the manager only. R6 records why that proves less than it looks |
| T015 ordinary operations match the model | `project/ghfdb/managers.py:49` | `test_managers.py:118` covers count, filter and order_by. Slicing is absent, and nothing compares the result against `HeatFlow` restricted to published rows |
| T016 every scalar column resolves | `project/ghfdb/managers.py:89` | the test that asserts the annotation set is `xfail(strict=True)` (`test_managers.py:28`). `test_resources/test_managers.py:22` covers ten annotation keys and passes, against `.none()` — so it checks the keys exist and never that a value resolves on a row |
| T017 the site block reaches each row | `project/ghfdb/managers.py:112` | no test reads the restated parent block off a determination row |
| T018 query count equal at two row counts | `project/ghfdb/managers.py:78` | `test_managers.py:17` bounds the count at one chain. R2 records why a bound at one row cannot fail for the reason it exists |
| T019–T021 absent gradient, conductivity, probe metadata | `project/ghfdb/managers.py:89` | no partial-chain fixture exists, so no test covers a missing relationship at all |
| T022 a missing correction empties only its own column | `project/ghfdb/managers.py:25` | `test_managers.py:82` asserts `hasattr` for all nine flags on a chain that has all nine corrections. It never removes one, and never reads a value |
| T023 annotations carry published names | `project/ghfdb/managers.py:89` | ten of thirty-four keys are pinned. Nothing checks that each name on the collision list is a field the base class actually declares, so the list is an escape hatch rather than a rule |
| T024 every column resolves on the complete row | `project/ghfdb/managers.py:143` | nothing reads the fifteen many-valued columns off an export row |
| T025 export query count equal at two row counts | `project/ghfdb/managers.py:152` | `test_managers.py:106` bounds at sixteen queries on one chain |
| T026 many-valued columns read without further queries | `project/ghfdb/managers.py:152` | the sixteen-query bound covers evaluation, not the zero-query read after it |
| T031, T032 the spine and the scalar annotation set | `project/ghfdb/managers.py:78`, `:89` | both exist. They close when T016, T017 and T018 do. The review collapsed the seven per-block tasks into T032, because they split one dictionary literal into seven pieces of work that would have collided on it |
| T040 the export queryset | `project/ghfdb/managers.py:143` | closes when T024, T025 and T026 do |

T027, T039 and T041 are not in this group. See "never built".

### Phase 3 — sites

| Task | Built at | What remains |
|---|---|---|
| T049 a non-colliding parent column keeps its published name | `project/ghfdb/managers.py:260` | nothing reads the value off a row. The only parent-side key assertion is also `.none()`-based and sits behind a dead conditional skip (`tests/test_ghfdb/test_resources/test_managers.py:189`) |
| T042 the proxy adds no table | `project/ghfdb/models.py:84` | as T011 |
| T043 translated verbose names | `project/ghfdb/models.py:86` | as T012 |
| T045 scoping survives chaining | `project/ghfdb/managers.py:278` | as T014 |
| T046 every scalar parent column resolves | `project/ghfdb/managers.py:248` | `test_resources/test_managers.py:188` covers six of fourteen keys, against `.none()` |
| T047 query count equal at two row counts | `project/ghfdb/managers.py:243` | no query-count test covers the parent flattening at all |
| T048 the colliding site name is annotated distinctly | `project/ghfdb/managers.py:257` | the annotation is pinned. The restoration of the published name at the surface is not, because that surface does not read the annotation |
| T050 counts are correct across contribution shapes | `project/ghfdb/managers.py:216` | `test_managers.py:160` covers one site with one contributing determination. All-contributing, some, and none are not covered |
| T052 count query equal at two row counts | `project/ghfdb/managers.py:216` | `test_managers.py:145` bounds at three queries on one chain |
| T053 attachment costs no query per site | `project/ghfdb/managers.py:231` | `test_managers.py:177` bounds evaluation and iteration together at three queries on one site. A per-site query would not breach that bound at one site |
| T054 attachment query equal at two row counts | `project/ghfdb/managers.py:231` | as T053 |
| T055 every parent column on the complete row | `project/ghfdb/managers.py:233` | the one many-valued parent column is never read off a row |
| T059, T061, T062 the parent annotation set and its two methods | `project/ghfdb/managers.py:248`, `:216`, `:231` | each exists. They close when the tests above do. T060 folded into T059, and T059 now excludes `explo_purpose` — see the defects above |

### Phase 4 — the changelists

| Task | Built at | What remains |
|---|---|---|
| T078 the determination changelist renders for a staff user | `project/ghfdb/admin.py:129` | the test takes a superuser, so nothing proves the page is reachable on view permission alone |
| T098 the site changelist renders for a staff user | `project/ghfdb/admin.py:511` | as T078. Its test additionally asserts the heading `quality`, which D2 rules must read `quality_parent`, so the test it was closed on has to change |
| T079 published columns in canonical order | `project/ghfdb/admin.py:147` | `test_admin.py:17` asserts against a literal copy of the list, which is the third copy. The current order also disagrees with `constants.py` on three names and on the order of the last two (D2) |
| T080 four orientation columns and no fifth | `project/ghfdb/admin.py:147` | the leading columns are right. Nothing asserts there is no fifth |
| T081 site values not restated per row | `project/ghfdb/admin.py:147` | true of the code, asserted nowhere |
| T083 the eight filters are offered | `project/ghfdb/admin.py:209` | the tuple is asserted. No filter is applied and no rows are checked |
| T084 each vocabulary filter offers its own terms | `project/ghfdb/admin.py:30,56,80` | environment and exploration method are covered properly (`test_admin.py:220,247`). Exploration purpose asserts the concept set and never that the choice text is the label |
| T085 no route to add, change or delete | `project/ghfdb/admin.py:434` | the three hooks return false and `list_display_links` is `None`. No test asserts any of it |
| T090 the registration | `project/ghfdb/admin.py:129` | closes when T079, T080 and T081 do |
| T092 the changelist queryset | `project/ghfdb/admin.py:413` | `test_admin.py:158` proves it evaluates. Nothing proves an unpublished row is absent from it, or that its query count is constant |
| T093 search fields | `project/ghfdb/admin.py:204` | the search test cannot fail — see the split above |
| T094 the plain filters | `project/ghfdb/admin.py:209` | closes with T083 |
| T096 the three vocabulary filters wired on | `project/ghfdb/admin.py:209` | closes with T084 |
| T097 the resources attached | `project/ghfdb/admin.py:231` | closed as T089 for the positive half. The exclusivity half is T110, which is open and failing |
| T099 parent columns in canonical order | `project/ghfdb/admin.py:521` | `test_admin.py:324` asserts a literal copy, including the heading `quality`, which D2 rules should read `quality_parent` |
| T100 the geography follows the published block | `project/ghfdb/admin.py:536` | the order is right. Nothing asserts it is *after* rather than among |
| T101 the two counts come last | `project/ghfdb/admin.py:541` | position asserted. The rendered values are not |
| T102 parent search | `project/ghfdb/admin.py:544` | no search test exists for this changelist at all |
| T103 the eight filters | `project/ghfdb/admin.py:548` | the tuple is not asserted for this changelist, and no filter is applied |
| T104 each vocabulary filter on this changelist | `project/ghfdb/admin.py:467,489` | environment and exploration method are covered (`test_admin.py:278,299`). Exploration purpose on this changelist is covered by nothing, though the filter class exists (`admin.py:444`) |
| T105 no route to add, change or delete | `project/ghfdb/admin.py:696` | as T085 |
| T111–T113 the registration and its columns | `project/ghfdb/admin.py:511` | close when T099, T100 and T101 do |
| T115 the changelist queryset | `project/ghfdb/admin.py:685` | it does not read the flattening method. R5 records that fifteen display methods walk relationships per column instead |
| T116–T118 search, plain filters, vocabulary filters | `project/ghfdb/admin.py:544–557` | close with T102, T103 and T104 |

## Open — never built

Seventy-four tasks. Grouped by what is absent rather than listed one by one. The identifiers are
exhaustive.

**The published-column mapping and everything on it — T063 to T077, and the parts of T090, T111 and
T113 that consume it.** There is no `columns.py`, no mapping from published column name to
accessor, and no builder. Both changelists hand-write their column tuples
(`project/ghfdb/admin.py:147,521`) and the determination list is hand-written a second time in its
test (`tests/test_ghfdb/test_admin.py:17`). This is the structural change the rest of the work turns
on: fifteen mapping tasks, and it is what makes T079, T099 and SC-007 provable rather than restated.

**Test fixtures — T001, T005, T006, T007, T008, T010.** The counted fixture every constancy test
needs, the unpublished chain, the four partial chains, the four contribution shapes, and the
constant-query-count helper. The helper is itself a gate and T010 requires it proven against a
deliberately linear callable, not only against a passing one.

**The three columns nothing resolves — T027, T041, T069, T075.** `Ref_IGSN` returns an empty string
from a stub (`project/ghfdb/admin.py:409`), and `publication_reference` and `data_reference` reach
for attributes that do not exist on `HeatFlow` and fall through a `getattr` guard
(`project/ghfdb/admin.py:295,302`). R4 dumps the model's field set: there is no reference
relationship on it. Nothing tests any of the three. The guards are replaced by the explicit
treatment `Ref_IGSN` gets, so a reader cannot mistake a guard for a working accessor, and the two
reference columns are filed against the roadmap item that attaches literature to records.

**Absent-relationship behaviour — T039.** Nothing proves a row survives a missing relationship,
because no fixture produces one.

**The parameterised vocabulary filter — T095.** Six near-identical `SimpleListFilter` subclasses
exist (`project/ghfdb/admin.py:30,56,80,444,467,489`), differing only in the vocabulary and the
lookup path. One class taking both is the task, and six callers is what earns it.

**Read-only proof — T085, T105, and the rendered halves of T091 and T114.** The hooks are written.
No test opens either changelist and looks for an add link or a row that links into a form.

**Scoping proved at the changelist — T086, T106.** R6 records these as the assertions that would
catch an override that stopped going through the scoped manager.

**Query constancy at the changelist — T087, T107.** Neither changelist has ever been measured.

**The framework's admin checks — T088, T108.** Nothing runs them against either registration, which
is the mechanical way FR-020 is discharged for the display, filter and search declarations at once.

**Resource exclusivity — T110, and the corrected T109 and T119.** The site changelist's export path
is live and specified not to be, as recorded in the split above.

**Two tasks the audit missed, added by the review — T122, T123.** D7 rules that
`GHFDBParent.as_dict()` is removed and no task did it. And the import route named above.

**Migrations — T029, T057.** Both proxies are recorded
(`project/ghfdb/migrations/0002_ghfdb.py`, `0003_ghfdbchild_ghfdbparent.py`), and `tests/
test_migrations.py` exists, but nothing asserts that either migration's operations are a proxy
`CreateModel` alone. The task's own defence — that an `AddField` in a proxy migration is the defect
— is unarmed.

**Suite health — T120.** Fourteen tests under `tests/test_ghfdb/` are `xfail(strict=True)` and one
carries a conditional `skip` that can no longer fire
(`tests/test_ghfdb/test_resources/test_managers.py:193`). Thirteen of the fourteen belong to
`003-ghfdb-import-export` and stay, by D5. The fourteenth
(`tests/test_ghfdb/test_managers.py:28`) is this feature's and is resolved by D6. So T120 asserts
the condition for this feature's own modules and names the exclusion, rather than asserting it
across the package.

**Documentation — T121.** No page describes the query surface. `docs/ghfdb_fields.md` is the field
map and does not cover the proxies, their scoping rule or the five queryset methods.

## What this feature does not build, restated

Confirmed absent and deliberately so: any reference relationship on the determination model, any
field holding sample numbers, any change to `ghfdb_colmeta.json` or the routes serving it, and the
map viewer page. The first is filed, the rest are settled in `decisions.md`.
