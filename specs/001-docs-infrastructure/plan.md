# Implementation Plan: Documentation Infrastructure & Conventions

**Branch**: `001-docs-infrastructure` | **Date**: 2026-01-02 | **Spec**: `specs/001-docs-infrastructure/spec.md`
**Input**: Feature specification from `specs/001-docs-infrastructure/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Standardize how documentation is authored and organized (audiences + placement rules), ensure governance docs are discoverable and linked (including rendering the canonical constitution from `.specify/memory/constitution.md`), and add pre-merge documentation validation.

Validation approach:

- Treat Sphinx build warnings as failures for the primary docs build.
- Run the Sphinx `linkcheck` builder for hyperlink validation, with explicit allow/ignore configuration where needed.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python (repository target is Python >=3.13)
**Primary Dependencies**: Sphinx, sphinx-book-theme, sphinx-design, MyST Markdown (already in use in `docs/`)
**Storage**: N/A (documentation + CI validation only)
**Testing**: pytest (project tests), plus documentation validation via Sphinx builds (html + linkcheck)
**Target Platform**: Cross-platform dev (Windows/macOS/Linux), CI typically Linux, published via docs hosting (e.g., RTD)
**Project Type**: Django web application repository with a Sphinx documentation site
**Performance Goals**: Documentation validation should complete quickly enough for pre-merge gating (target: < 5 minutes in CI)
**Constraints**: Warnings MUST fail docs build; include canonical constitution content in rendered docs; avoid scope creep into theme migration
**Scale/Scope**: Documentation conventions + validation gates + governance discoverability (no new runtime app features)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates derived from `.specify/memory/constitution.md`:

- Pass: Continue using Sphinx + sphinx-book-theme for documentation (explicitly required).
- Pass: Governance docs must be clearly discoverable and linked; constitution is canonical at `.specify/memory/constitution.md` and must be included in the docs build.
- Pass: Avoid unrelated schema/model work; this feature is documentation-only and must not introduce new application behavior.
- Pass: Preserve open documentation expectations and avoid restricting access.

No constitution violations are required for this feature.

## Project Structure

### Documentation (this feature)

```text
specs/001-docs-infrastructure/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
project/
├── ghfdb/
├── heat_flow/
└── review/

docs/
├── index.md
├── guides/
├── development/
├── constitution/
└── conf.py

.specify/
└── memory/
  └── constitution.md

tests/
└── ...
```

**Structure Decision**: Use the existing Django repository structure (`project/` + `tests/`) and the existing Sphinx docs site under `docs/`. This feature introduces additional documentation pages/conventions and CI validation behavior; it does not restructure application code.

## Phase Plan

### Phase 0: Research (completed)

Outputs:

- `specs/001-docs-infrastructure/research.md`

Decisions captured:

- Strict Sphinx build with warnings treated as failures.
- Use Sphinx `linkcheck` builder for hyperlink validation.
- Keep MyST + sphinx-design as supported authoring primitives.

### Phase 1: Design & Contracts (completed)

Outputs:

- `specs/001-docs-infrastructure/data-model.md`
- `specs/001-docs-infrastructure/contracts/openapi.yaml` (explicitly “no runtime API”)
- `specs/001-docs-infrastructure/contracts/README.md`
- `specs/001-docs-infrastructure/quickstart.md`

Design notes:

- Documentation conventions will be expressed as docs pages under `docs/development/`.
- Governance discoverability requires a rendered page that includes `.specify/memory/constitution.md` as-is and is linked from the docs home page within 3 clicks.

### Phase 1: Agent Context Update (completed during planning)

Update the Copilot agent context to include Sphinx validation gate expectations and the selected documentation stack.

### Phase 2: Implementation Tasks (next)

`tasks.md` is produced by `/speckit.tasks`, but the intended task breakdown is:

1. Add/confirm documentation conventions page(s): audiences, placement rules, linking rules.
2. Add governance landing links and ensure the constitution canonical file is rendered.
3. Add feature documentation checklist and integrate it into contribution guidance.
4. Add CI docs validation commands (Sphinx html build with warnings-as-errors + linkcheck), including any linkcheck ignore/redirect rules needed.
5. Validate against success criteria (SC-001..SC-004).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --- | --- | --- |
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
