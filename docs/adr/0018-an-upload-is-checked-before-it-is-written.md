# ADR 0018 — An upload is checked before it is written, with no way to skip the check

**Status:** accepted

## Decision

Every file uploaded through the portal is read and reported on before anything reaches the database.
The person uploading sees what the import would do and confirms it, and only then is anything
written. No setting, parameter or route writes without checking first, and a test enumerates the
write paths so that stays true.

Confirmation re-runs the check against the stored file rather than writing from the report the user
saw, and writes in the same transaction as that fresh check.

## Why

An import that writes first and reports afterwards cannot be undone by anyone without database
access. The portal holds data other people's work depends on, and a bad file discovered after the
fact is a manual repair by whoever has a shell.

The obvious alternative is a checkbox offering a trial run. It was rejected because a checkbox has to
be defaulted, and whichever way it is defaulted the other setting is one click from writing
unexamined data. The people most likely to click past it are the ones the check exists for.

Re-checking at confirmation costs one more read of a file that is already stored, and buys two
things: a report that has gone stale cannot write stale numbers, and a confirmation submitted twice
writes once, because the assessment's own state decides whether there is anything left to do.

## Revisit if

Files grow large enough that reading one twice is a real cost. At that point the question is whether
to hold the parsed result rather than whether to skip the check.
