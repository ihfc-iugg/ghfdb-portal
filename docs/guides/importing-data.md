# Importing data

Heat flow data enters the portal as a completed **GHFDB upload template** — the spreadsheet the
data assessment team fills in, one file per dataset. This guide covers what the portal does with
that file when it reads it.

## The template the portal reads

The portal reads the published upload template and nothing else. A copy of the empty template ships
with the documentation at `docs/constitution/references/data_upload_template.xlsx`, and a
byte-identical copy is the fixture the reader is tested against, so a change to the published
template shows up as a test failure rather than a silent mismatch.

Column names are taken from the header row of the `data list` sheet. Each one falls into one of
four groups:

- **Stored columns.** The bulk of the template. Each maps to a field on a site, a depth interval, a
  determination, a gradient, a conductivity, a correction or probe metadata.
- **Portal additions.** `Country`, `Region`, `Continent` and `Domain` are held on the site and
  stored exactly as supplied, never recomputed from the coordinates.
- **Accepted but not stored.** `ID`, `Reviewer_name`, `Reviewer_comment` and `Review_date` are
  recognised and discarded. Nothing in the data model holds them, and their presence is not an
  error. They are declared as a named group so that a column the portal deliberately ignores can
  never be mistaken for one it failed to recognise.
- **Refused.** Two names, covered below.

## Two column names are refused on sight

The published structure carries two misspellings: `tc_pT_fuction`, which should be
`tc_pT_function`, and `Ref_ISGN`, which should be `Ref_IGSN` — an IGSN being an International Geo
Sample Number.

The portal uses the corrected spellings internally, and **a file whose header carries either
misspelled form is refused**, naming the offending column, rather than being quietly accepted and
mapped across. The reasoning is recorded in
[ADR 0003](../adr/0003-misspelled-published-columns-are-corrected-and-rejected.md): accepting them
silently would work, and it would also make the errors permanent, because every downstream
consumer, template revision and page of documentation would inherit them.

The practical consequence is worth stating plainly. **The template distributed today carries both
misspellings**, so a file produced from it is refused until the template is corrected upstream. The
refusal is the mechanism by which that correction gets asked for.

## Checking a header

`project.ghfdb.constants.validate_official_header` decides whether a header row is the official
template's. It takes the list of column names read from the header row and returns nothing if they
are the official set:

```python
from project.ghfdb.constants import validate_official_header

validate_official_header(header)
```

Anything else raises `ValueError`, with a message naming the header it was given. The function
inspects only the header it is handed and reads no rows and touches no database, so a file refused
here is refused before any part of it could have been written.

`project.ghfdb.constants.OFFICIAL_TEMPLATE_HEADER` holds the set it checks against, should you need
to compare a header yourself rather than have one validated.

## Running an import

`project.ghfdb.importers.import_ghfdb_template` is the callable entry point: one file, one dataset,
nothing else. The caller names the dataset explicitly — the import never guesses one, even when
exactly one exists — and gets back the combined outcome of the two passes it runs underneath.

```python
from fairdm.core.models import Dataset

from project.ghfdb.importers import import_ghfdb_template

dataset = Dataset.objects.get(pk=...)

with open("filled_template.xlsx", "rb") as f:
    outcome = import_ghfdb_template(f, dataset)

if outcome.has_errors():
    ...  # outcome.parent and outcome.child are the two import_export.results.Result objects
```

Underneath, it runs the **parent pass** — every site and its parent heat flow value — before the
**child pass** — the determinations beneath each site — since a child row resolves its parent from
the site the parent pass has already created. Both passes run inside one transaction and are wired
to the dataset the caller named. `file` may also be an already-parsed `tablib.Dataset`, for a caller
that already holds one.

Calling either resource directly without naming a dataset — `GHFDBParentImportResource().import_data(...)`
with no `fairdm_dataset=` keyword — is refused the same way: a `ValueError` from `before_import`,
or a base error on the returned result if the resource absorbed it (the default, since
`raise_errors` is not set). A dataset existing in the database is never enough on its own; the
caller always names it.
