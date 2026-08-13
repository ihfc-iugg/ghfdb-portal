# AGENTS.md — Agent Configuration for the GHFDB Portal

<!-- Thin index only. Details live in the pointed-to files. -->

This repository is the web application behind [portal.heatflow.world](https://portal.heatflow.world),
the access and contribution point for the Global Heat Flow Database. It is a Django project built
on the FairDM framework: `heat_flow` holds the data model, `ghfdb` holds the import, export and
proxy layer that maps that model onto the published GHFDB spreadsheet structure, and `review` holds
the workflow that submissions pass through before publication. It is deployed, not published to a
package index.

## Stack & commands

- **Stack:** Python 3.13, Django 5.x on the FairDM framework, Poetry-managed, PostgreSQL with
  PostGIS in production
- **Install:** `poetry install --with dev,docs`
- **Test:** `poetry run pytest`
- **Lint:** `poetry run pre-commit run --all-files`. This is *not* the gate CI enforces. CI runs
  `poetry run ruff check .` and `poetry run ruff format --check .` directly, and the two differ in
  both scope and version: `.pre-commit-config.yaml` excludes `docs/`, `migrations/` and `tests/`,
  and pins ruff at v0.3.2 while `pyproject.toml` resolves ^0.15.10. Run raw ruff to predict CI.
- **Format:** `poetry run ruff format .`
- **Type-check:** `poetry run mypy project`
- **Templates:** `poetry run djlint templates/ --check`
- **Docs:** `poetry run sphinx-build -b html docs docs/_build/html -W --keep-going`
- **Task runner:** `poetry run invoke --list` (`check`, `test`, `docs`, `create_fixtures`, others)

**Python version matters here.** `pyproject.toml` allows `>=3.13,<4.0`, so Poetry will pick 3.14 if
that is the default interpreter, and psycopg2-binary, pyproj and lxml have no 3.14 wheels — they
fall back to source builds and fail without system development packages. Pin the environment with
`poetry env use python3.13`, which is also what CI uses.

There is no PostgreSQL in the local test path: pytest runs with `--nomigrations --reuse-db` against
SQLite, while `main-integration.yml` runs the full suite against PostgreSQL 15.

## Agent skills

### Issue tracker

GitHub Issues via the `gh` CLI. External PRs are not a triage surface; Discussions carry feature
demand. See `docs/agents/issue-tracker.md`.

### Triage labels

Six canonical triage labels plus the feature-lifecycle set and this repo's own priority and type
labels. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — `CONTEXT.md` at the root, `docs/adr/` for architectural decisions. The
GHFDB structure itself is defined in published literature held under
`docs/constitution/references/`. See `docs/agents/domain.md`.

### CI checks

Required status checks (exact names, as they report on a pull request):

- `Linting & Formatting`
- `Type Checking`
- `Documentation Build`
- `Template Validation (djlint)`
- `Secrets Scanning`

`Unit Tests & Coverage` runs on every pull request but is **not** required while the GHFDB column
coverage gap is open, because it is red on `main` for a reason that predates any current work.
It becomes required as soon as the suite is green.

CI is repo-native rather than calling the shared family workflows: `pr-validation.yml` on pull
requests, `main-integration.yml` on pushes to `main` (full PostgreSQL suite, Docker image build,
staging deploy), `production-deploy.yml`, `docs-validation.yml`, and a monthly `nightly-checks.yml`.

## Development workflow

Feature work follows a spec-driven process: spec → plan → tasks → implement → review → PR, with a
`specs/NNN-slug/` directory per feature. `specs/` holds the specs written so far and stays as the
record of what was built and why. There is no spec-kit toolchain installed in the repo. It was
removed because it was a vendored copy of software maintained elsewhere.

Project standards and the quality bar live in `memory/constitution.md`.
