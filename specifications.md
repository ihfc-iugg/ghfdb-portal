# Specification Backlog (Spec-Driven Development)

This document is a curated backlog of **potential feature specifications** for the Global Heat Flow Database Portal.
It exists to make it easy to pick the next piece of work and convert it into a concrete, testable spec.

These candidates are derived from:

- The portal constitution (see [.specify/memory/constitution.md](../../.specify/memory/constitution.md))
- Existing user workflow docs (e.g., [docs/guides/reviewing.md](../guides/reviewing.md), [docs/guides/importing-data.md](../guides/importing-data.md))
- The required “canonical model + IHFC interchange product” approach (Constitution Principles I + III)
- Non-negotiable provenance + dual-review governance (Constitution Principle VI)

---

## How to use this backlog

1. Pick one item (preferably a P0/P1 item) and create a feature spec folder:

   - `specs/###-short-name/spec.md`

1. Author the spec using the repo’s Speckit templates:

   - Template: [.specify/templates/spec-template.md](../../.specify/templates/spec-template.md)
   - Then generate `plan.md` and `tasks.md` per your SpecKit workflow.

1. Keep specs “executable”:

   - User scenarios + acceptance scenarios
   - Requirements that are independently testable
   - Explicit constraints and out-of-scope

---

## Suggested starting sequence

If you’re adopting spec-driven development right now, the recommended first two specs are:

1. **Docs Infrastructure & Conventions** (P0-01)
2. **Testing Infrastructure & Conventions** (P0-02)

Those two specs make every later feature spec cheaper to write, review, and ship.

---

## Selection rubric (pick the next spec)

Prefer items that:

- Are **constitution-critical** (especially Principles VI, IV, I/III)
- Reduce risk/ambiguity in the data lifecycle (import → curate → approve → publish → export)
- Unlock other work (dependency-heavy foundations first)
- Can be validated end-to-end with a small test fixture

---

## P0 — Workflow foundations (docs + tests)

### P0-01 Documentation Infrastructure & Conventions

Define how documentation is authored, validated, and kept in sync with the constitution and features.

Scope should include:

- Sphinx structure and where new docs live (user guides vs dev docs)
- Canonical locations for governance docs (constitution, references) and how they’re cross-linked
- Conventions for feature documentation (“what must be updated when a feature ships”)
- Spec-driven workflow docs: how `spec.md`, `plan.md`, `tasks.md` are created and referenced

Touches: Constitution III, IV, VI (governance clarity), Development Workflow

### P0-02 Testing Infrastructure & Conventions

Define the testing strategy and minimum fixtures required to make specs enforceable.

Scope should include:

- Test layers (unit/integration/contract) and where they live under `tests/`
- Minimal fixture datasets for: import, review submission, admin approval, export
- CI expectations (what runs on PR, what runs nightly) and coverage goals (if any)
- How to write tests for schema mapping and round-trip integrity

Touches: Constitution IV, VI, Testing Requirements

---

## P1 — Foundation (review + provenance + permission boundaries)

### P1-01 Dual Review Workflows (Curation vs Publication Approval)

Define states, transitions, and invariants for:

- Literature assessment review (reviewer-driven curation)
- Publication approval review (admin-only gating)

Touches: Constitution VI, IV

### P1-02 Provenance & Attribution Model (Authors vs Curators vs Editors)

Define canonical storage of:

- Original publication metadata (DOI, citation)
- Original scientific authors
- Portal contributors (reviewers/curators)
- Editorial approvers (admin actions + timestamps)

Touches: Constitution VI, I

### P1-03 Role Hierarchy & Permission Matrix

Specify roles and permissions (minimum set) such that:

- Review/curation permissions do not imply publish/approve permissions
- Publication approval is restricted to a designated admin role
- Role assignment is tightly controlled

Touches: Constitution VI

### P1-04 Audit Trail for Editorial Actions

Specify what events must be logged for admin/editorial actions:

- Approve / reject / request revisions
- Permission/role changes
- Dataset visibility state changes

Touches: Constitution VI, IV

### P1-05 Review Submission Package + Admin Checklist

Define what must be present when a reviewer submits for approval:

- Minimum provenance
- Minimum metadata completeness gates (publish-time, not UI-time)
- Failure modes and “needs revisions” loop

Touches: Constitution VI, IV, I

---

## P2 — Import/Export reliability (interchange product guarantees)

### P2-01 GHFDB Template Import Contract

Define workbook invariants (sheets, headers, required columns) and importer behavior.

Touches: Constitution I, III

### P2-02 Import Error Payload & UX Contract

Specify the required error reporting format:

- sheet/row/column
- expected type/vocab
- actionable remediation hint

Touches: Constitution IV

### P2-03 Controlled Vocabulary & Units Normalization

Define accepted vocabularies and unit handling:

- case-sensitivity
- normalization rules
- what is validated at import vs publish time

Touches: Constitution I, IV

### P2-04 IHFC Export Contract (Flat Spreadsheet Reconstruction)

Define rules for reconstructing the IHFC/Excel “product” from the canonical relational model.

Touches: Constitution I, III

### P2-05 Round-Trip Integrity (Import → Export → Re-Import)

Define acceptance criteria for deterministic mapping and tolerated lossiness.

Touches: Constitution I, III

---

## P2 — Schema mapping transparency (docs + tooling consistency)

### P2-06 Mapping Source of Truth for GHFDB Fields

Specify how [docs/ghfdb_fields.md](../ghfdb_fields.md) is maintained and validated:

- required columns
- update process on schema changes
- who approves mapping changes

Touches: Constitution III

### P2-07 Unmappable/Derived Fields Policy

Specify how derived fields, nullability mismatches, and schema divergences are documented:

- release notes requirements
- mapping table conventions

Touches: Constitution I, III

### P2-08 Accessor Path + ORM Example Standards

Specify a consistent pattern for documenting how users query canonical data corresponding to GHFDB fields.

Touches: Constitution III

---

## P3 — Publication pipeline (open science and DOI releases)

### P3-01 Publication Workflow End-to-End (Portal → Public → DOI Archive)

Specify the full publication pipeline, including artifacts, failure handling, and manual steps.

Touches: Constitution IV, VI

### P3-02 Publish-Time Completeness Gates

Specify what must be present before publication approval:

- provenance completeness
- minimum metadata (abstract, license, contributors)
- identifier requirements (DOI where available, ORCID/ROR where available)

Touches: Constitution I, IV, VI

### P3-03 Post-Publication Immutability & Amendment Workflow

Define what becomes read-only after publication and how corrections/new versions are handled.

Touches: Constitution IV, VI

---

## P3 — Quality scoring (official scheme + practical governance)

### P3-04 Quality Scoring Implementation (U-score, M-score, correction flags)

Specify calculation inputs/outputs, storage, and export mapping.

Touches: Constitution I, IV

### P3-05 Automated Checks vs Manual Overrides

Specify what is automated, what can be overridden, and how overrides are tracked.

Touches: Constitution IV, VI

---

## P4 — API surface (harvesting + permission boundaries)

### P4-01 Public API Harvesting Contract

Specify minimum REST API endpoints and stable field guarantees needed for harvesting.

Touches: Constitution IV

### P4-02 API Authorization Rules

Specify what is public vs authenticated vs reviewer-only vs admin-only.

Touches: Constitution VI, IV

### P4-03 API Versioning & Deprecation Policy

Specify compatibility guarantees and deprecation windows.

Touches: Constitution (Technology Stack & Standards: API versioning)

---

## Optional “workflow hygiene” specs (lower priority)

### P5-01 Reference Document Ingestion & Indexing

Define process and metadata for adding/maintaining governance references under `docs/constitution/references/`.

Touches: Constitution (Governance + documentation expectations)

### P5-02 Testing Strategy for Import/Export + Review Pipelines (Expanded)

Define an expanded suite of integration tests and fixtures once P0-02 exists.

Touches: Constitution (Testing Requirements), IV, VI

