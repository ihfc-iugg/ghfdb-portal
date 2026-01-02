# Phase 1 Data Model: Documentation Infrastructure & Conventions

Date: 2026-01-02

This feature does not introduce application database tables. “Data model” here describes conceptual entities and relationships used for documentation organization and validation.

## Entities

### Documentation Page

Represents a single authored documentation unit.

- Fields:
  - `path`: repository-relative path (e.g., `docs/guides/importing-data.md`)
  - `audience`: `user` | `developer` | `governance`
  - `section`: logical grouping (Guides / Development / Governance / etc.)

### Documentation Section

A navigation grouping represented by toctree groupings.

- Fields:
  - `name`: e.g., `Guides`, `Development`
  - `index_path`: landing page path (typically a `toctree` root)

- Relationships:
  - A section contains many pages.

### Governance Canonical Source

Represents a canonical governance file that must be published in docs.

- Fields:
  - `canonical_path`: `.specify/memory/constitution.md`
  - `published_link_target`: a Sphinx-rendered page that includes the canonical file as-is

### Validation Gate

Represents CI checks that run “before merge”.

- Fields:
  - `check_name`: `docs-build`, `linkcheck`
  - `failure_condition`: warnings/errors

### Feature Documentation Checklist

Represents a reusable checklist for feature PRs.

- Fields:
  - `items`: list of required documentation updates
  - `applies_when`: “user-facing behavior changes”

## State / Transitions

- Pages/sections evolve through normal PR review.
- Validation gate transitions:
  - `pass` → merge allowed
  - `fail` → merge blocked until fixed
