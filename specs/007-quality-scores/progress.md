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

## 2026-09-30T21:13:49Z · Forge · US1 acceptance

Did: the independent verify at 37531f4 was red on the docs step. Six public names in
`quality.py` and `models/child.py` were quoted on no page. Added an "In the code" section to
`docs/guides/quality-scores.md` that names each one. It is a documentation-only fix made directly
rather than by re-dispatch.
Verified: the tamper-check against e42524a flags only the D24 assertion. The receipts check is
green.
Next: re-verify, then accept US1 and dispatch US2.
Watch: D25–D27 need ADR verdicts at convergence.

## 2026-09-30T23:45:00Z · Implementer US2 · T004

Did: added `QualityScheme` (`u_score`, `m_score`, `perturbation_flags`, `code`) to `quality.py`.
Tests first in `test_quality.py`: U bands and the six-place rounding, zero, empty and negative
inputs; M classes, the boundary products and rounding before classing, the `x` suffix and `Mx`; every
flag letter, place and status; the code format; and the U, M and flags of every R3 case against the
conformance cases' T and TC. Amended the `testing.md` project addition: reference values are the
toolbox's output.
Verified: red first (`ImportError: cannot import name 'QualityScheme'`), then
`uv run pytest tests/test_heat_flow/test_quality.py -n0 -q`, 230 passed; `pre-commit run --files`
on the changed files clean.
Next: T005a.
Watch: the new names are quoted on a page in T007.

## 2026-09-30T23:58:00Z · Implementer US2 · T005a

Did: `_parse_correction_status` now also resolves a cell by its status label, normalised with
`normalize_vocab_token`, and takes the correction type so a label the type refuses stores `-`. Keys
and the yes shorthands go through the same branches as before. `importing-data.md` states the change
and that earlier imports keep `-` until re-imported.
Verified: red first (the twelve label cases and the whitespace case stored `-`; the refused-label and
keys cases passed as regression guards), then `uv run pytest tests/test_ghfdb/test_resources/test_child.py
-n0 -q`, 55 passed; `pre-commit run --files` on the changed files clean.
Next: T006.
Watch: a key the type refuses (for example `considered_p` on IS) still raises at save, as before.

## 2026-10-01T00:30:00Z · Implementer US2 · T006

Did: added `T_score`, `TC_score`, their two missing marks and `quality_scheme` to `HeatFlow` (the two
scores indexed), widened `quality` to 14, made the calculated fields `editable=False`, and added
`HeatFlow.refresh_quality()`: corrected T and TC under the child's rules (tilt waiver from T
`tilt_corrected`, bottom-water waiver from SUR `present_corrected`, the IS status or `None` to the
borehole agreement rule), then U, M, flags and code, stored by `update`. Deleted `get_quality` and
`get_perturbation_effects`. Receivers: a child's save, a correction's save, and a correction's delete
through one deduplicated on-commit refresh. Regenerated the single `0014_quality_scores` migration.
Tests first: the stored scores of every R3 case whose corrections the model accepts (X1-X5, P2-P5,
B2-B4, B6, B9), N1 and N2, both marks, the seven flags, a correction's save and delete, the bottom-water
waiver, a delete of the child itself, and a query on `T_score` and `TC_score`.
Verified: red first (`AttributeError: 'HeatFlow' object has no attribute 'T_score'` and `FieldError`),
then `uv run pytest tests/test_heat_flow tests/test_migrations.py tests/test_factories.py -q`, 419 passed,
1 skipped; two mutations (dropping the IS argument, dropping the delete receiver's collection or
its de-duplication) each failed the matching test; `makemigrations heat_flow --check` clean.
Next: T007.
Watch: P1, B1, B5, B7 and B8 reach the child only through the scheme until T005 lands (they need tilt
corrected on T or considered on IS). `ParentHeatFlow.get_quality` still calls the deleted child method;
nothing calls it and US3 deletes it. Every correction saved on an import row refreshes the child, nine
times per row, until US4 defers it.

## 2026-10-01T00:55:00Z · Implementer US2 · T007

Did: `docs/guides/quality-scores.md` gains the child's scores, the U-score, corrected scores and the
three child rules (D2, D3, D11, D13, D14), the M-score, the flags, the code, and how the portal's
`T_score` and `TC_score` equal the toolbox's per-row T and TC (FR-020); the disagreement list adds
D5, D6, D7, D11, D13 and D14, and "In the code" quotes `QualityScheme` with its four methods,
`HeatFlow.refresh_quality()`, `Recalculation` and the three child receivers. `CONTEXT.md` has the
dotted fourteen-character code, the flag letters and order, and "Corrected score".
`docs/ghfdb_fields.md` and the ERD list the child fields and the two new indexes.
Verified: `uv run pytest tests/test_docs -q -n0`, 304 passed, 1 skipped; `forge verify --steps
docs,conformance --base ca1db49` passed.
Next: the full verify, then the report.
Watch: the guide says a stored child cannot yet hold tilt corrected or the considered statuses; it
needs a line when T005 lands.

## 2026-09-30T21:38:59Z · Forge · US2 check

Verified: the receipts check is green, the tamper-check against ca1db49 is clean, and forge verify
at d594832 is green on all six steps. T004, T005a, T006 and T007 are done. T005 is blocked on the
maintainer's ruling (research R5), so US2 stays open and its completion comment waits for it.
Next: US3.
Watch: the correction-delete collector reads Django's internal `connection.run_on_commit`.
Replace it with a plain on-commit flag at the convergence cleanup.

## 2026-09-30T21:52:00Z · Implementer US3 · T008

Did: tests first, each seen failing for the right reason (`AttributeError: ... no attribute
'inherit'`, then the missing parent fields, `refresh_quality` and receivers). `QualityScheme.inherit`
with `U_RANK`, `M_RANK` and `NOT_DETERMINED`; `ParentHeatFlow` gains `U_score`, `M_score` (indexed),
`quality_scheme`, a non-editable 14-character `quality`, and `refresh_quality()`; `get_quality` is
deleted. `Recalculation.child` now ends with the parent, `Recalculation.parent` and
`parent_after_child_deleted` are new, and `remember_parent_before_save` and
`refresh_parent_on_child_delete` are connected in `ready()`. `0014_quality_scores.py` was regenerated
(the old file plus the parent operations only). `"quality"` left `ParentHeatFlowConfig.fields` (D32).
D24: in `test_two_determinations_under_one_parent_repeat_its_values` only the setup order changed, the
quality is set and saved after the children are built; its assertions are untouched.
Verified: `uv run pytest tests/test_heat_flow tests/test_ghfdb -n auto --dist loadscope -q`, 869
passed, 13 xfailed; `uv run pre-commit run --all-files` clean; `uv run python manage.py makemigrations
heat_flow --check --dry-run` no changes.
Next: T009.
Watch: the registry form for `ParentHeatFlow` still raises on `ghfdb_id` (D32). An unflushed
`_deleted_child_parents` survives a rolled-back delete, as D28 notes for corrections.

## 2026-09-30T21:58:00Z · Implementer US3 · T009

Did: `docs/guides/quality-scores.md` gains "What a parent inherits" (D9: which children count with the
single-child rule, the U and M ranking with marked grades poorer than unmarked and `Mx` poorest, flags
from the poorest-U child, the pk-order tie, the value untouched, and when a parent is refreshed),
with a worked example run against `QualityScheme.inherit` (`U3.M1x.-E-----`); "In the code" quotes
`QualityScheme.inherit`, `U_RANK`, `M_RANK`, `NOT_DETERMINED`, `ParentHeatFlow.refresh_quality()`,
`Recalculation.parent()`, `Recalculation.parent_after_child_deleted()` and the two new receivers.
`CONTEXT.md`'s quality-code text and its "a parent is never updated automatically" line now say the
value is designated and the quality inherited. `docs/ghfdb_fields.md` lists the four parent fields
and `docs/data_models/ghfdb-erd.md` the parent fields, the inheritance rules and the two indexes.
Verified: `uv run pytest tests/test_docs -q -n0`, 304 passed, 1 skipped. Every new public name under
`project/` was grepped as code on a page. `sphinx-build` is not installed in this worktree, so the
docs build itself was not run.
Next: the full verify, then the report.
Watch: the guide does not yet describe the cascades from measurement, interval and site changes
(US4) or the refresh command (US5).

## 2026-09-30T23:10:00Z · Implementer US4 · T010

Did: `Recalculation` is rebuilt around one collector and one `request()`; the refresh expands
measurements, then their children, then the parents. New receivers for interval saves, probe
metadata saves and deletes and site saves; every delete path collects and refreshes on commit. The
collector no longer reads `connection.run_on_commit` (D33). Found and fixed a US1 defect that made
every stored record score `None` when read back (D34, outside the listed scope). Tests first, one per
row of the table, each with a refresh spy (what moved, what did not) and the SC-004 helper
`StoredScores.differing()` after every change; a dataset delete; a rolled-back transaction.
Verified: `uv run pytest tests/test_heat_flow/test_signals.py tests/test_heat_flow/test_quality.py
-n0 -q`, 279 passed; `uv run pre-commit run --files <changed>` clean. Probed the flag: replacing the
weak reference with a plain flag fails seven tests.
Next: T011.
Watch: `.set()` on a concept field sends `post_remove` and `post_add`, so outside an import it
refreshes twice. The deferral in T011 removes that for imports.

## 2026-09-30T23:40:00Z · Implementer US4 · T011

Did: `GHFDBChildImportResource` defers recalculation from `before_import` and flushes it in
`after_import`, inside the import's transaction, resetting it on failure (D35).
`Recalculation.deferred()` itself landed with the collector in T010 (D33), so its three unit tests
in `tests/test_heat_flow/test_signals.py` (`TestDeferral`) were written after the code and were not
seen failing; I broke the flush instead and watched two of them fail. Import tests first in
`tests/test_ghfdb/test_importers.py`: every record scored and equal to a fresh calculation, each
record refreshed once (44 calls before, 0 repeats after), a check leaves nothing stored, a dry run
of the child resource leaves nothing, a failed import leaves recalculation on (seen failing with the
`with` removed), a `quality_child` column still refused.
Verified: `uv run pytest tests/test_ghfdb tests/test_heat_flow/test_signals.py -n auto --dist
loadscope -q`, 480 passed, 13 xfailed; `uv run pre-commit run --files <changed>` clean.
Next: T012.
Watch: the parent pass's site saves are outside the deferral and cascade per site (documented in
the plan).

## 2026-10-01T00:20:00Z · Implementer US4 · T012

Did: `refresh_quality` (`project/heat_flow/management/commands/refresh_quality.py`): stale-only by
default, `--all` for every record, in cascade order, in chunks with concept fields and corrections
prefetched, reporting counts (D36). `deploy/Dockerfile` runs it after `migrate --noinput`. Tests
first (10, all failing with "unknown command" before): unscored and other-revision records are
scored, a child reads its fresh measurements, a parent with no children is not determined, a second
run refreshes nothing and changes nothing, `--all` gives identical values, a current record is left
alone by default and repaired by `--all`, every record reads back `hfqa_tool 0.2`, chunking, and the
`CMD` order (migrate, refresh_quality, gunicorn).
Verified: `uv run pytest tests/test_heat_flow/test_management tests/test_heat_flow/test_models -n0
-q`, 122 passed; `uv run pre-commit run --files <changed>` clean; `manage.py refresh_quality --help`
runs. Query counts measured: 56 queries for 2 networks, 248 for 14 (about 18 per determination).
Next: T013.
Watch: the first run was not timed on PostgreSQL. A command `help` is a plain string, as Django's own
commands are, because argparse does not format a lazy one.

## 2026-10-01T00:40:00Z · Implementer US4 · T013

Did: `docs/guides/quality-scores.md` gains "How scores stay current" (the recalculation table, the
order, deletes waiting for the commit, one recalculation per import, `refresh_quality --all` as the
repair for writes that skip the ORM, what the command does without `--all`, and that re-importing is
the repair for a value never stored); "In the code" now quotes `Recalculation.request()`,
`.measurement()`, `.measurements_on()`, `.deferred()` and `.flush()`, the four new receivers,
`GHFDBChildImportResource`'s two hooks and `Command.levels()`, `Command.refresh()` and
`Command.CHUNK_SIZE`; the removed `Recalculation.child()`, `.parent()`,
`.child_after_correction_deleted()`, `.parent_after_child_deleted()` and `.refresh_collected()` are
gone from the page. The two earlier sentences about when a score is recalculated point to the new
section. `docs/guides/importing-data.md` says scores are calculated when the import ends.
`deploy/README.md` lists what the container runs on start in order, the first run's cost at release
size (about 18 queries per determination measured in tests, on the order of 1.6 million at 90,000,
not timed on PostgreSQL) and that an error in it stops the container from starting. Every new
public name under `project/` was grepped as code on a page. The guide's T005 sentence is untouched
(T005 has not landed).
Verified: `uv run pytest tests/test_docs -q -n0`; `uv run pre-commit run --files <changed>`.
`sphinx-build` is not installed in this worktree, so the docs build itself was not run.
Next: the full verify, then the report.
Watch: `CONTEXT.md` was not changed in this story.
