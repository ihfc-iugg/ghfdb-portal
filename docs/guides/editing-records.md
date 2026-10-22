# Editing records

A researcher who finds a mistake in a heat flow record corrects it in the portal, on the record's own
edit page, instead of re-uploading the spreadsheet. Each kind of record has a form built for it. A
form offers the fields the upload template has a column for, grouped the way the template orders its
columns, so a researcher who filled the template in finds the same things in the same order. This
page describes the site's form, then the pieces the forms are built from.

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
does: a value entered in another unit is converted, and a decimal value is rounded to the places
the field keeps. A value shown for editing is the stored value in the base units.

### The true vertical depth

The site keeps the true vertical depth entered for it. A change to it is stored even when the site
already has a bottom depth: the portal sets the bottom to the top plus the vertical depth.

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
  units, so a stored quantity is always in base units. The initial numbers are the stored
  quantities in base units.
- The form's helper has `form_tag = False`, because FairDM's page draws the form tag and buttons.

### `ConceptTextField`

A `CharField` that stands for a vocabulary field (`BaseConceptField` or `ConceptManyToManyField`).
It draws a stored term as its label, several joined by `; `, and reads text with `resolve_term` or
`resolve_terms`. Text that equals the stored value as drawn returns the stored value without being
read again. An unknown term is a `ValidationError` against the field with the code `unknown_term`.
Building a field or a form touches no database. `PostedText` is the `str` subclass the field uses
to tell text a researcher posted from a stored value to be drawn.

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
