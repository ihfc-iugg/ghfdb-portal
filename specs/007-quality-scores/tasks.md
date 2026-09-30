# Tasks: Quality scores calculated with the current community scheme

**Input**: Design documents from `specs/007-quality-scores/`

**Prerequisites**: plan.md, spec.md, research.md, decisions.md

**Tests**: required. Every task writes its failing test first (Article I). Test modules mirror the
source module they exercise and group tests in `Test<Subject>` classes. Records come from
`tests/factories.py`. Every concept a score reads is set explicitly, because the factories attach
random ones. Expected values for the scheme come from research.md R3, the toolbox's own output,
never from re-deriving the rule in the test.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel with its neighbours (different files, no shared dependency)
- **[Story]**: the user story the task serves

---

## Phase 1: User Story 1 — A gradient and a conductivity carry their own scores (P1)

**Goal**: every gradient and conductivity carries its uncorrected score, its missing-information
mark and the scheme revision, calculated from the measurement, its interval and its site.

**Independent test**: build gradients and conductivities at probe and borehole sites across the
scheme's criteria and compare their stored scores with research R3.

- [ ] T001 [US1] Rewrite `project/heat_flow/quality.py` per plan.md › *The scheme*:
      `SCHEME_REVISION`, `UScoreOptions`, `MScoreOptions` (with M1x–M4x), `SubScore`, `route()`,
      the private evaluators, and `ProbeRules` and `BoreholeRules` with `gradient()` and
      `conductivity()`, using the tables in research R1 and the concept mapping in R4 (D15, D16,
      D17). `QualityScheme` is T004's. Reduce `project/heat_flow/utils.py` to re-exporting the two
      choice lists. Tests first in `tests/test_heat_flow/test_quality.py`:
      - routing for every exploration-method concept and for an empty one (US1-7, FR-003)
      - every probe and borehole criterion, including each bin edge and the multi-valued case (D8)
      - empty against unspecified input (US1-5, US1-6, FR-009)
      - the borehole gate (US1-4)
      - the borehole location's unmatched mark and the unresolvable temperature case (D16)
      - the uncorrected T and TC for each R3 case, and the corrected T and TC that the three
        keyword arguments produce (tilt, bottom water, in-situ status or `None`)

      Hold the evaluators on a `Criterion` class, and have `route()` return the rules class (plan.md).
      At this point the models still carry the old methods that import from the old module. Keep
      the tree importable: remove `HeatFlow.get_U_score` and `get_M_score` and their imports here,
      since nothing else calls them.
- [ ] T001a [US1] Make `MultiConceptWidget` (`project/ghfdb/resources/widgets.py`) store the
      vocabulary's own `unspecified` concept for an `[unspecified]` cell wherever the vocabulary
      defines one. A blank cell stays empty (D23). Tests first in
      `tests/test_ghfdb/test_resources/test_widgets.py`: both directions for a vocabulary with and
      without an `unspecified` concept, and the export round trip writing it back. State the change
      in `docs/guides/importing-data.md`.
- [ ] T002 [US1] Add the gradient and conductivity fields from D18 (nullable `score` with no 0–1
      bound, `score_missing`, `quality_scheme`, and an index on the conductivity's `score`). Add
      `refresh_score()` on both models, writing by `update` and rounding to three places. Delete
      both `calculate_score()` methods. Add `project/heat_flow/signals.py` with the `Recalculation`
      class and the first receivers: a gradient or conductivity refreshes its own score when saved,
      and on `post_add`, `post_remove` and `post_clear` of any concept field its score reads.
      Connect them in `HeatFlowSchemaConfig.ready()`. Generate one migration. Tests first:
      - in `tests/test_heat_flow/test_models/test_child.py`, the stored values after save and
        after a concept change, and the revision (US1-1 to US1-3, FR-002, FR-014)
      - one gradient used by two children with different corrections keeps one score (US1-8,
        SC-003)
      - in `tests/test_heat_flow/test_signals.py`, the receivers do not re-enter
      - the existing `test_conductivity_vocabulary_fields_count_and_score_persist`
        (`test_child.py`) asserts that a supplied `score=0.9` persists. Replace that one assertion
        with the calculated score, per FR-002 and ADR-0004 (D24). Leave the rest of the test
        unchanged.
- [ ] T003 [US1] Documentation for the measurement scores:
      - Write `docs/guides/quality-scores.md` with the introduction (toolbox V0.2, reference,
        ADR-0004), the T-score and TC-score sections (both routes, the missing-information mark,
        not determined), and the decisions that bear on them (D1, D8, D10, D12, D15–D17). Link it
        from `docs/index.md`.
      - In `CONTEXT.md` › Quality, define T-score, TC-score, uncorrected score, missing-information
        mark and scheme revision, and remove the "live gap" note.
      - Add the new fields to `docs/ghfdb_fields.md` and `docs/data_models/ghfdb-erd.md`.

**Checkpoint**: measurements are scored, stored, documented and green.

---

## Phase 2: User Story 2 — A child carries its quality code (P1)

**Goal**: every child carries a U-score, corrected T and TC, an M-score, seven flags and a code.

- [ ] T004 [US2] Add `QualityScheme` to `project/heat_flow/quality.py`: `u_score`, `m_score`,
      `perturbation_flags` and `code`. Tests first in `tests/test_heat_flow/test_quality.py`:
      - U-score bands, zero and empty inputs, a negative value, the six-place rounding (US2-1,
        US2-2)

      Also amend the *Project additions* bullet in `docs/contributing/standards/testing.md`: the
      U-score and M-score reference values are toolbox V0.2's own output (research R3), and the
      paper's examples are used only where they agree (D10, D12).
      - M classes, the boundary products 0.25, 0.5 and 0.75 taking the better class, the `x`
        suffix and `Mx` (US2-7 to US2-9, FR-007, FR-008)
      - every flag encoding (US2-10, FR-011)
      - the code format (FR-010)
      - the U, M and flags of every R3 case (SC-001)
- [ ] T005 [US2] **Held until the maintainer rules on research R5.** Make `HeatFlowCorrection` accept
      "tilt corrected" on type T and "considered – p/T/pT" on type IS, as ruled, update the valid-
      status table in `docs/ghfdb_fields.md`, and adjust the existing assertion the ruling names.
- [ ] T005a [US2] Make `_parse_correction_status` (`project/ghfdb/resources/child.py`) resolve a
      cell by its status label as well as its key, normalised the way the vocabulary widgets
      normalise. A status the type does not accept falls back to `-` (D22). Tests first in
      `tests/test_ghfdb/test_resources/test_child.py`: `[Present and corrected]`,
      `[Present and not corrected]`, `[Present not significant]` and `[not recognized]` on S, SUR
      and HR, plus a label the type refuses, which stores `-`. State the change in
      `docs/guides/importing-data.md`, including that records imported earlier keep `-` until they
      are re-imported.
- [ ] T006 [US2] Add the child fields from D18 and `HeatFlow.refresh_quality()` per plan.md. Delete
      `get_quality` and `get_perturbation_effects`, and the old scoring classes if T001 left any. Receivers: a child refreshes on
      its own save, and on save or delete of one of its corrections. Parents are T008's. Migration
      changes fold into the feature's single migration. Tests first in
      `tests/test_heat_flow/test_models/test_child.py`:
      - US2-1 to US2-12 through stored fields, including a query on `T_score` and `TC_score`
        returning exactly the children whose corrected score matches (US2-12, FR-005)
      - the R3 child cases end to end from factories, which covers X1–X5, P1–P5, B1–B9, N1 and N2
      - US2-3 and US2-5 need T005. Until it lands, cover the waiver and the agreement through
        `QualityScheme` and the rule classes, and leave those two model-level cases for T005.
      - the existing fresh-child assertion (`Ux`, `Mx`) must still hold unchanged
- [ ] T007 [US2] Documentation for the child's scores: the guide sections on the U-score, corrected
      scores and the three child rules (D2, D3, D11, D13, D14), the M-score, the flags and the code
      (D5–D7), and how the portal's corrected T and TC equal the toolbox's per-row values (FR-020).
      `CONTEXT.md`: correct the quality-code entry to the dotted code and the flag letters and
      order, and add "corrected score". Update `docs/ghfdb_fields.md` and the ERD for the child
      fields.

**Checkpoint**: every child carries its code; conformance cases green.

---

## Phase 3: User Story 3 — A parent inherits its quality from its children (P2)

- [ ] T008 [US3] Add `QualityScheme.inherit()`, the parent fields from D18 and
      `ParentHeatFlow.refresh_quality()`, and delete `ParentHeatFlow.get_quality`. Receivers: a
      child's save refreshes its parent, and the parent it left when `parent` changed (read in
      `pre_save`). A child's deletion refreshes its former parent. Tests first in
      `tests/test_heat_flow/test_quality.py` (the ranking, including marked against unmarked and
      `Mx` last, and the flags tie-break) and `tests/test_heat_flow/test_models/test_parent.py`
      (US3-1 to US3-7):
      - one non-relevant only child passes its quality
      - several children with none relevant gives not determined
      - deleting the last child leaves not determined
      - moving a child refreshes both parents
      - the parent's value is untouched
      - saving a parent does not recalculate it, so the existing persistence test still holds
      - the existing `test_two_determinations_under_one_parent_repeat_its_values`
        (`tests/test_ghfdb/test_viewsets.py`) sets the parent's quality before building its
        children, which now overwrite it (FR-012). Set the quality after the children are built.
        That changes the test's setup order, not its assertion (D24).
- [ ] T009 [US3] Documentation: the guide's inheritance section (D9, the single-child rule) and the
      `CONTEXT.md` inheritance text. Update `docs/ghfdb_fields.md` and the ERD for the parent
      fields.

**Checkpoint**: parents inherit, documented and green.

---

## Phase 4: User Story 4 — Scores stay current (P2)

- [ ] T010 [US4] Complete the recalculation table in plan.md: interval, probe metadata and site
      saves cascade to their measurements, children and parents, and a measurement's own change
      cascades to its children and their parents. Delete receivers go through the collector and
      refresh on commit (D24). Tests first in
      `tests/test_heat_flow/test_signals.py`, one per row of the table (US4-1 to US4-3). Each
      asserts that every score depending on the change moved and that one not depending on it did
      not. Include probe metadata deleted, and a whole dataset deleted: no error, no stale parent
      and no per-correction refresh. Add a helper that recomputes every score into memory and
      compares it with what is stored, and use it after each change (SC-004).
- [ ] T011 [US4] Add `Recalculation.deferred()` and wire it into `GHFDBChildImportResource` per
      plan.md › *Deferral during import*. Tests first under `tests/test_ghfdb/test_resources/`:
      - an imported file leaves every record scored (US4-4)
      - each record is refreshed once, not per save
      - a dry run leaves nothing stored
      - a failed import leaves recalculation switched back on
      - a quality code in the file is still refused (ADR-0004)
- [ ] T012 [US4] Add the management command `refresh_quality` (stale-only by default, `--all`) and
      run it after `migrate` in `deploy/Dockerfile`. Tests first in
      `tests/test_heat_flow/test_management/test_commands/test_refresh_quality.py`. Iterate in
      chunks, with the concept fields and corrections prefetched:
      - records written before scoring existed (revision null) are scored (US4-6, FR-015)
      - a second run changes nothing, and `--all` over unchanged inputs gives identical values
        (US4-7, FR-016)
      - every stored score reads back its revision (US4-5, SC-005)
- [ ] T013 [US4] Documentation: the guide's "how scores stay current" section, naming
      `refresh_quality --all` as the repair for bulk writes (D19, D20). `deploy/README.md`: what the
      container now runs on start, the first run's cost at release size, and that an error in it
      stops start-up.

**Checkpoint**: no stored score can be stale without a write that bypasses the ORM.

---

## Phase 5: User Story 5 — A reader sees how a child's quality was reached (P3)

- [ ] T014 [US5] Override `templates/measurement/detail.html` per plan.md (placeholder alert dropped) and add
      `tests/test_templates/` to `non-mirror-paths` in `pyproject.toml` with a comment saying why.
      Tests first in `tests/test_templates/test_measurement_detail.py`, through the measurement
      page's URL:
      - a child whose correction changed its T-score shows both the gradient's own and the
        corrected value (US5-1)
      - a scored child shows its U-score, M-score, flags, code, and the mark on a score reached
        with missing information (US5-2)
      - a gradient and a conductivity show their own score (US5-3)
      - a not-determined score is shown as not determined
      - the page's query count does not depend on the number of corrections
- [ ] T015 [US5] Documentation: the guide says where a reader sees the scores and what the mark
      means on the page.

**Checkpoint**: the walkthrough can show every state.

---

## Dependencies

US1 → US2 → US3 → US4 → US5, sequential, one worktree. T005 is held on the maintainer's ruling and
lands in US2 or, if the ruling comes later, as a scoped fix before convergence.
