# global-heat-flow-database Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-09

## Active Technologies
- Python 3.13 (as specified in pyproject.toml) + GitHub Actions (CI/CD platform), Poetry (dependency management), pytest with pytest-django/pytest-cov/pytest-mock (testing), Ruff (linting/formatting), mypy (type checking), Sphinx (documentation), Docker & docker-compose (containerization) (001-cicd-pipeline)
- GitHub Actions workflow artifacts, GitHub Container Registry (GHCR) for Docker images, Codecov for coverage reports (001-cicd-pipeline)
- Python ≥3.13 + Django 5.0+, FairDM (`fairdm`, `fairdm-geo`, `fairdm-discussions`, `fairdm-rest-api`), django-polymorphic, django-pint-field, django-research-vocabs (ConceptField), django-tables2, django-filter (002-data-model)
- PostgreSQL (production) / SQLite (dev/test) (002-data-model)
- Python ≥3.13 + Django 5.0+, FairDM ecosystem (fairdm, fairdm-geo, fairdm-discussions, fairdm-rest-api), django-pint (quantities), django-research-vocabs (ConceptField/ConceptManyToManyField) (002-data-model)
- PostgreSQL (production), SQLite (development/testing), PostGIS for geospatial (002-data-model)
- Python ≥3.13 + Django 5.0+, FairDM (`fairdm`, `fairdm-geo`), `research_vocabs`, `django-pint` (via `fairdm.db.fields`), `django-polymorphic`, `factory_boy` (001-ghfdb-data-model)
- SQLite (development), PostgreSQL + PostGIS (production) (001-ghfdb-data-model)


## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python (repository target is Python >=3.13): Follow standard conventions

## Recent Changes
- 001-ghfdb-data-model: Added Python ≥3.13 + Django 5.0+, FairDM (`fairdm`, `fairdm-geo`), `research_vocabs`, `django-pint` (via `fairdm.db.fields`), `django-polymorphic`, `factory_boy`
- 002-data-model: Added Python ≥3.13 + Django 5.0+, FairDM ecosystem (fairdm, fairdm-geo, fairdm-discussions, fairdm-rest-api), django-pint (quantities), django-research-vocabs (ConceptField/ConceptManyToManyField)
- 002-data-model: Added Python ≥3.13 + Django 5.0+, FairDM (`fairdm`, `fairdm-geo`, `fairdm-discussions`, `fairdm-rest-api`), django-polymorphic, django-pint-field, django-research-vocabs (ConceptField), django-tables2, django-filter


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
