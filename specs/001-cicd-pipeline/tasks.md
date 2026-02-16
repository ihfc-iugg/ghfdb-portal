# Tasks: CI/CD Pipeline & Automation

**Input**: Design documents from `/specs/001-cicd-pipeline/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, quickstart.md ✅, contracts/ ✅

**Tests**: Tests are NOT explicitly requested in the feature specification. This is an infrastructure feature focused on implementing the CI/CD workflows themselves.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each workflow.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This project uses standard GitHub repository structure with workflows in `.github/workflows/` and scripts in `.github/scripts/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and GitHub Actions infrastructure setup

- [X] T001 Create `.github/scripts/` directory for helper scripts
- [X] T002 [P] Create smoke-test.sh script in `.github/scripts/smoke-test.sh` for post-deployment health checks
- [X] T003 [P] Create notification helper script in `.github/scripts/notify.sh` for Slack/Discord messages
- [X] T004 Document required GitHub Secrets in `.github/SECRETS.md` (CODECOV_TOKEN, SLACK_WEBHOOK, STAGING_DEPLOY_KEY, PRODUCTION_DEPLOY_KEY)
- [X] T005 Configure Codecov integration and obtain CODECOV_TOKEN for coverage reporting

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration that MUST be complete before ANY workflow can be implemented

**⚠️ CRITICAL**: No workflow implementation can begin until this phase is complete

- [X] T006 Verify pyproject.toml has complete pytest configuration (markers, coverage threshold, Django settings)
- [X] T007 Verify pyproject.toml has complete Ruff configuration (linting rules, formatting settings)
- [X] T008 Verify pyproject.toml has complete mypy configuration (project path, Django plugin)
- [X] T009 Create or verify docker-compose.yml is configured for staging deployment
- [X] T010 Create or verify production.yml is configured for production deployment
- [X] T011 Verify stack.development.env has staging environment variables
- [X] T012 Verify stack.env has production environment variables (template only, secrets go in GitHub)

**Checkpoint**: Foundation ready - workflow implementation can now begin in parallel

---

## Phase 3: User Story 1 - Contributor PR Validation (Priority: P1) 🎯 MVP

**Goal**: Fast automated feedback on code quality, tests, and documentation for pull requests

**Independent Test**: Open a PR with intentional linting error → CI runs → Status check shows failure with actionable message → Fix and push → Status check passes

### Implementation for User Story 1

- [X] T013 [P] [US1] Create `.github/workflows/pr-validation.yml` workflow file with pr_request trigger
- [X] T014 [US1] Add checkout and Python 3.13 setup steps to pr-validation.yml
- [X] T015 [US1] Add Poetry installation and caching steps to pr-validation.yml using snok/install-poetry@v1
- [X] T016 [US1] Add dependency installation step with `poetry install --with dev,docs` to pr-validation.yml
- [X] T017 [US1] Add Ruff linting step with `poetry run ruff check .` to pr-validation.yml
- [X] T018 [US1] Add Ruff formatting check step with `poetry run ruff format --check .` to pr-validation.yml
- [X] T019 [US1] Add mypy type checking step with `poetry run mypy project` to pr-validation.yml
- [X] T020 [US1] Add fast unit test step with pytest markers and `--nomigrations --reuse-db` flags to pr-validation.yml
- [X] T021 [US1] Add coverage collection with `--cov=project --cov-report=xml` to pr-validation.yml
- [X] T022 [US1] Add Codecov upload step with codecov/codecov-action@v4 to pr-validation.yml
- [X] T023 [US1] Add documentation validation job (conditional on docs file changes) to pr-validation.yml
- [X] T024 [US1] Configure Sphinx build with `-W` flag (warnings as errors) in docs validation job
- [X] T024a [US1] Configure Sphinx linkcheck builder in docs validation job to validate external links (github.com/ihfc-iugg/*, heatflow.world)
- [X] T025 [US1] Add concurrency group to pr-validation.yml to cancel stale PR runs
- [X] T026 [US1] Set 10-minute timeout for pr-validation.yml jobs
- [X] T027 [US1] Test pr-validation.yml by opening a test PR with intentional failures, verify status checks appear
- [X] T027a [US1] Add djlint template validation step to pr-validation.yml (conditional on template file changes in templates/)
- [X] T031a [P] [US2] Add secrets scanning job to pr-validation.yml using gitleaks-action to detect hardcoded credentials

**Checkpoint**: At this point, PR validation workflow should run on every pull request and provide fast feedback within 5 minutes

---

## Phase 4: User Story 2 - Main Branch Integration & Deployment (Priority: P1)

**Goal**: Comprehensive validation, Docker builds, and automated staging deployment on main branch merges

**Independent Test**: Merge a PR to main → Full test suite runs with PostgreSQL → Docker image builds → Staging deploys → Team receives notification

### Implementation for User Story 2

- [X] T028 [P] [US2] Create `.github/workflows/main-integration.yml` workflow file with push to main trigger
- [X] T029 [US2] Add `test-full-suite` job with PostgreSQL 15 service container to main-integration.yml
- [X] T030 [US2] Add checkout, Python setup, and Poetry installation steps to test-full-suite job
- [X] T031 [US2] Configure DATABASE_URL environment variable to connect to PostgreSQL service
- [X] T032 [US2] Add Django migrations step with `poetry run python manage.py migrate --noinput` to test-full-suite job
- [X] T033 [US2] Add full pytest suite execution with `poetry run pytest --reuse-db` (no marker exclusions) to test-full-suite job
- [X] T034 [US2] Add coverage collection and Codecov upload with flags=main-tests to test-full-suite job
- [X] T035 [P] [US2] Create `build-docker-image` job that depends on test-full-suite success
- [X] T036 [US2] Add Docker Buildx setup with docker/setup-buildx-action@v3 to build-docker-image job
- [X] T037 [US2] Add GHCR login step with docker/login-action@v3 to build-docker-image job
- [X] T038 [US2] Add Docker metadata extraction with tags for commit SHA and latest to build-docker-image job
- [X] T039 [US2] Add Docker build and push step with GitHub Actions cache to build-docker-image job
- [X] T040 [US2] Add GitHub deployment record creation with actions/github-script@v7 to build-docker-image job
- [X] T041 [P] [US2] Create `deploy-staging` job that depends on build-docker-image success
- [X] T042 [US2] Add SSH agent setup with webfactory/ssh-agent@v0.9.0 and STAGING_DEPLOY_KEY to deploy-staging job
- [X] T043 [US2] Add deployment command using ssh to execute `docker-compose -f docker-compose.yml pull && docker-compose up -d` on staging environment server
- [X] T044 [US2] Add smoke test execution calling `.github/scripts/smoke-test.sh` with staging URL
- [X] T045 [US2] Add retry logic (3 attempts, 30s delay) to smoke test step
- [X] T046 [US2] Add deployment status update (success) with actions/github-script@v7 to deploy-staging job
- [X] T047 [US2] Add rollback-on-failure step that runs if deployment fails, restores previous image
- [X] T048 [P] [US2] Create `notify-team` job that always runs after deploy-staging completes
- [X] T049 [US2] Add Slack notification with 8398a7/action-slack@v3 including commit SHA, deployer, status, links
- [X] T050 [US2] Configure job dependencies (test → build → deploy → notify) in main-integration.yml
- [X] T051 [US2] Set appropriate timeouts for each job (test=20min, build=15min, deploy=10min)
- [X] T052 [US2] Test main-integration.yml by merging a test PR to main, verify full pipeline executes

**Checkpoint**: At this point, main branch merges trigger full validation and staging deployment within 15 minutes

---

## Phase 5: User Story 4 - Test Execution Strategy & Coverage (Priority: P1)

**Goal**: Enforce test categorization and coverage thresholds across PR and main workflows

**Independent Test**: Run pytest with different marker combinations → Verify correct test selection → Verify coverage enforcement

**Note**: This phase refines and validates test execution from US1 and US2

### Implementation for User Story 4

- [X] T053 [US4] Verify pytest markers are properly defined in pyproject.toml (integration, contract, slow, external, django_db)
- [X] T054 [US4] Add pytest marker documentation comment to pyproject.toml explaining when each marker should be used
- [X] T055 [US4] Verify coverage configuration in pyproject.toml includes source=["project"], omit patterns, fail_under=80
- [X] T056 [US4] Add coverage per-app reporting configuration to show heat_flow, ghfdb, review separately
- [X] T057 [US4] Update pr-validation.yml to explicitly document which markers are excluded (integration, contract, slow, external)
- [X] T058 [US4] Update main-integration.yml to explicitly document that all markers are included
- [X] T059 [US4] Add coverage report format that clearly categorizes results by marker type
- [X] T060 [US4] Create docs/development/ci-cd-guide.md contributor guide explaining test strategy and marker usage
- [X] T061 [US4] Test coverage enforcement by submitting PR with intentionally low coverage, verify it fails

**Checkpoint**: Test execution strategy is properly configured and documented, coverage thresholds enforced

---

## Phase 6: User Story 3 - Scheduled & On-Demand Operations (Priority: P2)

**Goal**: Nightly comprehensive checks and manual production deployment capability

**Independent Test**: Manually trigger nightly workflow → Security scans run → Dependency audit completes → Report generated

### Implementation for User Story 3 - Nightly Checks

- [X] T062 [P] [US3] Create `.github/workflows/nightly-checks.yml` workflow file with schedule trigger (cron: `0 3 * * *`)
- [X] T063 [US3] Add workflow_dispatch trigger to nightly-checks.yml to allow manual runs
- [X] T064 [P] [US3] Create `security-scan` job in nightly-checks.yml
- [X] T065 [US3] Add Bandit security scanning step with `poetry run bandit -r project/ -f json -o bandit-report.json`
- [X] T066 [US3] Add poetry audit step with `poetry audit` for dependency vulnerability checking
- [X] T067 [US3] Add security findings parser script to classify HIGH/MEDIUM/LOW severity
- [X] T068 [US3] Add GitHub issue creation step for HIGH/CRITICAL findings using actions/github-script@v7
- [X] T069 [US3] Add security report upload as artifact
- [X] T070 [P] [US3] Create `test-comprehensive` job with PostgreSQL service in nightly-checks.yml
- [X] T071 [US3] Add full pytest suite including slow/external markers with fresh database (no --reuse-db)
- [X] T072 [US3] Add flaky test detection script that compares results from past 7 days
- [X] T073 [US3] Add flaky test report generation and upload as artifact
- [X] T074 [US3] Add coverage trends upload to Codecov with flags=nightly
- [X] T075 [P] [US3] Create `dependency-audit` job in nightly-checks.yml
- [X] T076 [US3] Add `poetry show --outdated --format json` step to find outdated dependencies
- [X] T077 [US3] Add deprecated packages check script querying PyPI deprecation warnings
- [X] T078 [US3] Add combined dependency report generation (security, outdated, deprecated)
- [X] T079 [P] [US3] Create `coverage-trends` job that depends on test-comprehensive
- [X] T080 [US3] Add Codecov API query script to retrieve 7-day coverage trend
- [X] T081 [US3] Add coverage trend analysis with threshold alert if decreased >2% in a week
- [X] T082 [US3] Add GitHub issue creation for declining coverage trends
- [X] T083 [P] [US3] Create `notify-results` job that always runs after all nightly jobs
- [X] T084 [US3] Add artifact collection step to download all reports from previous jobs
- [X] T085 [US3] Add summary email generation with HTML format including all findings
- [X] T086 [US3] Add email notification with dawidd6/action-send-mail@v3 to maintainer list
- [X] T087 [US3] Add Slack webhook notification with summary metrics
- [X] T088 [US3] Set appropriate timeouts for nightly jobs (security=15min, test=30min, audit=10min)
- [X] T089 [US3] Test nightly-checks.yml by manually triggering workflow, verify all jobs complete

### Implementation for User Story 3 - Production Deployment

- [X] T090 [P] [US3] Create `.github/workflows/production-deploy.yml` workflow file with workflow_dispatch trigger only
- [X] T091 [US3] Add workflow inputs: environment (choice: production), commit_sha (string), approval_confirmation (string)
- [X] T092 [P] [US3] Create `validate-deployment` job in production-deploy.yml
- [X] T093 [US3] Add approval confirmation validation script checking input == 'APPROVED'
- [X] T094 [US3] Add environment validation script checking input == 'production'
- [X] T095 [US3] Add checkout step for target commit SHA from workflow input
- [X] T096 [US3] Add test verification step using actions/github-script@v7 to query main-integration.yml success for commit
- [X] T097 [US3] Add commit authorization check verifying commit is tagged or on main branch history
- [X] T098 [US3] Add pre-deployment report generation collecting commits, test results, coverage, security findings
- [X] T099 [P] [US3] Create `build-release-image` job depending on validate-deployment
- [X] T100 [US3] Add version tag extraction script (parse tag or use SHA)
- [X] T101 [US3] Add Docker build and push with release version and production tags
- [X] T102 [P] [US3] Create `deploy-production` job depending on build-release-image with environment: production
- [X] T103 [US3] Add deployment start recording with GitHub deployment API (status: in_progress)
- [X] T104 [US3] Add SSH setup with PRODUCTION_DEPLOY_KEY
- [X] T105 [US3] Add production state backup command creating rollback tags
- [X] T106 [US3] Add production deployment command using production.yml docker-compose config
- [X] T107 [US3] Add container health check polling (30s max wait)
- [X] T108 [US3] Add smoke test execution calling `.github/scripts/smoke-test.sh` with production URL
- [X] T109 [US3] Add deployment success recording updating GitHub deployment status
- [X] T110 [US3] Add failure handler with automatic rollback to backup image if deployment fails
- [X] T110a [P] [US3] Create `.github/scripts/query-audit-log.sh` script to query GitHub Deployments API with filters for environment, date range, and deployer
- [X] T111 [P] [US3] Create `create-release` job depending on deploy-production (conditional: success and tag deploy)
- [X] T112 [US3] Add changelog generation with github-changelog-generator-action@v2
- [X] T113 [US3] Add GitHub release creation with actions/create-release@v1 including changelog
- [X] T114 [US3] Add deployment report attachment to GitHub release
- [X] T115 [P] [US3] Create `notify-deployment` job that always runs after deploy-production
- [X] T116 [US3] Add team Slack notification with deployment status, version, deployer, links
- [X] T117 [US3] Add stakeholder email notification with deployment report details
- [X] T118 [US3] Configure GitHub environment protection rules requiring maintainer approval for production
- [X] T119 [US3] Set appropriate timeouts for production deploy jobs (validate=5min, build=15min, deploy=15min)
- [X] T120 [US3] Test production-deploy.yml validation by attempting deploy without APPROVED confirmation, verify rejection
- [X] T121 [US3] Document production deployment procedure in docs/development/ci-cd-guide.md

**Checkpoint**: Nightly checks run on schedule, production deployment requires manual trigger with approval

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, testing, and refinements across all workflows

- [X] T122 [P] Complete docs/development/ci-cd-guide.md with all workflow documentation
- [X] T123 [P] Update CONTRIBUTING.md to reference CI/CD guide and explain what runs on PRs
- [X] T124 [P] Add CI/CD troubleshooting section to docs/development/ci-cd-guide.md
- [X] T125 [P] Create `.github/SECRETS.md` with complete list of required secrets and setup instructions
- [X] T126 Verify `.github/scripts/smoke-test.sh` has proper error handling and timeout
- [X] T127 Verify `.github/scripts/notify.sh` handles both success and failure cases
- [X] T128 Add workflow status badges to README.md for pr-validation and main-integration
- [X] T129 Create workflow diagram showing PR → main → staging → production flow
- [X] T130 Verify all workflow files have appropriate comments explaining complex steps
- [X] T130a [P] Create contributor feedback form (Google Forms or GitHub Discussions template) for quarterly CI/CD experience survey
- [ ] T131 Run complete CI/CD validation: PR → merge → staging deploy → manual production deploy
- [X] T132 Validate quickstart.md matches actual implemented workflows
- [X] T133 Update specs/001-cicd-pipeline/checklists/requirements.md marking feature complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - PR validation is MVP
- **User Story 2 (Phase 4)**: Depends on Foundational - Main integration extends PR validation concepts
- **User Story 4 (Phase 5)**: Depends on US1 and US2 - Refines test execution from both workflows
- **User Story 3 (Phase 6)**: Depends on US2 - Nightly checks extend main integration patterns, production deploy is separate
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - MVP, no dependencies on other stories
- **User Story 2 (P1)**: Can start after US1 - Extends PR validation patterns and shares setup steps
- **User Story 4 (P1)**: Validates US1 and US2 - Requires those workflows to exist
- **User Story 3 (P2)**: Can start after US2 - Nightly extends main integration, production is independent

### Within Each User Story

- Workflow file creation before adding jobs
- Setup steps (checkout, Python, Poetry) before action steps
- Job dependencies must be explicit (e.g., deploy depends on build)
- Test workflows by triggering them manually before relying on automatic triggers

### Parallel Opportunities

**Phase 1 Setup**: T002 and T003 (scripts) can run in parallel

**Phase 2 Foundational**: T006, T007, T008 (config verification) can run in parallel; T011, T012 (environment files) can run in parallel

**Phase 3 User Story 1**: T013 can start first, then T014-T022 (workflow steps) can be added incrementally

**Phase 4 User Story 2**: T028-T034 (test job), T035-T040 (build job), T041-T047 (deploy job), T048-T049 (notify job) can be developed in parallel once job structure is defined

**Phase 5 User Story 4**: T053-T056 (config updates), T057-T059 (workflow updates), T060 (docs) can run in parallel

**Phase 6 User Story 3**: Nightly checks (T062-T089) and Production deploy (T090-T121) are completely independent and can be developed in parallel

**Phase 7 Polish**: T122, T123, T124, T125 (documentation) can all run in parallel

---

## Parallel Example: User Story 2 (Main Integration)

```bash
# Once workflow structure is defined, these jobs can be developed in parallel:
Task: "Create test-full-suite job with PostgreSQL" (T029-T034)
Task: "Create build-docker-image job" (T035-T040)
Task: "Create deploy-staging job" (T041-T047)
Task: "Create notify-team job" (T048-T049)

# Then integrate them with dependencies
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T012) ← CRITICAL
3. Complete Phase 3: User Story 1 (T013-T027) ← **PR Validation MVP**
4. **STOP and VALIDATE**: Open test PRs, verify fast feedback works
5. Deploy documentation, train contributors

### Incremental Delivery

1. **MVP**: Setup + Foundational + US1 → PR validation working (5min feedback)
2. **Phase 2**: Add US2 → Main integration + staging deploy (15min deploy)
3. **Phase 3**: Add US4 → Test strategy validated and documented
4. **Phase 4**: Add US3 nightly → Security scanning and dependency audit
5. **Phase 5**: Add US3 production → Manual production deployment
6. **Phase 6**: Polish → Complete documentation and refinements

Each phase adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T012)
2. **Once Foundational is done:**
   - Developer A: User Story 1 (PR validation) - T013-T027
   - Developer B: User Story 2 (main integration) - T028-T052
   - Developer C: User Story 4 (test strategy docs) - T053-T061
3. **After US1 and US2 complete:**
   - Developer D: User Story 3 nightly - T062-T089
   - Developer E: User Story 3 production - T090-T121
4. **Final sprint:**
   - All developers: Phase 7 polish in parallel

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 7 tasks ← BLOCKS everything
- **Phase 3 (US1 - PR Validation)**: 17 tasks ← MVP (added T024a, T027a)
- **Phase 4 (US2 - Main Integration)**: 26 tasks (added T031a)
- **Phase 5 (US4 - Test Strategy)**: 9 tasks
- **Phase 6 (US3 - Nightly + Production)**: 61 tasks (added T110a)
- **Phase 7 (Polish)**: 13 tasks (added T130a)
- **Total**: 138 tasks

---

## Notes

- [P] tasks = different files or independent jobs, no dependencies
- [Story] label maps task to specific user story from spec.md
- Each workflow file should be testable independently via manual trigger
- Verify workflows work in test PRs before relying on automatic triggers
- GitHub Secrets must be configured before workflows can succeed
- Staging and production servers must have deployment infrastructure ready
- Stop at any checkpoint to validate workflow independently
- Commit workflow files incrementally (one job at a time) to enable debugging
