# Governance and constitution

This section covers how the Global Heat Flow Database Portal is governed: the rules development
works to, and the source material those rules were drawn from.

## The constitution

The constitution sets out the principles, technical constraints, and quality gates that govern
work on the portal. It is what a specification is checked against before it is planned, and what a
pull request is reviewed against before it is merged.

There is exactly one copy, and it lives at
[memory/constitution.md](../../memory/constitution.md). This page deliberately does not repeat any
of it. An earlier version of this page listed the principles in its own words, and the two lists
drifted apart until they named different principles in a different order, with each document
claiming to be authoritative. A page that summarises the constitution will always be at risk of
that, so this one points at it instead. The reasoning is recorded in
[ADR 0008](../adr/0008-one-constitution-one-glossary.md).

To read the principles, follow the link above. To propose a change to them, open a pull request
against `memory/constitution.md` that states the change, the reason for it, and its expected
impact. The amendment and versioning rules are in the Governance section of the constitution
itself.

## Two things called "constitution"

The naming here is unhelpful and worth stating plainly.

- `memory/constitution.md` is the engineering constitution: the principles and gates that govern
  how code is written for this repository.
- `docs/constitution/` is this documentation section: project governance and the published
  reference material that the portal's structure was built on.

They are not two versions of the same document. If you are looking for a rule that development
must follow, it is in `memory/constitution.md`. If you are looking for the specification, proposal,
or paper that a rule was derived from, it is in `references/` below.

Domain terminology is separate again. Definitions of heat flow terms and GHFDB entities live in
`CONTEXT.md` at the repository root, which is the only place they are defined.

## Reference material

The [references/](references/README) directory holds the source documents behind the portal's data
model and its obligations as a funded project. They are kept in the repository so that a claim made
in a specification can be traced back to the document it came from.

What is there:

- **Project funding and scope.** The Phase 1 and Phase 2 DFG project descriptions, the public
  Heatflow.world overviews of both phases, and the final Phase 1 report. These define what the
  World Heat Flow Database Project committed to deliver.
- **GHFDB conceptual schema.** A specification of the conceptual metadata structure, a field
  reference for the database, and the official Excel template used for data uploads.
- **Publications.** The two papers that define the current database structure and its
  quality-assurance scheme: Fuchs et al. (2021) on the IHFC database structure, and the 2023 paper
  on quality assurance of heat flow data.
- **Quality scheme templates.** The spreadsheets accompanying the 2023 quality-assurance paper,
  covering the methodological scoring tables for probe and borehole or mine measurements, the
  structure overview, and worked examples.

`references/README.md` indexes the individual files and explains how to cite them from a
specification.

:::{toctree}
:maxdepth: 1

references/README
:::

## How governance is applied

Non-trivial changes go through the spec-driven workflow. A feature starts as a specification, gains
an implementation plan that is checked against the constitution's principles, and is reviewed
against those same principles before it merges. Where a principle has to be broken for a practical
reason, the plan records the violation and the justification rather than leaving it unstated.

See the [spec-driven workflow](../development/spec-driven-workflow) for the full process, and
[documentation conventions](../development/documentation-conventions) for how the artefacts are
written.
