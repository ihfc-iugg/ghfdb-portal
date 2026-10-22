# Implementation Plan: Forms designed for heat flow sites and measurements

**Branch**: `009-heat-flow-forms` | **Date**: 2026-10-23 | **Spec**: [spec.md](spec.md)

**Input**: the approved specification (ea4ed12), the approved sketch (6162381), and
[research.md](research.md).

## Summary

Six edit forms, one per heat flow record, registered as each model's `form_class` so FairDM's
"Edit details" page uses them. The sketch drew them and Sam approved the screens. This build keeps
the screens and rebuilds the code behind them test-first: a shared form base that groups fields
into panels, a vocabulary text field, the related rows each form saves (corrections, probe
metadata, relevance), and the refusal of a record from another interval or site. Alongside it, an
unspecified correction becomes an empty status in the database, with the published file
unchanged.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Django 6.0, FairDM v0.2.1 (865964f2), django-mvp 0.31.0, django-mvp-forms
0.8.0, django-crispy-forms (declared direct by this feature), django-pint (`quantityfield`),
research_vocabs

**Storage**: PostgreSQL with PostGIS. One migration: `heat_flow` 0018, correction status.

**Testing**: pytest with pytest-django, against PostGIS, under xdist. Form tests call the forms
directly; page tests post to FairDM's edit page as a signed-in researcher.

**Target Platform**: the portal's web application

**Project Type**: Django web application on FairDM

**Performance Goals**: none beyond today's edit page

**Constraints**: the approved screens are kept exactly. No leading-underscore names. Line length 88.
No compatibility aliases. No test of text content or of layout and widths. Reusable template pieces
are Cotton components; these forms add no templates.

**Scale/Scope**: six forms, one migration, five readers of the correction status brought in line

## Constitution Check

| Article | How the plan meets it |
|---|---|
| I Testing | Every task is test-first. Because the sketch's code already exists, each test is shown red by removing or breaking the piece it covers, and the failure is recorded. |
| II Simplicity / III Anti-Abstraction | One small form base, `SectionedForm`, shared by six forms. Related rows are fields on the record's own form, not formsets (research.md, "How the related rows are saved"). |
| IV Integration-First | Page tests go through FairDM's real edit page with a real signed-in researcher. |
| V Security & data-safety | Access to the edit page is FairDM's, unchanged. The record searches use `scope="edit"`. Refusal of a record from elsewhere is enforced on save, not by the search. A save leaves visibility unchanged (FR-015), and a test pins it. |
| VI Documentation | `docs/guides/editing-records.md`, grown story by story. A changelog entry. |
| VII Dependency discipline | django-crispy-forms declared because the portal imports it. No other dependency moves. |
| VIII Internationalization | Every label, heading, help text and error the forms add is `gettext_lazy`. |
| IX Data-model conventions | The status field keeps its `verbose_name` and `help_text`. |
| X Cohesion | Term reading lives with the vocabularies in `heat_flow`, and `ghfdb` calls it (ADR-0001). |
| XII Schema fidelity | Import and export of the published file are byte-for-byte unchanged. The existing import, export and round-trip tests are the check. |
| XIII FairDM-First | FairDM's edit page, location field, search fields, base form mixins and quantity widgets are used as they are. No FairDM defect is worked around. |

## Design

### The form base: `SectionedForm`

In `project/heat_flow/forms.py`. Listed first among a form's bases so the layout is built after
FairDM's mixins have replaced their fields.

- `sections`: `(heading, rows)` pairs in page order. A row is a field name, a tuple of names drawn
  side by side from `md` up, or a measured pair. The first group has no heading; every other group
  is an `mvp_forms.layout.Fieldset` panel. A field in no section is drawn after them, so nothing
  the form carries is lost.
- `measured_pairs`: `(value, uncertainty)` names. Each pair becomes two plain number fields and one
  unit choice named `<value>_unit`, drawn as one `Join(value, HTML("±"), uncertainty, unit)` under
  the value's label. `clean()` gives both numbers the chosen unit, converted to the field's base
  units (Decimal fields quantised to the field's places), so a stored value is always in base
  units, as an import stores it. The initial numbers are the stored quantities in base units.
- Stored vocabulary values are handed to their `ConceptTextField`s so an untouched field keeps the
  stored value (FR-007).
- The helper has `form_tag = False`: FairDM's page draws the form tag and buttons.

### The vocabulary field: `ConceptTextField`

A `CharField` standing for a `BaseConceptField` or `ConceptManyToManyField`.

- Shows a stored term by its label, several joined by `; `.
- Reads text with the term reading moved into `project/heat_flow/vocabularies.py`
  (`resolve_term`, `resolve_terms`), the same code the importer uses: brackets and case ignored,
  label then key. An unknown token is a `ValidationError` naming it, against the field.
- Text equal to the stored value as drawn returns the stored value without resolving it again, so a
  term the vocabulary no longer offers survives a save that does not touch it.
- `heat_flow_formfield`, every form's `formfield_callback`: a concept field becomes a
  `ConceptTextField`; any other many-to-many gets `TomSelectMultiple(counted=True)`.

### How each form saves its related rows

A form that stands for related rows writes them after the record, in one method,
`save_related(record)`. `save(commit=True)` calls it at once; `save(commit=False)` chains it onto
`save_m2m`, exactly as Django defers many-to-many data, so a caller saving later still gets every
row. FairDM's page saves with `commit=True` inside the request's transaction, so a refused or
failed save writes nothing.

- **Child, corrections.** Nine `correction_<code>` choice fields, one per
  `CorrectionTypeChoices` member, labelled by the type. Each offers an empty entry labelled
  "Unspecified" and the statuses `VALID_STATUS_FOR_TYPE` (or `ENVIRONMENTAL_VALID`) gives that type.
  On save: a type with a stored row gets the chosen status, empty when cleared; a type with no row
  and no status gets no row; a type with no row and a status gets one. A stored correction comment
  is never touched.
- **Interval, probe metadata.** Four `probe_<name>` fields built from `ProbeMetadata`
  (`penetration`, `probe_type`, `length`, `tilt`), all optional, initial from the stored row. On
  save: no row and nothing entered gives no row; otherwise the row is created or updated and its
  probe types set.
- **Parent, relevance.** `relevant_children`, a `MeasurementMultipleChoiceField` over `HeatFlow`,
  `scope="edit"`, initial the site's relevant children. On save: exactly the chosen children at the
  site are relevant, every other child at the site is not. The parent's own value is written only
  from its own fields (FR-014).

### Refusing a record from elsewhere

FairDM's search fields offer every record of the kind the researcher may change, and cannot be
narrowed (ruling, 2026-10-23). The forms refuse on save:

- Child: `clean_thermal_gradient`, `clean_thermal_conductivity` refuse a measurement whose interval
  is not the child's, with an error against that field.
- Parent: `clean_relevant_children` refuses any child not at the parent's site, with an error
  against the field.

### Unspecified is no status

As research.md tabulates. In short:

- `HeatFlowCorrection.status`: `blank=True`, `default=""`. `StatusChoices.UNSPECIFIED` is removed,
  and `-` leaves `VALID_STATUS_FOR_TYPE` and `ENVIRONMENTAL_VALID`. `clean()` accepts an empty
  status for any type.
- Migration `0018`: alters the field, then a reversible data step turns `-` into `""` (and back).
  It stays standalone through the S5 squash, because a data step cannot be regenerated.
- Importer: every case that gave `-` gives `""`.
- Export: the correction subquery writes `-` for an empty status, so the file is unchanged.
- Quality: an empty in-situ status scores as `-` did.
- API: a correction with no status serialises `status` as `null`. The correction row is still
  listed, so "recorded with no status" stays distinct from "no row" (FS-010).
- Overview page: a correction with no status shows an em dash.
- Demo data: draws only real statuses.

### The six forms

Fields, groups and pairs exactly as the sketch draws them (`sketch.md`, "What was ruled by eye").
Each is the model's registry `form_class` (FR-005).

| Form | Bases | Adds |
|---|---|---|
| `HeatFlowSiteForm` | `SectionedForm`, `SampleFormMixin`, `ModelForm` | `location` as `LocationField(full=False)`, labelled "Coordinates" |
| `HeatFlowIntervalForm` | `SectionedForm`, `SampleFormMixin`, `ModelForm` | probe metadata fields and their save |
| `HeatFlowForm` | `SectionedForm`, `MeasurementFormMixin`, `ModelForm` | corrections, gradient and conductivity search fields, their refusal and save |
| `ThermalGradientForm` | `SectionedForm`, `MeasurementFormMixin`, `ModelForm` | two measured pairs |
| `IntervalConductivityForm` | `SectionedForm`, `MeasurementFormMixin`, `ModelForm` | one measured pair |
| `ParentHeatFlowForm` | `SectionedForm`, `MeasurementFormMixin`, `ModelForm` | relevant children, their refusal and save |

### Score recalculation

Nothing new. The signal receivers in `project/heat_flow/signals.py` already refresh a child when
it, its corrections, gradient, conductivity, interval, probe metadata or site is saved, and its
parent when a child changes (ADR-0022). The tests read the stored scores back after a save
through the form and compare them with what `quality.py` calculates.

### fairdm-geo (#308)

A test that fails only because fairdm-geo's pinned commit declares `CheckConstraint(check=...)` is
marked `pytest.mark.xfail(reason="fairdm-geo #308: ...", strict=False)`. Nothing in the portal works
round it, and the local virtualenv patch is never committed.

## Testing approach

- `tests/test_heat_flow/test_forms.py` mirrors `project/heat_flow/forms.py`: one class per form and
  one for each shared piece (`TestConceptTextField`, `TestSectionedForm`, `TestHeatFlowSiteForm`,
  …). Forms are built with the record and posted data directly.
- Page tests, one class per record, post to FairDM's edit page as a researcher who owns the dataset
  and holds no team role, and read the stored record back. They live in the same module, named
  `Test<Record>EditPage`.
- Tests find fields by name and assert stored values, errors by field, and which choices are
  offered. They do not assert wording, layout, widths or column classes.
- Vocabulary terms come from the session-loaded concepts (`tests/README.md`). No per-test concept
  loading.
- Each test is shown red against the sketch's code by removing or breaking the piece it covers,
  and the command and failure go in the task's evidence.

## Project Structure

### Documentation (this feature)

```text
specs/009-heat-flow-forms/
├── spec.md
├── decisions.md
├── sketch.md
├── research.md
├── plan.md
└── tasks.md
```

### Source Code (repository root)

```text
project/heat_flow/
├── forms.py                  # the six forms, SectionedForm, ConceptTextField
├── config.py                 # form_class on six registry configs
├── vocabularies.py           # resolve_term, resolve_terms (moved from ghfdb)
├── models/child.py           # status optional, UNSPECIFIED removed
├── migrations/0018_*.py      # correction status
├── quality.py                # empty in-situ status
├── serializers.py            # empty status as null
├── demo.py                   # real statuses only
└── templates/heat_flow/heatflow_overview.html   # em dash for no status
project/ghfdb/
├── managers.py               # export writes - for an empty status
└── resources/
    ├── child.py              # importer stores an empty status
    └── widgets.py            # calls the moved term reading
docs/guides/editing-records.md
tests/test_heat_flow/test_forms.py
```

## Complexity Tracking

None. No article is set aside.
