# Decisions — 005 assessment upload workflow

Decisions taken while writing the specification, with the reasoning behind each. Answers short
enough to live in the specification are inlined there instead; this file carries the ones whose
reasoning would crowd it out.

## The workflow is one feature, not two

The roadmap splits this work across two items. R6 asks for the page the team uploads through and
the validation result they read there, and says in as many words that the trust and review
distinctions separating team members from outside contributors are out of its scope. R7 asks for
the role, the private-until-reviewed rule, the queue and the recorded decision.

Building only R6's half would mean shipping a workflow where an upload becomes public the instant it
is confirmed, then rebuilding the confirmation path a second time to add a gate in front of it. The
gate is not a decoration on the workflow, it is the last step of it.

So this feature takes R6's remaining half together with R7's first three deliverables, and R7 is
narrowed to what it is actually about: contribution from people outside the assessment team.

## The role is the trust level

R7's fifth deliverable reads "datasets from team members published without waiting". Taken at face
value that makes every member of the assessment team exempt from the gate, which is the opposite of
why the gate was asked for: the team includes student helpers and people passing through for a
semester, and their work is exactly what needs a second pair of eyes.

The alternative would be a per-person trust setting, which means an administrative surface for
granting and revoking it, a decision about who may grant it, and a second workflow for the trusted
path. Two roles already carry that distinction. A Data Curator's upload does not wait, a Data
Assessor's does, and nothing else about the two paths differs.

This supersedes R7's fifth deliverable, and R7's text is corrected on this branch rather than left
contradicting the specification.

## The vocabulary changes rather than the code working around it

CONTEXT.md defines **Reviewer** as a member of the assessment team who carries out data assessment,
and **publication approval** as a separate decision made by a **data administrator**. Those are the
two roles this feature needs, under different names from the ones now agreed.

The glossary's own rule is that definitions describe the code as it stands. Keeping the old names in
the glossary while the code, the pages and the group names say Data Assessor and Data Curator would
break that rule on the first commit. The glossary is updated on this branch.

The existing group named `Reviewers` in the code, and the `heat_flow_reviews` relation behind it,
are carried into the new naming rather than left as a second vocabulary.

## What the template's reviewer columns are for

The upload template carries columns naming who reviewed what. FS-004 already accepts and ignores
them. This feature does not start reading them: the same information is collected on the form that
precedes the upload, where it can be checked against real contributor profiles instead of arriving
as free text in a spreadsheet cell.

That makes the form the authority and the columns vestigial, which is the intended direction. The
columns stay accepted-and-ignored rather than becoming an error, because the template is not ours to
change and a file that fills them in is not wrong.

## Why the check cannot be optional

The obvious shape for this is a checkbox offering a trial run. It was rejected.

A checkbox has to be defaulted, and whichever way it is defaulted, the other setting is one click
away from writing unexamined data into a shared database with no undo. The people most likely to
click past it are the ones the gate exists for. The check costs one extra page in the flow and
removes a class of accident entirely, so it is unconditional.

## Why the confirmation re-checks

The report a user confirms was produced at some earlier moment, against data that may since have
moved. Storing the report and writing from it would mean writing numbers the portal no longer
believes.

Re-running the check at confirmation and writing from that run keeps the report honest, makes a
duplicate submission harmless, and costs one more read of a file that is already stored.

## Files are kept, including the ones that were rejected

The stated reason for keeping the file at all is traceability from a dataset back to the spreadsheet
it came from. A single file that is overwritten by the next submission satisfies that only for
assessments that succeeded first time, and the interesting case is the one where a curator sent
something back.

Every submitted file is therefore retained and distinguishable. The submitted file lives on the
assessment record rather than in a separate store, which is where someone looking for it would
expect it to be.
