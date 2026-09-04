# ADR 0012 — A file is imported whole or not at all

**Status:** accepted

## Decision

An import writes everything or nothing. If any value anywhere in the file is refused, the whole
import is rolled back, including the rows that passed, and the curator is told the import failed.

This covers every kind of refusal, not missing values alone: a header fault, an unrecognised
vocabulary term, a type mismatch, an ambiguous publication reference, two rows disagreeing about a
record they share, or an identifier repeated inside one file.

Refusals are collected and reported together, each carrying the line number as it appears in the
file, the published column name, the offending value and the reason. A curator corrects the file at
source and imports it again.

## Why

A partial import is worse than a failed one. It leaves the portal in a state nobody chose, holding
some of a publication's determinations and not others, with no record of which rows were dropped or
why. The next person to look cannot tell an incomplete import from a publication that reported less.

The argument for tolerance was made during the audit and rejected: the release file profiles clean,
so a refusal is more likely to indicate a fault in the reader than a fault in the data. A profile
only measures the checks somebody thought to run, and it is exactly the checks nobody thought of
that this guarantee exists to survive. The safe reading of a refused row is that the data is wrong.

The working practice this supports is that a file is dry-run before it is run for real, so a
refusal costs a correction at source rather than a partial write to undo.

## Revisit if

Releases become large enough that a single refused value in a file of tens of thousands of rows
makes a correct import impractical to achieve, in which case the answer is a staged review of
refusals rather than a silent partial write.
