# Phase 0 Research: Documentation Infrastructure & Conventions

Date: 2026-01-02

This document resolves technical choices needed to plan and implement the documentation infrastructure spec.

## Decision 1: Use Sphinx strict-build for internal link and warning gating

- Decision: Use `sphinx-build` with warnings treated as errors for the primary docs build, so internal references (cross-references, toctree links, missing documents, etc.) fail CI.
- Rationale: Internal doc regressions generally surface as Sphinx warnings; treating warnings as failures aligns with FR-005 (“warnings MUST be treated as failures”) and keeps validation technology-native.
- Alternatives considered:
  - A standalone Markdown link checker: rejects some valid Sphinx/MyST constructs and misses Sphinx-specific references.
  - Relying on human review only: does not satisfy FR-005.

Notes (from Sphinx docs): Sphinx supports strict build behavior via `-W` and related options; newer Sphinx versions also add `--exception-on-warning`.

## Decision 2: Use Sphinx `linkcheck` builder for hyperlink validation

- Decision: Run the `linkcheck` builder in CI to validate hyperlinks and manage expected redirects.
- Rationale: `linkcheck` provides first-party link validation and configurable ignore/redirect/header behaviors.
- Alternatives considered:
  - Checking only internal references: misses broken external URLs.

Notes (from Sphinx docs):

- `linkcheck_ignore` can ignore URL patterns.
- `linkcheck_allowed_redirects` can whitelist expected redirects.
- `linkcheck_request_headers` can add request headers when needed.
- `linkcheck_exclude_documents` can exclude specific doc sets.


## Decision 3: Keep MyST + sphinx-design as supported authoring primitives

- Decision: Standardize on MyST Markdown for authored pages, with `sphinx_design` allowed for layout components.
- Rationale: The repository already uses MyST directives (`toctree`, frontmatter like `sd_hide_title`) and has `sphinx_design` enabled in the docs configuration.
- Alternatives considered:
  - ReStructuredText-only: would require rewriting existing content and patterns.

Notes (from sphinx-design docs):

- `sphinx_design` integrates cleanly with MyST.
- It supports cards/grids/tabs/dropdowns and custom directive defaults via `sd_custom_directives`.


## Decision 4: Sphinx-book-theme usage

- Decision: Continue using `sphinx-book-theme` as the HTML theme (already in use via templates/config).
- Rationale: Matches existing documentation output and avoids a theme migration.
- Alternatives considered:
  - Switching themes: out of scope for this spec.

## Open Questions (resolved)

- Constitution canonical location + docs link target: Use the canonical `.specify/memory/constitution.md` and include/link it in the docs build directly.
- Validation scope: Fail on broken internal links and build errors; warnings fail.
- Documentation landing page: Docs site home page is primary; repository README links to it.
