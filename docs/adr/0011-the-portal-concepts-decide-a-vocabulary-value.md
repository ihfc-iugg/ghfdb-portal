# ADR 0011 — The portal's own concepts decide what a controlled-vocabulary value may be

**Status:** accepted

## Decision

For every column that takes a controlled value, the concepts this portal holds are the authority. A
value resolves if the portal has a concept for it, and refuses the file if it does not.

The upload template ships a sheet named `controlled vocabulary` listing permitted terms. That sheet
is guidance for whoever fills the spreadsheet in. The import never opens it. A value the sheet
permits but the portal holds no concept for still refuses the file, and a value the portal holds but
the sheet omits is accepted.

The rule applies the same way to a column that takes one value and to a column that takes several.

## Why

Validating against a sheet inside the file puts the authority inside the artefact being checked. A
stale copy of the template, or an edited one, would then decide what enters the database. The
portal's vocabularies are the thing the rest of the application reasons about, so they are the thing
an import has to agree with.

The convenience argument for the sheet is real: it travels with the file, so a contributor and the
portal would never disagree about which list applies. That was rejected because the disagreement is
the useful signal. When a file offers a term the portal does not hold, somebody needs to decide
whether the portal should hold it, and a refusal is how that decision gets asked for.

The two lists do disagree today, and that is worked out as real datasets arrive rather than by
reconciliation code written in advance.

## Revisit if

The portal's vocabularies are generated from the published template rather than curated separately,
which would collapse the two authorities into one and make the question moot.
