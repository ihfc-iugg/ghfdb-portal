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
