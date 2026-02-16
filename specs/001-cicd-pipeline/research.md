# Research: CI/CD Pipeline & Automation

**Feature**: CI/CD Pipeline & Automation
**Branch**: `001-cicd-pipeline`
**Date**: January 5, 2026

## Research Objectives

This document resolves technical unknowns and establishes best practices for implementing the CI/CD pipeline. All decisions are grounded in existing project configuration and GitHub Actions conventions.

## GitHub Actions Workflow Design

### Decision: Separate workflows per trigger pattern

**Rationale**: GitHub Actions best practice is to separate workflows by trigger (PR, push, schedule, manual) rather than creating monolithic workflows with complex conditionals. This improves readability, enables independent execution, and allows different concurrency settings per workflow.

**Implementation**:

- `pr-validation.yml`: Triggered on `pull_request` events
- `main-integration.yml`: Triggered on `push` to `main` branch
- `nightly-checks.yml`: Triggered on `schedule` (cron)
- `production-deploy.yml`: Triggered on `workflow_dispatch` (manual)

**Alternatives considered**:

- Single workflow with conditional steps: Rejected due to complexity and harder debugging
- Branch-based workflows: Rejected as existing pattern uses separate files per purpose

### Decision: Use Poetry with caching for dependency management

**Rationale**: Project already uses Poetry (evidenced by `pyproject.toml` and existing workflows). Poetry provides deterministic dependency resolution and virtualenv management. GitHub Actions has mature caching support for Poetry via `snok/install-poetry` action.

**Implementation**:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.13'
- uses: snok/install-poetry@v1
  with:
    virtualenvs-create: true
    virtualenvs-in-project: true
- uses: actions/cache@v4
  with:
    path: .venv
    key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}
- run: poetry install --with dev,docs
```

**Alternatives considered**:

- pip + requirements.txt: Rejected as project uses Poetry consistently
- Conda: Rejected as not currently used in project

## Test Execution Strategy

### Decision: Marker-based test selection with pytest

**Rationale**: Project already uses pytest markers (`integration`, `contract`, `slow`, `external`) defined in `pyproject.toml`. Fast feedback on PRs requires excluding slow tests while main branch needs comprehensive validation.

**PR Test Command**:

```bash
poetry run pytest -m "not integration and not contract and not slow and not external" --nomigrations --reuse-db
```

**Main Branch Test Command**:

```bash
poetry run pytest --reuse-db
```

**Nightly Test Command**:

```bash
poetry run pytest  # All markers, fresh database
```

**Alternatives considered**:

- Test directory separation: Rejected as markers provide more flexibility
- Parallel test execution: Deferred to future optimization (not blocking MVP)

### Decision: PostgreSQL service for integration tests on main

**Rationale**: Integration tests require real database to validate Django ORM queries, migrations, and FairDM integration. GitHub Actions supports service containers.

**Implementation**:

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_DB: test_ghfdb
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

**Alternatives considered**:

- SQLite for all tests: Rejected as PostgreSQL-specific features need validation
- Docker Compose in CI: Rejected as service containers are simpler for test database

## Coverage Collection & Reporting

### Decision: pytest-cov with Codecov upload

**Rationale**: Project already configures pytest-cov in `pyproject.toml` with 80% threshold. Codecov is standard for open-source Python projects and provides trend analysis.

**Implementation**:

```yaml
- run: poetry run pytest --cov=project --cov-report=xml --cov-report=term
- uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    file: ./coverage.xml
    fail_ci_if_error: true
```

**Alternatives considered**:

- Coveralls: Rejected as Codecov has better GitHub integration
- Inline coverage only: Rejected as trend analysis requires external service

### Decision: Fail CI if coverage decreases below 80%

**Rationale**: Constitution Principle VII requires >80% coverage. `pyproject.toml` already sets `fail_under = 80`.

**Implementation**: pytest-cov will exit with non-zero code if coverage <80%, failing the workflow.

## Code Quality Validation

### Decision: Ruff for linting and formatting checks

**Rationale**: Project already uses Ruff with configuration in `pyproject.toml`. Ruff is significantly faster than flake8+black and combines both linting and formatting.

**Implementation**:

```yaml
- run: poetry run ruff check .
- run: poetry run ruff format --check .
```

**Alternatives considered**:

- flake8 + black: Rejected as Ruff is faster and already configured
- Auto-fix in CI: Rejected as fixes should happen locally, CI only validates

### Decision: mypy for type checking

**Rationale**: Project already uses mypy with configuration in `pyproject.toml` targeting `project/` directory.

**Implementation**:

```yaml
- run: poetry run mypy project
```

**Alternatives considered**:

- pyright: Rejected as mypy is already configured
- Skip type checking: Rejected as Constitution emphasizes code quality

## Documentation Validation

### Decision: Extend existing docs-validation.yml workflow

**Rationale**: `.github/workflows/docs-validation.yml` already exists and builds Sphinx docs with `-W` (warnings as errors). This workflow should be triggered on PR and main.

**Implementation**: Update existing workflow to trigger on both PR and push to main, ensure it covers all doc paths including specs/.

**Alternatives considered**:

- Separate docs workflow: Rejected as existing workflow is well-structured
- Skip docs validation: Rejected as Constitution Principle VIII requires it

## Docker Build & Registry

### Decision: Build on main only, tag with commit SHA and latest

**Rationale**: Existing `docker-build-and-publish.yml` builds on tags. We need to build on every main merge to enable staging deployment. GHCR is already configured.

**Implementation**:

```yaml
- uses: docker/build-push-action@v5
  with:
    push: true
    tags: |
      ghcr.io/${{ github.repository }}:${{ github.sha }}
      ghcr.io/${{ github.repository }}:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Alternatives considered**:

- Build on every PR: Rejected as unnecessary and slow
- Build on tags only: Rejected as staging needs main branch images

## Deployment Automation

### Decision: Automated staging, manual production

**Rationale**: Staging should reflect main branch immediately for continuous validation. Production deployments require human approval for audit and control.

**Staging Implementation**:

```yaml
- name: Deploy to staging
  run: |
    # SSH to staging server or use deployment tool
    docker-compose -f docker-compose.yml pull
    docker-compose -f docker-compose.yml up -d
```

**Production Implementation**: Use `workflow_dispatch` with required inputs (commit SHA, approval confirmation).

**Alternatives considered**:

- Auto-deploy production: Rejected due to audit and approval requirements
- No staging auto-deploy: Rejected as manual staging is too slow

### Decision: Smoke tests post-deployment

**Rationale**: Deployment success doesn't guarantee application health. Basic health check validates deployment.

**Implementation**:

```bash
#!/bin/bash
# smoke-test.sh
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:8000/admin/ || exit 1
```

**Alternatives considered**:

- No smoke tests: Rejected as deployment could succeed but app fail
- Full E2E tests: Deferred as smoke tests sufficient for MVP

## Security Scanning

### Decision: Bandit for Python security, poetry audit for dependencies

**Rationale**: Bandit detects security issues in Python code. `poetry show --outdated` and security plugins check for vulnerable dependencies.

**Nightly Implementation**:

```yaml
- run: poetry run bandit -r project/
- run: poetry audit  # If poetry-audit-plugin installed
```

**Alternatives considered**:

- Snyk: Rejected as requires external service and poetry audit covers CVEs
- Safety: Considered but poetry audit is more integrated

### Decision: Create GitHub issues for HIGH/CRITICAL vulnerabilities

**Rationale**: Automates incident response and ensures visibility.

**Implementation**:

```yaml
- uses: actions/github-script@v7
  if: failure()
  with:
    script: |
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: 'Security vulnerability detected',
        body: '...',
        labels: ['security', 'dependencies']
      })
```

**Alternatives considered**:

- Email only: Rejected as GitHub issues provide tracking
- Manual review: Rejected as automation ensures timely response

## Notifications

### Decision: GitHub Actions status checks + Slack/Discord webhooks

**Rationale**: GitHub status checks are required for PR blocking. Team notifications for staging/production deployments improve visibility.

**Implementation**:

```yaml
- uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployed to staging: ${{ github.sha }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Alternatives considered**:

- Email only: Rejected as Slack/Discord are more responsive
- No notifications: Rejected as team needs deployment awareness

## Environment Configuration

### Decision: Use GitHub Secrets for sensitive values, .env files for non-sensitive

**Rationale**: Existing pattern uses `stack.env` and `stack.development.env`. Secrets (API keys, passwords) must be in GitHub Secrets.

**Required Secrets**:

- `CODECOV_TOKEN`: For coverage upload
- `SLACK_WEBHOOK`: For team notifications
- `STAGING_DEPLOY_KEY`: SSH key for staging deployment
- `PRODUCTION_DEPLOY_KEY`: SSH key for production deployment

**Alternatives considered**:

- Hardcode in workflows: Rejected as insecure
- External secret management: Deferred as GitHub Secrets sufficient for MVP

## Failure Handling & Retries

### Decision: Retry transient failures up to 3 times

**Rationale**: Network issues and service unavailability can cause spurious failures. Exponential backoff reduces false negatives.

**Implementation**:

```yaml
- uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 60
    command: poetry run pytest
```

**Alternatives considered**:

- No retries: Rejected as infrastructure can have transient issues
- Unlimited retries: Rejected as wastes resources on real failures

### Decision: Rollback staging on deployment failure

**Rationale**: Failed staging deployment should not leave environment broken.

**Implementation**: Store previous Docker image tag, `docker-compose down && docker-compose up` with previous tag on failure.

**Alternatives considered**:

- Leave broken: Rejected as staging is shared resource
- Manual rollback: Rejected as automation is faster and more reliable

## Audit Logging

### Decision: Store deployment events in GitHub Actions run metadata

**Rationale**: GitHub Actions provides built-in audit trail (who triggered, when, from what commit). Additional structured logging can use GitHub API.

**Implementation**: Use `github-script` action to add deployment annotations:

```yaml
- uses: actions/github-script@v7
  with:
    script: |
      github.rest.repos.createDeployment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        ref: context.sha,
        environment: 'staging',
        required_contexts: [],
        auto_merge: false
      })
```

**Alternatives considered**:

- External audit database: Deferred as GitHub's audit is sufficient initially
- No audit: Rejected as Constitution Principle VI requires it

## Technology Choices Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| CI/CD Platform | GitHub Actions | Already in use, native GitHub integration |
| Dependency Management | Poetry 1.1.0+ | Already configured in pyproject.toml |
| Test Framework | pytest + pytest-django | Already configured with markers |
| Linting/Formatting | Ruff | Already configured, fast, combines lint+format |
| Type Checking | mypy | Already configured |
| Coverage Reporting | pytest-cov + Codecov | Standard for Python, trend analysis |
| Container Registry | GHCR | Already in use, free for public repos |
| Documentation | Sphinx | Already configured |
| Security Scanning | Bandit + poetry audit | Python-native, no external dependencies |
| Notifications | Slack/Discord webhooks | Team already uses, better than email |
| Database (CI) | PostgreSQL 15 service | Matches production, validates PG features |

## Implementation Priorities

### Must Have (MVP)

1. PR validation workflow (fast feedback)
2. Main integration workflow (full tests + build)
3. Coverage enforcement (80% threshold)
4. Documentation validation
5. Staging auto-deploy

### Should Have (Phase 2)

1. Nightly security scans
2. Production manual deploy workflow
3. Smoke tests
4. Team notifications

### Could Have (Future)

1. Parallel test execution
2. Performance benchmarks
3. Dependency update automation
4. Multi-region deployments

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| GitHub Actions quota exceeded | PRs blocked | Monitor usage, optimize caching, consider self-hosted runners |
| Flaky tests cause false negatives | Developer frustration | Track test stability, quarantine flaky tests, improve test isolation |
| Staging deployment credentials compromise | Security breach | Rotate keys regularly, use short-lived tokens where possible |
| Coverage drops gradually | Quality erosion | Weekly coverage reports, require 100% for critical paths |
| Docker image size grows | Slow deployments | Multi-stage builds, .dockerignore, periodic image optimization |

## Open Questions (None Remaining)

All technical decisions have been made based on existing project configuration and best practices. No clarifications needed.
