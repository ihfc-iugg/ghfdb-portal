# CI/CD Pipeline Guide

This guide explains the continuous integration and deployment pipeline for the Global Heat Flow Database Portal.

## Overview

The CI/CD pipeline provides automated quality gates, testing, and deployment across three main workflows:

1. **PR Validation** - Fast feedback on pull requests (<5 minutes)
2. **Main Integration** - Full testing and staging deployment on merges to main
3. **Nightly Checks** - Comprehensive security scans and slow tests (scheduled)
4. **Production Deployment** - Manual deployment to production (approval-gated)

## What Runs on Pull Requests

When you open or update a pull request, the **PR Validation** workflow automatically runs:

### Jobs

- **Linting & Formatting** (~2 minutes)
  - Ruff linting with project configuration
  - Ruff format checking (line length 120, LF endings)
  - Fails on any linting errors or formatting violations

- **Type Checking** (~2 minutes)
  - mypy type checking on `project/` directory
  - Django plugin enabled for model type checking
  - Fails on any type errors

- **Unit Tests & Coverage** (~3 minutes)
  - Fast unit tests only (excludes `integration`, `contract`, `slow`, `external` markers)
  - Runs with `--nomigrations --reuse-db` for speed
  - Coverage collection with 80% minimum threshold
  - Coverage report uploaded to Codecov with `pr-tests` flag

- **Documentation** (conditional, ~2 minutes)
  - Only runs if documentation files are modified (`docs/`, `pyproject.toml`)
  - Sphinx build with warnings as errors (`-W` flag)
  - Linkcheck validation for external links (GitHub, project domain)
  - Fails on any broken links or invalid documentation syntax

- **Template Validation** (conditional, ~1 minute)
  - Only runs if template files are modified (`templates/`)
  - djlint validation with project configuration
  - Checks Django template syntax and formatting

- **Security Scan** (~2 minutes)
  - bandit reports insecure code patterns in `project/`
  - pip-audit reports known vulnerabilities in the installed dependencies
  - Both upload a report as an artifact. Findings do not fail the build, but a
    scanner that produces no report does

Secret scanning is deliberately **not** a job here. GitHub scans the repository
itself, which covers the whole history rather than one pull request's diff, and
push protection rejects a credential before it is ever pushed. See
[Secret scanning blocked my push](#secret-scanning-blocked-my-push).

### Expected Feedback Time

- **Target**: <5 minutes for most PRs
- **Typical**: 2-4 minutes for code-only changes
- **With docs**: +2 minutes for documentation builds
- **With templates**: +1 minute for template validation

### Viewing Results

1. Check the **Checks** tab on your PR for status
2. Click individual check names to see detailed logs
3. Failed checks show direct links to error locations
4. Coverage reports link to Codecov for detailed analysis

## What Runs on Main Branch Merges

When a PR is merged to `main`, the **Main Integration** workflow runs:

### Jobs (Sequential)

1. **Full Test Suite** (~10 minutes)
   - All test markers included (integration, contract, slow, external)
   - PostgreSQL 15 service container for database tests
   - Django migrations run before tests
   - Uses `--reuse-db` (no `--nomigrations`)
   - Coverage uploaded with `main-tests` flag
   - **Blocks deployment if any tests fail**

2. **Build Docker Image** (~8 minutes)
   - Builds production Docker image
   - Tags: `main-<sha>`, `latest`
   - Pushes to GitHub Container Registry (GHCR)
   - Uses GitHub Actions cache for layer caching
   - Creates GitHub deployment record for staging

3. **Deploy to Staging** (~5 minutes)
   - SSH to staging server
   - Pulls latest Docker image
   - Runs docker-compose up
   - Runs Django migrations and collectstatic
   - Executes smoke tests (health check, homepage, database, static files)
   - **Automatic rollback if smoke tests fail**
   - Updates GitHub deployment status

4. **Notify Team** (~30 seconds)
   - Sends Slack notification to #deployments channel
   - Includes commit SHA, committer, status, and links
   - Runs regardless of success/failure

### Staging Environment

- **URL**: <https://staging.heatflow.world>
- **Auto-deployment**: Every main branch merge
- **Database**: Separate from production
- **Purpose**: Continuous validation in production-like environment

## What Runs Nightly

The **Nightly Checks** workflow runs on a schedule (3 AM UTC) or can be manually triggered:

### Jobs (Parallel)

- **Security Scanning** (~10 minutes)
  - Bandit: Static analysis for security issues in Python code
  - Poetry audit: Checks for known vulnerabilities in dependencies
  - Creates GitHub issues for HIGH/CRITICAL findings
  - Uploads security report as artifact

- **Comprehensive Tests** (~20 minutes)
  - Full pytest suite including `slow` and `external` markers
  - Fresh database (no `--reuse-db`) to catch migration issues
  - Flaky test detection (compares results from past 7 days)
  - Coverage trends uploaded to Codecov with `nightly` flag

- **Dependency Audit** (~5 minutes)
  - Lists outdated packages (`poetry show --outdated`)
  - Checks for deprecated packages via PyPI
  - Generates combined dependency report

- **Coverage Trends** (~2 minutes)
  - Queries Codecov API for 7-day coverage history
  - Alerts if coverage decreased >2% in a week
  - Creates GitHub issue for declining trends

- **Notification** (~30 seconds)
  - Email summary to maintainer list
  - Slack notification with metrics and findings
  - Runs regardless of job success/failure

### Nightly Reports

- Artifacts available in workflow run for 90 days
- Security report: JSON format with vulnerabilities
- Flaky test report: List of tests with <100% pass rate
- Dependency report: Outdated, deprecated, and vulnerable packages

## Production Deployment

Production deployments are **manual and approval-gated** via the **Production Deploy** workflow.

### Trigger

1. Navigate to **Actions** → **Production Deploy** workflow
2. Click **Run workflow**
3. Fill required inputs:
   - **Environment**: `production` (required)
   - **Commit SHA**: Commit or tag to deploy (required)
   - **Approval**: Type `APPROVED` to confirm (required)
4. Workflow requires approval from maintainer team

### Deployment Process

1. **Validation** (~3 minutes)
   - Verifies approval confirmation is `APPROVED`
   - Checks commit exists on main branch or is a tag
   - Verifies all tests passed for that commit (queries main integration run)
   - Generates pre-deployment report (commits, tests, coverage, security)

2. **Build Release Image** (~10 minutes)
   - Builds Docker image with release version tag
   - Tags: `v<version>`, `production`, `<sha>`
   - Pushes to GHCR

3. **Deploy to Production** (~10 minutes)
   - **Requires manual approval** (GitHub environment protection)
   - Creates backup of current production state
   - SSH to production server
   - Pulls release image
   - Runs docker-compose with production.yml
   - Health checks and smoke tests
   - **Automatic rollback on failure**
   - Updates deployment status

4. **Create Release** (conditional, ~2 minutes)
   - Only runs if deploying from a tag
   - Generates changelog
   - Creates GitHub release with deployment report
   - Attaches deployment metadata

5. **Notify Stakeholders** (~30 seconds)
   - Slack notification to #deployments
   - Email to stakeholder list with deployment details
   - Includes version, deployer, links to release notes

### Production Environment

- **URL**: <https://heatflow.world>
- **Deployment**: Manual trigger only
- **Approval**: Required from maintainer team
- **Audit**: Complete deployment history in GitHub Deployments API

## Test Execution Strategy

### Test Markers

Tests are categorized using pytest markers:

| Marker | Description | Runs On |
|--------|-------------|---------|
| `integration` | Requires full Django stack, database, multiple components | Main, Nightly |
| `contract` | Validates API response schemas | Main, Nightly |
| `slow` | Takes >5 seconds (e.g., data processing, report generation) | Nightly only |
| `external` | Requires external services (S3, APIs) | Nightly only (skipped if unavailable) |
| `django_db` | Requires database access | PR (if fast), Main, Nightly |

### Coverage Thresholds

- **Overall**: 80% minimum (enforced in all workflows)
- **Critical paths**: 100% required for:
  - Data import/export (`ghfdb.importers`, `ghfdb.exporters`)
  - Quality scoring (`heat_flow.quality`)
  - Publication workflow (`review.publication`)

### Test Selection by Context

**Pull Request**:

```bash
pytest -m "not integration and not contract and not slow and not external" \
       --nomigrations --reuse-db
```

**Main Branch**:

```bash
pytest --reuse-db
```

**Nightly**:

```bash
pytest  # No --reuse-db, fresh database to catch migration issues
```

## Troubleshooting

### PR checks failing with linting errors

**Problem**: Ruff reports formatting or linting violations

**Solution**:

```bash
# Auto-fix linting issues
poetry run ruff check . --fix

# Auto-format code
poetry run ruff format .

# Commit the fixes
git add .
git commit -m "Fix linting and formatting"
git push
```

### Coverage below threshold

**Problem**: Coverage dropped below 80%

**Solution**:

1. Check Codecov report in PR comments for uncovered lines
2. Add tests for uncovered code or mark as excluded:

```python
# Mark code as not requiring coverage (use sparingly)
def debug_only_function():  # pragma: no cover
    ...
```

### Documentation build failing

**Problem**: Sphinx build fails with warnings/errors

**Solution**:

1. Check the error message in CI logs
2. Common issues:
   - Broken internal links: Fix references in `.md` or `.rst` files
   - Missing files: Add referenced files or remove references
   - Invalid syntax: Fix Markdown/RST formatting

```bash
# Test documentation build locally
poetry run sphinx-build -b html -W docs docs/_build/html
```

### Tests passing locally but failing in CI

**Problem**: Tests work on your machine but fail in GitHub Actions

**Common causes**:

1. **Database differences**: CI uses PostgreSQL, you might use SQLite
2. **Migration issues**: CI runs migrations fresh, check for migration conflicts
3. **Environment variables**: CI uses different settings, check `DJANGO_ENV`
4. **Test isolation**: CI runs tests in different order, check for test dependencies

**Solution**:

```bash
# Run tests with same markers as CI
poetry run pytest -m "not integration and not contract and not slow and not external" \
                  --nomigrations --reuse-db

# Run with PostgreSQL locally
docker-compose up -d postgres
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ghfdb_test
poetry run pytest
```

### Secret scanning blocked my push

**Problem**: `git push` is rejected with a message naming a secret type and the
file and line it was found on. This is GitHub push protection, not a CI check,
so it happens before any pull request exists.

**Solution**:

1. **If it is a real credential**, treat it as compromised even though the push
   was blocked, because it has been on your machine and in your shell history.
   Rotate it at the provider, take it out of the code, and read it from an
   environment variable instead. Then amend or rebase the commit that contained
   it. Pushing a later commit that removes it is not enough, because the earlier
   commit still carries it.
2. **If it is not a real credential** — a fixture, an example in a docstring —
   the block message links to a form for allowing that specific push. Say which
   it is and why. There is no ignore file to edit.

Alerts for anything already in the history appear under **Security → Secret
scanning** in the repository, and only maintainers can see them.

### Staging deployment failed

**Problem**: Main integration workflow succeeded but deployment failed

**Check**:

1. View deployment logs in GitHub Actions
2. Check staging server SSH connectivity
3. Verify `STAGING_DEPLOY_KEY` secret is configured
4. Check smoke test results

**Manual rollback** (if needed):

```bash
# SSH to staging server
ssh deploy@staging.heatflow.world
cd /opt/ghfdb-portal
docker-compose down
docker-compose up -d
```

## Local Development Workflow

Recommended workflow for contributors:

1. **Create feature branch**:

   ```bash
   git checkout -b feature/my-feature
   ```

2. **Write tests first** (TDD - Test-Driven Development):

   ```bash
   # Write failing test
   poetry run pytest tests/test_my_feature.py -v
   ```

3. **Implement feature**:

   ```python
   # Write code to make test pass
   ```

4. **Run fast tests locally**:

   ```bash
   poetry run pytest -m "not integration and not contract and not slow and not external"
   ```

5. **Check coverage**:

   ```bash
   poetry run pytest --cov=project --cov-report=term-missing
   ```

6. **Run linting**:

   ```bash
   poetry run ruff check . --fix
   poetry run ruff format .
   ```

7. **Run type checking**:

   ```bash
   poetry run mypy project
   ```

8. **Commit and push**:

   ```bash
   git add .
   git commit -m "Add my feature with tests"
   git push origin feature/my-feature
   ```

9. **Open PR** - CI will automatically run all checks

10. **Address feedback** - If CI fails, fix issues and push again

## Getting Help

- **CI/CD issues**: Check [.github/SECRETS.md](.github/SECRETS.md) for configuration
- **Test failures**: See [docs/guides/testing-standards.md](../../guides/testing-standards.md)
- **Deployment problems**: Contact maintainer team in #deployments Slack channel
- **Questions**: Open a discussion in GitHub Discussions

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Codecov Documentation](https://docs.codecov.io/)
