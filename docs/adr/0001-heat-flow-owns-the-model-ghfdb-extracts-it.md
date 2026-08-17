# ADR 0001 — The heat flow application owns the data model; the GHFDB application extracts from it

**Status:** accepted

## Decision

`heat_flow` holds the complete heat flow data model, including the parent value, the link from a
child to its parent, and the `is_relevant` flag that records whether a child fed its parent's value.

`ghfdb` is an extraction interface. It contains the proxy models, the flat column definitions, the
import resources, the export resource and the admin views built on them, and it reads from
`heat_flow`. It defines no domain models of its own beyond `GHFDBRelease`.

The dependency points one way. `heat_flow` does not import from `ghfdb`.

## Why

An earlier design, written in February 2026, took the opposite position. It proposed that
`heat_flow` should be reusable by any researcher measuring heat flow, independent of the GHFDB
administrative layer, and moved the parent model, the parent link and the relevance flag out into
`ghfdb`. The relevance flag in particular was to live on a through model, on the reasoning that a
curatorial judgement maintained by the assessment team has no business sitting on a scientific
measurement record.

That reasoning is sound in isolation, and the goal is not. The two concerns turned out to be too
tightly related for the separation to pay: the heat flow data model as this project needs it *is*
the GHFDB structure, expressed relationally. Keeping a boundary between them meant maintaining a
fiction that nothing consumed, at the cost of a junction table and an extra join on every export
query.

The migration was begun and abandoned partway. Its residue is still visible: `ParentHeatFlow` lives
in `heat_flow` but its database table is named `ghfdb_parentheatflow`, for the application it was
going to move to.

## Revisit if

Another project wants the heat flow data model without the GHFDB structure, and it is a real
consumer rather than a hypothetical one. The separation becomes worth its cost at the point where
someone is actually paying it.
