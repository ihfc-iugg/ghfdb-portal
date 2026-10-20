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
- **Quantity fields.** FairDM's quantity model fields give a plain number form field, so no form can
  take a unit. The stored value reaches the input as text with its unit, which a browser drops
  (#307).

## What the screens need from the code

1. Each form groups its fields under headings in the template's order, the first group with no
   heading, a pair of fields side by side from `md` up.
2. The site's form takes the coordinates as latitude and longitude only, and the site's own
   elevation with its datum beside it.
3. The child's form shows nine corrections, one row each: the type as the label of a status choice
   holding only the statuses valid for that type, and a one-line comment beside it. An unset
   correction shows "unspecified".
4. The child's gradient and conductivity choices list only the measurements on the child's own
   interval.
5. The interval's form shows the four probe fields on every interval, empty when it has none.
6. The parent's form lists the children at its site as checkboxes, each named by its heat flow and
   its depth range, ordered by depth.
7. Every quantity input shows its stored value.

## What the sketch faked

- **Quantity inputs are empty** on every form, and a form with a stored quantity cannot be saved
  unchanged. This is FairDM's defect (#307), not the sketch's, and the sketch does not work around
  it. Every form has at least one quantity, so none of them saves today, on main or here.
- **The grouping code is a copy** of FairDM's profile form `sections` logic, in the portal. The plan
  decides whether FairDM should offer it.
- **Saving corrections, probe metadata and relevance** is hand-written in each form's `save()`, with
  no tests. The plan chooses the mechanism (a formset on the form, or fields on it).
- **A stored vocabulary value the vocabulary no longer holds** (FR-007) is not handled.
- **Gradient and conductivity choices are named by FairDM's default string**, the record's name.
- **The unit of an elevation** cannot be chosen: a plain number input has none (#307).
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
