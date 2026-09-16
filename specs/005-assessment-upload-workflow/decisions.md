# Decisions — 005 assessment upload workflow

Decisions taken while specifying and planning, with the reasoning behind each. Answers short enough
to live in the specification are inlined there instead. ADR verdicts are recorded against each
decision at convergence, once the code that would carry them exists.

## D1 — The workflow is one feature, not two


The roadmap splits this work across two items. R6 asks for the page the team uploads through and the
validation result they read there, and says in as many words that the trust and review distinctions
separating team members from outside contributors are out of its scope. R7 asks for the role, the
private-until-reviewed rule, the queue and the recorded decision.

Building only R6's half would mean shipping a workflow where an upload becomes public the instant it
is confirmed, then rebuilding the confirmation path a second time to put a gate in front of it. The
gate is not a decoration on the workflow, it is its last step.

This feature therefore takes R6's remaining half together with R7's first three deliverables, and R7
narrows to what it is actually about: contribution from people outside the assessment team.

**ADR:** none — a scope decision about which roadmap items this feature covers. The roadmap itself now records the outcome, and nothing downstream inherits the reasoning.

## D2 — The role is the trust level


R7's fifth deliverable reads "datasets from team members published without waiting". Taken at face
value that exempts every member of the assessment team from the gate, which is the opposite of why
the gate was asked for: the team includes student helpers and people passing through for a semester,
and their work is exactly what needs a second pair of eyes.

The alternative is a per-person trust setting, which brings an administrative surface for granting
and revoking it, a decision about who may grant it, and a second workflow for the trusted path. Two
roles already carry the distinction. A Data Curator's upload does not wait, a Data Assessor's does,
and nothing else about the two paths differs.

This supersedes R7's fifth deliverable, and R7's text is corrected on this branch rather than left
contradicting the specification.

**ADR:** docs/adr/0017-a-role-carries-the-trust-that-decides-publication.md

## D3 — The vocabulary changes rather than the code working around it


`CONTEXT.md` defines **Reviewer** as a member of the assessment team who carries out data
assessment, and **publication approval** as a separate decision made by a **data administrator**.
Those are the two roles this feature needs, under names that are no longer the agreed ones.

The glossary's own rule is that definitions describe the code as it stands. Keeping the old names
there while the code, the pages and the group names say Data Assessor and Data Curator would break
that rule on the first commit. The glossary is updated on this branch, and the existing `Reviewers`
group and `heat_flow_reviews` relation are carried into the new naming rather than left as a second
vocabulary.

**ADR:** none — a vocabulary change, carried by CONTEXT.md, which is the file that owns the project's terms.

## D4 — The template's reviewer columns stay ignored


The upload template carries columns naming who reviewed what, and FS-004 already accepts and ignores
them. This feature does not start reading them: the same information is collected on the form that
precedes the upload, where it can be checked against real contributor profiles instead of arriving
as free text in a spreadsheet cell.

That makes the form the authority and the columns vestigial, which is the intended direction. The
columns stay accepted-and-ignored rather than becoming an error, because the template is not ours to
change and a file that fills them in is not wrong.

**ADR:** none — the behaviour and its reasoning were settled by FS-004 and are unchanged here.

## D5 — The check cannot be turned off


The obvious shape for this is a checkbox offering a trial run. It was rejected.

A checkbox has to be defaulted, and whichever way it is defaulted the other setting is one click
away from writing unexamined data into a shared database with no undo. The people most likely to
click past it are the ones the gate exists for. The check costs one extra page in the flow and
removes a class of accident entirely, so it is unconditional, and a test enumerates the write paths
to keep it that way.

**ADR:** docs/adr/0018-an-upload-is-checked-before-it-is-written.md

## D6 — Confirmation re-checks rather than trusting its report


The report a user confirms was produced at some earlier moment, against data that may since have
moved. Storing the report and writing from it would mean writing numbers the portal no longer
believes.

Re-running the check at confirmation and writing from that run keeps the report honest and makes a
duplicate submission harmless, at the cost of one more read of a file that is already stored. The
assessment's own state is the idempotency key, so one mechanism covers both the double submission
and the stale report.

**ADR:** docs/adr/0018-an-upload-is-checked-before-it-is-written.md — the mechanism that makes the guarantee in 0018 hold, recorded there rather than as a second ADR.

## D7 — Every submitted file is kept, including the rejected ones


The stated reason for keeping the file at all is traceability from a dataset back to the spreadsheet
it came from. A single file that is overwritten by the next submission satisfies that only for
assessments that succeeded first time, and the interesting case is the one where a curator sent
something back.

Files are therefore rows against the assessment rather than a field on it. The current submission is
the most recent row, read through a property, so there is no second pointer to keep in step.

**ADR:** docs/adr/0019-every-submitted-file-is-kept.md

## D8 — No notification framework is added


FR-022 asks for Data Curators to be notified in the portal. Neither the framework nor its installed
addons provide any notification mechanism: there is no notifications application in
`fairdm/contrib/`, `fairdm_discussions` carries none, and the framework's own views use Django's
per-request messages, which do not survive to another user's session.

Three options were weighed. Adding a notification framework to the portal is a dependency, a data
model, a rendering surface and a settings story for one use. Email is explicitly out of the
specification's scope and is the wrong first move for a team of ten who are already in the portal
daily. Making the queue visible where curators already look costs nothing and is the thing they
would check anyway.

The navigation entry therefore carries the count of assessments waiting on a decision, and the queue
lists them. If the team finds that too quiet, email is a small change once the queue exists.

**ADR:** docs/adr/0020-the-queue-is-the-notification.md

## D9 — `Person.is_data_admin` is left alone


The framework fixes `is_data_admin` to a group named "Data Administrators" and gates its own import
and publication views on it. Renaming that group to match the portal's vocabulary would silently
switch those gates off, because the framework would then find nobody in the group it looks for.

This feature creates its own two groups alongside it and checks its own predicates in its own pages.
Whether the framework should take the group name from a setting is a question for the framework, and
it is raised there rather than worked around here.

**ADR:** none — a deliberate non-action on a framework concern, raised where it belongs rather than decided here.

## D10 — SC-006 is amended to match the constitution


The specification as signed off asked the `review` application to meet "the coverage floor the
constitution sets". The constitution sets none: Article VI says in terms that coverage is a guide to
find untested paths, not a merge gate.

The criterion is amended to what the constitution actually requires, which is that every behaviour
added or changed here is tested, in a tree mirroring `project/review/`. This narrows nothing and
adds nothing, so it does not reopen the gate.

**ADR:** none — a correction to this feature's own specification, with no life beyond it.

## D11 — Groups come from a data migration, not a fixture


`project/review/fixtures/ghfdb_review_group.json` creates a group by loading `auth.permission` rows
pinned by primary key, which breaks whenever a migration reorders permissions, and its `loaddata`
hook is commented out of the settings so it has never run.

A data migration creates both groups in every environment with no load step and nothing pinned by
id. The fixture is deleted rather than left as a second, wrong answer to the same question.

While reading it: the group it creates is named `reviewers`, and `ReviewCreateView` requires
`Reviewers`. Django group lookups are case-sensitive, so that check could never have passed. This
feature replaces the group entirely, so the defect resolves rather than needing its own fix, and the
predicates in `review.permissions` are what stop it recurring.

**ADR:** none — how one migration is written; nothing downstream inherits it.

## D12 — The checking mode uses an outer rollback, never `dry_run=True`


The plan first proposed running both import passes with `dry_run=True`. The design review caught it,
and the record it cited settles the question rather than opening one.

`specs/004-import-upload-template/decisions.md` D16 tested this directly while building the reader.
`import_data()` wraps each resource in its own savepoint, and `dry_run=True` rolls that savepoint
back at the end of the same call, before the next pass runs. The child pass resolves its parent
through `ID_parent` and coordinates, so it needs the parent pass's rows visible mid-transaction. A
parent import run with `dry_run=True` leaves zero rows visible to a query issued immediately
afterwards inside the same outer transaction. Calling both passes that way would refuse every file,
clean ones included, for a reason that has nothing to do with the file.

The checking mode therefore runs both passes for real and rolls the outer transaction back
unconditionally: `if check_only or outcome.has_errors(): transaction.set_rollback(True)`. That is
the mechanism `importers.py` already uses for the error case, already verified in this repository,
and it adds no new code path.

The lesson worth keeping is not about savepoints. A decision this project had already made
empirically, one feature earlier, in the same file, was re-derived from first principles and got a
different answer. The prior feature's `decisions.md` is part of the codebase for the next feature
that touches the same code.

**ADR:** none — FS-004's own decision record already carries this at the code, in the comment above the rollback it explains. A second record would be a second place to keep in step.

## D13 — Superseded views are deleted in the same phase that changes the record


`project/review/` holds views, forms, an admin registration and a card template that read
`Review.status` and a `Reviewers` group, both of which this feature removes. The plan left their
removal implied by a structure diagram rather than stated as work.

They are deleted in the foundational phase, in the same commit range that changes the field, with a
test asserting no reference survives. A tree carrying two answers to the same question is how the
next reader picks the wrong one, and a structure diagram is not a task anybody executes.

**ADR:** none — sequencing within this feature's own phases.

## D14 — The assessment list carries no filterset (US-1)


`FairDMListView` auto-generates a `django-filter` `FilterSet` from every model field when
`filterset_class` is left unset, and `Review.start_date`/`end_date` are `PartialDateField`, a type
django-filter has no mapping for — the auto-generated set raises `AssertionError` the first time
anyone requests the page.

Filtering the list is not named anywhere in spec.md or plan.md's access table for US-1, so building
a real `FilterSet` would be scope the story never asked for. `ReviewListView.filterset_fields = []`
disables the auto-generation without adding a filtering feature; a later story that does want
filtering replaces it with an explicit `filterset_class`, the pattern `fairdm.core.dataset.views.
DatasetListView` already uses.

**ADR:** none — a local accommodation of a framework limitation in one view.

## D15 — T014's route lands in T011's commit; T013 follows T014, not the reverse


Two implementation-order departures from tasks.md's listed order (T011, T012, T013, T014), both
forced by a dependency the task breakdown does not surface:

- **T014 inside T011.** This repo's own view-test convention (`tests/test_ghfdb/test_views.py`) is
  `client.get(reverse(...))`, which resolves through `ROOT_URLCONF` — there is no way to exercise
  "a direct URL is refused" (US-1's own acceptance wording) without the route already existing. T011's
  commit therefore carries the `path("assessments/", ...)` registration that is nominally T014's, and
  T014's own commit adds the confirming resolution test only.
- **T013 after T014.** `AssessmentMenuItem.check()` resolves its `view_name` through
  `flex_menu`'s `resolve_url` → `reverse()`; without `review-list` registered, the item cannot
  resolve, marks itself invisible regardless of role, and T013's own acceptance test would pass for
  the wrong reason (invisible-because-broken, not invisible-because-refused). `[P]` on T013 reads as
  "no ordering dependency on its listed neighbours" for cases where that is true; here it was not.

Every task still lands as its own commit with its own tests, in the task IDs tasks.md assigns them —
only the wall-clock order changed.

**ADR:** none — the order two tasks landed in.

## D16 — The served-list tests stop at an unrendered response


Discovered mid-story, not part of any known-red state at the starting commit: any authenticated
request that reaches this project's shared page chrome (the sidebar via `mvp`'s
`cotton/app/sidebar/index.html`, which calls `{% render_menu %}` for `AppMenu`) raises
`KeyError: 'request'`. It reproduces identically, with no `review/` code in the call stack at all, on
the pre-existing `/datasets/` page (`fairdm.core.dataset.views.DatasetListView`) for any logged-in
user — anonymous requests to the same page render fine. Instrumenting `flex_menu`'s `process_menu`
showed the first `render_menu` call for a page carries a real `RequestContext`; every subsequent call
for the same page (the sidebar and the mobile dock both call it, for `AppMenu` and
`MobileFooterMenu`) carries a plain `Context` with no request bound, consistent with `django_cotton`
re-rendering a component through `render_to_string()` without forwarding the request on a second
pass. This is upstream of `project/review/`, sitewide (every authenticated visitor to any portal page
built on this chrome hits it), and not a defect this story's files can fix — see the completion
report's `concerns`.

`ReviewListView`'s and `AssessmentMenuItem`'s own tests for the roles that should be *granted* entry
therefore stop short of forcing that render: the view's tests use `RequestFactory` and assert on the
unrendered `TemplateResponse`'s status code, and the menu item's tests call `check()` directly. Both
assert exactly what US-1 asks these two units to be responsible for — access and visibility — without
depending on chrome that is broken for reasons neither owns. The *refusal* paths (`PermissionDenied`,
the anonymous redirect) are unaffected: both short-circuit in `dispatch()`, before any template
renders, so the ordinary test client is used for them. T012's list-item-template test renders that
one template directly (`render_to_string`) for the same reason, rather than through the full list
page.

**ADR:** none — a workaround for a defect raised upstream as django-mvp/django-mvp#367; it disappears when that is fixed, and an ADR would outlive it.

## D17 — The navigation entry is wired through `apps.py.ready()`, imported via `fairdm.menus`


`review/menus.py` had no caller anywhere in the tree — `project/ghfdb/menus.py` carries the same gap
today, its one entry never actually reaching `AppMenu`, because nothing autodiscovers a `menus`
module the way Django admin autodiscovers `admin.py` (`fairdm.apps.FairDMConfig.ready()` calls
`autodiscover_modules("config")` and `autodiscover_modules("plugins")`, not `"menus"`). Without an
explicit import, `assessment_entry`'s tests would pass — importing the module for the test is enough
to register it — while the running site never showed the entry at all, exactly the gap between "the
tests are green" and "the feature works" this org exists to close.

`review/apps.py`'s `GHFDBReviewConfig.ready()` now imports `. import menus` explicitly. Confirmed
against the app registry directly (`root.get("AppMenu")` lists `"assessments"` among its children
after a bare `django.setup()`, with no test importing `review.menus` itself) rather than only through
the module import that would have masked the gap.

`ghfdb/menus.py`'s equivalent gap is out of `project/review/`'s scope and is left for the repo to
triage on its own — noted in the completion report's `concerns` rather than fixed here.

Separately, `menus.py` imports `AppMenu` from `fairdm.menus` rather than `mvp.menus`: both name the
identical object (`fairdm/menus/__init__.py` re-exports `mvp.menus.AppMenu` unchanged, and
`project/ghfdb/menus.py` already imports it this same way), but `mvp` is only a transitive dependency
of this project's `pyproject.toml` — `poetry run deptry` flags a direct import of it as `DEP003`.
Importing through `fairdm`, which is a direct dependency, resolves the lint finding and matches the
one precedent already in the tree.

**ADR:** none — how one navigation entry is wired.

## D18 — The bibliography-file path (T016) accepts CSL-JSON, not BibTeX/RIS/EndNote


`django-literature`'s own "add a publication without leaving the page" mechanism
(`ImportView`/`ImportForm`) relies on a bundled client-side JS library to parse BibTeX, RIS and
EndNote XML into CSL-JSON in the browser before posting; the server-side half only ever validates
and saves an already-parsed CSL-JSON dict (`literature.utils.csl.process_single_entry`). No
server-side parser for those three formats is installed — `pybtex` and `citeproc-py` are present
only as transitive dependencies of `django-literature` itself, unused by any of its own import code,
and `poetry run deptry` (DEP003) would refuse a direct import of either from `project/review/`
regardless. Adding a parsing dependency is out of scope (the brief's own prohibition), and wiring
`ImportView`'s browser-side flow into this form would mean adding popup-response support
(`django_addanother.views.CreatePopupMixin`) to an installed package this repository does not own.

`ReviewDescriptionForm.clean_bibliography_file` instead reads the uploaded file as a CSL-JSON
object directly (`json.loads`, stdlib only) and passes it straight to `LiteratureItem.objects.create(item=...)`
— the same dict shape `LiteratureItem.save()` already derives `type`/`title`/`issued`/`citation_key`
from. This satisfies FR-004 and US-2 scenario 2 exactly as specified (a bibliography file adds the
publication and links it without leaving the form) without a new dependency or cross-app changes.
A future story that wants BibTeX/RIS/EndNote specifically would extend `django-literature` itself,
not this form.

**ADR:** none — a format choice bounded by what parsers are available; it changes the moment a server-side parser is.

## D19 — Assessors are credited as `DataCollector`, not `DataCurator`


The retired create view (`git show 78c12d1`) credited every reviewer as a dataset contributor under
the FairDM role `DataCurator` (`fairdm.core.vocabularies.FairDMRoles`). That role name is now the
name of one of this feature's two portal groups (`review.permissions.DATA_CURATOR_GROUP`) — carrying
it forward as a contributor-role label would read as "this person is a Data Curator" on every
dataset an assessor merely helped assess, which is neither true nor what FR-016 asks for (attribution
for carrying out the assessment, not a claim about portal role). `DataCollector` — "the person(s) who
collected the data" — is the closest existing `FairDMRoles` concept to what an assessor actually did,
and is credited instead.

**ADR:** none — which credit role one relation uses.

## D20 — The uploader's object permissions reuse `assign_all_model_perms`, redirected to `uploaded_by`


`fairdm.core.dataset.views.DatasetCreateView.form_valid` — the newer, direct-dataset-creation
precedent — grants its creator five named permissions via `guardian.shortcuts.assign_perm`.
`guardian` is only a transitive dependency here (`django-guardian` is not in this project's
`pyproject.toml`), and `poetry run deptry` (DEP003) refuses a direct import of it from
`project/review/`. `fairdm.utils.permissions.assign_all_model_perms` — the helper the retired
create view already called once per reviewer — wraps the same `guardian.shortcuts.assign_perm`
call through `fairdm`, a direct dependency, and grants every permission for the `Dataset` content
type rather than a named five. `ReviewCreateView.form_valid` calls it once, for `self.request.user`
alone, which is the brief's actual correction: not the breadth of what the old code granted, but
who it granted it to.

**ADR:** none — corrects a defect in code this feature replaced, and the correct rule is stated in 0017's permission model.

## D21 — T017's own tests call the view directly, not through `reverse("review-create")`


T014's route registration had to land inside T011's commit (D15) because the list view's own
access-control tests need a resolvable URL to exercise through the test client. T017 (the create
view) and T019 (its route) face the same dependency in principle, but T017's tests exercise
`form_valid` — POST behaviour verified against the database, not against a rendered response — so
`RequestFactory().post(...)` followed by calling `ReviewCreateView.as_view()(request)` directly
proves everything T017's acceptance asks without a route to reverse. T019 registers
`review-create` and adds its own access-control and route-resolution tests afterwards, independent
of T017's landing order, rather than repeating the forced reordering D15 recorded.

**ADR:** none — how one story's tests avoid depending on another's landing order.

## D22 — `review.views` imports GHFDB symbols as `project.ghfdb.*`, and `deptry` is told so


`ghfdb.apps.GhfdbConfig` registers itself under the dotted name `project.ghfdb` rather than the bare
`ghfdb` its sibling apps (`heat_flow`, `review`) use — an existing inconsistency this story did not
introduce and has no reason to correct (`ghfdb.apps.py` is outside `project/review/`'s scope, and
the fix would ripple through every existing `project.ghfdb.*` import in `tests/test_ghfdb/`).
A first attempt at `from ghfdb.importers import import_ghfdb_template` in `review/views.py` failed
at collection with `RuntimeError: Model class ghfdb.models.GHFDBRelease doesn't declare an explicit
app_label` — the bare path re-executes the whole `ghfdb.models`/`ghfdb.resources` chain under a
module identity Django's app registry never registered, since the registry populated
`project.ghfdb.models` instead. `tests/test_ghfdb/test_importers.py` already imports through
`project.ghfdb.importers` for the same reason. `review/views.py` now does the same, which left
`poetry run deptry` flagging `project` as an undeclared dependency (`DEP001`) — `project` is this
repository's own source root (`pythonpath = ["project"]`), not a package deptry can see any other
way, so it joins `ghfdb`/`heat_flow`/`review` in `[tool.deptry] known_first_party`.

**ADR:** none — an import path and the dependency check that reads it.

## D23 — T022 and T023 land as one commit


D6 makes confirmation's re-check-and-write and its double-submission guard the same mechanism: the
assessment's own state is what both a stale report and a second POST have to pass. Building T022's
write path without also gating it on `review.state` would mean shipping a working confirm view that
writes twice on a repeated POST for one commit's worth of work — a state the story's own D5 (the
check cannot be turned off) and D6 exist specifically to rule out. The two tasks' tests (writing and
idempotency) landed in the same commit rather than the guard being added as an afterthought once
T023's test caught its absence.

**ADR:** none — two tasks in one commit.

## D24 — Brief skill receipts are generated, never copied


The receipt gate went red accepting US-3: the brief named a `craft-tdd` receipt the implementer had
not echoed. The implementer was right and the brief was wrong. The skill was edited between the
story being briefed and being dispatched, so the file on disk carried a newer receipt, the child read
that file and echoed what it actually saw, and the brief still carried the receipt copied from the
previous story's.

The cause is that US-2's and US-3's briefs were built by copying the previous brief and editing it,
including its `required_skills` block. That block is meant to be generated by the pre-dispatch gate
at the moment of dispatch, precisely so it describes the skills as they are rather than as they were.
Copying it turns a check on the child's work into a check on the orchestrator's clipboard.

Every brief from here regenerates that block at dispatch. Nothing else about the copy-and-edit
approach to briefs is a problem — the rest is context that genuinely carries forward.

**ADR:** none — a rule about how this organisation writes its own briefs, not about the portal. Recorded in the workspace's own operating notes.

## D25 — Failure reasons are sanitized in `report.py`, not at their source


T028's deny-list test (FR-013: no internal field name, model name or traceback reaches a failure
report) failed on its first run against real data, not a contrived one: `RelatedModelWidget.clean()`
and `set_m2m_relations()` (`project/ghfdb/resources/widgets.py`) both prefix a wrapped sub-field's
error with `self.model.__name__` — e.g. `"HeatFlowSite: Column 'environment': Invalid value ..."` —
to help a developer reading raw `import_export` output place the fault. And a child row whose parent
failed to import reaches `import_export`'s own `ForeignKeyWidget`, which raises Django's default
`Model.DoesNotExist` — `"ParentHeatFlow matching query does not exist."` — naming the model class
directly. Neither is this story's own code, and neither is something a caller can pass a flag to
suppress.

The fix landed in `project/ghfdb/report.py`'s `_base_error_failures`, not in the widgets or in
`import_export` itself. That module already exists to turn raw `Result` data into the report FR-012
requires — translating Django field names to template column names is its established job — and it
is the one seam every failure this checking pipeline can produce already passes through before
reaching a template. `_sanitize_reason` handles the two known leaks: where the message carries an
embedded `Column '...'` marker (`RelatedModelWidget`'s own wrapping), everything before that marker
is dropped, reusing the same regex `_column_from_message` already searches with for column
extraction; Django's `"... matching query does not exist."` pattern is replaced with a generic,
still-actionable message pointing the reader at the row's other reported problem rather than at the
model that failed to resolve. The row is still reported in both cases — only the leaking text is
replaced, not the failure itself.

Editing `widgets.py` to stop building model-named messages was considered and rejected: that
message is also read directly by developers debugging raw `Result` output outside this report (the
admin's own django-import-export UI, for one), so removing the model name there would trade a
leak in one reader-facing surface for a real loss of information in another. Sanitizing at the
report boundary fixes the one surface FR-013 actually governs.

**ADR:** none — where one sanitisation step sits within the reporting layer 0018 describes.

## D26 — T029's curator half is blocked: `Dataset.published` does not exist in the pinned `fairdm`


`data-model.md` ("Dataset visibility") and `research.md` ("Visibility is two fields, not one") both
state "public" means `Dataset.visibility` set to its public value **and** `Dataset.published` set
true, reading directly from `fairdm.core.dataset.models`. Confirmed against the actual installed
package rather than the docs describing it, per the brief's own ritual: `Dataset._meta.get_fields()`
against the pinned commit (`poetry.lock`'s `resolved_reference`, `8c9290f4b01365688117be69a5c1885d18
15a3b1`) lists no `published` field, and `dir(Dataset)` finds no attribute of that name at all — not
a missing migration, the field is not declared on the model class this dependency version installs.
Fetched `fairdm/core/dataset/models.py` from `FAIR-DM/fairdm`'s `main` branch directly (2026-09-16)
and found `published = models.BooleanField(...)` there, plus a `DatasetQuerySet.published` filter
method — the field exists upstream, added to `main` after the commit this repository's `poetry.lock`
resolved to. This is a dependency-version gap, not a mistake in either design doc.

Setting only `visibility = PUBLIC` on the curator path and leaving `published` alone (because it
cannot be set) was considered and rejected: every enforcement point read for this story
(`DatasetManager.get_queryset`, `fairdm.contrib.plugins.mixins.dataset_is_visible`) currently checks
`visibility` alone, so a visibility-only write would make the dataset fully public today — and then
silently regress once the `fairdm` pin is next bumped and `published` starts defaulting `False` on
every dataset already marked public this way, reproducing exactly the half-published state
data-model.md names as the failure mode to avoid, for every curator-confirmed dataset created before
the bump. No code was written for the curator branch of T029 as a result; see `progress.md`.

Bumping the `fairdm` git pin was considered and rejected as something to do unilaterally inside this
story: `poetry.lock` regeneration against a moving `HEAD` reference can pull in unrelated upstream
changes, is a dependency-version decision outside an Implementer's authority, and the brief's own
prohibitions ("do not add any new dependency") place dependency changes out of this run's scope even
though this is technically a version bump rather than a new package. Resolving D26 is a prerequisite
for T029's curator branch, tracked as follow-up work rather than attempted here.

**ADR:** none — superseded by D27, which records the cause and the corrected design.

## D27 — A dependency claim is checked against the resolved package, never a sibling checkout


US-5's T029 was briefed to make a dataset public by setting two fields, `Dataset.visibility` and
`Dataset.published`. The second does not exist on the framework version this project resolves. The
implementer verified that against the running model class rather than accepting the brief, reported
it as a blocker, and wrote no code for it. That was the right call.

The error is upstream of the brief, in `research.md`. The field was read from the framework's working
checkout on this machine, which tracks its development branch, rather than from the package in this
project's virtualenv. The two share a name and a version number and carry different code. The
development branch has `published`; the resolved release does not.

On the resolved version, public means `visibility = Visibility.PUBLIC` and nothing else. The default
manager excludes private datasets, so the guarantee the specification asks for holds with one field.
When the pin moves to a release carrying `published`, both the confirmation path and the approval
path must set it alongside `visibility`.

T029 moves into US-6 rather than being patched into a finished story. A curator's confirmation and a
curator's approval make a dataset public by the same mechanism, so the behaviour belongs in one place
and was split across two stories by an accident of decomposition.

**ADR:** none — a rule about how this organisation verifies a dependency claim, not about the portal's architecture.

## D28 — The decision queue renders its own rows, not through `FairDMListView`'s item-card mechanism


`ReviewListView` (T011) uses `FairDMListView`'s stock rendering: `list_item_template` cards are
built by `mvp`'s `render_list_item` template tag, which calls `render_to_string(template_name, new)`
with a plain dict — no `request` — because `c-page.list` calls it from inside `list_view.html`
without passing the page's own context through. A `{% csrf_token %}` inside a template rendered that
way has no `csrf_token` in its context and renders nothing usable; a `<form>` built there would fail
CSRF validation on every submission, silently, since nothing surfaces the missing token at render
time.

The queue's rows carry two POST forms per assessment (T037), so this mattered here in a way it never
has for a read-only card. `ReviewQueueView` sets its own `template_name` (`review/queue.html`)
instead of relying on `FairDMListView`'s auto-derived one, and that template loops `object_list`
itself, including `review/review_queue_item.html` with Django's `{% include %}` rather than the
`render_list_item` tag — `{% include %}` inherits the parent template's context, which does carry
`csrf_token` because `queue.html` itself is rendered the normal way, through the view's own
`TemplateResponse`. `list_item_template` stays set on the view (consistent with the rest of the
plan, and harmless since nothing calls `render_list_item` for this view), but `queue.html`'s own loop
is what actually renders each row.

Revisit if: `FairDMListView`'s card mechanism gains a way to pass `request` through to
`render_list_item`, at which point a read-only queue row could go back to the standard mechanism —
though the two POST forms would still need it, so this is unlikely to become the simpler path even
then.

**ADR:** none — how one page renders its rows.

## D29 — R6 converts to prose on delivery; R7 keeps only its undelivered deliverable


T039 asked for R6 marked delivered and R7 narrowed. R6's own bullet-list "Deliverables"/"Out of
scope" shape is how every still-open roadmap item is written; every already-delivered item (R1, R2,
R4) drops that shape for a paragraph describing what the portal now does. R6 follows the delivered
convention rather than keeping its bullets with a status tag changed, since the bullets describing
what would be built read as future tense once it exists.

R7's original six deliverables include three this feature actually built as infrastructure — the
role, the private-until-approved rule, and the decision queue — but only for the assessment team's
own uploads (D1). Nothing yet lets a person outside both roles create a dataset at all, so that
remains R7's real gap. Its deliverables list is trimmed to that one route plus its test coverage,
and its intro paragraph says plainly that the mechanism already exists and names what is missing,
rather than re-listing finished work as still to do.

The new guide (T040) is linked only from `docs/index.md`'s toctree, not from
`docs/guides/introduction.md`'s prose list of GHFDB-specific guides — that list does not mention
`importing-data.md` either, so it already omits an existing guide and fixing it is outside this
scope.

**ADR:** none — the roadmap records its own state; that is what the roadmap is for.

