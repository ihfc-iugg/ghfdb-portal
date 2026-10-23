# ADR 0027 — An unspecified correction is stored with no status

**Status:** accepted

## Decision

A child's correction whose status is unknown is stored with an empty status. "Unspecified" is not
one of the statuses a correction can hold.

- The published file is unchanged. The importer stores an empty status for a `-`, an
  `[unspecified]` or an empty cell, and the export writes `-` for an empty status. A child with no
  row for a correction type still exports an empty cell.
- The quality scores are unchanged. An empty in-situ status scores as `-` did.
- The API gives an empty status as `null`, and still lists the correction, so a correction recorded
  with no status stays distinct from one never recorded.
- The child's form offers an empty entry, labelled "Unspecified", and no unspecified status.

## Why

An unspecified correction is the absence of a status, not a status. Stored as `-`, it was offered
on the form as one of the choices, counted among each correction type's valid statuses, and served
through the API as if it were a value. Storing it empty makes the model say what the data means.
The `-` is the published file's way of writing an empty status, so it stays in the file and nowhere
else.

## Revisit if

The published format gains a status that means unspecified, or a consumer of the API needs the
file's `-` rather than `null`.
