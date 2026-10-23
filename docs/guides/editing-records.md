# Editing records

A researcher who finds a mistake in a heat flow record corrects it in the portal, on the record's own
edit page, instead of re-uploading the spreadsheet. Each kind of record has a form built for it. A
form offers the fields the upload template has a column for, grouped the way the template orders its
columns, so a researcher who filled the template in finds the same things in the same order. This
page describes the site's form, the depth interval's form, the child heat flow's form, and the forms
for a thermal gradient and an interval conductivity, then the pieces the forms are built from.

## Correcting a site

Open the site, choose **Edit details** from the Manage menu, change what is wrong and save. Anyone
who may change the site's dataset may do this; no team role is needed. A save never changes who can
see the site: a site in a dataset that has not been published stays hidden from everyone outside
the dataset's team.

The site's form has these groups:

- **The name**, at the top.
- **Location.** The coordinates, the elevation with its datum, and the geographic environment.
- **Borehole.** The measured length, the true vertical depth, the azimuth and the inclination.
- **Exploration.** The exploration method and the exploration purpose.
- **Rock.** The lithology, the geologic age and the stratigraphy.
- **Region.** The country, region, continent and domain, stored exactly as typed.

The form never offers a value the portal calculates or assigns, such as a quality score or a
GHFDB id. It offers no dataset or sample either: a record stays where it is.

### Coordinates

The coordinates take a latitude and a longitude in decimal degrees (WGS 84) and nothing more. Enter
both or neither. Two sites cannot share one pair of coordinates, so a pair that another site already
holds is refused, with the message beside the coordinates, and nothing is saved.

The elevation is not part of the coordinates. It has its own field, with its unit, and the
elevation datum beside it. The portal stores the elevation on the site itself.

### Terms

A field that takes a term from a controlled vocabulary is a text box, and the term is written the
way the published file writes it:

- Type the term's label or its key, in any case, with or without square brackets. `Onshore
  (continental)`, `onshore (continental)` and `onshore_continental` mean the same term.
- A field that holds several terms, such as the exploration purpose, takes them separated by
  semicolons: `Research; Hydrocarbon`.
- Leave the box empty for no term.
- A term the vocabulary does not hold is refused and named, and nothing is saved.

A stored term is shown as its label. If a field is saved without touching it, the stored value is
kept as it was, even when the vocabulary no longer offers that term.

### Values and units

On a form that takes a value with an uncertainty, they are entered as the value, the uncertainty
and one unit for both. The portal stores every quantity in the field's base units, as an import
does. A value entered in another unit is converted, and the result is rounded to the places the
field keeps. A value entered in the base unit is stored as typed, so one with more places than the
field keeps is refused, with the message beside the value, and nothing is saved. A value shown for
editing is the stored value in the base units.

### The true vertical depth

The site keeps the true vertical depth entered for it. A change to it is stored even when the site
already has a bottom depth: the portal sets the bottom to the top plus the vertical depth.

## Correcting a depth interval

Open the interval, choose **Edit details** from the Manage menu, change what is wrong and save. The
same people may do this as for a site: anyone who may change the interval's dataset.

The interval's form has these groups:

- **The depth.** The top and the bottom of the interval, and the vertical datum. The bottom must be
  below the top; if it is not, the form is refused and nothing is saved. The vertical depth is
  calculated from the top and the bottom when the interval is saved.
- **Marine probe.** The penetration, the probe type, the probe length and the probe tilt, for an
  interval measured with a marine heat flow probe. All four are optional.
- **Rock.** The lithology, the geologic age and the stratigraphy.

The probe values are stored with the interval as its probe metadata. An interval that has none
gains none while you leave the four fields empty. Enter any of them, a tilt of 0 included, and the
interval gains probe metadata holding what you entered. When the interval already has probe
metadata, the form shows the stored values and a save updates them. Clearing a field removes that
value. The probe type takes the terms described under Terms, several separated by semicolons.

The interval's IGSN is not on this form. It is edited on FairDM's identifiers page.

## Correcting a child heat flow

Open the child heat flow value, choose **Edit details** from the Manage menu, change what is wrong
and save. The same people may do this as for a site: anyone who may change the child's dataset.

The child's form has these groups:

- **The value**, with its uncertainty and one unit for both, then the method and a comment.
- **Corrections.** One choice for each of the nine corrections.
- **Acquisition.** The expedition, the surface temperature and the date of acquisition.
- **Calculated from.** The thermal gradient and the interval conductivity the value was
  calculated from.

Whether the child counts towards its parent's value is not on this form. The parent's form carries it.

### Corrections

Each correction has a choice of its own, and it offers only the statuses that are valid for that
correction. The first entry is **Unspecified**, a blank choice: a correction with no status is
stored with an empty status, and it reads back as unspecified in the portal, as `-` in the
published file and as `null` in the API.

After a save every correction holds a row, as it does after an import. A correction you set holds
the status you chose. The eight you did not touch hold an empty status. Clearing a correction
stores an empty status and keeps the comment the correction already had, because the form carries
no comment for a correction.

A save recalculates the child's quality score from the corrections as they now stand, and
the parent's score from its children.

### Choosing a gradient and a conductivity

The thermal gradient and the interval conductivity are searched for by name. The search offers
the gradients, or the conductivities, in datasets you may change. It cannot offer only those on the
child's own depth interval, so the form checks the one you chose: a gradient or conductivity that
belongs to another depth interval is refused, with the message beside its field, and nothing is
saved. The same goes for one in a dataset you may not change.

## Correcting a thermal gradient

Open the gradient, choose **Edit details** from the Manage menu, change what is wrong and save. The
same people may do this as for a site: anyone who may change the gradient's dataset.

The gradient's form has these groups:

- **The gradient**, with its uncertainty and one unit for both, then the corrected gradient with its
  uncertainty and its own unit.
- **Temperature measurements.** The methods used at the top and bottom of the interval, the shut-in
  times, the corrections applied at each end and the number of temperature recordings.

The two pairs are separate: each has its own unit, so the gradient can be entered in one unit and
the corrected gradient in another. Values and units, above, describes how they are stored.
The methods and corrections are terms from controlled vocabularies, entered as described under
Terms.

The form offers no quality score. A save recalculates the gradient's score from the methods and the
number of recordings as they now stand, and the score of each child heat flow calculated from the
gradient, and then the parent's.

## Correcting an interval conductivity

Open the conductivity, choose **Edit details** from the Manage menu, change what is wrong and save.
The same people may do this as for a site: anyone who may change the conductivity's dataset.

The conductivity's form has these groups:

- **The conductivity**, with its uncertainty and one unit for both.
- **Samples.** The source of the samples and the location of the conductivity data.
- **Measurement.** The method, the saturation state, the pressure and temperature conditions and
  the function used to correct towards them.
- **Averaging.** The number of determinations and the averaging methodology.

Every vocabulary field takes the terms described under Terms, several separated by
semicolons. The form offers no quality score. A save recalculates the conductivity's score from the
location, source, number of determinations, saturation and conditions as they now stand, and the
score of each child heat flow calculated from it, and then the parent's.

## Correcting a parent heat flow

Open the parent heat flow value, choose **Edit details** from the Manage menu, change what is wrong
and save. The same people may do this as for a site: anyone who may change the parent's dataset.

The parent's form carries:

- **The value**, with its uncertainty and one unit for both.
- **Comment** and **HP correction flag**, the heat production correction.
- **Children this value rests on.** The child heat flows at the parent's site that the value is
  drawn from.

The form offers no quality score and no GHFDB id.

### Choosing the children

The children are searched for by name, and the choice starts with the children already marked
relevant. After a save exactly the children you chose are marked relevant, and the other children
at the site are not. The parent's value is not calculated from them: saving changes the value only
where you changed it.

The form manages only the children you may change. A child at the site in a dataset you may not
change keeps its relevance as it was. It is not offered as chosen, it does not stop the save when
you leave it out, and it is refused if you choose it.

The search cannot offer only the children at the parent's site, so the form checks every child you
chose: one at another site is refused, with the message beside the field, and nothing is saved.

A save recalculates the parent's quality from the children now marked relevant. With one child at
the site the parent rests on that child whether or not it is marked. With several, the parent rests
on those marked relevant, and with none marked its quality is not determined.

A site with no parent has no parent form. This form does not create one.

## For developers

The forms are in `project/heat_flow/forms.py` and are registered as each model's `form_class` in
`project/heat_flow/config.py`, so FairDM's edit and add pages use them. The pieces shared by every
form are below.

### `SectionedForm`

A mixin that draws a model form in titled groups. List it first among a form's bases, so the layout
is built after FairDM's mixins have replaced their fields.

- `sections` is a tuple of `(heading, rows)` pairs in page order. A row is a field name, a tuple of
  names drawn side by side from the medium breakpoint up, or a measured pair. The first group has
  no heading; every other group is an `mvp_forms.layout.Fieldset` panel. A field named in no
  section is drawn after them, so nothing the form carries is lost.
- `measured_pairs` is a tuple of `(value, uncertainty)` field names. Each pair becomes two plain
  number fields and one choice named `<value>_unit`, drawn as one `Join` with a `±` between the
  numbers. `clean()` gives both numbers the chosen unit and converts them to the field's base
  units, so a stored quantity is always in base units. A number converted from another unit is
  quantised to the field's places. A number in the base unit with more places than the field keeps
  is an error against that field, with the code `max_decimal_places`. The initial numbers are the
  stored quantities in base units.
- The form's helper has `form_tag = False`, because FairDM's page draws the form tag and buttons.

### `ConceptTextField`

A `CharField` that stands for a vocabulary field (`BaseConceptField` or `ConceptManyToManyField`).
It draws a stored term as its label, several joined by `; `, and reads text with `resolve_term` or
`resolve_terms`. Text that equals the stored value as drawn returns the stored value without being
read again. An unknown term is a `ValidationError` against the field with the code `unknown_term`.
Building a field or a form touches no database. A form that holds a stored record sets each
concept field's initial value to the field's `as_text` of the stored value, so the field itself
only has to draw the text it is given, whether stored or posted.

### `heat_flow_formfield`

Every form's `formfield_callback`. A vocabulary field becomes a `ConceptTextField`; any other
many-to-many field gets `mvp_forms.widgets.TomSelectMultiple(counted=True)`; every other field is
drawn as the model draws it.

### `resolve_term` and `resolve_terms`

In `project/heat_flow/vocabularies.py`, the one place a vocabulary term is read from text. The
importer and the forms both call them. `resolve_term(vocabulary, text)` returns the term's key, or
`None` for blank text and `unspecified`. `resolve_terms(vocabulary, text)` reads semicolon-separated
text and returns the matching concepts as a queryset. Both raise `ValueError` naming each token the
vocabulary does not hold.

### `HeatFlowSiteForm`

The site's form. `location` is a `LocationField(full=False)`, which takes a latitude and a longitude
only. The elevation and its datum are the site's own fields, and FairDM's `location_elevation` stays
empty.

Two rules live on the model, not the form, so every way of saving a site follows them:

- `HeatFlowSite.save` sets `bottom = top + vertical_depth` before saving when a vertical depth is
  set, so the true vertical depth entered is the one stored.
- `HeatFlowSite.clean` raises the duplicate-location error against the `location` field with the
  code `duplicate_location`, so `form.has_error("location", code="duplicate_location")` is true.

### `HeatFlowIntervalForm`

The interval's form. `PROBE_FIELDS` names the four `ProbeMetadata` fields it carries as
`probe_penetration`, `probe_type`, `probe_length` and `probe_tilt`, all optional and drawn from the
stored row. `probe_type` is a `ConceptTextField`. `save_related` writes the probe metadata: with no
row stored and nothing entered it writes none, where nothing entered means every probe value is
`None` and no probe type is chosen, so a tilt of 0 is a value and creates the row. Otherwise it
creates or updates the interval's one row and sets its probe types. A bottom that is not below the
top is refused by `HeatFlowInterval.clean` as a form error, and nothing is written.

### `HeatFlowForm`

The child's form. Its nine correction fields are named `correction_<type>`, one for each member of
`HeatFlowCorrection.CorrectionTypeChoices`. Each is a `ChoiceField` that offers an empty entry and
the statuses `HeatFlowCorrection.VALID_STATUS_FOR_TYPE` (or `ENVIRONMENTAL_VALID`) gives that
type. `thermal_gradient` and `thermal_conductivity` are FairDM `MeasurementChoiceField`s with
`scope="edit"`. They cannot be narrowed to an interval, so `clean_thermal_gradient` and
`clean_thermal_conductivity` refuse a measurement whose interval is not the child's, with the code
`other_interval`.

Pass `request=` when you build the form outside FairDM's edit page, because the search fields
accept only the records the request's user may change.

### `ThermalGradientForm`

The gradient's form. `measured_pairs` holds two pairs, `("value", "uncertainty")` and
`("corrected_value", "corrected_uncertainty")`, so the form carries two unit choices,
`value_unit` and `corrected_value_unit`, and each pair is converted with its own. The four
temperature method and correction fields are `ConceptTextField`s. The form offers neither `score`,
`score_missing` nor `quality_scheme`, and no dataset or sample. The score receivers in
`project/heat_flow/signals.py` refresh the gradient, its children and their parents when the form
saves.

### `IntervalConductivityForm`

The conductivity's form. `measured_pairs` holds `("value", "uncertainty")`, so the unit choice is
`value_unit`. The seven vocabulary fields (`source`, `conductivity_location`, `method`,
`saturation`, `pT_conditions`, `pT_function` and `strategy`) are `ConceptTextField`s that hold
several terms. As with the gradient, the form offers no score fields, dataset or sample, and the
score receivers refresh the affected scores on save.

### `ParentHeatFlowForm`

The parent's form. `relevant_children` is a FairDM `MeasurementMultipleChoiceField` over `HeatFlow`
with `scope="edit"`. It cannot be narrowed to a site, so `clean_relevant_children` refuses a child
whose interval is not at the parent's site, with the code `other_site`. `children()` returns the
children at the parent's site, and `managed_children()` narrows them to the records the field offers
the request's user. The initial value and `save_related` read `managed_children()`, so a child in a
dataset the user may not change keeps its relevance. `save_related` marks exactly the chosen
children relevant and the other managed children not, and writes nothing to the parent's own
fields. Pass `request=` when you build the form outside FairDM's edit page.

### Related rows: `save_related`

`SectionedForm.save()` writes the rows a form stands for with `save_related(record)`, inside
`Recalculation.deferred()`, so each affected score is refreshed once rather than once for every
row. With `commit=False` the rows are written when `save_m2m()` is called, as Django writes
many-to-many data. `HeatFlowForm.save_related` gives the child a row for each correction type
holding the chosen status, and never touches a stored comment. `HeatFlowIntervalForm.save_related`
writes the interval's probe metadata. `ParentHeatFlowForm.save_related` marks the chosen
children relevant.
