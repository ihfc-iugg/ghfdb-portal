# Goals

These are the standing directions the GHFDB portal works toward. Each one is a capability or
quality to steer by, not a task that gets ticked off. Whether any goal has been served well enough
is decided in the roadmap, the feature specs, and review, never by the goal itself.

This file carries no version numbers or release plan; that lives in the roadmap. For what the
portal is and the principles behind it, read [about](docs/about.md). For what the terms below
mean, read [CONTEXT.md](CONTEXT.md).

Importance is a tag on each goal, not a ranking:

- **Essential** — not worth adopting without it.
- **Expected** — a complete, dependable version is expected to have it.
- **Aspirational** — a genuine want whose absence never makes the portal incomplete.

| ID | Goal | Importance | Status | Notes |
|----|------|------------|--------|-------|
| G1 | Heat flow data held as a normalised relational model, designed for the science rather than for the spreadsheet | Essential | | |
| G2 | Faithful two-way translation between that model and the GHFDB structure, so internal queries stay predictable and exports match the published format exactly | Essential | | |
| G3 | The complete GHFDB held in the portal as a collection of individual datasets, each mapped one-to-one to its reviewed literature item | Essential | | |
| G4 | The data assessment team can add datasets to the portal one at a time | Essential | | |
| G5 | Community members outside the team can upload and publish their own datasets, with nothing becoming public until the team has reviewed it | Essential | | |
| G6 | Quality scores computed by the portal and authoritative over anything supplied | Essential | | |
| G7 | The published GHFDB freely reachable by anyone, no account required | Essential | | |
| G8 | The GHFDB structure reachable through the API, alongside the relational model's own endpoints | Expected | | |
| G9 | Releases generated from the portal's own data and served as addressable, citable artefacts | Expected | | |
| G10 | The map viewer integrated as part of the portal, reading its API and hosted releases and holding no data of its own | Expected | | |
| G11 | Data publication with DOIs semi-automated through GFZ Data Services | Expected | | |
| G12 | Supporting measurements beyond heat flow, such as thermal rock properties and subsurface temperature, held in the same model | Aspirational | | |
| G13 | Data assessment and record keeping carried out in the portal rather than on spreadsheets | Aspirational | | |
| G14 | Modelled 2D grids of temperature and heat flow stored, described and served | Aspirational | | |

_Written 2026-08-19. Revise as the goals change._
