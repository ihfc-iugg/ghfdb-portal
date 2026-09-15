# Data model — 005 assessment upload workflow

One model changes, one is added, and nothing existing is removed.

## `review.Review` — the assessment record

Kept as they are: `literature` (OneToOne, the publication), `dataset` (OneToOne), `reviewers`
(ManyToMany to `contributors.Person`), `start_date`, `end_date`, `comment`.

Added:

| Field | Type | Why |
|---|---|---|
| `uploaded_by` | FK to `contributors.Person`, set when the assessment is created | Who holds the assessment. Object permissions follow this, not the assessor list, because an assessor may be an unclaimed profile with no account. Set at creation rather than at first upload, because the upload page is gated on it and the person who described the assessment is the person who must be able to reach that page next. |
| `state` | small integer, choices from `review.states` | Where the assessment has got to. Replaces the current three-value `status`. |
| `decided_by` | FK to `contributors.Person`, null | The curator who approved or sent back. |
| `decided_at` | datetime, null | When that decision was made. |
| `decision_comment` | text, blank | What the curator said when sending it back. |

The existing `status` field is migrated into `state` rather than kept alongside it. Two fields both
describing where an assessment has got to is how they drift apart.

`reviewers` keeps its current meaning: the people who carried out the assessment, credited as
contributors on the dataset. It is not an access-control list and never has been.

## `review.SubmittedFile` — the files, all of them

A file per submission rather than a field on the assessment, because a curator can send an
assessment back and the replacement must not erase what was rejected. FR-015 asks for exactly that,
and a single `FileField` satisfies it only for assessments that succeed first time.

| Field | Type | Why |
|---|---|---|
| `review` | FK to `Review`, related name `submissions` | Its assessment. |
| `file` | FileField, upload path scoped to the assessment | The template as supplied. |
| `submitted_by` | FK to `contributors.Person` | Who submitted this one. |
| `submitted_at` | datetime, set on creation | Ordering, and the audit trail. |
| `imported_at` | datetime, null | Set when this file's contents were written. Null means checked but never confirmed. |

The current submission is the most recent row. The assessment reads it through a property rather
than caching a pointer, so there is one source of truth.

## `review.states` — the state vocabulary

| State | Meaning | Reached from |
|---|---|---|
| `DESCRIBED` | The publication, assessors and dates are recorded. No file yet. | Creation |
| `AWAITING_DECISION` | A file has been confirmed and written. The dataset is private, waiting on a curator. | `DESCRIBED` or `CHANGES_REQUESTED`, by an assessor confirming |
| `CHANGES_REQUESTED` | A curator sent it back. The dataset stays private and a replacement file is expected. | `AWAITING_DECISION` |
| `COMPLETE` | Either a curator approved it, or a curator uploaded it themselves. The dataset is public. | `AWAITING_DECISION` by approval, or `DESCRIBED` directly when the uploader is a curator |

Four states, five transitions, and every one of them is an action a person takes. Nothing transitions
on a timer or a signal.

Transitions live beside the states as functions taking the assessment and the acting person, so the
rule that only a curator may reach `COMPLETE` from `AWAITING_DECISION` is enforced in one place
rather than in each view.

## Dataset visibility

"Public" means both of the framework's fields: `Dataset.visibility` set to its public value and
`Dataset.published` set true. `visibility` governs the metadata and `published` governs the data
beneath it, and a dataset that is one without the other is half-published.

Both default to private on creation, so an assessor's path sets nothing and a curator's path sets
both. That asymmetry is deliberate: the private outcome is what happens when no code runs, which is
the safe direction for a default to fail in.

## Groups

`Data Assessor` and `Data Curator`, created by a data migration. The migration is idempotent and
grants no Django model permissions: access in this feature is decided by the two predicates in
`review.permissions`, and object-level permissions on a dataset continue to come from the
framework's own grant when the assessment is created.

The existing `ghfdb_review_group.json` fixture is deleted. It pins `auth.permission` rows by primary
key, which breaks whenever a migration reorders them, and the group it creates is named in a case
no code in the repository actually looks for.
