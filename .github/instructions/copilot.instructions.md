# GitHub Copilot Instructions for Global Heat Flow Database Portal

This file provides guidance and context for AI agents (GitHub Copilot, Claude, etc.) working on this codebase.

## Project Overview

The Global Heat Flow Database Portal is a Django-based research data portal built on the FairDM framework. Its internal
data model is canonical and it supports import/export interoperability with the official IHFC GHFDB schema defined by
Fuchs et al. (2021, 2023).

**Key Facts**:
- **Framework**: Django 5.0+ with FairDM ecosystem
- **Language**: Python ≥3.13
- **Governance**: See [.specify/memory/constitution.md](../../.specify/memory/constitution.md) for constitutional principles
- **Funding**: DFG grant 491795283 (WHDB Project)
- **Authority**: International Heat Flow Commission (IHFC-IUGG)

## Constitutional Principles (Non-Negotiable)

When working on this codebase, **all changes MUST comply** with the core principles:

1. **Schema Compatibility**: The portal schema is canonical; the IHFC GHFDB schema is an import/export “product”
2. **FairDM Integration**: Use FairDM components; do not create custom implementations
3. **Schema Transparency**: Document mappings between flat GHFDB spreadsheet and relational database
4. **Open Science & Data Quality**: Maintain FAIR principles, rigorous curation, and DFG compliance
5. **Community Collaboration**: Support user engagement, ORCID integration, and knowledge sharing
6. **Provenance & Review Governance**: Preserve attribution and enforce admin-only publication approval

Read the full constitution before making architectural decisions: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)

## Working with Project Reference Documents

### Available PDF/Excel Documents

Project governance, funding, and schema documents are located in:
- `docs/constitution/references/` - Constitution reference materials (PDFs, Excel templates)

Key documents include:
- DFG funding proposals (Phase 1 & 2)
- WHDB project descriptions and reports
- Conceptual metadata structure specification
- GHFDB data upload templates (Excel)
- Published literature (Fuchs et al. papers)

### How to Read PDF Content for Context

**AI agents cannot directly read PDF files.** To access PDF content:

#### Method 1: Extract and Read Full Content

```bash
# Install dependency (if not already installed - already in dev dependencies)
poetry install

# Extract full content to terminal (for AI to read)
poetry run python scripts/parse_pdf_for_ai.py "docs/constitution/references/WHDB - Project Description.pdf"

# Save to file for later reference
poetry run python scripts/parse_pdf_for_ai.py "docs/constitution/references/filename.pdf" output.md
```

#### Method 2: Get Summary Only

```bash
# Quick metadata summary (pages, word count, tokens)
poetry run python scripts/parse_pdf_for_ai.py "docs/constitution/references/filename.pdf" --summary-only
```

#### Method 3: Extract Specific Pages (using head/tail)

```bash
# Read first 80 lines of extracted content (PowerShell)
poetry run python scripts/parse_pdf_for_ai.py "docs/constitution/references/filename.pdf" | Select-Object -First 80

# Or in bash/Linux
poetry run python scripts/parse_pdf_for_ai.py "docs/constitution/references/filename.pdf" | head -n 80
```

### When to Read Reference Documents

**Before:**
- Writing or updating the constitution
- Making architectural decisions that affect schema design
- Proposing new features that impact core principles
- Documenting governance or compliance requirements

**For:**
- Understanding DFG grant objectives and deliverables
- Verifying GHFDB schema specifications (Fuchs et al.)
- Checking project scope and constraints
- Resolving questions about community requirements

### Workflow Example

```bash
# 1. Check what documents are available
ls docs/constitution/references/

# 2. Get summary to estimate reading time
poetry run python scripts/parse_pdf_for_ai.py "docs/constitution/references/WHDB - Project Description.pdf" --summary-only

# 3. Extract full content for AI analysis
poetry run python scripts/parse_pdf_for_ai.py "docs/constitution/references/WHDB - Project Description.pdf" > /tmp/whdb_project.md

# 4. AI agent reads the markdown file
# [Agent reads /tmp/whdb_project.md]

# 5. Make informed decisions based on document content
```

## Code Architecture Guidelines

### Django Apps Structure

- **heat_flow**: Core GHFDB models (HeatFlowSite, SurfaceHeatFlow, HeatFlow, intervals, measurements)
- **ghfdb**: Global Heat Flow Database proxy models and releases
- **review**: Quality review workflows
- **config**: Django settings and URL routing

### FairDM Integration Patterns

```python
# ✅ CORRECT: Extend FairDM base classes
from fairdm.core.models import Measurement
from fairdm_geo.models.features import Borehole

class HeatFlowSite(Borehole):
    # Add GHFDB-specific fields
    environment = ConceptField(...)

# ✅ CORRECT: Register with FairDM
import fairdm
from fairdm.metadata import ModelConfig

@fairdm.register(HeatFlowSite)
class HeatFlowSiteConfig(ModelConfig):
    description = _("A heat flow site...")
    # Configuration...

# ❌ WRONG: Custom implementation of existing FairDM feature
class CustomDatasetManager:  # Don't do this - use FairDM's Dataset
    pass
```

### Schema Mapping Documentation

When adding/modifying GHFDB fields:

1. Update Django model in `project/heat_flow/models/`
2. Update [docs/ghfdb_fields.md](../../docs/ghfdb_fields.md) mapping table
3. Include reference to Fuchs et al. section in docstring
4. Add migration with descriptive comment

## Development Workflow

### Running the Portal Locally

```bash
# Install dependencies
poetry install

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Testing

```bash
# Run test suite
poetry run pytest

# Run specific test file
poetry run pytest tests/test_heat_flow/test_models.py

# Check code style
poetry run ruff check .
```

### Before Committing

- [ ] All tests pass
- [ ] Code formatted with Ruff
- [ ] Constitution compliance verified (check core principles)
- [ ] [docs/ghfdb_fields.md](../../docs/ghfdb_fields.md) updated if schema changed
- [ ] Docstrings reference Fuchs et al. where applicable

## Common AI Agent Tasks

### Task: Understand GHFDB Schema

```bash
# Read the official mapping documentation
cat docs/ghfdb_fields.md

# Extract conceptual schema PDF
poetry run python scripts/parse_pdf_for_ai.py "docs/constitution/references/Conceptual Metadata structure.pdf"

# Review Django models
ls project/heat_flow/models/
```

### Task: Verify DFG Grant Compliance

```bash
# Extract project description
poetry run python scripts/parse_pdf_for_ai.py "docs/constitution/references/WHDB - Project Description.pdf" > /tmp/dfg_project.md

# Check against constitution requirements
grep -i "DFG\|funding\|grant" .specify/memory/constitution.md
```

### Task: Implement New Feature

1. **Read constitution**: Check principles alignment
2. **Check GHFDB schema**: Does Fuchs et al. define this?
3. **Search FairDM docs**: Is there existing functionality?
4. **Create spec**: Use SpecKit workflow (`/speckit.plan`)
5. **Implement**: Follow Django/FairDM patterns
6. **Test**: Write integration tests
7. **Document**: Update schema mapping if needed

## Resources

- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
- **Schema Mapping**: [docs/ghfdb_fields.md](../../docs/ghfdb_fields.md)
- **Features**: [docs/features.md](../../docs/features.md)
- **About**: [docs/about.md](../../docs/about.md)
- **Contributing**: [CONTRIBUTING.md](../../CONTRIBUTING.md)
- **Project Site**: [portal.heatflow.world](https://portal.heatflow.world)
- **IHFC**: [ihfc-iugg.org](https://ihfc-iugg.org)

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/ihfc-iugg/ghfdb-portal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ihfc-iugg/ghfdb-portal/discussions)
- **Maintainers**: World Heat Flow Database Project team
