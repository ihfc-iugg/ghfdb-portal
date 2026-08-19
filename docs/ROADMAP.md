# Roadmap

**Date:** 2026-08-19

This document was designed against [GOALS.md](../GOALS.md). See also [CONTEXT.md](../CONTEXT.md)
for domain terminology and [memory/constitution.md](../memory/constitution.md) for project
standards.

The first four items are already built. They are carried here so the sequence reads as a whole
rather than opening midway.

## Versioning

The portal is a deployed application rather than a published package, and its releases are dated:
`v<year>.<release>`, currently `v2025.21`. A version number records when a deploy happened and says
nothing about which goals it met, so the milestones below are gated on goals instead.

| Milestone | Gate |
|---|---|
| Essential goals | Every Essential goal delivered. The portal does the job it exists for. |
| Expected goals | Every Expected goal delivered. Complete and dependable. |
| Aspirational goals | Taken on as capacity allows, in any order. |

A goal is not one release. Some take several, and one release can move two.

## Essential goals

Everything the portal has to do to be worth running.

### R1 — Heat flow held as a normalised relational model

*Delivered · needs verification · advances G1*

Heat flow is stored as a set of related records covering sites, the depth intervals within them,
the measurements made over those intervals, and the corrections applied to each measurement. Field
names describe the science rather than the spreadsheet the data arrives in.

Serves G1.

### R2 — The published structure readable from the model

*Delivered · needs verification · advances G2*

The published parent and child structure is derived from the stored records rather than kept
alongside them, so a query written in the portal's own terms and a query written in published
column names return the same facts.

Serves G2.

### R3 — The spreadsheet round trip

*Delivered · needs verification · advances G2, G3*

Files in the community upload template and in the release format can be read into the portal, and
the portal's data can be written back out in the release format.

Serves G2 and G3.

### R4 — Quality computed from what the portal holds

*Delivered · needs verification · advances G6*

Every heat flow record carries a quality code the portal calculates from its own stored metadata.
Codes present in an incoming file are rejected rather than stored.

Serves G6.

### R5 — The published database imported in full

*multi-feature · advances G3*

The portal holds a sample rather than the database. Until the current published release is in,
nothing downstream has real data to work against: public access, generated releases and the map
viewer all wait on it. The import has to land the release as a collection of individual datasets,
each tied to the reviewed literature item it came from, not as one undifferentiated pile of sites
and measurements. Reliability matters more here than repeatability, because this is a one-off
seeding and everything after it arrives dataset by dataset.

**Deliverables:**

- Every row of the current published release loaded into the portal.
- One dataset per reviewed literature item, with that mapping stored rather than inferred later.
- The correct literature attached to each record, resolved against existing bibliographic records
  where they already exist.
- A record of what was skipped or rejected and why, in a form a curator can act on.
- Confirmation that a release exported after the import carries the same data as the release that
  went in.

Serves G3. Out of scope: any change to the published structure, and any user-facing upload path.

### R6 — Datasets added to the portal from inside it

*feature · advances G4*

The only working import today is in the Django admin, and the views that once offered it elsewhere
were removed. The assessment team needs to add one dataset at a time through the portal's own
pages, against a dataset they own, without going through the admin.

**Deliverables:**

- Upload of a completed template file against a dataset, from the portal rather than the admin.
- A validation result the uploader can read and act on, naming the row and column at fault.
- A file that fails validation leaves the dataset unchanged.

Serves G4. Out of scope: the trust and review distinctions that separate team members from outside
contributors.

### R7 — Contribution from outside the team, reviewed before it goes public

*multi-feature · advances G5*

A heat flow researcher with their own data should be able to create a dataset and upload into it
unaided. What separates them from the assessment team is trust rather than mechanism: data from
outside the team stays private until someone on the team has looked at it, while data from team
members does not wait.

**Deliverables:**

- A role marking a portal user as part of the assessment team, and the permissions that follow it.
- A dataset uploaded from outside that role stays invisible to the public until it is reviewed.
- A queue of datasets awaiting review, and a route from that queue to a decision.
- The outcome of each review, and who made it, recorded on the dataset.
- Datasets from team members published without waiting.
- Test coverage for the review application, which currently has none.

Serves G5. Out of scope: assessing the science of a submission. This is the gate on publication,
not the assessment work itself, which is R15.

### R8 — Public access to the database itself

*feature · advances G7*

The download served today is a static file of the 2024 release, and the catalogue page for browsing
public datasets was never built. Once R5 lands the portal holds the database and can serve it
directly instead.

**Deliverables:**

- Public browsing of the datasets the portal holds, with no account required.
- Download of the current database, served from the portal's own data.
- The superseded static download removed rather than left alongside the new one.

Serves G7. Out of scope: the map viewer, which is R12, and generated citable releases, which are
R11.

### R9 — The quality scheme kept current

*feature · advances G6*

The portal's calculations follow the 2023 quality scheme. The community's current toolbox is the
2026 revision. Whether the portal tracks that revision is undecided, and the longer the two
diverge, the more of the database carries scores computed against a superseded scheme. Making the
decision is the first deliverable, and it may close the item.

**Deliverables:**

- A decision on whether the portal tracks the 2026 revision, written down where a later reader
  will find it.
- If it does: scores recalculated across the database, with the scheme each score was computed
  under recorded alongside it.
- If it does not: the reason stated somewhere a data user will see it.

Serves G6. Out of scope: changing which component scores exist, or how the composite code is
formatted.

## Expected goals

What a complete and dependable portal has.

### R10 — The published structure reachable through the API

*feature · advances G8*

The framework already generates and documents an API over the portal's own models. What it does
not offer is the database in its published parent and child shape, which is what an outside
consumer expects and what the map viewer will read.

Serves G8.

### R11 — Releases generated from the portal's data

*multi-feature · advances G9*

Releases are produced and maintained outside the portal as spreadsheets. Generating them here, and
serving each one as an addressable artefact that can be cited, is what makes the portal the source
of the published product rather than a companion to it.

Serves G9. Depends on R5.

### R12 — The map viewer running inside the portal

*feature · advances G10*

The map viewer is embedded as an iframe pointing at an externally hosted build. Bringing it inside
the portal, reading this portal's API and its published releases, removes that split.

Serves G10. Depends on R10 and R11.

### R13 — Data publication with DOIs

*multi-feature · advances G11*

Metadata for a dataset can already be exported in the schema GFZ Data Services expects.
Semi-automating the rest of the path, from a finished dataset to a minted DOI, is what remains.

Serves G11.

## Aspirational goals

Genuine wants whose absence never makes the portal incomplete.

### R14 — Supporting measurements beyond heat flow

*multi-feature · advances G12*

Thermal rock properties and subsurface temperature held in the same model as heat flow, so that the
metadata behind a heat flow value can be stored as data rather than as description.

Serves G12.

### R15 — Assessment and record keeping in the portal

*multi-feature · advances G13*

Extracting heat flow data from a publication, quality-controlling it and recording the decisions
made along the way, all done in the portal rather than on spreadsheets.

Serves G13.

### R16 — Modelled grids

*multi-feature · advances G14*

Two-dimensional grids of temperature and surface heat flow produced by numerical or statistical
models, stored with metadata describing how each grid was made, and downloadable.

Serves G14.
