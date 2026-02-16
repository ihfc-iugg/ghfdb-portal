# Quickstart: CI/CD Pipeline & Automation

**Feature**: CI/CD Pipeline & Automation
**Audience**: Contributors and Maintainers
**Last Updated**: January 5, 2026

## Overview

The Global Heat Flow Database Portal uses automated CI/CD pipelines to ensure code quality, run tests, and deploy to staging/production environments. This guide explains what happens when you submit a PR and how to interpret CI results.

## What Runs on Your PR

When you open or update a pull request, the following automated checks run within ~5 minutes:

### 1. Code Quality Checks ✨

**Linting (Ruff)**

- Validates Python code style
- Checks for common errors and anti-patterns
- Fix locally: `poetry run ruff check . --fix`

**Formatting (Ruff)**

- Ensures consistent code formatting
- Fix locally: `poetry run ruff format .`

**Type Checking (mypy)**

- Validates type hints and catches type errors
- Fix locally: `poetry run mypy project`

### 2. Fast Unit Tests 🧪

**What runs**: Unit tests without `integration`, `contract`, `slow`, or `external` markers
**Why**: Fast feedback without slow database operations
**Run locally**: `poetry run pytest -m "not integration and not contract and not slow and not external"`

**Coverage Requirement**: 80% overall, 100% for critical paths
**Run locally with coverage**: `poetry run pytest --cov=project --cov-report=html`

### 3. Documentation Build 📚

**What runs**: Sphinx documentation build with warnings-as-errors
**Why**: Ensures docs stay in sync with code and specs
**Run locally**: `poetry run sphinx-build -b html -W docs docs/_build/html`

## Understanding PR Status Checks

Your PR will show status checks in the GitHub interface:

✅ **Green checkmark**: All checks passed, ready for review
❌ **Red X**: One or more checks failed, click for details
🟡 **Yellow dot**: Checks are running, wait for completion

### Common Failure Patterns

**Linting Failures**

- **Error**: `Ruff found issues in file.py`
- **Fix**: Run `poetry run ruff check . --fix` locally, commit changes

**Test Failures**

- **Error**: `test_something failed with AssertionError`
- **Fix**: Review test output, fix code or test, ensure tests pass locally

**Coverage Decreased**

- **Error**: `Coverage is 78% (required: 80%)`
- **Fix**: Add tests for new code, run `pytest --cov` to verify coverage

**Documentation Build Failed**

- **Error**: `Sphinx build failed with warnings`
- **Fix**: Check docs for broken links or invalid syntax, rebuild locally

## What Runs When PR Merges to Main

After your PR is approved and merged, a comprehensive pipeline runs automatically:

### 1. Full Test Suite 🧪

**What runs**: All tests including integration, contract, and slow tests
**Database**: Real PostgreSQL database with migrations
**Duration**: ~10-15 minutes
**Run locally**: `poetry run pytest`

### 2. Docker Image Build 🐳

**What happens**:

- Builds Docker image from `Dockerfile`
- Tags with commit SHA and `latest`
- Pushes to GitHub Container Registry (GHCR)

**View images**: `https://github.com/orgs/ihfc-iugg/packages`

### 3. Staging Deployment 🚀

**What happens**:

- Pulls latest Docker image
- Deploys to staging environment
- Runs smoke tests
- Sends team notification

**Staging URL**: `https://staging.heatflow.world` (internal)

### 4. Notification 📢

Team receives Slack/Discord notification with:

- Commit SHA and author
- Deployment status (success/failure)
- Link to staging environment
- Link to workflow logs

## Nightly Operations

Every night at 3 AM UTC, additional checks run:

- **Security Scans**: Bandit for code, poetry audit for dependencies
- **Slow Tests**: Tests marked with `@pytest.mark.slow` or `@pytest.mark.external`
- **Coverage Trends**: Compare coverage over past 7 days
- **Flaky Test Detection**: Flag tests with <100% pass rate

**Issues Created**: If HIGH/CRITICAL vulnerabilities found, GitHub issue auto-created

## Manual Production Deployment

Production deployments require manual approval:

### Prerequisites

- Must be a repository maintainer
- All tests must pass on target commit
- Changes reviewed and approved

### Steps

1. Go to Actions tab in GitHub
2. Select "Production Deployment" workflow
3. Click "Run workflow"
4. Enter:
   - **Environment**: `production`
   - **Commit SHA or Tag**: The commit to deploy (e.g., `v2025.21` or commit SHA)
   - **Approval Confirmation**: Type `APPROVED` to confirm
5. Click "Run workflow"

### What Happens

1. Validates all tests passed for specified commit
2. Builds release-tagged Docker image
3. Deploys to production using `production.yml`
4. Runs smoke tests on production
5. Creates GitHub release with changelog
6. Records deployment in audit log
7. Sends team notification

## Troubleshooting

### My PR checks are taking too long

**Normal**: 3-5 minutes for PR checks
**Slow**: 10+ minutes may indicate resource contention
**Solution**: Check GitHub Actions status page, retry if infrastructure issue

### Tests pass locally but fail in CI

**Common causes**:

- Environment differences (Python version, dependencies)
- Database state issues (migrations not applied)
- Timezone or locale differences

**Solution**: Review CI logs carefully, check for differences in setup

### Coverage decreased but I added tests

**Cause**: New code adds more lines faster than tests cover them
**Solution**: Ensure test coverage for all new code paths, aim for 100% on new code

### Documentation build fails but builds locally

**Cause**: Missing dependencies or environment differences
**Solution**: Ensure `poetry install --with docs` runs cleanly, check Sphinx warnings

### Staging deployment failed after successful tests

**Cause**: Deployment configuration issue, network problem, or resource constraint
**Solution**: Check deployment logs, verify staging environment health, contact maintainers

## Local Development Workflow

### Recommended Flow

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Write failing test (TDD)
# Edit tests/test_my_feature.py

# 3. Run test locally
poetry run pytest tests/test_my_feature.py

# 4. Implement feature
# Edit project/my_feature.py

# 5. Run tests until passing
poetry run pytest tests/test_my_feature.py

# 6. Run full fast test suite
poetry run pytest -m "not integration and not contract and not slow and not external"

# 7. Check coverage
poetry run pytest --cov=project --cov-report=html
open htmlcov/index.html

# 8. Run linting and formatting
poetry run ruff check . --fix
poetry run ruff format .

# 9. Run type checking
poetry run mypy project

# 10. Build docs if modified
poetry run sphinx-build -b html -W docs docs/_build/html

# 11. Commit and push
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature

# 12. Open PR and wait for CI
```

## Best Practices

### ✅ Do

- Run tests locally before pushing
- Write tests first (TDD)
- Keep PRs focused and small
- Add documentation for user-facing changes
- Update specs when requirements change
- Monitor CI feedback promptly

### ❌ Don't

- Push without running tests locally
- Ignore linting errors
- Decrease test coverage
- Skip documentation updates
- Force-push after PR opened (breaks CI history)
- Merge with failing CI checks

## Getting Help

- **CI pipeline issues**: Check workflow logs in Actions tab
- **Test failures**: Review test output, run locally with `-v` flag
- **Deployment issues**: Contact maintainers on Slack/Discord
- **Questions**: Open discussion in GitHub Discussions

## Monitoring & Metrics

### Coverage Reports

View coverage trends: `https://codecov.io/gh/ihfc-iugg/global-heat-flow-database`

### CI Status

View workflow runs: `https://github.com/ihfc-iugg/global-heat-flow-database/actions`

### Deployments

View deployment history: Actions → Deployments

## Configuration Files Reference

- `pyproject.toml`: pytest, coverage, linting, type checking configuration
- `.github/workflows/pr-validation.yml`: PR checks workflow
- `.github/workflows/main-integration.yml`: Main branch pipeline
- `.github/workflows/nightly-checks.yml`: Scheduled checks
- `.github/workflows/production-deploy.yml`: Production deployment
- `docker-compose.yml`: Staging deployment config
- `production.yml`: Production deployment config

## Next Steps

- Read [Testing Standards](../../docs/guides/testing-standards.md) for testing conventions
- Read [Documentation Standards](../../docs/guides/documentation-standards.md) for documentation requirements
- Review [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines
- Join team communication channel for support
