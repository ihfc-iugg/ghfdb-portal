# Spec-Driven Development Workflow

This document describes the spec-driven development workflow used for feature development in this project. The workflow emphasizes planning, documentation, and constitutional alignment before implementation.

## Overview

The spec-driven workflow breaks feature development into discrete phases, each producing specific artifacts that guide implementation and facilitate review. This approach ensures features are well-planned, aligned with project governance, and properly documented before code is written.

## Workflow Phases

### Phase 0: Specification

Create a feature specification that defines the problem, user stories, requirements, and success criteria.

**Artifact**: `specs/[###-feature]/spec.md`

**Contents**:

- Feature ID and branch name
- User stories with priorities (P1, P2, P3, etc.)
- Functional requirements (FR-###)
- Success criteria (SC-###)
- Edge cases and assumptions

**Example**:

```text
specs/001-docs-infrastructure/spec.md
- User Story 1: Follow documentation conventions (Priority: P1)
- FR-001: Documentation MUST define audiences
- SC-001: Contributors can find placement in under 2 minutes
```

**Constitutional Alignment**: Specifications must reference relevant constitutional principles (see [Constitution](../../constitution/index.md)).

### Phase 1: Planning

Create an implementation plan that translates requirements into technical decisions and design.

**Artifact**: `specs/[###-feature]/plan.md`

**Contents**:

- Technical approach and architecture
- Technology stack and libraries
- Project structure (file organization)
- Phase breakdown (phases 0-6)
- Dependencies and external documentation

**Example**:

```text
specs/001-docs-infrastructure/plan.md
- Tech stack: Sphinx + sphinx-book-theme + MyST Markdown
- Phase 1: Setup and configuration
- Phase 2: Documentation conventions
- Phase 3: CI validation
```

**Supporting Artifacts** (created alongside plan.md):

- `research.md`: Technical research and decisions
- `data-model.md`: Entity definitions and relationships (if applicable)
- `contracts/`: API specifications or test requirements (if applicable)
- `quickstart.md`: Integration scenarios (if applicable)

### Phase 2: Task Breakdown

Break the implementation plan into concrete, actionable tasks organized by user story.

**Artifact**: `specs/[###-feature]/tasks.md`

**Contents**:

- Task list with IDs (T001, T002, etc.)
- Phase organization (Setup, Foundational, User Story 1, User Story 2, etc., Polish)
- Parallel execution markers [P] for independent tasks
- File paths and specific implementation details
- Dependencies and execution order

**Example**:

```text
specs/001-docs-infrastructure/tasks.md
- T001: Audit existing documentation structure
- T006 [P] [US1]: Create documentation-conventions.md
- T011 [P] [US2]: Create .github/workflows/docs-validation.yml
```

**Task Format**: `[ID] [P?] [Story] Description`

- `[P]`: Optional parallel execution marker
- `[Story]`: User story tag (US1, US2, etc.)

### Phase 3: Implementation

Execute tasks in phase order, marking each task complete as you finish it.

**Artifacts**:

- Code changes in feature branch
- Updated tasks.md with completed checkboxes

**Process**:

1. Create feature branch: `git checkout -b [###-feature]`
2. Implement tasks phase by phase
3. Mark completed tasks: `- [X] T001 ...`
4. Run validation after each phase
5. Commit regularly with descriptive messages

**Validation**:

- Run tests: `pytest`
- Run linting: `ruff check .`
- Run docs build: `sphinx-build -b html -W --keep-going`
- Run linkcheck: `sphinx-build -b linkcheck -W --keep-going`

### Phase 4: Review & Merge

Submit a pull request for review and address feedback.

**PR Requirements**:

- [ ] All tasks marked complete in tasks.md
- [ ] Tests pass
- [ ] Documentation updated (see [Feature Documentation Checklist](./feature-documentation-checklist.md))
- [ ] Constitutional alignment verified
- [ ] Success criteria validated

**Review Focus**:

- Alignment with specification requirements
- Code quality and maintainability
- Documentation completeness
- Test coverage

## Relationship Between Artifacts

```text
spec.md
  ↓
  defines user stories, requirements, success criteria
  ↓
plan.md
  ↓
  translates requirements into technical approach
  ↓
tasks.md
  ↓
  breaks plan into actionable implementation steps
  ↓
feature branch
  ↓
  implements tasks and validates against spec
```

## Benefits of Spec-Driven Development

1. **Clear Requirements**: Specifications prevent scope creep and ensure alignment with project goals
2. **Constitutional Compliance**: Planning phase validates features against governance principles
3. **Reduced Rework**: Detailed planning catches issues before implementation
4. **Better Reviews**: Reviewers can check implementations against documented plans
5. **Improved Onboarding**: New contributors can understand features by reading specs first
6. **Traceable Decisions**: Technical decisions are documented and justified

## Example: Documentation Infrastructure Feature

Let's trace a real example through the workflow:

### 1. Specification (spec.md)

```markdown
# Feature Specification: Documentation Infrastructure & Conventions

**User Story 1**: As a contributor, I want clear documentation conventions
**FR-001**: Documentation MUST define audiences
**SC-001**: Contributors can find placement in under 2 minutes
```

### 2. Planning (plan.md)

```markdown
# Implementation Plan: Documentation Infrastructure

**Tech Stack**: Sphinx + sphinx-book-theme + MyST Markdown
**Phase Breakdown**:
- Phase 1: Setup (audit existing structure)
- Phase 2: Conventions (create conventions guide)
- Phase 3: CI Validation (automated quality gates)
```

### 3. Task Breakdown (tasks.md)

```markdown
# Tasks: Documentation Infrastructure

- [ ] T001: Audit existing documentation structure
- [ ] T006 [P] [US1]: Create documentation-conventions.md
- [ ] T011 [P] [US2]: Create .github/workflows/docs-validation.yml
```

### 4. Implementation

```bash
git checkout -b 001-docs-infrastructure
# Implement T001, T006, T011...
# Mark tasks complete in tasks.md
git commit -m "feat(docs): add documentation conventions and CI validation"
```

### 5. Review & Merge

Submit PR with:

- Completed tasks.md
- New documentation files
- GitHub Actions workflow
- Updated contributing guide

## Tips for Effective Spec-Driven Development

- **Start Small**: Begin with a minimal specification and expand as needed
- **Iterate**: Refine specs based on feedback before implementation
- **Be Specific**: Include concrete examples and file paths in plans and tasks
- **Validate Early**: Run validation steps after completing each phase
- **Document Decisions**: Capture "why" in research.md or plan.md comments
- **Stay Aligned**: Regularly check implementation against spec requirements

## See Also

- [Feature Documentation Checklist](./feature-documentation-checklist.md) - Documentation requirements for features
- [Documentation Conventions](./documentation-conventions.md) - File placement and authoring format
- [Constitution](../../constitution/index.md) - Governance principles guiding development
- [Contributing Guide](./contributing/index.md) - General contribution guidelines
