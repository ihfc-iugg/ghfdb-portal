# Uploading an assessment

Members of the data assessment team turn a completed **GHFDB upload template** into a dataset
through the portal's own pages, without needing the Django admin. This guide covers describing an
assessment, uploading the file, reading what the portal reports back, and what to do next.

## The template distributed today is refused, and that is expected

If your file is refused immediately — on its header, before any row is checked — this is why. The
published structure has two misspelled column names, and the upload template currently distributed
to the community still carries both. The portal refuses a file on sight if either is present in its
header, naming the template as out of date, rather than silently accepting the misspelling.

**Nothing about the file you filled in fixes this.** The correction has to happen in the template
itself, upstream of the portal, and is tracked separately
([ADR 0003](../adr/0003-misspelled-published-columns-are-corrected-and-rejected.md)). Until it
lands, no file produced from today's template will pass this page. If your file is refused this
way, that is not a mistake on your part and not a portal defect to report.

## What each role may do

Two roles see the assessment pages at all. Neither is visible to anyone else, in the navigation or
by a direct link.

- **Data Assessor** — a member of the assessment team. Can describe an assessment, upload a file
  against it, and see every assessment's progress. An upload confirmed by a Data Assessor stays
  private until a Data Curator decides on it.
- **Data Curator** — everything a Data Assessor can do, and one thing more: deciding a waiting
  assessment, approving it or sending it back with a comment. An upload confirmed by a Data Curator
  is public immediately, without anyone else's decision.

Sign in and look for **Assessments** in the site navigation. It leads to the list of assessments
uploaded so far, each showing the publication it covers and the state it has reached — Described,
Awaiting decision, Changes requested or Complete.

## Describing an assessment

Before choosing a file, start an assessment from the list and describe it:

- **Publication** — search the portal's own literature catalogue. If the publication is not there
  yet, supply a **bibliography file** instead, in **CSL-JSON** format, and it is added to the
  catalogue for you without leaving the form.
- **Assessors** — the people who carried out the assessment. Anyone with a contributor profile can
  be named, whether or not they hold a portal account of their own.
- **Start and end dates** — the dates the work ran between. An end date before the start date is
  refused, naming both.
- **Title** — optional. Left blank, the dataset takes the publication's own title.

A publication can only be described once. Naming one that already has an assessment is refused,
naming the existing one.

The template's own reviewer columns (`Reviewer_name`, `Reviewer_comment`, `Review_date`) are read
and then ignored — the assessors named here are what the portal records, not what the spreadsheet
carries.

## Uploading the file and reading the report

With the assessment described, upload the completed template. The portal reads it and reports what
importing it would do — nothing is written yet, whichever way the report comes back.

**If the file is clean**, the report names how many sites and determinations would be created and
how many existing records would be updated. Nothing is written until you press **Confirm and
import**.

**If the file has problems**, every one of them is listed together, not just the first. Each entry
names the row, the column heading exactly as the template spells it, and what specifically is
wrong with the value there. Fix the file and upload it again against the same assessment — as many
times as it takes. A previous upload's problems never carry over to the next one.

**If the header itself is refused**, see "The template distributed today is refused" above — no
row-level problems are reported in that case, because the portal never gets far enough to read one.

## After you confirm

- A **Data Curator's** confirmed upload is public immediately.
- A **Data Assessor's** confirmed upload stays private and joins the queue of assessments awaiting a
  decision.

Either way, the file you uploaded is kept against the assessment record — including a file that was
later replaced — so the dataset can always be traced back to exactly what produced it.

## Deciding on a waiting assessment

Data Curators see **Assessments awaiting a decision** listing every upload waiting on them, naming
its publication and who uploaded it. For each one:

- **Approve** makes the dataset public and records the decision, who made it and when.
- **Send back** takes a comment saying what needs to change, leaves the dataset private, and returns
  the assessment to its uploader.

A Data Assessor cannot approve any assessment, including their own — that decision belongs to a
Data Curator alone.

A sent-back assessment shows the curator's comment on its upload page. Its uploader corrects the
file and uploads it again through the same page; it is checked afresh and, once confirmed, returns
to waiting on a decision.

## If a report doesn't make sense

A failure report should always be specific enough to act on — a row, a column heading from your own
template, and a plain reason. It should never show you a field name, a model name or anything that
looks like a program error. If you see one of those, that is a defect in the portal, not something
to work around, and it is worth reporting to whoever maintains the portal.
