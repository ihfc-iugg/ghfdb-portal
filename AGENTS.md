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

- `call-build / Code Quality`
- `call-build / Security Scan`
- `call-build / Build Package`
- `call-tests / Test Python 3.13, Django 5.2`

The `call-build` and `call-tests` prefixes come from the job names in `build.yml` and `tests.yml`.
Branch protection has to name the prefixed context — the bare job name matches nothing.

CI calls the shared workflows from `django-mvp/shared`, pinned to a tag, rather than maintaining
its own copies:

| Workflow | Runs |
|---|---|
| `build.yml` | code quality, security scan, package build, on every pull request |
| `tests.yml` | the suite, on every pull request |
| `docs.yml` | the Sphinx build, on demand |
| `publish.yml` | the release image |
| `prepare-release.yml` / `tag-release.yml` | the version-bump and tagging flow |
| `auto-merge-dependabot.yml` | dependency updates, gated on the required checks |
| `production-deploy.yml` | manual production deployment |

Code Quality runs `pre-commit run --all-files`, so ruff, mypy, deptry and djlint all come from the
Poetry environment and their versions follow the single `mvp-shared` pin in `pyproject.toml`.

Coverage is reported to Codecov with a 90% project floor and 85% on changed lines. Neither is a
required check. Project coverage is below the floor today, so that status reads red — it is a
target to climb to, not a description of where the project is.

## Development workflow

Feature work follows a spec-driven process: spec → plan → tasks → implement → review → PR, with a
`specs/NNN-slug/` directory per feature. `specs/` holds the specs written so far and stays as the
record of what was built and why. There is no spec-kit toolchain installed in the repo. It was
removed because it was a vendored copy of software maintained elsewhere.

Project standards and the quality bar live in `memory/constitution.md`.
