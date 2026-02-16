# global-heat-flow-database Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-02

## Active Technologies
- Python 3.13 (as specified in pyproject.toml) + GitHub Actions (CI/CD platform), Poetry (dependency management), pytest with pytest-django/pytest-cov/pytest-mock (testing), Ruff (linting/formatting), mypy (type checking), Sphinx (documentation), Docker & docker-compose (containerization) (001-cicd-pipeline)
- GitHub Actions workflow artifacts, GitHub Container Registry (GHCR) for Docker images, Codecov for coverage reports (001-cicd-pipeline)


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
- 001-cicd-pipeline: Added Python 3.13 (as specified in pyproject.toml) + GitHub Actions (CI/CD platform), Poetry (dependency management), pytest with pytest-django/pytest-cov/pytest-mock (testing), Ruff (linting/formatting), mypy (type checking), Sphinx (documentation), Docker & docker-compose (containerization)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
