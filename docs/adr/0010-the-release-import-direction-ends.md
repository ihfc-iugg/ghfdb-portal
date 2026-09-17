# ADR 0010 — Reading a published release into the portal is not a direction the project takes

**Status:** accepted

## Decision

The portal will not read a published GHFDB release file into its database. Work on that stopped in
September 2026 at the request of the data assessment team, who judged it unnecessary. The open pull
request that carried it closes unmerged, with its branch.

Two roadmap items depended on that direction and are struck through rather than deleted, so the
record of why they existed survives:

- **R3, the spreadsheet round trip.** Half of it was already gone: an audit in August 2026 found
  that nothing in the codebase could read a published release, and writing one back out had already
  moved to R17. What remains of R3 is the community upload template, which belongs to R6.
- **R5, the published database imported in full.** This was the one-off seeding run that would have
  loaded the current release as a collection of datasets. It will no longer happen.

Data enters the portal one dataset at a time, from the official upload template. That is R6, whose
programmatic half is specified in `specs/004-import-upload-template/`.

## Why

The team who would have run the seeding decided they did not want it. That is their call to make:
they own how the database gets populated, and a bulk load nobody intends to run is a feature with no
user.

The technical picture agrees with them rather than merely permitting it. The release is a
comma-separated file with a single header row, while every importer in the portal reads a
spreadsheet with its header on the sixth row, so the two directions never shared as much machinery
as the roadmap assumed. Building a reader for a format that arrives once, to seed data the team
would rather assess dataset by dataset, spends effort on the path away from where the project is
going.

The cost accepted is that the portal holds a sample rather than the full published database, and
everything waiting downstream on real data waits longer. That is a slower route, not a blocked one:
the same records arrive through the upload template, reviewed as they come.

## Revisit if

The assessment team asks for a bulk load after all, or a use appears that needs the whole published
database in the portal at a point in time rather than accumulated dataset by dataset. Either would
be a fresh decision, not a resumption of this one.
