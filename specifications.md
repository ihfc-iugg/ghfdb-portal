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

1. Pick one item (preferably a P0/P1 item).

2. Use the item’s description below as the plain-language declaration of what the spec must cover.

3. Keep specs “executable”:

   - User scenarios + acceptance criteria
   - Requirements that are independently testable
   - Explicit constraints and out-of-scope
   - References to the constitution + relevant docs

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

#### What this spec should cover (P0-01)

This spec defines the project’s documentation system: where docs live, how they’re written, and how they’re kept accurate.

It should cover:

- The intended Sphinx information architecture (what belongs in user guides vs developer docs vs governance docs).
- Where governance materials live (constitution + references) and how they are cross-linked.
- The “feature docs checklist”: what docs must be updated when a feature ships.
- How specs are referenced from docs (so a reader can trace behavior back to a spec).
- What “docs are valid” means (build steps, link checks, failure conditions, and minimum expectations).
- Any migration/conformance work needed to bring existing docs into the conventions.

### P0-02 Testing Infrastructure & Conventions

Define the testing strategy and minimum fixtures required to make specs enforceable.

Scope should include:

- Test layers (unit/integration/contract) and where they live under `tests/`
- Minimal fixture datasets for: import, review submission, admin approval, export
- CI expectations (what runs on PR, what runs nightly) and coverage goals (if any)
- How to write tests for schema mapping and round-trip integrity

Touches: Constitution IV, VI, Testing Requirements

#### What this spec should cover (P0-02)

This spec defines the project’s testing “contract”: where tests go, what kinds of tests exist, and what fixtures are required to validate specs end-to-end.

It should cover:

- Test layers (unit/integration/contract), what each is for, and where each lives under `tests/`.
- The minimum fixture datasets needed to test the core lifecycle: import → review submission → admin approval → export.
- The standard way to write tests for schema mapping and round-trip integrity.
- CI expectations: which tests must run for PRs, and what is optional/extended.
- Naming conventions, structure conventions, and what assertions are required for each test category.
- Constraints on fixtures (small, versioned, reproducible; no unnecessary external dependencies).

---

## P1 — Foundation (review + provenance + permission boundaries)

### P1-01 Dual Review Workflows (Curation vs Publication Approval)

Define states, transitions, and invariants for:

- Literature assessment review (reviewer-driven curation)
- Publication approval review (admin-only gating)

Touches: Constitution VI, IV

#### What this spec should cover (P1-01)

- Two separate workflows (curation vs publication approval), each with named states and allowed transitions.
- Who can do what: required roles/permissions for each transition.
- What’s required to move forward (required data completeness, required artifacts).
- What happens on rejection / revision request (the full revision loop).
- Hard invariants (e.g., no path where a curator can approve publication).
- Audit requirements for transitions (what must be recorded).
- Minimum acceptance tests proving transitions and permission boundaries.

### P1-02 Provenance & Attribution Model (Authors vs Curators vs Editors)

Define canonical storage of:

- Original publication metadata (DOI, citation)
- Original scientific authors
- Portal contributors (reviewers/curators)
- Editorial approvers (admin actions + timestamps)

Touches: Constitution VI, I

#### What this spec should cover (P1-02)

- A clear definition of each attribution category: original scientific authors, portal curators/reviewers, and editorial approvers.
- The canonical data model/relationships that store provenance and attribution.
- What must be present at publish-time (minimum provenance + attribution completeness).
- What is shown publicly vs kept internal (if anything), and how exports represent attribution.
- How identifiers (DOI, ORCID, ROR) are stored and used when present.
- Migration/backfill expectations for existing records.

### P1-03 Role Hierarchy & Permission Matrix

Specify roles and permissions (minimum set) such that:

- Review/curation permissions do not imply publish/approve permissions
- Publication approval is restricted to a designated admin role
- Role assignment is tightly controlled

Touches: Constitution VI

#### What this spec should cover (P1-03)

- A minimal set of roles (names and responsibilities) and how they map to capabilities.
- A permission matrix that explicitly separates review/curation, publication approval, and role management capabilities.
- Rules for role assignment: who can grant/revoke which roles.
- Expected behavior when permission is missing (clear “unauthorized vs forbidden” semantics).
- Audit requirements for role changes.
- Minimum authorization tests for the most sensitive actions.

### P1-04 Audit Trail for Editorial Actions

Specify what events must be logged for admin/editorial actions:

- Approve / reject / request revisions
- Permission/role changes
- Dataset visibility state changes

Touches: Constitution VI, IV

#### What this spec should cover (P1-04)

- Which actions must always be audited (approvals/rejections/revision requests, role changes, visibility changes).
- The audit record schema (who/what/when/which object, and before/after values when relevant).
- Immutability expectations (audit events cannot be edited/deleted silently).
- Retention and access control rules (who can view audit history).
- Minimum query/display needs (what admins need to see to reconstruct history).
- Tests to prove audit events are created and queryable.

### P1-05 Review Submission Package + Admin Checklist

Define what must be present when a reviewer submits for approval:

- Minimum provenance
- Minimum metadata completeness gates (publish-time, not UI-time)
- Failure modes and “needs revisions” loop

Touches: Constitution VI, IV, I

#### What this spec should cover (P1-05)

- A precise definition of the “submission package” (required fields, relationships, and attached artifacts).
- Publish-time gates: what must be complete before an approval attempt is allowed.
- Admin review checklist: what must be verified and what evidence is expected.
- Failure modes: clear reasons for rejection vs “needs revisions”.
- Revision loop behavior: how resubmission works and what resets/doesn’t reset.
- Minimum tests for missing fields/artifacts and for the revision loop.

---

## P2 — Import/Export reliability (interchange product guarantees)

### P2-01 GHFDB Template Import Contract

Define workbook invariants (sheets, headers, required columns) and importer behavior.

Touches: Constitution I, III

#### What this spec should cover (P2-01)

- The workbook contract: required sheets, required headers, required columns, and allowed optional columns.
- Column-level expectations (types, formats, allowed blanks).
- How template versioning is handled (how to detect a version and what to do if it’s unknown).
- The importer’s mapping rules from workbook fields into the canonical relational model.
- Validation behavior: what is a hard error vs a warning.
- Minimum fixtures needed to test success and the most common failures.

### P2-02 Import Error Payload & UX Contract

Specify the required error reporting format:

- sheet/row/column
- expected type/vocab
- actionable remediation hint

Touches: Constitution IV

#### What this spec should cover (P2-02)

- A standard import error structure that always includes sheet/row/column.
- How “expected value” is represented (expected type, expected vocabulary, allowed range).
- A required remediation hint format (so messages are actionable, not just descriptive).
- Grouping rules and error limits (how many errors to show/return).
- UX/API expectations at a contract level (how errors are delivered to the user).
- Tests that assert error shape and key messaging for common failures.

### P2-03 Controlled Vocabulary & Units Normalization

Define accepted vocabularies and unit handling:

- case-sensitivity
- normalization rules
- what is validated at import vs publish time

Touches: Constitution I, IV

#### What this spec should cover (P2-03)

- The controlled vocabularies that apply (canonical values + any permitted aliases).
- Normalization rules (case, whitespace, formatting) and when normalization occurs.
- Unit rules: accepted units per field, conversion behavior, and canonical storage units.
- What is validated at import time vs publish time.
- Error behavior for invalid vocabulary and unit values.
- Tests for normalization and unit conversion edge cases.

### P2-04 IHFC Export Contract (Flat Spreadsheet Reconstruction)

Define rules for reconstructing the IHFC/Excel “product” from the canonical relational model.

Touches: Constitution I, III

#### What this spec should cover (P2-04)

- The export spreadsheet schema (sheets, headers, column order, types).
- How the relational model is flattened into rows (join/repetition rules).
- Determinism requirements (stable ordering and formatting for a given dataset snapshot).
- How nulls and derived fields appear in the export.
- Validation rules for the exported artifact.
- Minimum fixtures/tests proving export matches the contract.

### P2-05 Round-Trip Integrity (Import → Export → Re-Import)

Define acceptance criteria for deterministic mapping and tolerated lossiness.

Touches: Constitution I, III

#### What this spec should cover (P2-05)

- The round-trip definition: import → export → re-import and what “equivalent” means.
- What must be preserved exactly vs what may change (explicit tolerated lossiness).
- Comparison rules (how to compare rows/entities in a deterministic way).
- Required fixtures for a realistic round-trip test.
- Acceptance criteria that can be automated in integration tests.

---

## P2 — Schema mapping transparency (docs + tooling consistency)

### P2-06 Mapping Source of Truth for GHFDB Fields

Specify how [docs/ghfdb_fields.md](../ghfdb_fields.md) is maintained and validated:

- required columns
- update process on schema changes
- who approves mapping changes

Touches: Constitution III

#### What this spec should cover (P2-06)

- What the mapping doc must contain (required columns/sections and conventions).
- Who owns mapping changes and what the approval process is.
- How mapping changes are validated for completeness/consistency.
- How mapping changes are coordinated with schema changes.
- Minimum checks that prevent mapping drift.

### P2-07 Unmappable/Derived Fields Policy

Specify how derived fields, nullability mismatches, and schema divergences are documented:

- release notes requirements
- mapping table conventions

Touches: Constitution I, III

#### What this spec should cover (P2-07)

- A consistent way to document derived fields and non-1:1 mappings.
- How nullability/type mismatches are represented in documentation.
- When divergence is acceptable vs when it must be rejected.
- Release note requirements whenever mapping behavior changes.
- A minimal validation/checklist to ensure policy compliance.

### P2-08 Accessor Path + ORM Example Standards

Specify a consistent pattern for documenting how users query canonical data corresponding to GHFDB fields.

Touches: Constitution III

#### What this spec should cover (P2-08)

- A standard “accessor path” format for each GHFDB field (what canonical object/relationship holds it).
- How joins/relationships are described in docs (naming and conventions).
- Standards for ORM/query examples (minimal, correct, and performance-aware).
- How accessor docs stay in sync with the mapping source of truth.

---

## P3 — Publication pipeline (open science and DOI releases)

### P3-01 Publication Workflow End-to-End (Portal → Public → DOI Archive)

Specify the full publication pipeline, including artifacts, failure handling, and manual steps.

Touches: Constitution IV, VI

#### What this spec should cover (P3-01)

- The end-to-end publication pipeline from portal state to public release.
- The artifacts produced (exports, metadata records, archives) and their required contents.
- Which steps are automated vs manual, and who performs manual steps.
- Failure modes and recovery expectations (retry/rollback/idempotency where relevant).
- Audit requirements for publication actions.

### P3-02 Publish-Time Completeness Gates

Specify what must be present before publication approval:

- provenance completeness
- minimum metadata (abstract, license, contributors)
- identifier requirements (DOI where available, ORCID/ROR where available)

Touches: Constitution I, IV, VI

#### What this spec should cover (P3-02)

- The exact publish-time checklist (required provenance, metadata, contributors, identifiers).
- Which items are required vs recommended.
- Validation rules and error messaging expectations.
- Tests proving approval cannot proceed when required items are missing.

### P3-03 Post-Publication Immutability & Amendment Workflow

Define what becomes read-only after publication and how corrections/new versions are handled.

Touches: Constitution IV, VI

#### What this spec should cover (P3-03)

- What becomes read-only after publication (and what remains editable, if anything).
- How corrections are made (new version vs amendment; lineage and visibility rules).
- How public artifacts (exports/archives/DOIs) are updated or superseded.
- Audit requirements for amendments.
- Tests preventing silent post-publication mutation.

---

## P3 — Quality scoring (official scheme + practical governance)

### P3-04 Quality Scoring Implementation (U-score, M-score, correction flags)

Specify calculation inputs/outputs, storage, and export mapping.

Touches: Constitution I, IV

#### What this spec should cover (P3-04)

- Definitions for each score/flag and the required inputs.
- Calculation rules (or authoritative references) and determinism requirements.
- How scores are stored and how they map to exports.
- How correction flags are represented.
- Tests for known inputs producing known outputs.

### P3-05 Automated Checks vs Manual Overrides

Specify what is automated, what can be overridden, and how overrides are tracked.

Touches: Constitution IV, VI

#### What this spec should cover (P3-05)

- Which validations are automated and which require human judgement.
- Which checks are hard gates vs warnings.
- Override rules: who can override, what must be recorded, and what must be audited.
- How override rationale is captured and displayed.
- Tests proving overrides are permissioned and recorded.

---

## P4 — API surface (harvesting + permission boundaries)

### P4-01 Public API Harvesting Contract

Specify minimum REST API endpoints and stable field guarantees needed for harvesting.

Touches: Constitution IV

#### What this spec should cover (P4-01)

- The minimum set of REST resources/endpoints needed for harvesting.
- Request/response shapes for those endpoints, including pagination conventions.
- Field-level stability guarantees (what is stable vs allowed to change).
- Error response conventions (status codes and response shape).

### P4-02 API Authorization Rules

Specify what is public vs authenticated vs reviewer-only vs admin-only.

Touches: Constitution VI, IV

#### What this spec should cover (P4-02)

- Role/permission model for API access (public, authenticated, reviewer, admin).
- Authorization rules per endpoint/resource (including read vs write).
- Authentication mechanism expectations (session/token) if applicable.
- Standard responses for unauthorized vs forbidden.
- Minimum tests proving permission boundaries.

### P4-03 API Versioning & Deprecation Policy

Specify compatibility guarantees and deprecation windows.

Touches: Constitution (Technology Stack & Standards: API versioning)

#### What this spec should cover (P4-03)

- The chosen versioning mechanism (one approach, consistently applied).
- Backward-compatibility guarantees and what counts as breaking.
- Deprecation policy: how changes are announced and timelines.
- How clients discover supported versions and deprecation status.
- Minimum tests/checks ensuring the policy is followed.

---

## Optional “workflow hygiene” specs (lower priority)

### P5-01 Reference Document Ingestion & Indexing

Define process and metadata for adding/maintaining governance references under `docs/constitution/references/`.

Touches: Constitution (Governance + documentation expectations)

#### What this spec should cover (P5-01)

- Required metadata for each governance reference (title, source, date, canonical link, summary).
- How references are added/updated, and who owns review/approval (if any).
- Where references live under docs and how they're organized.
- Indexing and cross-linking expectations so references are discoverable.
- How to handle superseded/invalid references without breaking links.

### P5-02 Testing Strategy for Import/Export + Review Pipelines (Expanded)

Define an expanded suite of integration tests and fixtures once P0-02 exists.

Touches: Constitution (Testing Requirements), IV, VI

#### What this spec should cover (P5-02)

- A prioritized list of additional integration tests beyond the minimal happy path.
- Edge-case fixture coverage (partial data, conflicting vocab, multi-source joins).
- Performance/CI constraints (target runtimes, what runs on PR vs nightly).
- How to incrementally implement and maintain this suite.


