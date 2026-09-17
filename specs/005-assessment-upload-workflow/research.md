# Research — 005 assessment upload workflow

What the codebase and the framework already provide, and where the gaps are. Every finding here was
read out of the source at `1caed37` (main) or the framework checkout beside it, not recalled.

## The reader is already built

`project/ghfdb/importers.py::import_ghfdb_template(file, dataset)` takes one file and one dataset,
validates the header before opening a transaction, runs the parent pass then the child pass, and
rolls both back if either faults. It returns `GHFDBImportOutcome`, holding the two
`import_export.results.Result` objects.

**The gap**: there is no checking mode. Adding one is a rollback at the end of the existing
transaction, not a second code path. `Result` already carries per-row outcomes and error rows, so
the counts FR-009 asks for and the row-level failures FR-012 asks for are both read off the existing
return value.

**`dry_run=True` is not the route, and this is settled rather than open.**
`specs/004-import-upload-template/decisions.md` D16 records the empirical test:
`import_data()` wraps each resource in its own savepoint and `dry_run=True` rolls that savepoint
back at the end of the same call, before the next pass runs. The child pass resolves its parent
through `ID_parent` and coordinates (`project/ghfdb/resources/child.py:68`,
`child.py:469 _resolve_parent_by_location`), which needs the parent pass's rows visible
mid-transaction. A parent import run with `dry_run=True` leaves zero rows visible to a query issued
immediately afterwards inside the same outer transaction, so a literal dry run would refuse every
file, clean ones included. `transaction.set_rollback(True)` on the way out of the existing
`atomic()` block is the mechanism that works, and `importers.py` already uses it for the error case.

## The assessment record already exists, partly

`project/review/models.py::Review` has the publication (`literature`, OneToOne), the dataset
(OneToOne), `reviewers` (M2M to the user model), `start_date`, `end_date`, `status` and `comment`.
Its three status values are `OPEN`, `PENDING`, `COMPLETE`.

**The gaps**: no submitted file, no uploader, no record of who decided or when, and the status
vocabulary has no value for "checked and waiting on a decision" or "sent back".

`ReviewCreateView` already creates the dataset, names it from the publication, assigns object
permissions and adds each reviewer as a `DataCurator` contributor. Most of US-2 exists in it; what
changes is the entry point (dataset-first rather than from a publication's page) and the permission
assignment, which currently loops over the reviewers.

## Assessors do not need accounts

`AUTH_USER_MODEL` is `contributors.Person`, and `Person(AbstractUser, Contributor)`. The queryset
already distinguishes claimed accounts from `ghost` profiles (attribution only, no email, cannot be
invited) and `invited` ones. `Person.objects.real()` excludes only superusers and the guardian
anonymous user, so unclaimed profiles are already selectable and `CreateReviewForm` already uses it.

**The consequence for the plan**: `ReviewCreateView` currently calls `assign_all_model_perms` for
every reviewer. Object permissions on a ghost profile are meaningless, and the person who needs edit
access is the uploader. The permission grant moves to the uploader; reviewers keep the contributor
credit, which is attribution rather than access.

## Visibility is one field on the version this project resolves

`Dataset.visibility` is an `IntegerField` over `Visibility`, which offers Private and Public and
defaults to Private. The default manager excludes private datasets, so a private dataset is absent
from ordinary queries rather than merely marked. "Public" in this feature therefore means
`visibility = Visibility.PUBLIC`, and nothing else.

An assessor's upload leaves the field at its default, so the private path needs no action beyond not
acting. The curator path sets it.

**This entry was wrong when first written, and the way it was wrong is worth keeping.** It described
a second field, `Dataset.published`, read from the framework's development checkout on this machine
rather than from the package the project actually resolves. That field exists upstream and does not
exist here. Every claim in this file about a dependency is checked against the resolved package in
the virtualenv, not against a sibling working copy that happens to share the name — the two carry the
same version number and different code, and the difference cost a story a blocked task.

## The group check in the existing code has never matched

`project/review/fixtures/ghfdb_review_group.json` creates a group named `reviewers`, with four
hardcoded permission primary keys. `ReviewCreateView` requires `["Reviewers"]`, and
`ReviewListView` tests `groups__name="Reviewers"`, while `ReviewFilterSet` queries
`groups__name="reviewers"`. Django group lookups are case-sensitive, so the capitalised checks can
never match the fixture's group, and the fixture is commented out of the setup hooks anyway.

This feature replaces the group entirely, so the inconsistency resolves rather than needing a
separate fix. The hardcoded permission ids should not survive: a fixture pinning `auth.permission`
by primary key breaks on any migration that reorders permissions.

## There is no notification framework

Neither the framework nor its installed addons provide one. `fairdm/contrib/` has no notifications
app, `fairdm_discussions` carries none, and nothing in the settings pulls one in. The framework's
own views use `braces.views.MessageMixin`, which is Django's per-request messages and does not
survive to another user's session.

**Decision for the plan**: FR-022 is met by the queue being visible and counted where curators
already look, rather than by adding a notification framework to the portal for one use. The
navigation entry carries the number of assessments waiting on a decision, and the queue view lists
them. Email is the natural follow-up if the team finds that too quiet, and it is a small change once
the queue exists.

## Views and menus

`fairdm.views` exports `FairDMListView`, `FairDMCreateView`, `FairDMUpdateView`, `FairDMDetailView`
and `FairDMTemplateView`, all already used by the `review` application. Dataset-scoped pages are
registered with `fairdm.plugins.register(Dataset)` and carry a `check` callable that decides access,
which is how `ReviewSubmitView` already attaches itself to a dataset.

`project/review/menus.py` is entirely commented out. The navigation item is `flex_menu.MenuItem`
inserted into `fairdm.menus.SiteNavigation`, and needs a visibility check so it renders only for the
two roles.

## Testing

`tests/` mirrors `project/` with `test_` prefixes at each level, which the constitution requires.
There is no `tests/test_review/` at all: the application has no tests. The feature therefore
establishes that tree, its factories and its fixtures as well as covering its own work.

The constitution treats coverage as a guide rather than a merge gate, so the obligation is that each
behaviour added here is tested, not that a percentage is reached.

## The blocker nothing here can fix

ADR 0003 refuses a file whose header carries `tc_pT_fuction` or `Ref_ISGN`, and both are still in the
template the team fills in. `validate_official_header` enforces this before a row is read. These
pages will therefore refuse every real file until the template is corrected upstream. The plan keeps
the refusal and spends its effort on making the message say plainly that the template is out of
date, which is what puts the correction in front of the people who can make it.
