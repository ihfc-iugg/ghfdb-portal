# ADR 0020 — The queue is how curators are told there is something waiting

**Status:** accepted

## Decision

Data Curators learn that an assessment is waiting from the portal's own navigation, which carries a
count of assessments awaiting a decision, and from the queue page that lists them. No notification
framework is added, and no email is sent.

## Why

Neither the framework nor its installed additions provide a notification mechanism. Adding one means
a dependency, a data model, a rendering surface and a settings story, all for a single use.

Email is the other obvious answer and is the wrong first move. The people who would receive it are a
team of roughly ten who are in the portal daily, and an email about something they will see anyway is
a notification people learn to filter.

A count where curators already look costs nothing and is the thing they would check regardless.

## Revisit if

The team reports that assessments sit unnoticed. Email is then a small change, because the queue that
would populate it already exists.
