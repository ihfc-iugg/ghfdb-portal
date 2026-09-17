# ADR 0020 — A count in the navigation is how curators are told there is something waiting

**Status:** accepted

## Decision

Data Curators learn that an assessment is waiting from the portal's own navigation, which carries a
count of assessments awaiting a decision and leads to the assessment list narrowed to them. No
notification framework is added, and no email is sent.

## Why

Neither the framework nor its installed additions provide a notification mechanism. Adding one means
a dependency, a data model, a rendering surface and a settings story, all for a single use.

Email is the other obvious answer and is the wrong first move. The people who would receive it are a
team of roughly ten who are in the portal daily, and an email about something they will see anyway is
a notification people learn to filter.

A count where curators already look costs nothing and is the thing they would check regardless.

What the count leads to is a filter rather than a page of its own. A waiting list is the assessment
list with one question asked of it, and the same list answers every other question a reader has — who
assessed something, who uploaded it, who decided on it. A second listing page would duplicate the
first and drift from it.

## Revisit if

The team reports that assessments sit unnoticed. Email is then a small change, because what would
populate it is a query the list already runs.
