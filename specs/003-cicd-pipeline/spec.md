# Feature Specification: CI/CD Pipeline & Automation

**Feature Branch**: `003-cicd-pipeline`
**Created**: January 5, 2026
**Status**: Draft
**Input**: User description: "Create a feature spec defining continuous integration and deployment automation including what runs on PR, what runs on merge to main, and what runs nightly or on-demand. The spec should define test execution strategy in CI (which test suites run when), coverage collection and reporting expectations, build and deployment automation steps, environment-specific configurations, and failure notification and handling."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Contributor PR Validation (Priority: P1)

A developer submits a pull request and needs immediate feedback on code quality, test status, and documentation validity before reviewers examine the changes.

**Why this priority**: This is the primary quality gate ensuring only working, tested code enters the codebase. Without automated PR checks, reviewers waste time catching basic errors, and broken code can reach main.

**Independent Test**: Submit a PR with intentionally broken tests/linting → CI pipeline runs → PR status checks show failures with actionable error messages → Developer can fix issues and re-push until checks pass.

**Acceptance Scenarios**:

1. **Given** a contributor opens a PR with new code, **When** the PR is created or updated, **Then** the CI pipeline automatically runs linting (Ruff), type checking (mypy), unit tests (pytest with database excluded), and documentation build validation within 5 minutes.

2. **Given** a PR with failing tests, **When** the CI run completes, **Then** the PR shows a red X status check with a direct link to the failed test output and clear error messages indicating which test failed and why.

3. **Given** a PR with passing checks, **When** all automated validations succeed, **Then** the PR shows green checkmarks on all status checks and is marked ready for human review.

4. **Given** a PR that modifies documentation files, **When** CI runs, **Then** the documentation build step must succeed with warnings treated as errors, and any broken links or invalid Sphinx syntax must block the PR.

5. **Given** a PR with decreased code coverage, **When** coverage is calculated, **Then** the CI pipeline fails the check and reports the current vs required coverage percentage (80% threshold).

---

### User Story 2 - Main Branch Integration & Deployment (Priority: P1)

When a PR is merged to main, the system must run comprehensive validation including slower integration/contract tests, build production artifacts, and deploy to staging environment with full audit trail.

**Why this priority**: Main branch must always be production-ready. Post-merge checks catch integration issues that unit tests miss, and automated staging deployment enables continuous testing of features in production-like environment.

**Independent Test**: Merge a PR to main → Full test suite runs including integration tests → Docker image builds → Staging deployment completes → Audit log records deployment timestamp, commit SHA, and actor.

**Acceptance Scenarios**:

1. **Given** a PR is merged to main, **When** the merge completes, **Then** CI runs the full pytest suite including unit, integration, and contract tests with a real database, and all tests must pass before deployment proceeds.

2. **Given** all tests pass on main, **When** the test run completes, **Then** the CI pipeline builds a Docker image tagged with the commit SHA and `latest`, pushes it to GitHub Container Registry (GHCR), and creates a deployment artifact record.

3. **Given** a Docker image is successfully built, **When** the build step completes, **Then** the CI pipeline automatically deploys the image to the staging environment using docker-compose configuration and runs smoke tests to verify the deployment succeeded.

4. **Given** deployment to staging succeeds, **When** smoke tests pass, **Then** the system sends a notification to the team Slack/Discord channel with deployment details: commit SHA, deployed at timestamp, deploying user, and link to staging site.

5. **Given** any step in the main branch pipeline fails, **When** the failure is detected, **Then** the pipeline halts, sends immediate notification with error details and logs, and the system rolls back the staging deployment to the previous stable version.

---

### User Story 3 - Scheduled & On-Demand Operations (Priority: P2)

The system runs nightly comprehensive checks (security scans, dependency audits, slow tests, coverage reports) and supports manual triggers for production deployments or full test runs.

**Why this priority**: Nightly checks catch issues that develop over time (dependency vulnerabilities, flaky tests, performance regressions) without slowing down PR feedback loops. Manual deployment triggers are essential for controlled production releases.

**Independent Test**: Nightly schedule triggers → Security scan runs → Dependency audit completes → Slow/external test suite runs → Coverage report uploads to Codecov → Team receives summary email with any warnings.

**Acceptance Scenarios**:

1. **Given** the nightly schedule triggers (3 AM UTC), **When** the scheduled workflow runs, **Then** the system executes security scanning (Bandit/Safety), dependency vulnerability checks (poetry audit), and slow/external test markers that are skipped in PR runs.

2. **Given** nightly tests complete, **When** results are collected, **Then** the system generates a comprehensive coverage report, uploads to Codecov, and compares coverage trends over the past 7 days.

3. **Given** a team member needs to deploy to production, **When** the authorized user manually triggers the production deployment workflow with a specific commit SHA or tag, **Then** the workflow validates all tests pass for that commit, builds a release-tagged Docker image, deploys to production, and creates a GitHub release with changelog.

4. **Given** a nightly security scan detects vulnerabilities, **When** the scan completes, **Then** the system creates a GitHub issue with vulnerability details (CVE, severity, affected package, remediation), assigns to the maintainer team, and sends urgent notification if severity is HIGH or CRITICAL.

5. **Given** nightly tests reveal flaky tests (intermittent failures), **When** test results are analyzed, **Then** the system flags tests that passed <100% of runs over the past week and creates a report for maintainer review.

---

### User Story 4 - Test Execution Strategy & Coverage (Priority: P1)

Tests are categorized by speed and dependencies, with fast unit tests running on every PR, integration tests running on main branch merges, and comprehensive suites running nightly or on-demand.

**Why this priority**: Fast feedback on PRs is critical for developer productivity. Slow or external-dependent tests must not block simple code reviews but must run before deployment to catch integration issues.

**Independent Test**: Check pytest configuration → Verify test markers (unit, integration, contract, slow, external) → Run `pytest -m "not integration"` on PR → Run full `pytest` on main → Verify coverage thresholds enforced in both runs.

**Acceptance Scenarios**:

1. **Given** a PR is opened, **When** the PR test suite runs, **Then** only tests without `integration`, `contract`, `slow`, or `external` markers execute (fast unit tests using mocks and `--nomigrations` flag).

2. **Given** a PR modifies database models or migrations, **When** the test suite runs, **Then** integration tests marked with `@pytest.mark.django_db` must run even in PR context to validate schema changes.

3. **Given** a merge to main, **When** the main branch test suite runs, **Then** all test markers execute including integration tests with real database, contract tests validating API schemas, and slow tests using `--reuse-db` but without `--nomigrations`.

4. **Given** any test run completes, **When** coverage is calculated, **Then** the system enforces 80% minimum overall coverage and 100% coverage for critical paths (data import, export, quality scoring, publication workflow).

5. **Given** a test suite execution, **When** tests are selected by marker, **Then** the test report clearly categorizes results by marker type (X unit tests passed, Y integration tests passed) and execution time for each category.

---

### Edge Cases

- **What happens when CI infrastructure is temporarily unavailable?** Pipeline must retry failed jobs up to 3 times with exponential backoff. If all retries fail, send notification but do not block the PR indefinitely; provide manual override option for maintainers.

- **What happens when a PR includes both code and documentation changes?** Both code tests and documentation build must pass independently; failure in either blocks the PR.

- **What happens when staging deployment fails but tests passed?** Deployment failures trigger immediate rollback to last known good version, send urgent notification, and create incident ticket. The failed deployment must not leave staging in a broken state.

- **What happens when coverage decreases but stays above 80%?** The CI pipeline logs a warning but does not fail the build. However, the coverage report must clearly show the trend, and repeated decreases trigger a review requirement.

- **What happens when a nightly job fails?** The system sends notification to maintainers with error details but does not create blocking issues. Maintainers must triage within 24 hours and decide whether to create a fix task or update the test.

- **What happens when multiple PRs are merged to main in quick succession?** Each merge triggers an independent CI run. If queued runs exceed 5, the system cancels older in-progress runs for the same branch (keep only the latest commit's run).

- **What happens when a manual production deployment is triggered during active staging deployment?** The system prevents concurrent deployments to different environments from the same repository. Production deployment must wait until staging deployment completes or times out (10 minute timeout).

- **What happens when a security vulnerability is detected in a dependency already deployed to production?** The nightly scan creates a HIGH priority issue, sends immediate notification, and flags the deployed version as vulnerable in the audit log. The deployment status dashboard must show the vulnerability warning.

## Requirements *(mandatory)*

### Functional Requirements

#### Test Execution

- **FR-001**: CI pipeline MUST execute fast unit tests (no `integration`, `slow`, `external`, or `contract` markers) on every PR creation and update, completing within 5 minutes.

- **FR-002**: CI pipeline MUST execute the full pytest suite including all test markers when code is merged to main branch.

- **FR-003**: CI pipeline MUST use pytest configuration from `pyproject.toml` including test paths, marker definitions, coverage settings, and Django settings module.

- **FR-004**: CI pipeline MUST enforce 80% minimum code coverage for all test runs and MUST fail the build if coverage falls below threshold.

- **FR-005**: CI pipeline MUST collect and report coverage by app (`heat_flow`, `ghfdb`, `review`) and identify uncovered lines in the test output.

- **FR-006**: CI pipeline MUST execute integration tests with a real PostgreSQL database using `--reuse-db` flag for main branch runs only.

- **FR-007**: CI pipeline MUST skip database migrations during PR tests using `--nomigrations` flag to improve speed, but MUST run migrations for main branch integration tests.

- **FR-008**: Nightly test runs MUST execute all test markers including `slow` and `external` tests that are excluded from PR/main runs.

#### Code Quality & Validation

- **FR-009**: CI pipeline MUST run Ruff linting with configuration from `pyproject.toml` on all Python files except excluded paths (migrations, staticfiles, docs).

- **FR-010**: CI pipeline MUST run Ruff formatting checks and MUST fail if code does not conform to configured format (line length 120, LF line endings).

- **FR-011**: CI pipeline MUST run mypy type checking on the `project/` directory with configuration from `pyproject.toml` and MUST fail on type errors.

- **FR-012**: CI pipeline MUST run djlint validation on Django templates if template files are modified in the PR.

- **FR-013**: Nightly runs MUST execute security scanning using Bandit or Safety to detect vulnerabilities in code and dependencies.

- **FR-014**: Nightly runs MUST execute `poetry audit` to check for known vulnerabilities in dependencies and MUST create GitHub issues for HIGH/CRITICAL findings.

#### Documentation Validation

- **FR-015**: CI pipeline MUST build Sphinx documentation with `-W` flag (warnings as errors) when documentation files or constitution are modified.

- **FR-016**: Documentation build MUST validate all internal links, external links to GitHub organization repositories (github.com/ihfc-iugg/*), project domain (heatflow.world), and cross-references to specs using Sphinx linkcheck builder.

- **FR-017**: CI pipeline MUST fail documentation build if any required sections are missing from spec files or if spec files reference non-existent files.

#### Build & Deployment

- **FR-018**: CI pipeline MUST build a Docker image on every merge to main using the Dockerfile in the repository root.

- **FR-019**: Docker image MUST be tagged with both the commit SHA and `latest`, and MUST be pushed to GitHub Container Registry (GHCR) under `ghcr.io/ihfc-iugg/global-heat-flow-database`.

- **FR-020**: CI pipeline MUST automatically deploy the built Docker image to staging environment after successful build and test completion on main branch.

- **FR-021**: Staging deployment MUST use `docker-compose.yml` with environment variables from `stack.development.env`.

- **FR-022**: Staging deployment MUST run smoke tests after container startup to verify the application responds to health check endpoint and database connectivity is established.

- **FR-023**: Production deployment MUST be triggered manually via GitHub Actions workflow dispatch with required parameters: deployment target (`production`), commit SHA or tag, and deployment approval confirmation.

- **FR-024**: Production deployment MUST validate that all tests passed for the specified commit before proceeding with deployment.

- **FR-025**: Production deployment MUST use `production.yml` docker-compose configuration with environment variables from `stack.env`.

- **FR-026**: Production deployment MUST create a GitHub release with auto-generated changelog, tag the commit, and record deployment metadata in audit log.

#### Environment Configuration

- **FR-027**: CI pipeline MUST use Poetry for dependency management and MUST cache the virtual environment keyed by `poetry.lock` hash to speed up runs.

- **FR-028**: CI pipeline MUST install Python 3.13 as specified in `pyproject.toml`.

- **FR-029**: CI pipeline MUST install dependencies with `poetry install --with dev,docs` for full test/build runs.

- **FR-030**: Staging environment MUST use separate database, secrets, and domain from production (e.g., `staging.heatflow.world`).

- **FR-031**: Environment-specific configuration MUST be loaded from `.env` files or GitHub Secrets, never hardcoded in workflow files. CI pipeline MUST run secrets scanning (e.g., gitleaks) to detect accidentally committed credentials.

- **FR-032**: CI pipeline MUST set `DJANGO_ENV=development` for test runs and `DJANGO_ENV=production` for production deployments.

#### Notifications & Failure Handling

- **FR-033**: CI pipeline MUST post status checks to GitHub PR interface showing pass/fail status for each validation step (tests, linting, type checking, docs).

- **FR-034**: CI pipeline MUST provide direct links from failed status checks to detailed error logs in GitHub Actions UI.

- **FR-035**: CI pipeline MUST send notifications to team communication channel (Slack/Discord) for main branch failures, staging deployment completion, and production deployment completion.

- **FR-036**: Notification messages MUST include: event type, commit SHA, committer/deployer name, status (success/failure), and links to logs and deployed environment.

- **FR-037**: CI pipeline MUST send urgent notifications (email + chat) for nightly security scan findings with HIGH or CRITICAL severity.

- **FR-038**: CI pipeline MUST automatically create GitHub issues for security vulnerabilities with labels `security`, `dependencies`, severity label, and assigned to maintainer team.

- **FR-039**: CI pipeline MUST retry failed jobs up to 3 times with exponential backoff (1 min, 5 min, 15 min) for transient infrastructure failures.

- **FR-040**: If staging deployment fails, CI pipeline MUST automatically roll back to the previous stable Docker image and send failure notification.

#### Audit & Compliance

- **FR-041**: CI pipeline MUST record deployment events in audit log including: timestamp, environment, commit SHA, deployer identity, Docker image tag, and deployment outcome.

- **FR-042**: Audit log entries MUST be immutable and MUST be queryable by environment, date range, and deployer.

- **FR-043**: CI pipeline MUST enforce that only authorized GitHub users (maintainer team) can trigger production deployments via workflow dispatch permissions.

- **FR-044**: CI pipeline MUST validate that production deployments only occur from tagged releases or explicitly approved commit SHAs, never from arbitrary branch tips.

- **FR-045**: CI pipeline MUST generate a deployment summary for each production release including: list of commits since last release, test results, coverage report, and any security scan findings.

### Key Entities

- **CI Workflow**: Represents a GitHub Actions workflow definition (YAML file) specifying triggers, jobs, steps, and environment configuration for automated checks.

- **Test Run**: Represents an execution of the pytest suite with specific markers, configuration, and environment, producing test results and coverage data.

- **Docker Image**: Represents a built container image with unique tag (commit SHA or release version), stored in GHCR, containing the application and dependencies.

- **Deployment Event**: Represents a deployment action to a specific environment (staging/production) with timestamp, deployer, target commit, status, and audit trail.

- **Status Check**: Represents a validation result (pass/fail) for a specific CI step (tests, linting, docs build) displayed in GitHub PR interface.

- **Security Finding**: Represents a detected vulnerability from security scans with CVE identifier, severity level, affected component, and remediation guidance.

- **Coverage Report**: Represents code coverage metrics by app and file, with trends over time, uploaded to Codecov and stored for historical comparison.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Contributors receive automated feedback on PR code quality within 5 minutes of pushing changes, as measured by median CI run time.

- **SC-002**: 95% of CI failures provide actionable error messages that allow contributors to fix issues without maintainer intervention, as measured by quarterly contributor feedback form and tracking ratio of "CI help needed" issues to total CI failures.

- **SC-003**: Main branch deployments to staging complete within 15 minutes of merge, as measured by CI workflow duration from merge event to deployment complete notification.

- **SC-004**: Zero undetected regressions reach production, as measured by post-deployment incident reports (all bugs caught by CI/CD must be documented as test gaps, not pipeline failures).

- **SC-005**: Code coverage remains above 80% for all main branch merges, with critical paths (import, export, quality scoring) maintaining 100% coverage, as measured by coverage reports in CI and Codecov.

- **SC-006**: Security vulnerabilities in dependencies are detected and reported within 24 hours of public disclosure, as measured by time delta between CVE publication and GitHub issue creation.

- **SC-007**: Production deployments follow documented approval process with complete audit trail, as measured by 100% of production deployments having recorded deployer, approval, and changelog.

- **SC-008**: CI infrastructure reliability is >99%, as measured by successful pipeline completion rate excluding intentional test failures.

- **SC-009**: Contributors can independently determine what checks will run on their PR by reading documentation, as measured by zero questions in issues/discussions asking "what tests run on PRs?"

- **SC-010**: Staging environment reflects main branch within 15 minutes, enabling continuous validation of features in production-like environment, as measured by deployment lag time.

## Out of Scope

- **Automated rollback of production deployments**: Production rollback requires manual approval and execution. Automated rollback is limited to staging environment only.

- **Blue-green or canary deployment strategies**: Initial implementation uses simple docker-compose replacement. Advanced deployment strategies are deferred to future iterations.

- **Multi-region deployments**: CI/CD initially supports single-region staging and production environments. Multi-region is out of scope.

- **Performance testing in CI**: Performance benchmarks and load testing are not automated in CI pipeline. These are manual operations or separate nightly jobs not blocking PRs.

- **Automatic dependency updates**: Dependency version updates (e.g., via Dependabot) are tracked but not automatically merged. Security patches may be expedited but require manual review.

- **Mobile app or frontend-specific build steps**: This spec covers backend Django application CI/CD. If separate frontend assets require build steps, those are handled in a different workflow.

- **Database migration rollback automation**: Failed migrations in staging trigger alerts, but automatic rollback of migrations is not supported. Migration failures block deployment, requiring manual intervention.

## Assumptions

- GitHub Actions is the CI/CD platform (evidenced by existing `.github/workflows/` directory).

- Docker and docker-compose are the deployment mechanisms (evidenced by existing `Dockerfile` and `docker-compose.yml`).

- PostgreSQL is the production database (implied by Django configuration and pytest markers for database tests).

- GitHub Container Registry (GHCR) is the Docker image registry (evidenced by existing workflow configuration).

- Team communication uses Slack or Discord for notifications (specific integration details to be configured during implementation).

- Staging and production environments have separate infrastructure with distinct URLs and credentials.

- Codecov or similar service is used for coverage tracking and trend analysis (common practice for open-source projects).

- Poetry is the established dependency management tool (evidenced by `pyproject.toml` and existing workflows).

- Python 3.13 is the target runtime (specified in `pyproject.toml`).

- Maintainer team has GitHub repository admin permissions and can configure workflow secrets and deployment permissions.

## Dependencies

- **External Services**:
  - GitHub Actions (CI/CD platform)
  - GitHub Container Registry (Docker image storage)
  - Codecov or equivalent (coverage reporting)
  - Slack/Discord (team notifications)

- **Internal Configuration**:
  - `.github/workflows/` workflow definitions (must be created/updated)
  - `pyproject.toml` test and tooling configuration (already exists)
  - `Dockerfile` and `docker-compose.yml` (already exist)
  - Environment variable files: `stack.env`, `stack.development.env` (already exist)

- **Related Specifications**:
  - `001-docs-infrastructure`: Documentation validation steps depend on documentation standards and conventions
  - `002-testing-infrastructure`: Test execution strategy depends on test layers, fixtures, and conventions defined in testing infrastructure spec

## References

- Constitution Principle VII: Test-Driven Development (non-negotiable pytest-based TDD mandate)
- Existing workflows: `.github/workflows/docs-validation.yml`, `.github/workflows/docker-build-and-publish.yml`
- pytest configuration in `pyproject.toml` (test paths, markers, coverage thresholds)
- Ruff, mypy, djlint configuration in `pyproject.toml`
- FairDM framework documentation for deployment patterns
