# FS-009 decisions

Rationale too long to inline in the spec, and the ambiguities resolved without asking. The
maintainer handed this specification over on 2026-10-20 with no questions to be put to him, so
every reading below was chosen here and is recorded for the specification review to overrule.

## It is a feature

After this work a Data Assessor or Data Curator can correct, in the portal, parts of a heat flow
record that today only the admin or a re-uploaded template can reach: a site's elevation and true
vertical depth, a child's corrections and the gradient and conductivity it was calculated from, an
interval's probe metadata, and which children a parent rests on. That is several new ways for a
user of the site to work with it, and no existing spec describes the forms.

## The interpretation taken as agreed

The six records with a form (site, depth interval, child heat flow, thermal gradient, interval
conductivity, parent heat flow) each get a form that covers what the upload template records about
them, arranged the way an assessor reads a publication, with vocabularies for term fields and
nothing the portal calculates. Pages, access and the API are out of scope. The assessment team is
the user named first, and an outside researcher uses the same forms once they may change a record.

## Self-resolved

### What "everything the template records" means

The field mapping table (`docs/ghfdb_fields.md`) is the authority on which model field holds which
template column, so it fixes each form's coverage. That gives a test an outside reader can check,
and keeps fields with no published column, such as FairDM's site type, off the forms. Fields
already on today's forms with no published column stay where they are, because the issue
does not ask for anything to be taken off.

### Relevance is marked on the parent, not the child

`is_relevant` is stored on the child, but CONTEXT.md describes it as a curatorial statement about
how the parent was derived. A curator decides it with all the site's children in view, and offering
it in two places would let two saves disagree. The parent's form carries it.

### Gradient and conductivity choices are limited to the child's interval

A child is calculated over one depth range from measurements made over that range. Offering every
gradient in the dataset would make a mistaken link easy and gives nothing an assessor needs.

### Corrections are edited on the child's form, all nine at once

The template carries all nine correction columns on every child row, and an assessor reads them
off the paper together. A correction never set reads as unspecified, which matches what import and
export already do with an empty column.

### Probe metadata is edited on the interval's form

It is attached to the interval (`ProbeMetadata.interval`), not to the child, per the mapping
table's own note. An interval saved without any gains none, so non-marine intervals are unaffected.

### No creation pages

FairDM decides which pages exist. The forms are what the registry hands out, so a page that adds a
record, whenever FairDM provides one, uses them.

### Goals

The issue footer claims G4, G5 and G13. G4 and G5 are Essential and the work is justified by them
alone. G13 is Aspirational and is cited only as a direction the work also serves. No requirement
exists for G13's sake.

### Sketch

These are user-facing forms, so the build drafts them and looks at them on a running portal before
writing the tests. The arrangement in FR-004 is the part most likely to change when it does.

## What FairDM provides, and what it does not

FairDM is pinned at `f69c9cb`. Its main branch has moved two commits since, to `2bebf29b`: the
move to Django 6.0 and the development accounts moving to example.com. Neither touches forms, so
the specification needs nothing from a newer FairDM.

Two gaps exist at both commits, and planning has to answer them:

- **The edit details page takes one form.** `EditDetails` in `fairdm/core/editing.py` uses the
  registry's form class and has no inline rows, unlike the key dates and identifiers pages, which
  do. Corrections (FR-009) and probe metadata (FR-010) are separate rows from the record being
  edited, so they need either an inline-capable edit page in FairDM or a portal form that saves
  them itself. Under the constitution (Article XIII) the first is preferred if FairDM will take it.
  Any request for it is filed in this repository for the maintainer to take upstream.
- **No page adds a sample or measurement.** FairDM's own roadmap item for create pages is marked
  delivered, but at the pin only projects and datasets have one. This feature does not depend on
  it (see "No creation pages").

## Sibling specifications

FS-010 (#287) owns the API representations of these records and FS-011 (#288) their overview pages.
Neither depends on this feature, and this feature depends on neither.
