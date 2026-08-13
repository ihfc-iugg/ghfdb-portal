# Triage Labels

The engineering skills speak in terms of canonical roles. This file maps each role to the label
string actually used in this repo's issue tracker. Where a skill mentions a role, use the label
string from the right-hand column.

## Triage roles

| Role              | Label in this tracker | Meaning                                                     |
| ----------------- | --------------------- | ----------------------------------------------------------- |
| `needs-triage`    | `needs-triage`        | Maintainer needs to evaluate this issue                     |
| `needs-info`      | `needs-info`          | Waiting on the reporter for more information                |
| `ready-for-agent` | `ready-for-agent`     | Fully specified, ready for an unattended agent              |
| `needs-approval`  | `needs-approval`      | Investigated and actionable, waiting on maintainer approval |
| `ready-for-human` | `ready-for-human`     | Cannot be automated, needs a person to carry it out         |
| `wontfix`         | `wontfix`             | Will not be actioned                                        |

Earlier colon-separated variants (`needs:triage`, `needs:info`) were unused and have been removed
so that only one spelling of each role exists.

## Feature lifecycle

`feature-request` is the permanent type label. When a request is assessed, exactly one decision
label is added alongside it:

- `accepted` — a committed feature in flight
- `rejected` — decided against, kept as a decision record
- `deferred` — decided not-now, still on the table

`chore` covers maintenance, tooling, and standards-alignment work with no user-facing behaviour
change.

## Feature specs and stories

This repo also uses two structural labels for spec-driven work:

- `feature-spec` — an epic issue representing one feature spec, parent of its user stories
- `user-story` — a single user story within a feature spec

## Repo-specific labels

These predate the canonical set and remain in use. They carry priority and subject, not workflow
state, so they sit alongside the roles above rather than replacing any of them.

- `High Priority`, `Low Priority` — maintainer prioritisation
- `Information required` — an older spelling of `needs-info`, still attached to open issues
- `type:*` (`type:feature`, `type:bug`, `type:refactor`, `type:docs`, `type:chore`, `type:test`)
- `blocked:upstream`, `blocked:external`, `breaking-change`
