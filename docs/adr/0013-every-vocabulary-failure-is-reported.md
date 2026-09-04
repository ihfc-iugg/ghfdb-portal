# ADR 0013 — Every vocabulary failure is reported, including on many-valued columns

**Status:** accepted

## Decision

A value that does not match the controlled vocabulary its column draws on is refused, and the
refusal names the line, the published column name, the value and the vocabulary it was checked
against.

This applies identically whether the column holds one term or several. The many-valued columns —
lithology, stratigraphy, each temperature method, each conductivity column, and exploration purpose
— are checked on the same terms as the rest, and a failure on any of them refuses the file.

Nothing falls back to an empty relationship, and no vocabulary error is caught and discarded.

## Why

Most of the vocabulary surface of a release is many-valued. Discarding failures there discarded
most of the checking this reader exists to do, while leaving every visible sign of success: the
import completed, the row was written, and the relationship was simply empty. Nothing anywhere went
red.

The failure mode is quiet and permanent. A row carrying an unrecognised lithology term imports
clean with no lithology at all, and there is nothing afterwards to distinguish it from a row that
genuinely reported none.

The rule is stated here rather than left to the reading code because the catch that swallowed these
errors is in shared machinery, one line, and it looks like defensive programming. Restoring it to
get a large file through would be an easy change to justify and an expensive one to notice.

## Revisit if

A vocabulary the portal maintains is knowingly narrower than the published one, in which case the
answer is to widen the vocabulary or record a correction at source, not to resume discarding the
failures.
