# ADR 0012 — Four things refuse an uploaded file, and the template's own reporting rules are not among them

**Status:** accepted

## Decision

An uploaded template is refused when, and only when, one of four things is true:

- the header is not the official one,
- a value cannot be stored in the field it maps to,
- a controlled value has no matching concept in the portal (ADR 0011),
- a mandatory model field is left empty by the cell that feeds it.

A refusal is all or nothing. Nothing from the file lands, including rows that were themselves fine.

The template carries two further contracts of its own: an obligation row marking each column
mandatory, recommended or optional, and an allowed-range row. Neither is enforced at import.

The header check is also how a revised template is detected. Nothing in the file says which revision
of the template it was produced from, so a renamed, added or dropped column is discovered when the
header stops matching.

"The header is not the official one" means one of two things: a column the template asks for is
missing, or a column the template does not carry is present. Seven columns are exempt from the first
half, because a perfectly good submission can be without them — the two identifier columns, which a
first submission has no values for and the portal supplies itself, the two sample-reference columns,
which nothing in the data model holds, and the three reviewer columns, which are filled in during
assessment after a submission has been read. Column order is not part of the check: every reader
addresses columns by name, and a contributor who moved one has still sent every value asked for.

## Why

The obligation row and the range row are data reporting contracts. They describe what a good
submission looks like to the assessment team, not what the database is able to hold. Enforcing them
at import would refuse files the portal can store perfectly well, which turns the import into a
review step and moves a judgement that belongs to data assessment into code. They become checks at a
point where somebody is reviewing the submission, not at the point it is read.

The four refusals that remain all share a property: the portal genuinely cannot absorb what it was
given. Each one is loud and names what it found, so a contributor can fix the file and send it again.

Detecting a template revision through the header is a deliberate non-mechanism. A revision scheme has
no requirement behind it yet, and the failure it would guard against already fails loudly: the file
is refused and the offending header is named. A scheme built now would be guessing at what a future
revision changes.

## Revisit if

The upload page acquires a review step, at which point the obligation and range rows have somewhere
sensible to be enforced. Or the template starts carrying a revision marker, which would make
detection cheaper and more precise than header comparison.
