# ADR 0005 — Exports use the release format; imports accept the upload template and a full release

**Status:** accepted

## Decision

**Export** produces the GHFDB release format, always. There is one export shape and no options.

**Import** accepts two things:

1. **The published upload template.** The DOI-bearing spreadsheet distributed to the community.
   One publication per file. This path is permanent.
2. **A full GHFDB release file.** The most recently published product, imported to seed the portal
   with the current state of the database. This path must work correctly at least once, mapping
   every column to the right field. Repeated re-import is not a near-term requirement.

The assessment team's internal management spreadsheet is not an import format. Fields their scripts
calculate are not ingested; the portal computes the equivalents itself.

## Why

Three spreadsheets are in circulation and they are routinely conflated, so naming which ones the
portal reads and writes is itself part of the decision.

Export has exactly one consumer, the published product, so a second export shape would exist only
to serve a workflow the portal is trying to replace.

The upload template import is permanent because not every contributor will ever work directly in
the portal. Some will always fill in a spreadsheet and send it, and that has to keep working
indefinitely.

The release import is different in kind: it is a migration, not a workflow. Its purpose is to get
the current published product into the portal so that the portal has something to serve. It carries
the highest correctness bar of the three, because a mistake there is silently wrong across the
whole dataset, and the lowest longevity, because once the portal is the system of record the
direction of travel reverses.

The management spreadsheet is excluded because ingesting values computed elsewhere means importing
another system's derivations along with its assumptions, and the portal can compute all of them
from data it already holds. See ADR 0004.

## Revisit if

The assessment team adopts a different exchange format for community contributions, or the portal
begins generating releases directly, at which point the release import becomes a rollback path
rather than a seeding path.
