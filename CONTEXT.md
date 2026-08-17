# CONTEXT.md — domain glossary

The vocabulary this codebase speaks. Use these terms, with these meanings, in issues, commit
messages, test names, specs and code. Where a term has a tempting synonym, the synonym to avoid is
named so that it does not creep back in.

Two rules govern this file:

1. **Definitions describe the code as it stands**, not as it is planned to be. Where something is
   aspirational it says so.
2. **This vocabulary serves development.** It is not a transcription of how the heat flow community
   or the data assessment team speak. Several terms here are deliberately narrower than their
   everyday use, because the everyday use is ambiguous and the ambiguity has cost us. Do not
   "correct" an entry toward common usage.

The framework this portal is built on has its own glossary, and it is not repeated here. Terms like
Project, Dataset, Sample, Measurement, Contributor, registry and plugin are defined by FairDM and
inherited unchanged. This file covers what is specific to heat flow and to the GHFDB.

## Naming discipline

Four different things in this project were all being called "the database" or "the project". They
are not interchangeable, and most confusion in older documents traces back to this.

| Term | Meaning |
|---|---|
| **GHFDB release** or **GHFDB dataset** | The published data product: a curated, quality-controlled collection distributed with a DOI through GFZ Data Services. What a researcher downloads and cites. |
| **GHFDB portal** | This application, at portal.heatflow.world. |
| **portal database** | The PostgreSQL database behind the portal. |
| **GHFDB structure** or **data model** | The schema standard defining what a heat flow record contains. Use **template columns** when referring to the spreadsheet's fields specifically. |

Never write "the database" unqualified. Never use "the GHFDB" to mean the portal.

"Project" is likewise overloaded. **WHDB Project** is the DFG-funded research programme.
**Project** with no qualifier is the FairDM model, a user's own grouping of their datasets. When
both appear near each other, qualify both.

## The two applications

The portal has three applications of its own. The split between the first two is the most important
structural fact in the codebase.

### `heat_flow` — the data model

Owns everything about heat flow as a scientific domain: the sites, the intervals, the measurements,
the relationship between parent and child values, and quality scoring. Field names here are plain
and descriptive: `value`, `uncertainty`, `top`, `bottom`. They are written for a reader who knows
the science, not for the spreadsheet.

### `ghfdb` — the extraction interface

Owns the translation between the data model and the published GHFDB structure: the flat column
names, the import resources, the export resource, the proxy models and the admin views built on
them. Everything here speaks the spreadsheet's language, using its exact column names and its exact
casing.

**The boundary between these two applications is where the translation happens.** A name is either
a domain name or a published column name depending on which side it is on, and neither borrows from
the other. An earlier design tried to make `heat_flow` reusable by a project with no interest in
the GHFDB, moving parent values and the relevance flag into `ghfdb`; that was dropped because the
two are too tightly related to separate cleanly. `heat_flow` holds the complete model, and `ghfdb`
reads from it.

### `review` — the assessment workflow

Owns the process by which a publication becomes a dataset. See **data assessment** below.

## The heat flow data model

### Heat flow, or heat-flow density

The terrestrial surface heat flow value, after all corrections for instrumental and environmental
effects, in mW/m². Written `q` in published columns. Negative values are legitimate and occur where
there is convective downflow, so never validate on the assumption that heat flow is positive.

### Heat flow site

A geographic location where heat flow data has been collected. **A site is its coordinates**: one
site per latitude and longitude pair, reported to five decimal places. Two boreholes a hundred
metres apart are two sites.

Implemented by `HeatFlowSite` in `project/heat_flow/models/parent.py`, a subclass of FairDM's
`Sample`. It carries the access geometry: total measured depth, total true vertical depth, azimuth
and inclination. It also holds the geographic environment and the method and purpose of exploration.

Do not treat "site" and "location" as different things. They are synonyms here, deliberately.

Two cautions about coordinates:

- Nothing currently enforces the uniqueness that the definition asserts. Tracked as
  [#143](https://github.com/ihfc-iugg/ghfdb-portal/issues/143).
- **A coordinate's stated precision is not its actual precision.** Values are supplied to five
  decimal places regardless of how precisely they were originally determined, so a coordinate
  reported to two decimal places arrives padded with zeros. Never infer accuracy from the number of
  digits.

### Depth interval

A depth range within a site, over which a heat flow determination is made. Implemented by
`HeatFlowInterval` in `project/heat_flow/models/child.py`, also a `Sample`. It carries the depth
range together with the lithology, stratigraphy and age of the rock in it.

An interval is the physical thing that several measurements are made on: the child heat flow, its
thermal gradient, its interval conductivity, and any probe metadata all attach to the same interval.

**One interval can carry several children.** Heat flow over the same depth range at the same site
can be calculated more than once, using different conductivity values, a different thermal gradient,
or a different set of corrections. Each such calculation is a separate child. Do not model or
assume a one-to-one relationship.

### Parent and child

These two words are reserved for **one specific relationship: between heat flow measurements**.
They are fixed by the published structure, which carries `ID_parent` and `relevant_child`, so they
cannot be renamed.

- A **child** is a single heat flow determination over one depth interval, computed from a thermal
  gradient and a thermal conductivity. Implemented by `HeatFlow`.
- A **parent** is the representative heat flow value for a site. There is one per site, and it is
  designated by curators rather than computed. Implemented by `ParentHeatFlow`.

Selecting a parent is knowledge-intensive and deliberately manual. Where a site has one child, that
child's value becomes the parent. Where it has several, curators choose, typically averaging
selected children and favouring corrected values. New children arriving at an existing site trigger
a manual review; **a parent is never updated automatically**.

`is_relevant` on a child records whether it was used in deriving its parent's value. It is a
curatorial statement about how a measurement was used, not a property of the measurement itself.

**Never use "parent" or "child" for samples.** FairDM has its own parent/child relationship between
samples, and the interval-to-site link is a sample relationship, not a measurement one. That link
is the `site` field on `HeatFlowInterval` and should be called the site, never the parent.

### Thermal gradient

The rate of temperature change with depth over an interval, in K/km. Implemented by
`ThermalGradient`. Carries both measured and corrected values, the temperature determination method
at the top and bottom of the interval, shut-in times, and the number of discrete temperature
recordings.

### Interval conductivity

The mean thermal conductivity over an interval, in W/mK. Implemented by `IntervalConductivity`.
Named for the distinction that matters: it is a value representative of a whole interval, not a
discrete measurement on a single rock sample.

Avoid "thermal conductivity" unqualified when you mean this model, since the phrase also names the
physical property in general.

### Correction

A statement that a particular disturbance was recognised at a child measurement, and what was done
about it. Implemented by `HeatFlowCorrection`, one row per correction type per child, each with a
status.

Nine correction types exist: in-situ conditions, temperature, sedimentation and subsidence,
erosion, topographic, paleoclimatic, surface and climatic, convection, and heat refraction. In
published columns they appear as `corr_IS_flag` through `corr_HR_flag`.

Avoid calling these "flags" in code, despite the column names. They were booleans once and were
deliberately replaced, because a boolean cannot distinguish "no correction was needed" from "a
correction was needed and not applied".

### Probe metadata

Instrument parameters for a marine probe deployment: probe type, length, penetration depth and
tilt. Implemented by `ProbeMetadata`, attached to an interval.

## Quality

### U-score, M-score, perturbation flags

The three components of the heat flow quality scheme, after Fuchs et al. (2023). The **U-score**
scores numerical uncertainty, the **M-score** scores methodological quality, and the
**perturbation flags** record which disturbing effects apply. Each score runs from 1 (excellent) to
4 (poor), with `Ux` and `Mx` meaning not determined.

### Quality code

The composite thirteen-character string combining the three components, for example `Ux.Mx.-------`.
Stored on both children and parents.

A parent inherits quality conservatively: with one child, its quality directly; with several, the
poorest quality among the children marked relevant.

**The portal computes its own quality scores, and the value it computes is authoritative.** Quality
codes present in an imported file are rejected rather than stored. This is a settled decision; do
not add a code path that ingests a supplied quality code.

Note one live gap: the implementation in `project/heat_flow/quality.py` follows Fuchs et al. (2023),
while the community's current quality toolbox is Dergunova et al. (2026). Whether the portal should
track that revision is open.

### Controlled vocabulary

A governed set of concepts with defined meanings, published as SKOS. The portal defines fifteen of
them in `project/heat_flow/vocabularies.py`, covering heat flow methods, probe types, geographic
environments, exploration methods and purposes, temperature methods and corrections, and the
several conductivity dimensions.

**Reserve "vocabulary" for this and nothing else.** A set of column names is not a vocabulary. Say
"column names".

## Spreadsheets

Three distinct spreadsheets exist, and confusing them has been a recurring source of error. All
three are called "the template" somewhere in older documents.

| Spreadsheet | What it is | How the portal treats it |
|---|---|---|
| **Upload template** | The official template published with a DOI and distributed to the community. What a contributor fills in. Currently 70 columns. | Imported. Supported indefinitely, since not every contributor will ever work directly in the portal. |
| **Management spreadsheet** | The assessment team's internal working file for quality-controlling the database as a whole. Contains fields their own scripts calculate. | Never imported. The portal calculates those values itself. |
| **Release format** | The format a published GHFDB release is distributed in. A superset of the upload template: the same columns plus `Review_status`, `Year`, `Quality_Code` and `ID_parent`. | **Exports are always in this format.** Imported at least once, to seed the portal with the current published product. |

### Published column names

The names in row 6 of the upload template, and the header row of a release file: `q`, `lat_NS`,
`corr_HP_flag`, `T_grad_mean`, `total_depth_MD` and the rest. Their casing is part of the name and
is preserved exactly inside `ghfdb`.

Two published names are misspelled: `tc_pT_fuction` and `Ref_ISGN`. **The portal uses the correct
spellings internally and rejects files carrying the misspelled forms**, with an error naming the
outdated template. Perpetuating a spelling error because a file contains it would make the error
permanent.

### Parent and child columns

The published format is one row per child, with the parent's columns repeated on every row
belonging to it. So `PARENT_COLUMNS` and `CHILD_COLUMNS` are two halves of a single flat row, not
two kinds of file.

## Workflow

### Data assessment

The activity of extracting heat flow data and metadata from a publication, quality-controlling it,
and recording it as a dataset. Implemented by the `review` app.

**One publication is always one dataset.** Datasets spanning several publications are possible in
principle but are out of scope.

Today this work is done outside the portal, on spreadsheets: a reviewer reads a paper, fills in a
per-publication spreadsheet by hand, and that spreadsheet is later merged into the aggregate. Every
hop in that chain loses information and none of it is traceable. **Moving this activity inside the
portal is the reason the portal exists**, and it is what the `review` app is building toward.

Avoid "literature review", which to a researcher means a survey article.

### Publication approval

The separate decision, made by a data administrator, that a completed dataset may become public. It
is a different act by a different person from data assessment, and no dataset becomes public
without it.

Never write "review" unqualified when either of these is meant.

### Reviewer

A member of the assessment team who carries out data assessment. Distinct from a data
administrator, who grants publication approval.

## Aspirational, not built

Named here so that nobody reads them as descriptions of working behaviour.

- **Generated releases.** `GHFDBRelease` exists as a model, but releases are currently produced and
  maintained externally as spreadsheets. The intent is that the portal will eventually generate a
  release from the current state of its public data. The portal database holds current state only
  and has no release dimension: one parent per site, full stop.
- **Assessment inside the portal.** Described under data assessment above.

## Standing constraints

1. **The portal imports the numbers it is given.** Where supplied data is imprecise, inconsistent
   or duplicated, that is resolved through data assessment, not by the portal guessing. Specifically,
   the portal does not attempt proximity matching on coordinates or merge near-duplicate sites.
2. **The published structure is the interface, not the model.** The portal's schema is normalised
   and the flat structure is generated from it. Never reshape the model to resemble the spreadsheet.
3. **Quality is computed here.** Supplied quality codes are not ingested.
4. **`heat_flow` owns the model; `ghfdb` reads it.** The dependency points one way.
5. **A parent is designated, never calculated.** Automation may support the decision; it does not
   make it.
