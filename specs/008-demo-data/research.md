# FS-008 research

Investigated against `origin/main` at `a0ea8f3` (2026-10-20), FairDM `1c2e0819`.

## Planning notes

There is no `planning-notes.md` for this feature.

## R1. The heat flow models cannot be inserted with `bulk_create`

Every heat flow model built on FairDM's `Sample` or `Measurement` is a concrete multi-table subclass
of a django-polymorphic model:

- `HeatFlowSite`
- `HeatFlowInterval`
- `ParentHeatFlow`
- `HeatFlow`
- `ThermalGradient`
- `IntervalConductivity`

Django refuses `bulk_create` on a model with a concrete parent ("Can't bulk create a multi-table
inherited model"). Writing the parent and child tables by hand would also need `polymorphic_ctype`
set by hand, and would skip the guards in each model's `save()`:

- one site per coordinate pair
- one parent per site
- the sample-type checks

**Decision:** these six models are saved through the ORM one at a time, the way the import saves
them. The models that are plain Django models are written with `bulk_create`:

- `HeatFlowCorrection`
- `ProbeMetadata`
- the concept many-to-many through rows
- `DatasetLiteratureRelation`

Writing through tables directly is the documented Django route for bulk many-to-many
(`Model.field.through.objects.bulk_create`), so nothing here is a workaround.

**Rejected:** raw inserts into the parent and child tables. They would be fast, but they would
duplicate django-polymorphic's bookkeeping and bypass the guards above. No experienced Django
developer would expect that in a seed command.

At the target size, one run of about 10,000 children, this means about 50,000 ORM saves. Each runs
inside a per-dataset transaction with the quality recalculation deferred (R2). That is the import's
own cost profile, which the portal already accepts for real files.

## R2. Quality scores: reuse the deferred recalculation

`heat_flow/signals.py` recomputes scores on every save through `Recalculation`, and
`Recalculation.deferred()` (signals.py:136) collects the requests and flushes them once when the
block ends. The GHFDB child import already uses it (`ghfdb/resources/child.py:213`). Wrapping each
dataset's writes in `Recalculation.deferred()` computes every score once, after the through rows are
written, so no score is ever generated (FR-008).

The through rows written with `bulk_create` fire no `m2m_changed`. That is harmless: the gradient,
conductivity and child saves in the same block have already requested the recalculation, and the
flush reads the final rows.

**Stopped at 2 on the existing-first list:** `Recalculation.deferred`.

## R3. Value ranges

`docs/ghfdb_fields.md` maps columns to fields and documents no ranges. The ranges are in
`docs/constitution/references/GHFDB-Field-Reference.md`, and they are looser than the model limits
in several places. The generator keeps to the tighter of the two:

| Quantity | Generated | Model limit |
|---|---|---|
| conductivity (W/m·K) | lognormal, median 2.5, clamped 0.8–6 | `clean()` 0.1–50, 4 digits |
| child heat flow (mW/m²) | gradient × conductivity | ±10⁶ |
| gradient (K/km) | heat flow ÷ conductivity, clamped below 300 | corrected value ±999.99 |
| heat flow target (mW/m²) | lognormal, median 65 on land, 95 at sea | — |
| uncertainty | 5–25 % of the value | ≥ 0 |
| probe penetration, length | 1–10 m | 0–100 |
| probe tilt | 0–20° | 0–90 |
| borehole interval | top 0–1,500 m, 50–1,500 m thick | top < bottom |
| probe interval | top 0 m, bottom 2–10 m | top < bottom |
| elevation | −6,000 to −200 m at sea, 0–3,000 m on land | −12,000 to 9,000 |

Drawing the gradient from the heat flow and conductivity keeps every child internally consistent,
and gives the quality scheme believable inputs.

`tests/factories.py` draws independent Gaussians and can produce out-of-range values. It is
test-support code that imports `factory_boy`, which is a development-only dependency, so it cannot
be imported by a management command. The generator uses the standard library's `random` module.

## R4. Coordinates, and land and sea

ADR-0006 makes a site its coordinates, checked in `HeatFlowSite.save()` and not by a database
constraint. Telling land from sea needs either a coastline dataset, which would be a new dependency,
or boxes chosen by hand.

**Decision:** a fixed table of about twenty regional boxes in the module, each labelled land or sea
with its environment and exploration method:

- continental boxes take drilling
- ocean boxes take marine probing

The boxes follow where heat flow is actually measured (North America, Europe, the North Sea, the
Pacific margins and so on). Points are drawn uniformly inside a box at five decimal places. The
model's own uniqueness check catches the rare collision with an earlier run, and the generator
redraws. The ratio of sea to land boxes follows the published database, about 40 % marine.

**Stopped at 7, new code:** nothing in the repo or its dependencies places a point on land or sea
without a geometry dataset.

## R5. Marking demo data

FairDM's own seeds mark what they make so they can find it again (`demo/seed/common.py`,
`config__seed` on contributors).

**Decision:** every demo dataset's `options` holds `{"demo_data": true}`, and every record below a
demo dataset belongs to it, so that one mark identifies everything. Two further marks:

- Demo literature uses the DataCite test DOI prefix `10.5072`, which no real publication can have,
  and citation keys that start with `demo-`.
- Generated people have addresses at `demo.example`, a reserved domain.

The command only adds records, so nothing that is not demo data is ever touched (FR-012).

## R6. Accounts

- FairDM's `create_dev_accounts` creates the five role accounts at `fairdm.org`, idempotently, and
  refuses outside development. The command calls it.
- The fleet-standard development accounts are added beside them: `regular.user`, `staff.user` and
  `super.user` at `example.com`. Two role accounts follow the same `<role>.user@example.com` shape:
  `data-assessor.user@example.com` in the `Data Assessor` group and
  `data-curator.user@example.com` in the `Data Curator` group.
- Every account has the password `password`.
- Email addresses are confirmed the way `create_dev_accounts` confirms them.

FairDM's `seed_contributors`, `seed_overviews` and `seed_profiles` live in its `demo` package, which
this portal does not install, so they are not used.

## R7. Production refusal

FairDM's pattern is `apps.get_app_config("fairdm").resolved_environment()` checked against
`fairdm.apps.NON_PRODUCTION_ENVIRONMENTS` (`create_dev_accounts.py:102-115`). The command uses the
same check before it writes anything. Calling `create_dev_accounts` first would also refuse, but a
check of its own makes the refusal the command's own and puts it ahead of the vocabulary preload.

## R8. States and publication

- `Review` (verbose name "Assessment") is one-to-one with a dataset and with a literature item.
- `States` are DESCRIBED, AWAITING_DECISION, CHANGES_REQUESTED and COMPLETE.
- The portal publishes a dataset on COMPLETE by setting `visibility=PUBLIC` and `published=True`
  (`review/views.py:238-253`).
- ADR-0021 serves a parent through the published-structure API only when it carries a `ghfdb_id`.

**Decision:**

- The first four datasets of every run take the four states in order. Later datasets are COMPLETE
  four times in five and spread over the other states otherwise.
- COMPLETE datasets are public and published. The rest are private.
- Parents and children in published datasets get `ghfdb_id`s numbered on from the highest already
  in the database, so the GHFDB endpoints serve them. Those in unpublished datasets get none, as a
  real unreleased upload would.
- A COMPLETE or CHANGES_REQUESTED assessment is decided by the demo Data Curator. Every assessment
  is uploaded by the demo Data Assessor, who is also its reviewer.

## R9. Size

- The size counts datasets.
- Each dataset holds 20 sites, one designated parent per site.
- Children per parent follow the fixed cycle 1, 2, 3, 4, so 50 children per dataset.
- A child is marked relevant except where a parent has three or more children, in which case one
  child is not relevant.
- Corrections and probe metadata follow the site's exploration method.
- The accepted range is 4 to 200 datasets. Four is the least that holds every assessment state.
  200 datasets give 10,000 children.
- The default is 20 datasets, 1,000 children.

## R10. Where the code lives

Neither `heat_flow` nor `review` imports the other today. The heat flow graph is generated in
`heat_flow` (`project/heat_flow/demo.py`), because `heat_flow` owns those models. The command
composes datasets, literature, assessments and accounts as well, so it lives in `review`
(`project/review/management/commands/seed_demo_data.py`). This adds one new import direction,
`review` → `heat_flow`, which follows the one already there: an assessment exists to put heat flow
data into a dataset. `ghfdb` is not involved, and standing constraint 4 is untouched.

## R11. FairDM pins

| Package | Pinned | Latest | Action |
|---|---|---|---|
| fairdm | `1c2e0819` | `1c2e0819` | none |
| fairdm-geo | `a58d86a` | `a58d86a` | none |
| fairdm-discussions | `643d0af` | `643d0af` | none |
| fairdm-docs | `bead56e` | `847fee1` | move, then build the docs |

## What already exists

| Piece | Stopped at | Found |
|---|---|---|
| production refusal | 3 | `fairdm.apps.NON_PRODUCTION_ENVIRONMENTS`, `resolved_environment()` |
| vocabulary and licence loading | 3 | FairDM `preload` and `seed_licenses` commands |
| FairDM role accounts | 3 | FairDM `create_dev_accounts` |
| score computation | 2 | `heat_flow.signals.Recalculation.deferred` |
| bulk many-to-many | 4 | Django `through.objects.bulk_create` |
| contributor credit | 3 | FairDM `Contribution.add_to` |
| assessment states | 2 | `review.states.States` |
| random values | 4 | standard library `random` |
| demo account creation (example.com set) | 7 | new code, a few lines following `create_dev_accounts` |
| heat flow graph generator | 7 | new code: `heat_flow/demo.py` |
| regional boxes | 7 | new code: a table in `heat_flow/demo.py` |
| the command | 7 | new code: `review/management/commands/seed_demo_data.py` |
