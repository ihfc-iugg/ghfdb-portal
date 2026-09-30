# Progress — 007 quality scores

## 2026-09-30T20:20:44Z · S3 plan

Did: branch reset to origin/main (2b691e7, the merged specification). The earlier spec branch had
an identical tree, so nothing was lost. Wrote plan.md, research.md and tasks.md, appended D12–D21
to decisions.md, and seeded feature-state.json with the spec gate read from PR #233.

Verified: toolbox V0.2 (e1688bf) scoring tests run locally, 43 pass and 2 fail (research R2).
Conformance table R3 produced from the toolbox's own functions.

Analyze: every FR and SC maps to a task. US2-3 and US2-5 are fully testable only after T005, which
is held on the maintainer's ruling about correction-status validation (research R5). No critical
findings.

Next: design review, plan notification, then US1.

Watch: T005 held. D13 put to the maintainer.

## 2026-09-30T21:10:00Z · Implementer US1 · T001

Did: rewrote `project/heat_flow/quality.py` to toolbox V0.2: `SCHEME_REVISION`, the two choice
lists (M1x–M4x added), `SubScore`, `route()`, `Criterion`, `ProbeRules` and `BoreholeRules`.
`utils.py` re-exports the two lists only. Removed `HeatFlow.get_U_score` and `get_M_score`.
Widened `M_score` to three characters with a placeholder migration (D25).

Verified: `uv run pytest tests/test_heat_flow/test_quality.py -n0 -q`, 157 passed (19 R3
conformance cases, corrected and uncorrected). Four mutations of the rules were each caught, one
after adding a direct test of `Criterion.mapping`. `test_child.py` 33 passed,
`test_migrations.py` green, `pre-commit run --all-files` and `manage.py check` clean.

Next: T001a, the `[unspecified]` cell in `MultiConceptWidget`.

Watch: T002 regenerates `0014_quality_scores.py` (D25).

## 2026-09-30T21:35:00Z · Implementer US1 · T001a

Did: `MultiConceptWidget` resolves `[unspecified]` to the vocabulary's own `unspecified` concept
and drops the token only where the vocabulary defines none. A blank cell stays an empty set.
`docs/guides/importing-data.md` states the change.

Verified: `uv run pytest tests/test_ghfdb/test_resources/test_widgets.py -n0 -q`, 58 passed, then
`uv run pytest tests/test_ghfdb -q`, 422 passed and 13 xfailed (the xfails predate this story).
Removing the vocabulary lookup made three of the new tests fail. `pre-commit` clean.

Next: T002.

Watch: the guide's link to `quality-scores.md` is written in T003, so the importing-data page
names the scores in plain text until then.

## 2026-09-30T22:05:00Z · Implementer US1 · T002

Did: `score` on the gradient and conductivity is nullable with no 0–1 bound, beside new
`score_missing` and `quality_scheme`, and the conductivity's `score` is indexed. A `ScoredMeasurement`
mixin holds `refresh_score()` (queryset `update`, so no re-entry) and both `calculate_score()`
methods are gone. `signals.py` has `Recalculation` and the two receivers, connected in
`HeatFlowSchemaConfig.ready()` on save and on `post_add`, `post_remove` and `post_clear` of the
concept fields each score reads. One migration, regenerated from D25's placeholder. Replaced the
single assertion D24 names in `test_conductivity_vocabulary_fields_count_and_score_persist`: its
site records no exploration method, so the score is `None` and the supplied 0.9 is not kept.

Verified: `uv run pytest tests/test_heat_flow tests/test_migrations.py tests/test_factories.py -q`,
307 passed, 1 skipped. Mutations: dropping `post_clear`, connecting one concept field only and
ignoring `raw` each failed a test. Acting on `pre_add` as well survives, because the `post_add`
refresh follows and writes the same values; it is wasted work, not a wrong result.
`pre-commit` and `manage.py check` clean.

Next: T003, the documentation.

Watch: old rows keep their hand-set score and an empty `quality_scheme` until the US4 refresh
command scores them.

## 2026-09-30T22:40:00Z · Implementer US1 · T003

Did: wrote `docs/guides/quality-scores.md` (scheme and reference, the T-score and TC-score on both
routes, the missing-information mark, not determined, and D1, D8, D10, D12, D15–D17) and linked it
from `docs/index.md` and `importing-data.md`. `CONTEXT.md` defines T-score, TC-score, uncorrected
score, missing-information mark and scheme revision, and the "live gap" note is gone.
`docs/ghfdb_fields.md` lists the six new fields and the widened `M_score`; `ghfdb-erd.md` carries
them on the two entities and in the index list. Dropped the RTD entry from the borehole lists in a
separate T001 commit: the vocabulary has no RTD concept.

Verified: `uv run pytest tests/test_docs tests/test_heat_flow/test_quality.py -q`, 462 passed.
`uv run --group docs sphinx-build -b html docs <dir> -W --keep-going` exits 1 with 32 warnings on
this branch and the same 32 on e42524a (only one line number moved), so the story adds none. The
build is not clean at the base commit.

Watch: the guide says the child's corrected scores, the code and inheritance are documented as they
are built (US2 onward).
