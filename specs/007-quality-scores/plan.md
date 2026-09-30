# Implementation Plan: Quality scores calculated with the current community scheme

**Branch**: `007-quality-scores` | **Date**: 2026-09-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/007-quality-scores/spec.md`

## Summary

One module, `project/heat_flow/quality.py`, is rewritten to follow toolbox V0.2, and every other
scoring method on the models goes (FR-017). Its rules are applied by model methods that store the
results:

- a gradient's and a conductivity's own uncorrected score
- a child's U-score, corrected sub-scores, M-score and code
- a parent's inherited quality

Signal receivers call those methods when an input is written. A file import holds them back and
scores once at its end. A management command scores everything whose stored revision is not the
current one, and the container runs it on start (FR-015). The measurement page template is
overridden to show the stored scores. The glossary and a new data-user guide are written story by
story.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2

**Primary Dependencies**: FairDM (measurement base classes and page), research-vocabs concept
fields, django-import-export. No new dependency.

**Storage**: PostgreSQL. One schema migration (fields listed in D18). No data migration: existing
records are scored by the refresh command at deploy (D20).

**Testing**: pytest, pytest-django, factory-boy through `tests/factories.py`. Test modules mirror
the source module, grouped in `Test<Subject>` classes, per `docs/contributing/standards/testing.md`.
Every concept a score reads is set explicitly in the test. The factories attach random concepts,
which would make a score test flaky.

**Target Platform**: Linux server

**Project Type**: Django web application

**Performance Goals**: an interactive save recalculates only the records that read what changed. An
import of N children scores each record once.

**Constraints**:

- Scores are stored, never calculated when read. A page never calculates one.
- Refreshes write with `QuerySet.update()`, so they never re-enter the receivers.

**Scale/Scope**: about 90,000 determinations at full release size. The deploy-time refresh is a
single count when every record is current.

## Constitution Check

*GATE: passed before research, re-checked after the design below.*

| Article | Bearing on this feature | Verdict |
|---|---|---|
| I. Testing | Every task writes its failing test first. The scheme is checked against the toolbox's own output (research R3). | Conforms |
| II. Simplicity | The rules are tables of penalties read by a handful of small evaluators, and the 2023 implementation is deleted. | Conforms |
| III. Anti-Abstraction | Two rule classes, probe and borehole, because there are two routes. Nothing else is layered. | Conforms |
| VI. Documentation | The guide, the glossary and `docs/ghfdb_fields.md` are updated in the story that introduces each name. | Conforms, own tasks |
| VIII. Internationalization | Choice labels, field verbose names, help text and page strings are translatable. | Conforms |
| IX. Data-model conventions | Every new field has a verbose name and help text, and each index decision is recorded (D18). One migration. | Conforms |
| X. Cohesion | Scoring for one route lives on one class. Storing a score is a model method, and the receivers are the exception the article names. | Conforms |
| XII. GHFDB Schema Fidelity | The code stays at child and parent level, where Fuchs et al. hold it, and the sub-scores sit on the gradient and the conductivity (D2). The field table is updated. | Conforms |
| XIII. FairDM-First Integration | Measurements keep the framework's page. One placeholder template is overridden because it has no extension point (D21). | Conforms, justified |
| XV. Spec-Driven Workflow | This plan follows an approved specification. | Conforms |

No violations to justify.

## Design

### The scheme (`project/heat_flow/quality.py`, rewritten)

Replaces the whole module. `utils.py` keeps its re-export of the two choice lists, and
`calculate_U_score` goes.

- `SCHEME_REVISION = "hfqa_tool 0.2"`, the value every stored score records (FR-014).
- `UScoreOptions` (U1–U4, Ux) and `MScoreOptions` (M1–M4, M1x–M4x, Mx), with translatable labels.
  They keep their names so the model fields and existing imports do not move.
- `SubScore`, a frozen dataclass holding `value: float | None` and `missing: bool`. A `None` value
  is "not determined".
- `route(site) -> "probe" | "borehole" | None`, from the site's exploration-method concept (D17).
- `ProbeRules` and `BoreholeRules`, each with two class methods. Every table is a class attribute
  keyed by concept identifier, and every value comes from research R1:
  - `gradient(gradient, *, tilt_corrected=False, bottom_water_corrected=False) -> SubScore`
  - `conductivity(conductivity, *, in_situ=UNCORRECTED) -> SubScore`. For the probe route
    `in_situ` is ignored. For the borehole route the default scores pT on its own terms (D3), and a
    status or `None` (no in-situ correction recorded) applies the agreement rule (D13, D14).
- `QualityScheme`, a class of class methods for the child and parent arithmetic:
  - `u_score(value, uncertainty)`
  - `m_score(t: SubScore, tc: SubScore)`: product rounded to three places, `x` suffix, `Mx` when
    either is not determined
  - `perturbation_flags(statuses: dict[str, str])`
  - `code(u, m, flags)`
  - `inherit(children)`: returns U, M and flags, per D9

Small private evaluators shared by both route classes: numeric bins largest-first, a flat mapping,
and cases that check every named field for emptiness first. Each returns `(penalty, missing)` with
the empty/unmatched semantics of research R1. A multi-valued field contributes every concept, and
the poorest penalty wins. The explicit `unspecified` concept counts as a value, never as empty
(FR-009). An empty concept set is empty.

**What scoring reads.** A measurement reaches its site as
`measurement.sample.heatflowinterval.site`, and the gradient reaches its probe metadata through the
same interval. A missing interval, site or probe metadata makes each dependent input empty. A
missing site makes the route not determined. Quantities are read as magnitudes in the field's base
units. Scoring reads concepts by identifier through the prefetch cache when one is present.

### Storing scores (model methods)

The fields are those in D18, in one migration, and `docs/ghfdb_fields.md` gets a row for each.

- `ThermalGradient.refresh_score()` and `IntervalConductivity.refresh_score()` score the
  measurement with no child input and write `score`, `score_missing` and `quality_scheme` with
  `type(self).objects.filter(pk=self.pk).update(...)`. They also set the values on `self`. The old
  `calculate_score()` methods are deleted.
- `HeatFlow.refresh_quality()` reads the child's corrections in one query, then:
  - U-score from value and uncertainty
  - corrected T from `route_rules.gradient(gradient, tilt_corrected=…, bottom_water_corrected=…)`
  - corrected TC from `route_rules.conductivity(conductivity, in_situ=<IS status or None>)`
  - M-score and flags, then the code

  It writes `U_score`, `T_score`, `T_score_missing`, `TC_score`, `TC_score_missing`, `M_score`,
  `quality` and `quality_scheme` by `update`. An absent gradient or conductivity, or a route of
  `None`, gives a `None` sub-score and `Mx` (FR-008). `get_U_score`, `get_M_score` and
  `get_quality` are deleted.
- `ParentHeatFlow.refresh_quality()` selects the children it rests on: its only child whatever the
  flag, else those marked relevant. It writes `U_score`, `M_score`, `quality` and `quality_scheme`
  from `QualityScheme.inherit`. With several children and none relevant, or none at all, it writes
  `Ux`, `Mx` and `-------`. It never writes `value` (FR-012). `get_quality` is deleted.

### Keeping scores current (`project/heat_flow/signals.py`, connected in `HeatFlowSchemaConfig.ready`)

A small `Recalculation` class holds the cascade: which gradients, conductivities, children and
parents to refresh, in that order, so each child reads fresh measurement scores and each parent
reads fresh child scores. The receivers only work out what changed and hand it the affected
records.

| Change | Refreshes |
|---|---|
| Gradient or conductivity saved, or a concept added, removed or cleared on it | it, its children, their parents |
| Interval saved (depths) | the conductivities and gradients on it, onward |
| Probe metadata saved | the gradients on its interval, onward |
| Site saved (elevation, exploration method) | every gradient and conductivity on its intervals, onward |
| Child saved | it and its parent. Also the parent it left, read in `pre_save` when the parent changed. |
| Child deleted | its former parent |
| Correction saved or deleted | its child and the child's parent |

Parents are never refreshed by their own save (D19). Deleting a gradient or conductivity is
refused by `PROTECT` while a child uses it, so it needs no receiver.

**Deferral during import.** `Recalculation.deferred()` is a context manager on a `ContextVar`. While
it is active the receivers only collect keys. On exit it refreshes what it collected, once each and
in cascade order. `GHFDBChildImportResource` enters it in `before_import` and flushes it in
`after_import`, inside the import's transaction, and resets it in a `finally` around `import_data`
so a failed import cannot leave recalculation switched off.

### Deploy-time scoring (`heat_flow` management command `refresh_quality`)

With no option, it refreshes every gradient, conductivity, child and parent whose `quality_scheme`
is not `SCHEME_REVISION`, in cascade order, and reports counts. With `--all` it refreshes every
record. `deploy/Dockerfile` runs it right after `migrate`, and `deploy/README.md` says what it does
on start. Running it twice gives the same stored values (FR-016).

### The measurement page (`templates/measurement/detail.html`)

A copy of the framework's placeholder with one added card, included per model:

- **Child:** U-score, then T and TC each as "own score → corrected score" (the measurement's
  uncorrected value beside the child's corrected one), then the M-score, the seven flags with a
  legend, and the quality code.
- **Gradient or conductivity:** its own score.

Every score reached with missing information carries a visible mark with a text explanation, not
colour alone. A "not determined" score reads as such, never as 0. The card reads stored fields only.

### Documentation

- `docs/guides/quality-scores.md`, linked from the docs index. It is for a data user, and each story
  writes its own section:
  - the toolbox version and reference
  - the measurement scores (US1), the child's scores and code (US2), inheritance (US3), and how
    scores stay current (US4)
  - the decisions where the sources conflict (D5–D16)
  - how the uncorrected and corrected sub-scores relate to the toolbox's T and TC (FR-020)
- `CONTEXT.md` › Quality: define the T-score, the TC-score, uncorrected and corrected scores, the
  missing-information mark and the scheme revision. Correct the quality-code description to the
  code this feature writes, and remove the "live gap" note (FR-019).
- `docs/ghfdb_fields.md`: the new and widened fields.
- `docs/data_models/ghfdb-erd.md`: the score fields.

## Project Structure

```text
project/heat_flow/
├── quality.py            # rewritten: the scheme
├── signals.py            # new: receivers and the Recalculation cascade
├── apps.py               # ready() connects signals
├── utils.py              # re-exports the two choice lists only
├── models/child.py       # fields, refresh_score(), refresh_quality(); old methods removed
├── models/parent.py      # fields, refresh_quality(); get_quality removed
├── management/commands/refresh_quality.py   # new
└── migrations/00NN_quality_scores.py        # new, one file
project/ghfdb/resources/child.py   # deferral around the import
templates/measurement/detail.html  # new override
deploy/Dockerfile, deploy/README.md
docs/guides/quality-scores.md (new), docs/index.md, CONTEXT.md, docs/ghfdb_fields.md,
docs/data_models/ghfdb-erd.md

tests/test_heat_flow/
├── test_quality.py                         # new: rules, conformance cases (R3)
├── test_signals.py                         # new: every row of the recalculation table
├── test_models/test_child.py, test_parent.py   # refresh methods, stored fields
└── test_management/test_refresh_quality.py     # new
tests/test_ghfdb/test_resources/…           # import scores once, dry run leaves nothing
tests/test_templates/test_measurement_detail.py   # the measurement page; tests/test_templates/
                                            # joins non-mirror-paths in pyproject.toml, since
                                            # its subject is a template, not a module
```

## Open items

- **Correction-status validation (research R5).** The tilt waiver and the borehole pT agreement
  need `HeatFlowCorrection` to accept "tilt corrected" on the temperature type and the three
  "considered" values on the in-situ type. Changing that alters a pinned behaviour, so it waits on
  the maintainer's ruling. Until then the task is held and those two rules are tested at the scheme
  level only.
- **US2 scenario 6 for borehole children (D13).** Put to the maintainer with the plan.

## Risks

- **Receivers across the polymorphic models.** Gradient, conductivity, child and parent are all
  `Measurement` subclasses, so a receiver must be connected with `sender=` for its concrete model.
  A receiver on `Measurement` would fire for every type.
- **`m2m_changed` fires with `pre_` and `post_` actions**, and `clear` reports no pks. Only
  `post_add`, `post_remove` and `post_clear` act, each on the instance.
- **Writes that bypass the child resource.** Both the admin import and the assessment upload go
  through `GHFDBChildImportResource` (`project/ghfdb/importers.py`, `admin.py`), so both are
  deferred and flushed. A queryset `update` or `bulk_create` elsewhere is not. The refresh command is the stated repair, and the guide names it.
- **Rounding.** Penalties are summed in floats. The M-score rounds the product to three places
  before comparing, as the toolbox does (D7). Stored sub-scores are rounded to three places, so
  that a later recalculation compares equal (FR-016).
