# Phase 1 Quickstart: Documentation Build & Validation

Date: 2026-01-02

This quickstart describes how to build and validate docs locally in a way that matches the intended CI gates.

## Prerequisites

- Python (as required by the repository)
- Poetry

## Install documentation dependencies

The repository manages documentation tooling via the Poetry `docs` dependency group.

- Install (including docs deps):
  - `poetry install --with docs`

## Build HTML docs (warnings as errors)

From the repository root:

- `poetry run sphinx-build -b html docs docs/_build/html -W --keep-going`

Expected behavior:

- Any Sphinx warning fails the build (per FR-005).

## Run link checking

- `poetry run sphinx-build -b linkcheck docs docs/_build/linkcheck -W --keep-going`

Notes:

- If some external URLs are expected to redirect, configure allow/ignore rules in `docs/conf.py` using Sphinx linkcheck configuration (`linkcheck_allowed_redirects`, `linkcheck_ignore`, etc.).

## Verify governance visibility

- Confirm the docs site includes and links to `.specify/memory/constitution.md` as rendered documentation.
- Confirm the repository `README.md` links to the docs site home page.
