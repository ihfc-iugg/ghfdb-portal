# ADR 0007 — The portal database holds current state; releases are artefacts

**Status:** accepted

## Decision

The portal database holds the current state of the data. It carries no release or version
dimension: a site has one parent value, not one per release.

A GHFDB release is a published artefact: a file, its version, its date and its DOI. `GHFDBRelease`
records that artefact. It does not partition the data.

Generating a release from the current state of the portal's public data is an intended future
capability. It does not exist today, and `GHFDBRelease` should not be read as evidence that it does.

## Why

Version-scoping the data would multiply every parent value by the number of releases it appears in,
add a release dimension to every query that assembles the flat structure, and require every
constraint to be re-expressed as unique-within-a-release. That is a substantial permanent cost.

What it would buy is historical reconstruction, the ability to ask what the database said in 2024.
That is already available, and more authoritatively, from the published release files themselves,
which are archived with DOIs and are the citable record. Reconstructing a past release from the
portal would produce an answer that could differ from the published one, which is worse than not
offering it.

The rule that a parent is designated by curators rather than calculated, and is never updated
automatically, means a parent value changes only through a deliberate act. Its history is therefore
a curation record, not a schema dimension.

## Revisit if

The portal becomes the system of record for releases rather than a consumer of them. At that point
the question changes from "should we store history" to "how do we reproduce what we published", and
the answer may well be different.
