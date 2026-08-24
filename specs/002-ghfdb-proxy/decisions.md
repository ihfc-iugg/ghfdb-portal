# Decisions — 002 the published structure read from the model

The specification in this directory was written in April 2026 and rewritten in place on 2026-08-23
after an audit against the code. This file records what the audit found and how each disagreement
was settled, so that the rewrite can be read against the original rather than replacing it
silently.

Git history holds the original text. Nothing here is a substitute for reading it.

## How the audit ran

Every requirement in the original specification was checked against the implementation and sorted
into four groups:

- still true
- drifted
- absent
- behaviour the code has that the specification never mentioned

The task list was then rewritten as though no code existed, and reconciled against the codebase
afterwards, so that what the feature is missing is measured against what it should have been
rather than against what was built.

The original `tasks.md` recorded 74 of 74 tasks complete. That is a claim made by the run that
wrote it and was not treated as evidence of anything.

The original specification was amended in place four times for defects and twice for design
changes, each time by striking the superseded text through and appending the replacement to the
same sentence. Several requirements had accumulated three readings in one paragraph. The rewrite
carries the final reading only.

## Settled

### D1 — The changelist column order is a requirement, and it is derived rather than restated

**Original**: the specification named all 54 determination columns and all 21 site columns in
order, twice each — once in an acceptance scenario and once in a functional requirement.

**Code**: `admin.py` restates both lists as `list_display` tuples, and `test_admin.py` restates the
determination list a third time as a literal to assert against.

**Ruled**: the order is a genuine requirement and stays. These changelists are how the assessment
team reads the database, and that team knows it as the published spreadsheet. A different order
would draw complaints from users who know only that file.

But four copies of one list is what let them drift — see D2. The requirement is now expressed as
"the order the canonical column definitions give", and both the changelist and its test read that
module rather than a copy of it. The specification names no column list at all.

### D2 — The changelists follow the canonical definitions, not the published file's spelling

**Original**: the determination changelist ends `tc_strategy`, `quality`, `Ref_ISGN`.

**Code**: as specified.

**Canonical**: `constants.py` ends the child block `tc_strategy`, `Ref_IGSN`, `quality_child`, and
names the site quality column `quality_parent`.

**Ruled**: the canonical definitions win, on all three columns and on the ordering of the last two.

ADR-0003 already rules that the portal uses `tc_pT_function` and `Ref_IGSN` internally and rejects
files carrying the misspelled headers, on the grounds that rejecting loudly puts the correction in
front of the only people who can make it. Those people are the assessment team, and this changelist
is where they read the database. Showing them the misspelling would be the same silent acceptance
the ADR exists to refuse. And a name that differs between the code and the screen is the drift
ADR-0002 rules out.

### D3 — The portal holds no sample numbers, and the column stays empty

**Original**: `Ref_ISGN` is required as a changelist column. Nothing says what fills it.

**Code**: it renders an empty string unconditionally, in the changelist and in the export.
`constants.py` carries the note "Recommend removing field." An `IGSN` field existed on the
determination model and was deleted on 2026-04-09, the day before this specification was written.

**Ruled**: no field is restored, and the column stays, empty.

The way this was originally proposed did not hold up. A sample number does not describe a heat flow
determination. A case could be made for one on the site, but that case has not been made or agreed.
And the framework's sample model already stores any number of identifiers, of which a sample number
is one, so a dedicated field in the heat flow application buys nothing. The later revision, a
comma-separated list of the samples used to determine the value, has no meaning in the published
database as a product.

If sample numbers are ever held, it happens at the site level or in the roadmap item that brings in
thermal property data, where actual physical samples are collected and stored. Neither is this
feature.

The column itself is not the same question. The published structure defines it, the export must
carry the published column set exactly, and a curator comparing a changelist against the file is
more confused by a column that is missing than by one that is blank.

### D4 — The map viewer page leaves this specification

**Original**: user story 4, FR-009 and FR-010 specify a portal page embedding the commission's
externally hosted map viewer in an iframe, and a menu item pointing at it.

**Code**: built, at `ghfdb/explore/`, with a menu entry and three tests.

**Ruled**: removed from this specification. It shares an application with the flat interface and
nothing else — no model, no queryset, no column, no test. It was swept in because both landed in
the same week.

The roadmap separates them too: the flat interface is R2, and the embedded viewer is superseded by
R12, which brings the viewer inside the portal to read the portal's own API. The page and its tests
stay exactly as they are, and R12 inherits them.

### D5 — The column metadata file and the routes serving it are out of scope

**Original**: the Assumptions name the column metadata file as authoritative for column
definitions.

**Code**: the file holds 62 entries with lowercase keys. It disagrees with the canonical
definitions on 25 columns by case and omits six outright. A route serves it unauthenticated, and a
second route serves a static copy of the 2024 release file. Neither route is specified anywhere,
neither has a test, and the tests that check the file against the canonical definitions are all
expected to fail.

**Ruled**: this feature touches neither the file nor the routes.

Whether the file needs to exist at all is a question for the API work, and answering it here would
be answering it in the wrong place. The Assumptions are corrected: the canonical definitions in the
constants module are the authority, per ADR-0002, and the metadata file is not.

The consequence is accepted: the schema-coverage tests that compare the two stay expected-to-fail
until that question is answered. They belong to `003-ghfdb-import-export`, not here.

### D6 — The flattening contract is tested, and the query-count claim is proven properly

**Original**: SC-001 and SC-002 require a constant query count "regardless of the number of records
returned".

**Code**: the annotation set has no passing test. The one test that asserts it is expected to
fail, because the queryset annotates site elevation under the published name while the test expects
a prefixed one. The query-count tests bound the count against a fixture holding a single record
chain, which cannot distinguish a constant count from a linear one.

**Ruled**: both are defects and both are this feature's work.

On the annotation name: the published name is correct and the test is wrong. ADR-0002 requires
annotations to carry published names, and the neighbouring site annotations are prefixed only
because those names collide with fields the framework's base class declares. Elevation does not
collide, so it takes its published name. FR-011 states the rule so the next reader does not have to
infer it from which names happen to be prefixed.

On the query counts: every constancy claim is measured at two different row counts. A bound
measured once is a bound on one number.

### D7 — Unreachable parent methods

**Original**: silent. The specification requires two parent queryset methods.

**Code**: three exist. The flattening method has no caller and no test. A dictionary accessor on
the proxy model has no caller and no test, and raises on any field that exists only as an
annotation.

**Ruled**: the flattening method is specified and tested. It is the natural counterpart of the
determination one and it is what the site changelist should be reading, rather than walking
relationships per column as it does now.

The dictionary accessor is removed. It is unreferenced, and it does not work.

### D8 — Site geography columns are portal additions and stay

**Original**: the superseded site column list included country, region, continent and geological
domain. The final reading dropped them, while FR-014 continued to require filters on all four.

**Code**: the site changelist shows all four, after the quality column.

**Ruled**: they stay, after the published block. They are not published columns, and the
specification now says so: the published parent columns come first in published order, then the
geography, then the two counts. A filter the user cannot see the value of is worth less than one
they can.

### D9 — What the design review reversed

The reconciliation was reviewed by an independent reviewer whose brief was to assume every closure
was wrong. Three of six were.

**T049** was closed on the determination queryset's elevation annotation and its test, for a task
about the site queryset. The test asserts a key on an empty queryset, and the same test class is
rejected as insufficient for a neighbouring task a few rows below in the same file.

**T078 and T098** were closed on tests taking a superuser client, while a third task was held open
on the grounds that a superuser is not the staff user the tasks name.

**Ruled**: all three reopened. The pattern in both is the same and worth naming, because it is what
the fourth lens exists to catch: evidence was accepted in one row on grounds that had already been
rejected in another. Consistency within the reconciliation is the check, and it is one a reader can
apply without re-deriving the verdicts.

The review also found three defects the reconciliation had not: a many-valued column annotated with
`F()` that duplicates rows, four changelist headings Django never reads because the entries are
named after model fields, and an import route that writes without consulting any of the three
read-only hooks the tests assert. Each is recorded in `reconciliation.md` with its measurement, and
each has a task.

### D10 — T026 is blocked: the export queryset's missing lithology/stratigraphy prefetches conflict with a pre-existing query-count test

**Original**: T040 (FR-007) names lithology and stratigraphy among the many-valued columns
`for_export()` must chain into its prefetches, alongside method, exploration purpose, the
gradient's methods and corrections, the conductivity's descriptive vocabularies and probe type.
T026 requires every many-valued column readable at zero further queries once the row is evaluated.

**Code**: `for_export()` prefetches 14 M2M paths, matching its own docstring, but two published
`CHILD_COLUMNS` — `geo_lithology` and `geo_stratigraphy`, reached via
`sample__heatflowinterval__lithology` and `...stratigraphy` — are not among them. Both resolve on a
row (T024 passes), but each costs one query per row to read, since neither is prefetched.
`project/ghfdb/admin.py`'s own `get_queryset()` independently prefetches both paths, which is
independent evidence the manager is missing them rather than the columns being intentionally
excluded.

**Tried**: added both prefetches to `for_export()`. `test_many_valued_columns_read_without_further_queries`
(T026) then passed. Running the wider class turned up a break:
`tests/test_ghfdb/test_managers.py::TestGHFDBChildQuerySet::test_for_export_max_queries` — a
pre-existing test, not authored in this story, asserting `django_assert_max_num_queries(16)` —
failed with 17 queries measured. Reverted the two prefetches.

**Ruled**: blocked, not fixed. The Implementer's brief prohibits modifying a pre-existing test not
authored in this story; the two tests' requirements are in direct, provable conflict (16 as a
ceiling vs. 18 as the correct count once FR-007 is satisfied), and resolving it requires a decision
about `test_for_export_max_queries` — retire it in favour of the T025 constant-query-count test,
which already supersedes its methodology (a bound proven at two row counts rather than asserted
once against a literal), or raise its ceiling to 18 — that only Sam or a future convergence pass can
make. T026 and the lithology/stratigraphy chunk of T040 stay open; the rest of both is done.

**Revisit if**: `test_for_export_max_queries` is retired or its bound is raised. At that point the
two prefetches (`sample__heatflowinterval__lithology`, `sample__heatflowinterval__stratigraphy`)
are a two-line addition to `for_export()`'s existing `prefetch_related()` call, and
`test_many_valued_columns_read_without_further_queries` (already written, not committed — see
`progress.md`'s 2026-08-23T22:45:00Z entry for its body) can be restored.

### D10 — The single-bound export query test is retired, not raised

**Found**: US-1 could not satisfy T026 and the last part of T040. FR-007 requires the export
queryset to prefetch lithology and stratigraphy, and adding them takes its query count from sixteen
to seventeen, which breaks `test_for_export_max_queries` — a test asserting
`django_assert_max_num_queries(16)` against a fixture holding one record chain.

**Ruled**: the old test is removed rather than its bound raised.

Raising it to eighteen would reinstate the same assertion one number further along, and that
assertion is the exact defect R2 names: a bound satisfied at one row is satisfied by a linear query
plan as well as by a constant one, so it cannot fail for the reason it exists. Its replacement,
`TestChildExportQuerySet::test_query_count_is_equal_at_two_row_counts`, asserts strictly more — it
measures at two row counts and compares the counts to each other rather than to a literal, which
also survives a framework change that adds or removes a fixed query.

The two prefetches were the point of the task. Without them the two geological columns cost a query
per row, and the changelist compensated independently by prefetching them itself — one more place
the same knowledge was written twice.

**Revisit if** a caller needs the export queryset's absolute query count bounded rather than its
growth. Nothing does today.

### D11 — The single-bound attachment test is retired too, for D10's reason

**Found**: T062 requires `with_children()` to prefetch the site's exploration purposes, the one
many-valued published parent column. Adding it costs four further queries through the polymorphic
inheritance chain, and breaks `test_parent_with_children_no_extra_queries` — a test bounding the
count at three against a fixture holding one site.

**Ruled**: removed, not raised, exactly as D10 rules for its counterpart on the determination side.

The four extra queries are a fixed cost, not a per-site one, which is precisely the distinction the
old test cannot make and its replacement can. `TestParentChildAttachment::test_query_count_is_equal_at_two_row_counts`
measures at two site counts and compares them to each other, so it fails if the cost is per-site and
passes if it is fixed, whatever the fixed number happens to be.

Both blocks were raised correctly rather than worked around: an implementer that had edited the test
in its own way would have left the same weak assertion in place one number further along.

**Revisit if** a caller needs the attachment's absolute query count bounded rather than its growth.
Nothing does today.

### D12 — The query-constancy measurement excludes the framework's audit watcher, and the watcher is raised upstream

**Found**: measuring the changelist's query count across a full request does not measure the
changelist. The framework installs a global audit-log watcher (`orbit`) whose cost is **per rendered
row**, so the count grows for a reason this feature does not own and cannot prefetch away.

Measured on this changelist, one warm-up request first:

| Rows | Watcher on | Watcher off |
|---|---|---|
| 2 | 112 | 31 |
| 6 | 124 | 31 |

**Ruled**: the assertion disables the watcher for the duration of the comparison, and says so in the
test. With it off the count does not move between the two row counts, so FR-019 is satisfied by this
feature's own work — the changelist issues a fixed number of queries however many rows it shows.

This is a measurement decision, not a fix. Nothing here changes the behaviour a real user gets, and
scoping an upstream cost out of a test is not the same as working around it. Raised upstream as
FAIR-DM/fairdm#281, with the numbers above: at the default page size that is roughly three hundred
extra queries per page view, on every changelist in every project built on the framework. It matters
here because the assessment team reads the published database through this admin, and the database
is about to grow from a sample to the full release.

**Revisit if** the upstream issue lands. The exclusion comes out of the test the day the cost stops
being per-row.

### D13 — GHFDBChildAdmin.search_fields keeps its own ghfdb_id, not narrowed to T093's two names

**Found**: T093 asks for `search_fields` on the site name and the site's published identifier, by
paths that exist from the determination — two names. The pre-existing `search_fields` already
carries both, plus a third: the determination's own `ghfdb_id`. A pre-existing test
(`TestGHFDBAdminChangelist::test_ghfdb_admin_changelist_refined_configuration`) asserts
`model_admin.search_fields == EXPECTED_SEARCH_FIELDS`, a three-entry tuple including that third
field, and this dispatch's brief authorises touching only one assertion in that test — the one
`EXPECTED_LIST_DISPLAY` fed (T079) — not this one.

**Ruled**: `search_fields` is left exactly as it was. T093's requirement is a minimum, not an
exclusive list — the two names it asks for are present and proven by
`TestGHFDBChildAdmin::test_search_matches_site_name_and_published_site_identifier` (T082) — and
removing the third field would have bought nothing this story needs while breaking a test outside
this dispatch's authorised edit.

**Revisit if** a future story is explicitly asked to narrow the determination changelist's search to
only the site name and the site's published identifier — that would be the point to also correct
`EXPECTED_SEARCH_FIELDS`.
