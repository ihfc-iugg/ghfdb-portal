# ADR 0008 — One constitution, one glossary, each with a single home

**Status:** accepted

## Decision

`memory/constitution.md` is the constitution. It is the only place principles are stated, and it
absorbs two that previously existed only in the documentation copy: **simplicity and
maintainability**, and **fidelity to the funding and mission of the WHDB Project**.

`docs/constitution/index.md` becomes a governance landing page. It describes what the constitution
is and where the reference material behind it lives, and it does not restate the principles.

`CONTEXT.md` at the repository root is the domain glossary, and it is the only place domain terms
are defined.

The two directories keep their confusingly similar names for now, and mean different things:
`docs/constitution/` holds project governance and the published reference material the structure is
built on; `memory/constitution.md` is the engineering constitution.

## Why

Both documents claimed to be authoritative and disagreed. The constitution listed eight principles;
the documentation page announced seven, named them differently, and linked the constitution as "the
single source of truth" in the same breath. Three other documents cited principle numbers against
the seven-principle list, so every principle citation in the repository resolved to the wrong
principle.

The failure mode is structural rather than clerical: two documents restating the same content will
diverge, and the divergence is invisible because each looks internally consistent. Making one of
them a pointer removes the possibility rather than fixing the instance.

The glossary is the same problem caught before it happened. Guidance for agents already instructed
them to read a glossary at `CONTEXT.md` and to follow its vocabulary; no such file existed, and
domain definitions were scattered across specifications, conceptual notes and a field reference
that disagreed with each other in places.

## Revisit if

The engineering constitution and the project governance material converge enough that maintaining
two documents with near-identical names stops being worth the confusion they cause.
