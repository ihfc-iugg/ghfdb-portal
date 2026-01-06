# Feature Documentation Checklist

This checklist defines the documentation updates expected when a feature changes user-facing behavior. Use it to ensure complete documentation coverage for new features and feature updates.

## When to Use This Checklist

Apply this checklist when:

- A feature adds or changes user-facing functionality (UI, workflows, API endpoints)
- A feature introduces new concepts, entities, or domain terminology
- A feature changes existing workflows or requires user action

Skip this checklist for:

- Internal refactoring with no user-visible changes
- Bug fixes that restore existing documented behavior
- Infrastructure changes (CI, build system) with no user impact

## Required Documentation Updates

### 1. User-Facing Documentation

For features that affect portal users (data contributors, reviewers, or readers):

- [ ] **Guide or tutorial**: Create or update a guide in `docs/guides/` explaining how to use the feature
- [ ] **Screenshots or diagrams**: Add visual aids if the feature involves UI changes
- [ ] **Navigation**: Link the new guide from `docs/index.md` or a relevant section index
- [ ] **Cross-references**: Update related guides that reference affected workflows

### 2. Developer Documentation

For features that affect developers or maintainers:

- [ ] **API documentation**: Document new models, services, or endpoints in `docs/development/`
- [ ] **Configuration**: Document new settings or environment variables
- [ ] **Development workflow**: Update contributing guides if the feature changes dev processes
- [ ] **Architecture notes**: Add to `docs/development/` if the feature introduces significant architectural changes

### 3. Governance & Constitutional Alignment

For features that relate to project governance or constitutional principles:

- [ ] **Constitution reference**: Cite relevant constitutional principles in the feature specification
- [ ] **Policy updates**: Update governance docs if the feature changes policies or review processes
- [ ] **Reference materials**: Link to relevant documents in `docs/constitution/references/`

### 4. Spec-Driven Workflow Artifacts

All features following the spec-driven workflow:

- [ ] **Specification**: Complete `specs/[###-feature]/spec.md` with user stories and requirements
- [ ] **Implementation plan**: Complete `specs/[###-feature]/plan.md` with technical approach
- [ ] **Task breakdown**: Complete `specs/[###-feature]/tasks.md` with implementation checklist
- [ ] **Feature branch**: Create and use a feature branch named after the feature ID

### 5. Data Models & Concepts

For features that introduce new entities or domain concepts:

- [ ] **Data model documentation**: Add or update `docs/data_models/` with entity descriptions
- [ ] **Field documentation**: Update `docs/ghfdb_fields.md` if the feature adds or changes database fields
- [ ] **Conceptual explanations**: Add conceptual overviews to help users understand new terminology

## Validation

Before merging a feature PR:

1. **Review this checklist**: Confirm all applicable items are complete
2. **Run documentation build**: Ensure `sphinx-build -b html -W --keep-going` passes
3. **Run linkcheck**: Ensure `sphinx-build -b linkcheck -W --keep-going` passes
4. **Test navigation**: Verify new documentation is discoverable from `docs/index.md`

## Example Application

### Example: Adding a "Data Export" Feature

A new feature allows users to export heat flow data in multiple formats.

**User-Facing Documentation**:

- ✅ Create `docs/guides/exporting-data.md` with step-by-step instructions
- ✅ Add screenshots showing the export UI
- ✅ Link from `docs/index.md` under "Guides" section
- ✅ Update `docs/guides/map_exploration/index.md` to mention export option

**Developer Documentation**:

- ✅ Document export formats and API endpoints in `docs/development/api.md`
- ✅ Add configuration options for export limits to `docs/development/configuration.md`

**Governance & Constitutional Alignment**:

- ✅ Reference Principle III (Interchange Compatibility) in `specs/042-data-export/spec.md`

**Spec-Driven Workflow Artifacts**:

- ✅ Complete `specs/042-data-export/spec.md` with user stories
- ✅ Complete `specs/042-data-export/plan.md` with technical design
- ✅ Complete `specs/042-data-export/tasks.md` with implementation tasks
- ✅ Create feature branch `042-data-export`

**Data Models & Concepts**:

- ✅ Update `docs/data_models/index.md` to explain export format mappings
- ✅ Update `docs/ghfdb_fields.md` if export adds metadata fields

## Tips for Efficient Documentation

- **Write docs early**: Draft user guides during spec/plan phase to validate UX clarity
- **Use templates**: Copy existing guides as starting points for similar features
- **Test with fresh eyes**: Ask a colleague unfamiliar with the feature to try following the guide
- **Keep it concise**: Focus on the "what" and "how"; link to specs for the "why"

## See Also

- [Documentation Conventions](./documentation-conventions.md) - File placement and authoring format
- [Contributing to Documentation](./contributing/contributing_docs.md) - Build instructions and quality guidelines
- [Constitution](../../constitution/index.md) - Governance principles guiding feature development
