# Tasks: Demo data for development

**Input**: Design documents from `specs/008-demo-data/`

**Prerequisites**: plan.md, spec.md, research.md, decisions.md

**Tests**: required. Every task writes its failing test first. Test modules mirror the source module
they exercise and group tests in `Test<Subject>` classes. The command's tests run at the smallest
size (4 datasets), seeded in a function-scoped fixture. Every dataset count uses
`Dataset.all_objects`, because `Dataset.objects` hides private datasets.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel with its neighbours (different files, no shared dependency)
- **[Story]**: the user story the task serves

---

## Phase 0: Foundational

- [x] T001 Move the `fairdm-docs` pin to `847fee1a27862e20c1fac1f7e4c9a4d2100473cd` in
      `pyproject.toml`, `uv lock`, `uv sync --python 3.13 --group docs`, and build the docs with
      `uv run sphinx-build -b html docs docs/_build/html -W --keep-going`. Done directly by the
      orchestrator (one line, no design content).

## Phase 1: User Story 1 — A developer fills an empty database with demo data (P1)

**Goal**: one command, no options, fills an empty database with valid demo data and computed scores.

**Independent test**: run the command at the smallest size against the test database, then assert
every heat flow model holds records, every record passes `full_clean`, every score equals a fresh
recompute, and every concept field holds a concept of its vocabulary.

- [x] T002 [US1] `project/heat_flow/demo.py` per plan.md › *Design* › `demo.py`: `Region`,
      `REGIONS`, `SITES_PER_DATASET`, `CHILDREN_CYCLE`, `DemoGraph`. Tests in
      `tests/test_heat_flow/test_demo.py`:
      - `TestRegions`: every environment and exploration method is a vocabulary value, the bounds
        are valid, and about 40 % of the regions are marine
      - `TestDemoGraph`, building one graph into a `DatasetFactory` dataset:
        - every model has rows
        - every multi-table record passes `full_clean()`, and every child's value equals its
          gradient times its conductivity
        - every site has exactly one parent, and coordinates are pairwise distinct
        - top is above bottom
        - corrections satisfy `VALID_STATUS_FOR_TYPE`, and probe intervals have probe metadata
        - every concept M2M is populated from its own vocabulary
        - `ghfdb_id` is set on all parents and children when `next_ghfdb_id` is given, and on
          none when it is `None`
        - building a second graph raises no coordinate collision, and a forced collision is
          redrawn
        - every generated quantity lies within its range in research R3 (one parametrised test)
        - every correction's status is accepted by `save()` for its type, and no child has a type
          twice
        - every multi-table record carries the graph's dataset
- [x] T003 [US1] `project/review/management/commands/seed_demo_data.py`, steps 1, 2, 4, 5 and 6 of
      plan.md › *Design* › the command, with the size fixed at the default. Steps 3 (accounts) and
      the state plan belong to US3. Until then every dataset is COMPLETE, uploaded and decided by a
      plain demo user. Tests in
      `tests/test_review/test_management/test_commands/test_seed_demo_data.py`:
      - `TestSeedDemoData`:
        - a run at the default size on an empty database fills every heat flow model, and every
          dataset is marked `options__demo_data=True`
        - every child and parent `quality_scheme` equals `SCHEME_REVISION`, and the scores of
          children, parents, gradients and conductivities (score, missing mark, scheme) equal
          those after `call_command("refresh_quality", "--all")`
        - with the `Concept` rows deleted inside the test's own transaction, the command loads the
          vocabularies and every concept field of the seeded records is populated
        - each dataset has its literature, with a `10.5072` DOI and a `demo-` key, and its
          contributors
        - a private dataset that existed before the run is unchanged afterwards
      - `TestSeedDemoDataEnvironment`: with `DJANGO_ENV` resolved to `production` the command
        raises `CommandError` and the count of every model is unchanged
- [x] T004 [US1] Documentation: `docs/development/demo-data.md` per plan.md › *Documentation*,
      the Development toctree entry in `docs/index.md`, a line in step 2a of
      `docs/development/getting-started.md`, and a **Demo data** entry in `CONTEXT.md`. The docs
      build with `-W` stays green.

## Phase 2: User Story 2 — A developer chooses how much data they get (P1)

**Goal**: one size, counted in datasets, sets the scale; reruns add more.

**Independent test**: seed at 4 and at 8 and compare counts; seed twice and check the second run
adds beside the first.

- [x] T005 [US2] `--size` with `DEFAULT_SIZE`, `MIN_SIZE`, `MAX_SIZE` (plan.md › the command ›
      Options). Tests in the command's test module, `TestSeedDemoDataSize`:
      - size 4 gives exactly 4 demo datasets, 80 sites and 200 children
      - size 8 doubles each count
      - sizes 0, -1, 3 and 201 each raise `CommandError` naming the range and write nothing
      - a second run at size 4 brings the totals to 8 datasets, 160 sites and 400 children, with
        every site's coordinates still distinct and the earlier demo datasets unchanged
      - every published identifier stays unique across both runs
      - `MAX_SIZE * 50` is at least 10,000 children, asserted from the constants and not by a run
        at that size
      Update `docs/development/demo-data.md` for the option.

## Phase 3: User Story 3 — A developer sees the portal in every state (P2)

**Goal**: every assessment state, both visibilities, and an account for each role.

**Independent test**: seed at size 4 and count by state and visibility, sign in as each account.

- [x] T006 [US3] Step 3 (accounts) and the state plan of plan.md › the command. Tests in the
      command's test module:
      - `TestSeedDemoDataStates`:
        - size 4 holds one assessment in each of the four states
        - COMPLETE datasets are public and published, the others private and unpublished
        - parents and children in unpublished datasets carry no `ghfdb_id`
        - CHANGES_REQUESTED and COMPLETE assessments are decided by the demo curator
        - every assessment is uploaded by the demo assessor, who is also its reviewer
      - `TestSeedDemoDataAccounts`:
        - the five FairDM development accounts and the five `example.com` accounts exist with
          confirmed addresses, and each can log in through `Client.login` with `password`
        - the assessor is in `Data Assessor` and the curator in `Data Curator`
        - a rerun creates no second account
        - the curator sees at least one assessment waiting for a decision (`is_data_curator` and
          `Review.objects.filter(state=AWAITING_DECISION)`)
      - `TestSeedDemoDataVisibility`: an anonymous request to the dataset list page and to the
        API's dataset endpoint returns only the public demo datasets, and the demo assessor can
        see its private demo datasets
      Account tests request the `data_assessor_group` and `data_curator_group` fixtures.
      Update `docs/development/demo-data.md` with the accounts and what each sees.

## Dependencies

T001 first. T002 → T003 → T004 → T005 → T006. Every task changes the command or its tests, so none
run in parallel.

## Phase 4: Fixes from the code review

- [ ] T007 [US1] DOC-001: the compose command on `docs/development/demo-data.md` runs `uv run python`.
- [ ] T008 [US1] DOC-002: docstrings with Args/Returns/Raises on every new function in
      `heat_flow/demo.py` and the command; `DemoGraph`'s arguments in its class docstring.
- [ ] T009 [US1] TEST-001: the production-refusal test fails when the command's own refusal is
      removed (assert nothing is called before the refusal).
- [ ] T010 [US1] COR-001: every region lies wholly on land or wholly at sea.
- [ ] T011 [US1] SIMP-001, TEST-002: inline `_round`; delete the unused module-level fixture.
- [x] T012 Move the `fairdm` pin to `f69c9cb1`, its latest commit, which moves list pages onto
      django-mvp 0.29 filtersets. The assessment list's title search moves from the view's
      `search_fields` onto `ReviewFilter` as an `mvp.filters.SearchFilter`.
- [x] T013 Fix `IntervalConductivity.clean()` to compare magnitudes, so a saved conductivity can be
      validated (#283). The generator's tests run `full_clean()` on conductivities too.
