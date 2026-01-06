# Documentation

## Overview

This project maintains comprehensive documentation for both users and developers. Documentation is written in MyST Markdown and built using Sphinx.

## Documentation Conventions

Please review the [Documentation Conventions](../documentation-conventions.md) guide for detailed information on:

- Where to place new documentation (user guides vs developer docs)
- How to add pages to the table of contents
- Authoring format and supported features
- When documentation updates are required

For features that change user-facing behavior, use the [Feature Documentation Checklist](../feature-documentation-checklist.md) to ensure complete documentation coverage.

## Building Documentation Locally

Install documentation dependencies:

```bash
poetry install --with docs
```

Build HTML documentation:

```bash
poetry run sphinx-build -b html docs docs/_build/html -W --keep-going
```

Run link checking:

```bash
poetry run sphinx-build -b linkcheck docs docs/_build/linkcheck -W --keep-going
```

The built documentation will be in `docs/_build/html/`. Open `index.html` in your browser to preview.

## Documentation Quality

All documentation changes are validated automatically in CI:

- **Warnings treated as errors**: Any Sphinx warning will fail the build
- **Link checking**: Internal and external links are validated
- **Markup validation**: Malformed MyST/Markdown is rejected

Please run the build commands locally before submitting a pull request to catch issues early.
