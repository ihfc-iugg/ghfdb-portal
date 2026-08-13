# Governance & Constitution

This section contains the governance framework and constitutional principles for the Global Heat Flow Database Portal project.

## Project Constitution

The project constitution defines the core principles, constraints, and governance rules that guide development of the portal.

:::{seealso}
**Canonical Constitution**: [memory/constitution.md](../../memory/constitution.md)

The constitution is maintained at `memory/constitution.md` as the single source of truth for project governance.
:::

### Core Principles

The constitution establishes seven foundational principles:

1. **Fidelity to DFG Funding & WHDB Mission**
2. **Conceptual Schema Compliance**
3. **Interchange Compatibility**
4. **Open Science & Data Quality**
5. **Simplicity & Maintainability**
6. **Provenance, Attribution & Review Governance**
7. **Spec-Driven Development**

For the complete text with detailed explanations and constraints, see the [canonical constitution](../../memory/constitution.md).

## Reference Documents

Supporting documentation that informs the constitution is maintained in the [references/](references/README) directory.

:::{toctree}
:maxdepth: 1

references/README
:::

These documents include:

- DFG funding proposals and project reports
- GHFDB conceptual metadata specifications
- Published literature on the database schema
- Data upload templates and quality schemes

## Governance Process

All feature development follows a spec-driven workflow aligned with constitutional principles:

1. **Specification**: Features are documented in `specs/` following the constitution
2. **Planning**: Implementation plans are validated against governance constraints
3. **Implementation**: Code changes must satisfy constitutional requirements
4. **Review**: Changes are reviewed for alignment with principles

For details on the spec-driven workflow, see the [Documentation Conventions](../development/documentation-conventions).
