# ADR 0019 — Every submitted file is kept, including the ones that were refused

**Status:** accepted

## Decision

Each file submitted against an assessment is stored as its own record. A file that failed its check,
or that a curator sent back, stays retrievable after a corrected file replaces it. The current
submission is the most recent one.

## Why

A dataset in the portal should be traceable to the spreadsheet it was built from. A single file that
each new upload overwrites gives that only for assessments that succeeded first time, and the case
worth tracing is the one where something had to be corrected.

Keeping every submission also makes the record honest about what happened. An assessment that took
three attempts looks like three attempts, which is information for whoever later asks why a dataset
says what it says.

The storage cost is a few hundred kilobytes per attempt, against a team producing one assessment at a
time.

## Revisit if

Submissions accumulate to the point of being a storage concern, in which case the question is a
retention policy for refused files rather than overwriting the current one.
