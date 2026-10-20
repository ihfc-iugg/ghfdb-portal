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
