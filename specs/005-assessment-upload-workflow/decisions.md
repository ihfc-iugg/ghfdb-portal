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

## D3 — The vocabulary changes rather than the code working around it

`CONTEXT.md` defines **Reviewer** as a member of the assessment team who carries out data
assessment, and **publication approval** as a separate decision made by a **data administrator**.
Those are the two roles this feature needs, under names that are no longer the agreed ones.

The glossary's own rule is that definitions describe the code as it stands. Keeping the old names
there while the code, the pages and the group names say Data Assessor and Data Curator would break
that rule on the first commit. The glossary is updated on this branch, and the existing `Reviewers`
group and `heat_flow_reviews` relation are carried into the new naming rather than left as a second
vocabulary.

## D4 — The template's reviewer columns stay ignored

The upload template carries columns naming who reviewed what, and FS-004 already accepts and ignores
them. This feature does not start reading them: the same information is collected on the form that
precedes the upload, where it can be checked against real contributor profiles instead of arriving
as free text in a spreadsheet cell.

That makes the form the authority and the columns vestigial, which is the intended direction. The
columns stay accepted-and-ignored rather than becoming an error, because the template is not ours to
change and a file that fills them in is not wrong.

## D5 — The check cannot be turned off

The obvious shape for this is a checkbox offering a trial run. It was rejected.

A checkbox has to be defaulted, and whichever way it is defaulted the other setting is one click
away from writing unexamined data into a shared database with no undo. The people most likely to
click past it are the ones the gate exists for. The check costs one extra page in the flow and
removes a class of accident entirely, so it is unconditional, and a test enumerates the write paths
to keep it that way.

## D6 — Confirmation re-checks rather than trusting its report

The report a user confirms was produced at some earlier moment, against data that may since have
moved. Storing the report and writing from it would mean writing numbers the portal no longer
believes.

Re-running the check at confirmation and writing from that run keeps the report honest and makes a
duplicate submission harmless, at the cost of one more read of a file that is already stored. The
assessment's own state is the idempotency key, so one mechanism covers both the double submission
and the stale report.

## D7 — Every submitted file is kept, including the rejected ones

The stated reason for keeping the file at all is traceability from a dataset back to the spreadsheet
it came from. A single file that is overwritten by the next submission satisfies that only for
assessments that succeeded first time, and the interesting case is the one where a curator sent
something back.

Files are therefore rows against the assessment rather than a field on it. The current submission is
the most recent row, read through a property, so there is no second pointer to keep in step.

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

## D9 — `Person.is_data_admin` is left alone

The framework fixes `is_data_admin` to a group named "Data Administrators" and gates its own import
and publication views on it. Renaming that group to match the portal's vocabulary would silently
switch those gates off, because the framework would then find nobody in the group it looks for.

This feature creates its own two groups alongside it and checks its own predicates in its own pages.
Whether the framework should take the group name from a setting is a question for the framework, and
it is raised there rather than worked around here.

## D10 — SC-006 is amended to match the constitution

The specification as signed off asked the `review` application to meet "the coverage floor the
constitution sets". The constitution sets none: Article VI says in terms that coverage is a guide to
find untested paths, not a merge gate.

The criterion is amended to what the constitution actually requires, which is that every behaviour
added or changed here is tested, in a tree mirroring `project/review/`. This narrows nothing and
adds nothing, so it does not reopen the gate.

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
