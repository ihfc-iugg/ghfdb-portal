# FS-009 decisions

Rationale too long to inline in the spec, and the ambiguities resolved without asking. Every
reading below was chosen without putting a question to the maintainer, and is recorded here for the
specification review to overrule.

## It is a feature

After this work a researcher with their own heat flow data can correct, in the portal, parts of the
records in their dataset that today only the admin or a re-uploaded spreadsheet can reach: a site's
elevation and true vertical depth, a child's corrections and the gradient and conductivity it was
calculated from, an interval's probe metadata, and which children a parent value rests on. That is
several new ways for a user of the site to work with it, and no existing spec describes the forms.

## The person the forms are for

The forms are written for a researcher in no team role, correcting the records in a dataset of their
own. The maintainer ruled on 2026-10-20 that the portal's users are regular researchers, not only
the assessment team, and that this specification is written from a researcher's point of view. An
earlier draft named a Data Assessor or Data Curator in every story, which made the forms read as a
team tool. The goal that carries the work is therefore G5, people outside the team adding their own
datasets, with G4 served because the team uses the same forms.

Nothing on a form differs by role. A Data Assessor correcting a dataset they are assessing sees the
same form as the researcher who owns the data, so no story is needed for them.

### Choosing which children a parent rests on is the researcher's

This was the one capability that might have belonged to the team. The evidence on each side:

- CONTEXT.md says a parent is designated by curators rather than computed, that selecting it is
  knowledge-intensive and deliberately manual, and that new children arriving at an existing site
  trigger a manual review.
- The upload template is "what a contributor fills in", and it carries the parent's value
  (`q`, `q_uncertainty`, `corr_HP_flag`, `p_comment`) and which children are relevant
  (`relevant_child`). A contributor already states both when they upload.
- ADR-0017 and R7 put a Data Curator's decision between a contribution and publication. That
  decision covers every value in the dataset, the parent included.

The ruling: a researcher states the parent value and its relevant children for their own data, on
the parent's form, as the template already asks them to. A Data Curator's approval of the dataset is
the team's check on it, and the manual review of a site that gains new children stays the team's
work outside these forms. Restricting the relevance choice to a curator on the form would take away
from a researcher something the upload template gives them, and would add a role check to a page
whose access FairDM decides.

### Corrections follow the private-until-approved rule

A researcher's dataset is private until a Data Curator approves it (ADR-0017, R7). A correction made
through these forms is part of the dataset like any other value, so it follows the same rule. The
forms change nothing about who can see a record (FR-015). What happens when a researcher corrects a
record in a dataset that is already public is whatever the workflow does today, and this feature does
not decide it.

### How a researcher's records reach their dataset

A researcher in no team role cannot upload yet: the upload route that holds their data for a
curator's decision is R7, which has no issue of its own yet, and FairDM at the pinned version has no
page that creates a sample or measurement. The forms do not wait for either. They serve every record
a researcher may change, however it arrived, and they are what a create page uses once one exists.

## Other readings

### What "everything the template asks for" means

The field mapping table (`docs/ghfdb_fields.md`) is the authority on which model field holds which
template column, so it fixes each form's coverage. That gives a test an outside reader can check,
and keeps fields with no published column, such as FairDM's site type, off the forms. Fields already
on today's forms with no published column stay where they are, because the issue does not ask for
anything to be taken off.

### Relevance is marked on the parent, not the child

`is_relevant` is stored on the child, but CONTEXT.md describes it as a statement about how the parent
was derived. It is decided with all the site's children in view, and offering it in two places would
let two saves disagree. The parent's form carries it.

### Gradient and conductivity choices are limited to the child's interval

A child is calculated over one depth range from measurements made over that range. Offering every
gradient in the dataset would make a mistaken link easy and gives a researcher nothing they need.

### Corrections are edited on the child's form, all nine at once

The template carries all nine correction columns on every child row, and a researcher reads them off
their own paper together. A correction never set reads as unspecified, which matches what import and
export already do with an empty column.

**ADR:** none — local to this feature's forms.

## The maintainer's sketch review, 2026-10-21

### Choices that are not records are sent with the form, as a counted control

Every choice that is not a record is in the page when it is drawn. A field holding several such
choices (an interval's or a site's stratigraphic units) is drawn with django-mvp-forms'
`TomSelectMultiple(counted=True)`: one control that shows how many are chosen and lists every
option, each ticked when chosen, with a search box in the list. The browser's standard multiple
select is never used. FairDM's base page loads Tom Select and its stylesheets on every page, so
the forms add no media of their own.

**ADR:** none — a widget choice inside these forms.

### A vocabulary term is typed as text, as the published file writes it

Every field backed by a controlled vocabulary is a plain text input until django-controlled-
vocabularies provides the autocomplete these forms will hook into. Nothing here picks, searches or
suggests terms, so nothing has to be undone when that arrives.

How the text maps onto what is stored:

- **Shown:** a stored term is shown by its label, exactly as the export writes it. Several terms
  are their labels joined by `; `, the export's separator.
- **Read:** the text is resolved as the importer resolves a cell, by the same code: each
  semicolon-separated token, brackets and case ignored, matched against the vocabulary's labels and
  then its keys. A token that matches nothing refuses the save with an error against the field,
  naming the token. An empty field stores no term.
- **Round trip:** text the researcher has not changed keeps the stored value as it is, without being
  resolved again. A term the vocabulary no longer offers survives a save that does not touch it
  (FR-007). A changed field is resolved in full.

So a record exported, corrected on its form and exported again gives the same cell for a field
nobody touched, and the cell the importer would have read for a field someone did.

**ADR:** none — an interim input, replaced when the vocabulary autocomplete arrives.

### Unspecified is no status

The correction choice offers no "unspecified" entry. It may be left empty, and its empty entry
reads "Unspecified". An empty choice means the correction is unspecified.

The stored model follows: `HeatFlowCorrection.status` becomes optional, with no default, and a
migration turns every stored `-` into an empty status. The development database holds 644 such rows
of 4,823. The importer writes `-` for an empty or unreadable column today. The status choices lose
the `-` entry.

The published file does not change. The importer stores an empty status where it stored `-`, and the
export writes `-` for an empty status, as it wrote the stored `-` before, so an exported file is
byte for byte what it was. The quality code reads an empty status as no flag, as it read `-`. The
existing import and export tests are the check that the published side has not moved.

Until that migration is built, the sketch stores `-` when a choice is emptied.

**ADR:** none — weighed again when the migration is built, since it changes how a published value is
stored.

### No comment for each correction

The child's form carries no comment for each correction. A comment about a correction goes on the
record's discussion, the comments every record already has, and `HeatFlow` gains no new field.

`HeatFlowCorrection.comment` stays in the model with whatever it holds. The form neither shows nor
writes it, so a comment stored by an earlier import or by the admin is kept as it was. No published
column carries it, so the export is unaffected. The development database holds no correction
comment today.

**ADR:** none — local to this feature's forms.

### Probe metadata is edited on the interval's form

It is attached to the interval (`ProbeMetadata.interval`), not to the child, per the mapping table's
own note. An interval saved without any gains none, so non-marine intervals are unaffected.

### The arrangement follows the template

A researcher who has filled in the upload template knows its order. Following it on the forms means
they find the same fields in the same places. These are user-facing forms, so the build drafts them
and looks at them on a running portal before writing the tests, and FR-004 is the requirement most
likely to change when it does.

### Goals

The issue footer claims G4, G5 and G13. G5 is the goal the researcher's stories serve, and G4 is
served by the same forms. Both are Essential and justify the work alone. G13 is Aspirational and is
cited only as a direction the work also serves. No requirement exists for G13's sake.

## What FairDM provides, and what it does not

FairDM is pinned at `f69c9cb`. Its main branch has moved two commits since, to `2bebf29b`: the move to
Django 6.0 and the development accounts moving to example.com. Neither touches forms, so the
specification needs nothing from a newer FairDM.

Two gaps exist at both commits, and planning has to answer them:

- **The edit details page takes one form.** `EditDetails` in `fairdm/core/editing.py` uses the
  registry's form class and has no inline rows, unlike the key dates and identifiers pages, which do.
  Corrections (FR-009) and probe metadata (FR-010) are separate rows from the record being edited, so
  they need either an inline-capable edit page in FairDM or a portal form that saves them itself.
  Under the constitution (Article XIII) the first is preferred if FairDM will take it. Any request
  for it is filed in this repository for the maintainer to take upstream.
- **No page adds a sample or measurement.** FairDM's own roadmap item for create pages is marked
  delivered, but at the pin only projects and datasets have one. This feature does not depend on it.

## Sibling specifications

FS-010 (#287) owns the API representations of these records and FS-011 (#288) their overview pages.
Neither depends on this feature, and this feature depends on neither.

## The FairDM pin moves to dd55cb5

FairDM's quantity fields drew an empty number box on every edit page, so none of these forms
could be saved (#307). FairDM fixed it at `dd55cb5`, where a quantity is edited as a number and a
unit and the stored value shows in base units. The pin moves there from `f69c9cb`, which brings in
three other FairDM changes:

- **Django 6.0.** FairDM now requires it. Django 6.0 drops a column without `CASCADE`, so
  migration `heat_flow.0005` failed on an empty database: it dropped the old surface heat flow's
  key while a child's parent foreign key still pointed at it. The drop now comes after that
  foreign key is repointed, just before the old model is deleted. The final schema is unchanged,
  and a database that has already applied the migration is unaffected.
- **The development accounts moved to example.com.** FairDM's accounts now include
  `regular.user@example.com`, which the demo data also creates, so the demo-data test counts
  distinct addresses rather than a fixed ten.
- **`fairdm.utils` is no longer an app and `fairdm.menus` is one module.** The portal imports
  neither path that moved.

The site's elevation already accepts metres and feet. No other field the specification covers
asks for a unit choice.

**ADR:** none — a dependency move, recorded in the changelog with the feature.

## django-mvp-forms moves to 0.7.0

From 0.7.0 the form pack draws a multi-widget's parts as one joined control when every part is an
input or a select, so each quantity's number and unit sit in one row with nothing added to
django-pint's fields. The portal gets django-mvp-forms through FairDM and django-mvp, both of which
accept 0.7.0, so the lockfile moves and no requirement is declared here, as for the rest of the
stack FairDM supplies. The forms now import `mvp_forms` directly, for Tom Select, so it joins the
list of modules the dependency check accepts through FairDM.

**ADR:** none — a dependency move.

## Fields that choose a record search with FairDM's record fields

From FairDM v0.2.0 a form chooses a project, dataset, sample, measurement, person or
organization with FairDM's record fields (`fairdm.contrib.autocomplete.fields`), which search on
the server and offer only the records the person may reach. The maintainer ruled on 2026-10-22 that
these forms use them for every field that chooses a record. Three fields do:

- the child's temperature gradient: `MeasurementChoiceField(type=ThermalGradient, scope="edit")`
- the child's thermal conductivity: `MeasurementChoiceField(type=IntervalConductivity,
  scope="edit")`
- the parent's children: `MeasurementMultipleChoiceField(type=HeatFlow, scope="edit")`, which
  FairDM draws as a counted control

No form chooses a site, an interval, a dataset or a person: FairDM's edit page leaves the fields
that move a record off it, and an interval's site is treated the same way.

`scope="edit"` because a link from a record in the researcher's dataset should name a record they
may change, and `type` keeps the search to the one kind the field holds.

### The search cannot be narrowed to one interval or one site

The specification limits a child's gradient and conductivity to the child's own depth interval and
a parent's children to its own site. FairDM's record fields narrow a search only by the value of
another field on the same form, and a measurement search accepts only the dataset and the type as
filters. The edit page has no dataset field, and neither filter is the interval or the site.

So the search offers every gradient, conductivity or child heat flow the researcher may change, and
the form refuses on save anything outside the child's interval or the parent's site, with an error
against the field. Checked as a researcher with one dataset: each search returned only that
dataset's measurements of the field's kind, a gradient from another interval and a child at
another site were refused with the form's error, and a gradient in someone else's dataset was
refused by FairDM's own field.

Narrowing the search itself needs FairDM to accept the interval (a measurement's sample) as a
filter. The portal does not work round that. It is FairDM's to add, and the maintainer decides
whether to ask for it.

**ADR:** none — the forms follow FairDM's record fields as they are.

## The FairDM pin moves to v0.2.0

FairDM v0.2.0 (`bea306dc`) brings the record fields above, and
django-mvp 0.30, which adds a side panel to overview pages and a filter panel to list pages.
django-tomselect comes in with it, and django-addanother and django-autocomplete-light go. The
portal imported neither of those two. The site and measurement overview pages and the project and
dataset lists render with no script errors at this pin.

**ADR:** none — a dependency move.

## A value and its uncertainty are one group, with one unit

The maintainer ruled on 2026-10-22 that every measurement with a value and an uncertainty is drawn
as one group under one label: the value, "±", the uncertainty and one unit, in a row, with the help
text of both under it, laid out with django-mvp-forms' layout objects. The pairs on the forms are
the child's heat flow, the parent's heat flow, the thermal gradient measured and corrected, and the
interval conductivity. The gradient's temperatures at the top and bottom also have uncertainties,
but no column of the upload template maps to them, so they are on no form.

How it is built:

- **The group** is django-mvp-forms' `Join`, labelled with the value's label. Each member keeps its
  own help text and errors, which the join draws under the row.
- **Two numbers and one unit.** A `Join` member must be a single input or select, and a quantity
  is a number and a unit drawn as one multi-widget, which a `Join` refuses. So the value and the
  uncertainty are each entered as a plain number in their field's base units, and one unit choice,
  `<value>_unit`, stands for both. The form's `clean` gives both numbers the chosen unit and stores
  them in base units. A stored value is shown in base units, so a form saved unchanged stores the
  same numbers. A number entered in another allowed unit is converted, both numbers alike. Today no
  paired field allows a second unit, so the unit choice holds the base unit alone.
- **The "±".** From django-mvp-forms 0.8.0 a `Join` holds text between its members, so the "±"
  is crispy's `HTML("±")` between the value and the uncertainty. The uncertainty is named by its
  own label.

**ADR:** none — a layout inside these forms.

## Related rows are fields on the record's own form

FairDM's edit page takes one form. A child's nine corrections, an interval's probe metadata and a
parent's children are fields on that record's form, and the form writes the rows they stand for
after the record: at once on `save()`, or through `save_m2m()` when saved with `commit=False`, as
Django writes a model form's many-to-many data. An inline formset was weighed and not taken: the
rows are fixed (nine correction types, at most one probe row, a choice of existing children), and
a formset would need the approved screens rebuilt to look the same. Detail in `research.md`.

**ADR:** none — local to these forms, and ordinary Django.

## The term reading lives with the vocabularies

The importer's label-or-key reading of a vocabulary term moves from the `ghfdb` widgets to
`project/heat_flow/vocabularies.py`, and both the importer and the forms call it. `heat_flow` owns
the models and `ghfdb` extracts them (ADR-0001), so the forms cannot import from `ghfdb`.

**ADR:** none — a move inside the existing rule of ADR-0001.

## An unspecified correction is stored with no status

`HeatFlowCorrection.status` is optional with an empty default, and every stored `-` becomes empty.
The published file is unchanged: the importer stores an empty status where it stored `-`, and the
export writes `-` for one. The quality code scores an empty in-situ status as it scored `-`. The
API gives such a correction's status as `null` and still lists the correction, so a correction
recorded with no status stays distinct from one never recorded. The child's overview page shows an
em dash, the portal's mark for missing information.

**ADR:** none — the published format, the scores and the API's distinction between a recorded and
an absent correction are all unchanged; only the stored spelling of "no status" moves.

## A record from another interval or site is refused on save

FairDM's record search fields offer every gradient, conductivity or child the researcher may
change, and cannot be narrowed to one interval or one site (orchestrator's ruling, 2026-10-23). The
child's form refuses a gradient or conductivity on another interval, and the parent's form a child
at another site, with an error against the field, and a test pins each refusal.

**ADR:** none — validation inside these forms.

## A site keeps the true vertical depth entered for it

A heat flow site inherits fairdm-geo's vertical interval, whose save overwrites the vertical depth
with the distance between top and bottom whenever both are set. A site's bottom only mirrors its
true vertical depth, so once a site had been saved, a corrected TVD was put back on every later
save, through the form and through a re-upload alike. The site's own save now sets its bottom from
its top and its vertical depth first, so the depth a researcher enters is the one kept.

**ADR:** none — the site model's own rule about a field it already holds.

## An interval's vertical depth stays calculated

An interval's vertical depth is calculated from its top and bottom by the same base class, and is
not a column of the upload template. The specification's US4 lists it among what a researcher
corrects. The build leaves it on the form as the sketch drew it and changes nothing about how it is
stored. Whether it should be correctable on its own is a question for the maintainer.

**ADR:** none — a question about the specification, not a design decision.

## Every correction type holds a row after a form save

An import writes all nine correction rows for every child, and the published export tells a row
with no status (`-`) from no row at all (an empty cell). The child's form leaves a child in the
same shape as an import: after a save, each of the nine types has a row, holding the chosen status
or an empty one.

**ADR:** none — local to the child's form.

## The parent's form manages only the children the researcher may change

A site's children can sit in more than one dataset. The parent's form offers, marks and unmarks
only the children at the site the researcher may change. A child in a dataset they may not change
keeps its relevance and does not block the save.

**ADR:** none — local to the parent's form, following FairDM's edit scope.
