# Constitution Reference Documents

This directory stores source documents that informed the Global Heat Flow Database Portal constitution, including funding proposals, published literature, and project governance materials.

## Purpose

These documents provide context for the constitutional principles and governance structure defined in [memory/constitution.md](../../../memory/constitution.md). They are kept alongside the rest of the documentation to:

- Maintain version control for large PDFs and Excel files
- Provide a stable, referenceable archive for project stakeholders

## Current Documents

The following documents from `docs/documents/` are directly referenced by the constitution:

### DFG Funding & Project Scope

- **WHDB - Project Description.pdf**: Original DFG grant proposal defining project scope and objectives
- **Heatflow.world - World Heat Flow Database project (Phase One).pdf**: Phase 1 project overview and deliverables
- **Heatflow.world - World Heat Flow Portal (Phase Two).pdf**: Phase 2 expansion including portal development
- **WHDB Phase 1 report_005_final.pdf**: Final report from Phase 1 activities

### GHFDB Conceptual Schema

- **Conceptual Metadata structure.pdf**: Detailed specification of the GHFDB conceptual metadata model
- **data_upload_template.xlsx**: Official GHFDB Excel template structure for user data uploads

### Published Literature

See `docs/documents/publications/` for peer-reviewed papers that define the GHFDB schema:

- Fuchs et al. (2021): *A new database structure for the IHFC Global Heat Flow Database*
- Fuchs et al. (2023): *The Global Heat Flow Database: Update 2023*

## Usage

When drafting specifications or making architectural decisions, reference these documents to ensure alignment with:

1. **DFG funding mandate** - Scope, deliverables, and open science requirements
2. **GHFDB interchange compatibility** - Export/publishing structure per Fuchs et al. publications
3. **Community needs** - User workflows and data collection practices

For a comprehensive overview of the WHDB project based on these reference documents, see [docs/whdb_project.md](../../whdb_project.md), which provides detailed documentation on the research data infrastructure, metadata standards, data publishing services, and institutional partnerships.

## Linking from Constitution

From [memory/constitution.md](../../../memory/constitution.md), reference these documents using relative Markdown links:

```markdown
See the [DFG Project Description](../../../docs/constitution/references/WHDB%20-%20Project%20Description.pdf) for funding objectives.
```

## Future Documents

As the project evolves, add new reference materials here:

- Governance decisions and meeting minutes
- Schema revision proposals (extensions to Fuchs et al.)
- Stakeholder agreements (IHFC, GFZ, partner institutions)
- Community consultation summaries (from GitHub discussions/polls)

## Notes

- Keep file names descriptive and avoid special characters (use underscores or hyphens)
- For private/sensitive documents (unpublished drafts, internal memos), store them in a secure location and reference by title only
- Update this README when adding new documents to maintain a clear index

