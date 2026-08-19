# Domain Docs

Which of this repository's domain documents to read when exploring the codebase, and in what
order.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root — the glossary of core domain concepts.
- **`docs/adr/`** — the architectural decisions that touch the area you are about to work in.
- **`memory/constitution.md`** — the project's standards and quality bar.

This is a single-context repo. There is no `CONTEXT-MAP.md` and no per-app glossary.

## The GHFDB structure is external and published

The database structure this portal implements is defined outside this repository, in the
peer-reviewed literature:

- Fuchs et al. (2021), *A new database structure for the IHFC Global Heat Flow Database*,
  Earth System Science Data
- Fuchs et al. (2023), *The Global Heat Flow Database: Update 2023*

`docs/constitution/references/` holds those publications, the project descriptions, the field
reference and the quality-scheme templates. When a question is about what a GHFDB column means or
which values are legal, the answer is in that reference material, not in the code — and where the
code disagrees with it, the code is what is wrong.

Note the name collision: `docs/constitution/` is the project's governance and reference material.
The engineering constitution is the single file `memory/constitution.md`.

## File structure

```
/
├── CONTEXT.md              ← domain glossary
├── memory/constitution.md  ← engineering standards and quality bar
├── docs/adr/               ← architectural decision records
├── docs/constitution/      ← project governance and published reference material
├── config/                 ← Django settings, URLs, WSGI
├── project/heat_flow/      ← the heat-flow data model
├── project/ghfdb/          ← the GHFDB import, export and proxy layer
├── project/review/         ← the submission review workflow
├── templates/              ← Django templates
├── tests/                  ← mirrors project/
└── specs/NNN-slug/         ← per-feature specs, plans, and tasks
```

## Use the glossary's vocabulary

When your output names a domain concept — in an issue title, a refactor proposal, a hypothesis, or
a test name — use the term as defined in `CONTEXT.md`. Do not drift to synonyms the glossary
explicitly rules out. Spreadsheet column names are case-sensitive and are quoted exactly as they
appear in the published template (`lat_NS`, `T_grad_mean`, `corr_HP_flag`).

If the concept you need is not in the glossary, that is a signal. Either you are inventing language
the project does not use, in which case reconsider, or there is a real gap worth recording.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding
it:

> _Contradicts ADR-0007 — but worth reopening because…_
