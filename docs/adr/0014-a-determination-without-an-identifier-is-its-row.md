# ADR 0014 — A determination with no identifier is recognised by its site, its publication and its place in the file

**Status:** accepted

## Decision

The upload template carries no identifier column, so a re-imported file has to recognise its own
earlier rows some other way.

A site is matched on its coordinates (ADR 0006). A determination beneath that site, when the row
carries no identifier, is matched on the site's coordinates, the publication reference, and the row's
position in the file.

Depth interval is deliberately not part of that identity. Neither is any other measured value.

This is what a repeat import survives: the same file sent again, and the same file with values
corrected. It does not survive a file whose rows have been reordered, or one with a row inserted or
removed ahead of an existing determination. Those are read as new determinations.

## Why

A correction arrives as a fresh copy of the same spreadsheet with one value changed, and correcting a
depth interval is the most plausible correction anyone sends. Keying identity on the depth interval
made exactly that correction unrecognisable: the second import wrote a new determination beside the
first, and the team's only remedy was to delete the dataset and start again.

Dropping the depth interval without replacing it was rejected. A paper reporting two depths from one
borehole yields two rows sharing a site and a publication reference, and with nothing left to tell
them apart the second import would overwrite the first determination's data rather than sit beside
it. That trades a visible duplicate for silent data loss, which is the worse failure.

Row position is what the correction scenario holds constant, and it separates two genuinely distinct
determinations at one site because each occupies its own row. It is also the weakest part of this
decision, which is why the limit is stated above rather than left to be discovered.

## Revisit if

Re-import needs to survive reordering or insertion, at which point position stops being a usable
proxy for identity. The real answer then is a persisted identifier: assign one, write it into the
export, and match on it when the file comes back.
