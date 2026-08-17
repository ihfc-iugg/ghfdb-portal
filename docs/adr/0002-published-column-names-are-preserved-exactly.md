# ADR 0002 — Published column names are preserved exactly inside the GHFDB application

**Status:** accepted

## Decision

Inside `ghfdb`, columns are named exactly as the published structure names them, casing included:
`lat_NS`, `long_EW`, `corr_HP_flag`, `total_depth_MD`, `T_grad_mean`. This applies to the column
constants, the column metadata file, the import and export resource field declarations, and the
queryset annotations that flatten the model.

Inside `heat_flow`, fields carry plain descriptive names chosen for the domain: `value`,
`uncertainty`, `top`, `bottom`, `elevation`.

The translation between the two happens at the boundary between the applications, in one place.

## Why

The published structure is maintained by the assessment team, not by this project, and it changes
on their schedule. The only defence against drift is that a name in the code is either identical to
the published name or obviously not a published name at all. A convention that lowercases published
names creates a third form that matches neither the file nor the model, and every mismatch then
needs a lookup to resolve.

This has already cost real time. The column constants were moved to published casing while the
column metadata file and the resource field declarations were not, and the resulting disagreement
left fourteen tests failing and the export column ordering unreliable.

Python convention would prefer lowercase attribute names throughout. That preference loses here to
the stronger requirement that the interface layer be checkable against the published file by eye.

## Revisit if

The portal stops consuming the published spreadsheet in both directions: that is, if generated
releases replace the exchange format entirely and no file is ever read from or written to it.
