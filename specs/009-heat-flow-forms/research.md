# FS-009 research: forms designed for heat flow sites and measurements

Read against origin/main at 484ce44, after FS-010 and FS-011 merged, with FairDM v0.2.1
(865964f2), django-mvp 0.31.0 and django-mvp-forms 0.8.0 on the branch. The approved sketch is
6162381.

The spec directory has no `planning-notes.md`, so there are no planning suggestions to answer.

## What the sketch needs, and how each need is met

Each line under "What the screens need from the code" and "What the sketch faked" in `sketch.md`,
with the way the build meets it.

| Sketch line | How the build meets it |
|---|---|
| Groups under headings, first group unheaded, pairs side by side from `md` up | Kept: the portal's own `SectionedForm` base builds a crispy `Layout` of `mvp_forms.layout.Fieldset` panels from a `sections` declaration. Rebuilt test-first. |
| Site coordinates are latitude and longitude only, elevation and datum side by side | Kept: FairDM's `LocationField(full=False)`, labelled "Coordinates". The site's own `elevation` stays a model quantity field (ADR-0023). |
| Nine corrections, valid statuses only, empty entry "Unspecified", no comment | Kept on the screen. The stored side changes: see "Unspecified is no status" below. |
| Gradient and conductivity on the child's own interval only | FairDM's search fields cannot be narrowed (orchestrator's ruling, 2026-10-23). The form refuses a measurement on another interval on save, with an error against the field, and a test pins the refusal. |
| Probe fields on every interval, empty when it has none | Kept: the four probe fields sit on the interval's form. An interval saved with none entered gains no probe metadata (FR-010). |
| Parent's children and child's measurements are FairDM record search fields | Kept: `MeasurementChoiceField` and `MeasurementMultipleChoiceField` from `fairdm.contrib.autocomplete.fields`, `scope="edit"`. The parent refuses a child at another site on save. |
| Every quantity shows its stored value | FairDM's quantity field shows the stored value in base units (FairDM #307, in v0.2.1). The joined value-and-uncertainty groups set their initial numbers from the stored quantities in base units. |
| Vocabulary fields are text, labels joined by `; `, unknown terms refused | Kept: `ConceptTextField`. Its term reading moves out of the `ghfdb` app (see below). |
| Other multiple choices are a counted Tom Select | Kept: `TomSelectMultiple(counted=True)` from `mvp_forms.widgets` for every model many-to-many that is not a vocabulary. |
| Each quantity's number and unit in one joined control | FairDM v0.2.1's quantity widget, drawn by django-mvp-forms 0.8.0. Nothing to build. |
| Value ± uncertainty under one label, one unit | Kept: `mvp_forms.layout.Join(value, HTML("±"), uncertainty, unit)`. django-mvp-forms 0.8.0 draws text between members, so the sketch's disabled button is already gone (729faea). |
| **Faked:** grouping code copied from FairDM's profile form | Stays in the portal. FairDM's `sections` logic is private to its profile form. This form base is the portal's own, built on django-mvp-forms' `Fieldset`, and is small. |
| **Faked:** saving corrections, probe metadata and relevance by hand, untested | Rebuilt test-first on the portal's own forms. See "How the related rows are saved". |
| **Faked:** an emptied correction stored as `-` | The migration that makes the status optional and turns every stored `-` into an empty status. |
| **Faked:** term reading imported from `ghfdb` inside the field | Moved into `heat_flow` (see below). |
| **Faked:** "±" as a disabled button | Already resolved by django-mvp-forms 0.8.0. |
| **Faked:** searches offer more than the form accepts | Kept, by ruling. Refusal on save is tested. |
| **Faked:** gradient and conductivity named by FairDM's default string | Kept. FairDM's search fields label a result with the record's string, and a measurement's string is its name, which an import sets. Nothing in the spec asks for more. |
| **Faked:** seeded walkthrough state in the development database | Reproduced for the walkthrough from the demo data (`seed_demo_data`) and a small seeding step run against the development database, never committed. |

## How the related rows are saved

FairDM's edit page (`fairdm.core.editing.EditDetails`, a `FairDMUpdateView`) takes one form: the
registry's `form_class`. It calls `form.save()` inside the request's transaction
(`ATOMIC_REQUESTS = True` in FairDM's database settings), so a failed save writes nothing.

Three records carry rows beyond their own: a child's nine corrections, an interval's probe
metadata, and a parent's children. Weighed:

- **An inline formset on the portal's form.** The orthodox Django tool when a page edits a
  variable number of related rows. These are not variable. A child has exactly nine correction
  types, each drawn as one labelled choice; an interval has at most one probe metadata row, a
  one-to-one; a parent's children are a choice of existing records, not rows to edit. A formset
  would add a management form, per-row hidden type fields and a second validation pass for nine
  fixed choices, and the screen Sam approved would have to be rebuilt to look the same.
- **Fields on the form, saved by the form.** Each related value is a field on the record's own
  form: nine status choices, four probe fields, one search field for the children. The form's
  `save()` writes the record, then the rows its fields stand for. This is the shape Django's own
  `ModelForm` takes for many-to-many fields, and it keeps the approved screen exactly.

**Chosen: fields on the form.** The form writes its related rows where Django writes a model
form's many-to-many data: after the record is saved, immediately when `commit=True`, and through
`save_m2m()` when `commit=False`, so a caller that saves later still gets every row. No FairDM
defect is worked around: FairDM's page is designed to take one form, and a form that saves its
own related rows is ordinary Django.

## Unspecified is no status

FR-009 and FR-017: an unspecified correction is stored as having no status, and import and export
of a published file read and write exactly as before. Everything that reads or writes
`HeatFlowCorrection.status` today, and what it does after:

| Reader or writer | Today | After |
|---|---|---|
| `HeatFlowCorrection.status` | required, default `-`, `-` is the `UNSPECIFIED` choice | `blank=True`, default `""`. The `UNSPECIFIED` choice is removed. |
| `VALID_STATUS_FOR_TYPE`, `ENVIRONMENTAL_VALID` | each holds `-` | `-` removed. The type check in `save()` accepts an empty status for every type. |
| Migration | — | Alters the field, and turns every stored `-` into `""` (a data step, reversible: `""` back to `-`). |
| Importer (`ghfdb/resources/child.py`, `_parse_correction_status`) | empty or unreadable cell → `-` | → `""`. An explicit `-` cell, or `[unspecified]`, also → `""`. |
| Export (`ghfdb/managers.py`, correction subqueries) | writes the stored status, so `-` for an unspecified row, empty for a child with no row | writes `-` for an empty status, and empty for no row, as before. The existing export and round-trip tests are the check. |
| Quality (`heat_flow/quality.py`) | in-situ `-` scores as not considered; a status with no flag writes `-` | an empty in-situ status scores as `-` did. Flags already treat any status outside the four flagged ones as no flag. |
| API (`heat_flow/serializers.py`, FS-010) | `status: {"name": "-", "label": "unspecified"}` | `status: null`. A correction row with no status is still served, so "recorded with no status" stays distinct from "no row" (FS-010 edge case). |
| API schema (`heat_flow/schema.py`, `ChoiceLabelFieldSchema`) | status a required `{name, label}` object | nullable |
| `HeatFlowCorrection.__str__` | type and `-` | type and "unspecified" |
| Test factories and fixtures (`tests/factories.py`, `tests/test_ghfdb/conftest.py`) | `UNSPECIFIED` | `""` |
| Documentation (`docs/ghfdb_fields.md`, guides on importing, quality scores and the API) | state a stored `-` | stored empty, `-` in the file, `null` in the API |
| Overview page (FS-011 template) | "Unspecified" from the choice label | an em dash, the portal's mark for missing information. |
| Demo data (`heat_flow/demo.py`) | draws a random status from the valid set, `-` included | draws from the valid set without `-`. |

## The term reading moves into `heat_flow`

`ConceptTextField` reads text the way the importer reads a cell, by the same code. That code is in
`project/ghfdb/resources/widgets.py` (`normalize_vocab_token`, and the label-or-key matching inside
`ConceptWidget.clean` and `MultiConceptWidget.clean`). `heat_flow` owns the models and `ghfdb`
extracts them (ADR-0001), so `heat_flow` must not import from `ghfdb`; the sketch dodged a circular
import by importing inside the method.

The matching moves to `project/heat_flow/vocabularies.py`, next to the vocabularies it reads: one
function that resolves a token to a single concept key, one that resolves semicolon-separated
tokens to concepts, both raising `ValueError` naming the unknown tokens. The `ghfdb` widgets call
them and keep their own message prefixes (the column name). The importer's behaviour does not
change, and the existing widget tests are the check.

## Smaller findings

- **deptry** reports `crispy_forms` as a transitive import (`DEP003`). `django-crispy-forms` is
  declared as a direct dependency in `pyproject.toml`, at the range FairDM declares, and the lock is
  refreshed without moving any other package.
- **fairdm-geo (#308).** Its pinned commit declares `CheckConstraint(check=...)`, which Django 6.0
  refuses. The worktree's virtualenv carries a local patch so tests run. Any test that fails only
  because of it is marked `xfail(strict=False)` naming #308. Nothing in the portal works round it.
- **The docs check** lists every new public name no page documents. The forms are documented in a
  new guide, `docs/guides/editing-records.md`: what a researcher can correct on each record, how a
  term, a correction and a record choice are entered, and, for developers, the form classes and the
  base they share.
- **Migrations:** one schema-and-data migration for the correction status, numbered after 0017.
  Its data step cannot be regenerated by `makemigrations`, so the S5 squash leaves it standalone.

## What already exists

One line per piece of new code the plan writes, with where the search stopped
(`kit/checklists/existing-first.md`).

- Grouped form layout → installed package: `mvp_forms.layout.Fieldset` and crispy's `Layout`/`Div`. The portal adds only the `sections` declaration reader, `SectionedForm`, because FairDM's equivalent is private to its profile form.
- Value ± uncertainty with one unit → installed package: `mvp_forms.layout.Join` with crispy `HTML`. The portal adds the unit choice and the conversion to base units.
- Unit conversion → installed package: `quantityfield.units.ureg` (Pint).
- Coordinates input → installed package: `fairdm.utils.location.forms.LocationField(full=False)`.
- Dataset choice and measurement base form → installed package: `fairdm.core.sample.forms.SampleFormMixin`, `fairdm.core.measurement.forms.MeasurementFormMixin`.
- Record search fields → installed package: `fairdm.contrib.autocomplete.fields.MeasurementChoiceField`, `MeasurementMultipleChoiceField`.
- Counted multiple choice → installed package: `mvp_forms.widgets.TomSelectMultiple(counted=True)`.
- Vocabulary text input → new code: `ConceptTextField`. django-controlled-vocabularies has no form field or autocomplete yet; research_vocabs' own form fields are choice fields, which Sam ruled out.
- Term reading → this repo: moved from `project/ghfdb/resources/widgets.py`, not rewritten.
- Correction statuses valid for a type → this repo: `HeatFlowCorrection.VALID_STATUS_FOR_TYPE`, `ENVIRONMENTAL_VALID`.
- Interval and site refusal on save → new code: two `clean_<field>` methods. FairDM's search cannot be narrowed (ruling).
- Saving related rows → Django: `ModelForm.save()` and `save_m2m()`; the forms add the writes for their own related rows.
- Score recalculation on save → this repo: the signal receivers in `project/heat_flow/signals.py` (ADR-0022). Nothing new.
- Registry wiring → installed package: FairDM `ModelConfiguration.form_class`.
- Empty status in the export → Django: a `Case`/`When` in the existing correction subquery.
