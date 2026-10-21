# FS-009 sketch: forms designed for heat flow sites and measurements

The six edit forms, drafted on the running portal so their arrangement can be judged before they
are built and tested.

## What exists

- **Models.** All six records already hold every field the field mapping table maps a template
  column to. A child's corrections are `HeatFlowCorrection` rows, one per type, with the statuses
  valid for each type declared on the model (`VALID_STATUS_FOR_TYPE`, `ENVIRONMENTAL_VALID`). Probe
  metadata is a `ProbeMetadata` row, one-to-one with the interval. Relevance is `is_relevant` on the
  child. A parent's `sample` is its site, a child's `sample` is its interval, and a gradient's and a
  conductivity's `sample` is the interval they were measured over.
- **Saving already recalculates scores.** Signal receivers refresh a child when it, its corrections,
  its gradient, its conductivity, its interval, its probe metadata or its site is saved, and refresh
  the parent when a child changes (ADR-0022).
- **How a form is chosen and drawn.** FairDM's edit page asks the registry for the model's form
  class and renders it with crispy forms, DaisyUI template pack, inside django-mvp's
  `form_view.html`. A registry `form_class` replaces the generated form. The tuples in a registry
  `fields` list are flattened, so today's forms have no grouping at all.
- **A grouping pattern exists in FairDM.** Its profile form (`fairdm.contrib.contributors.forms.
  profile.ProfileForm`) draws `sections`: `(heading, rows)` pairs, a tuple row side by side from
  `md` up, the first group with no heading. It is tied to the profile form and is not importable on
  its own.
- **Base form mixins.** FairDM's `SampleFormMixin` and `MeasurementFormMixin` limit the dataset
  choice and replace `location` with a full latitude, longitude, elevation and uncertainty input.
- **The site's location.** FairDM's `LocationField(full=False)` takes a latitude and a longitude
  only (ADR-0023).
- **Quantity fields.** From FairDM `dd55cb5`, a quantity is edited as a number and a unit, the
  stored value shown in base units (#307). The site's elevation offers metres and feet.

## What the screens need from the code

1. Each form groups its fields under headings in the template's order, the first group with no
   heading, a pair of fields side by side from `md` up.
2. The site's form takes the coordinates as latitude and longitude only, and the site's own
   elevation with its datum beside it.
3. The child's form shows nine corrections, two to a row on a wide screen: the type as the label of
   a status choice holding only the statuses valid for that type, with no "unspecified" entry. The
   choice may be empty, and its empty entry reads "Unspecified". No correction has a comment.
4. The child's gradient and conductivity choices list only the measurements on the child's own
   interval.
5. The interval's form shows the four probe fields on every interval, empty when it has none.
6. The parent's children and the child's gradient and conductivity are FairDM record search
   fields, offering only what the researcher may change. The form refuses a child at another site
   or a measurement on another interval.
7. Every quantity input shows its stored value.
8. Every vocabulary field is a text input showing its stored term's label, several terms joined by
   `; `, and refusing a term outside the field's vocabulary.
9. Every other field with several choices is a counted multiple choice control with all its
   choices in the page (Tom Select, from django-mvp-forms). No standard multiple select.
10. Each quantity's number and unit sit in one joined control.

## What the sketch faked

- **The grouping code is a copy** of FairDM's profile form `sections` logic, in the portal. The plan
  decides whether FairDM should offer it.
- **Saving corrections, probe metadata and relevance** is hand-written in each form's `save()`, with
  no tests. The plan chooses the mechanism (a formset on the form, or fields on it).
- **An emptied correction is stored as `-`.** The model cannot hold an empty status yet. The
  migration that makes it optional and clears every stored `-` is the plan's.
- **The vocabulary text input borrows the importer's term reading** from the `ghfdb` app, imported
  inside the field to avoid a circular import. The plan decides where that reading lives so both
  can use it.
- **The record searches offer more than the form accepts:** every gradient, conductivity or child
  the researcher may change, not only those on the interval or at the site. FairDM cannot narrow
  them further.
- **Gradient and conductivity choices are named by FairDM's default string**, the record's name.
- **Seeded state** in the development database: `regular.user@example.com` manages the private
  dataset "Oceanic crust heat flow cfe9ef", which waits for a Data Curator's decision. One of its
  intervals holds a second gradient and a second conductivity, so the child's choice shows two.

## What was ruled by eye

These are taste calls, each made once in the draft. The build keeps them unless review changes them.

- Groups and headings: site **Location · Borehole · Exploration · Rock · Region**; interval
  **Marine probe · Rock**; child **Corrections · Acquisition · Calculated from**; gradient
  **Temperature measurements**; conductivity **Samples · Measurement · Averaging**; the parent has
  no headings.
- A group's position follows the first template column in it. A field the template does not carry
  (azimuth, inclination, the rock fields on a site, an interval's vertical depth and stratigraphy)
  sits with the fields it describes.
- Pairs side by side: value and uncertainty, corrected value and uncertainty, top and bottom of
  every gradient field, elevation and datum, measured and true vertical depth, azimuth and
  inclination, source and location, method and saturation, the two pT fields, number and strategy,
  country and region, continent and domain, probe penetration and type, probe length and tilt.
- The child's comment follows the method, before the corrections, as the template orders it.
- The site's location input is labelled "Coordinates", so it does not repeat its group's heading.
- The parent's children choice is labelled "Children this value rests on" and follows the parent's
  own fields with no heading of its own.

## The maintainer's review

- **Several choices:** never the standard multiple select. Every multiple choice with its choices
  in the page is `TomSelectMultiple(counted=True)`. Done for stratigraphy and the parent's
  children.
- **No remote data:** every choice is sent with the form. Nothing is fetched.
- **Vocabulary fields:** a plain text input each, until the vocabulary autocomplete exists. Done on
  all six forms, reading and writing labels as the published file does.
- **Corrections:** "unspecified" is no status. The choice is optional with an "Unspecified" empty
  entry and offers no unspecified status. Done on the form; the stored change is planned.
- **Correction comments:** none on the form. Comments go on the record's discussion. Done.
- **Record fields (2026-10-22):** every field that chooses a record uses FairDM's record search
  fields. Done for the child's gradient and conductivity and the parent's children.
