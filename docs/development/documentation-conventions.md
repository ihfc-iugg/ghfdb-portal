# Documentation Conventions

This page defines the conventions for authoring, organizing, and maintaining documentation in the Global Heat Flow Database portal repository.

## Audiences

Documentation is written for two primary audiences:

### End Users

Portal users, data contributors, and researchers who use the portal to explore, contribute, or publish heat flow data.

- **Location**: `docs/guides/`
- **Examples**: Importing data, reviewing datasets, exploring the map interface
- **Style**: Task-oriented, assumes no technical background

### Developers and Maintainers

Contributors to the codebase, including developers extending the portal, system administrators, and documentation maintainers.

- **Location**: `docs/development/`
- **Examples**: Contributing guidelines, API documentation, development workflows
- **Style**: Technical, assumes familiarity with software development concepts

### Governance

Project governance material defining principles, roles, and responsibilities.

- **Location**: `docs/constitution/` and `memory/constitution.md`
- **Examples**: Constitution, licensing, data policies
- **Style**: Clear, authoritative, policy-oriented

## File Placement Rules

### Where to place new documentation

Follow these conventions when creating new documentation:

| Document Type | Directory | Examples |
| --- | --- | --- |
| User guides and tutorials | `docs/guides/` | How to import data, how to review datasets |
| Developer documentation | `docs/development/` | Contributing guidelines, API docs, workflows |
| Governance and policy | `docs/constitution/` | Constitution references, policy documents |
| Data models and schemas | `docs/data_models/` | Entity relationships, field mappings |
| Project information | `docs/` (root) | About, features, acknowledgements |

### Naming conventions

- Use lowercase with hyphens for file names: `importing-data.md`, not `Importing_Data.md`
- Use descriptive names that match the page title
- Prefer Markdown (`.md`) for authored content
- Use subdirectories for related pages that form a section

## Linking and Navigation

### Adding pages to the table of contents

All documentation pages must be added to a `toctree` directive to appear in navigation. The main toctree is in `docs/index.md`.

**Example**: Adding a new user guide:

```markdown
:::{toctree}
:maxdepth: 1
:caption: Guides

guides/map_exploration/index
guides/importing-data
guides/reviewing
guides/publishing
guides/your-new-guide
:::
```

### Internal links

Use relative paths for internal documentation links:

```markdown
See the [Contributing](development/contributing/index.md) page for more information.
```

### Cross-references

For more complex references, use MyST cross-reference syntax:

```markdown
{ref}`section-label`
```

## Authoring Format

### Markdown (MyST)

Documentation is authored in **MyST Markdown** (Markedly Structured Text), a flavor of Markdown that supports Sphinx directives.

**Supported features**:

- Standard Markdown syntax (headings, lists, links, images, code blocks)
- MyST directives: `:::` fence notation for Sphinx directives
- Sphinx roles for cross-references and inline markup

**Example**:

```markdown
## Section Title

This is a paragraph with a [link](other-page.md).

:::{note}
This is a note admonition.
:::
```

### Sphinx Design Components

The repository uses **sphinx-design** for layout components. Common components include:

- **Cards**: `{card}` directive for highlighted content boxes
- **Grids**: `{grid}` and `{grid-item}` for multi-column layouts
- **Tabs**: `{tab-set}` and `{tab-item}` for tabbed content
- **Dropdowns**: `{dropdown}` for collapsible sections

**Example**:

```markdown
:::{card} Card Title
Card content goes here.
:::
```

Refer to the [sphinx-design documentation](https://sphinx-design.readthedocs.io/) for full details.

## Updating Documentation

### When to update documentation

Documentation updates are expected when:

1. **User-facing behavior changes**: Any feature that affects how users interact with the portal
2. **New features are added**: New guides, workflows, or capabilities
3. **APIs change**: New endpoints, changed parameters, or deprecated features
4. **Governance changes**: Updates to policies, roles, or responsibilities

See the [Feature Documentation Checklist](feature-documentation-checklist.md) for a detailed list of required updates.

### Documentation review process

All documentation changes follow the same review process as code:

1. Create a feature branch
2. Make documentation changes
4. Submit a pull request
5. CI validation will check for broken links and build errors
6. Reviewer approval required before merge

## Validation and Quality

Documentation quality is enforced through automated checks:

- **Build warnings treated as errors**: Any Sphinx warning will fail the build
- **Link checking**: Internal and external links are validated
- **Markup validation**: Malformed MyST/Markdown is rejected

Run validation locally before pushing:

```bash
poetry run sphinx-build -b html docs docs/_build/html -W --keep-going
poetry run sphinx-build -b linkcheck docs docs/_build/linkcheck -W --keep-going
```

## Getting Help

- **Sphinx documentation**: <https://www.sphinx-doc.org/>
- **MyST Markdown guide**: <https://myst-parser.readthedocs.io/>
- **sphinx-design components**: <https://sphinx-design.readthedocs.io/>
- **Questions**: Open an issue on the GitHub repository
