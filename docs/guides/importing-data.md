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

Anything else raises `ValueError`, with a message naming both what is missing and what does not
belong, followed by the header it was given. The function inspects only the header it is handed and
reads no rows and touches no database, so a file refused here is refused before any part of it could
have been written. `import_ghfdb_template` calls it on every file it is given, before it opens a
transaction.

Seven columns are optional, and everything else the template carries is required:

- `ID` and `ID_parent`, which name a determination and its parent so that a later file can correct
  them. A first submission has none to give, and both resources fill the columns in when they are
  absent.
- `Ref_IGSN` and `igsn`, the two spellings of the sample reference, which nothing in the data model
  holds yet.
- `Reviewer_name`, `Reviewer_comment` and `Review_date`, which are filled in during assessment,
  after a submission has been read.

Column order is not checked — every reader here addresses columns by name — and the label the
template puts in the first cell of its header row is ignored.

`project.ghfdb.constants.UPLOAD_TEMPLATE_HEADER_ROW` is the template's header row in the template's
own order, and `REQUIRED_TEMPLATE_COLUMNS` and `OPTIONAL_TEMPLATE_COLUMNS` are the two sets the
check uses, should you need to compare a header yourself rather than have one validated.

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

What comes back is a `project.ghfdb.importers.GHFDBImportOutcome`, a small record holding the two
`import_export.results.Result` objects in the order the passes ran, as `parent` and `child`. Its
`has_errors()` is true when either pass reported an error, so a caller that only needs to know
whether the file landed can ask the outcome rather than unpack both results itself.

Underneath, it runs the **parent pass** — every site and its parent heat flow value — before the
**child pass** — the determinations beneath each site — since a child row resolves its parent from
the site the parent pass has already created. Both passes run inside one transaction and are wired
to the dataset the caller named. `file` may also be an already-parsed `tablib.Dataset`, for a caller
that already holds one.

Calling either resource directly without naming a dataset — `GHFDBParentImportResource().import_data(...)`
with no `fairdm_dataset=` keyword — is refused the same way: a `ValueError` from `before_import`,
or a base error on the returned result if the resource absorbed it (the default, since
`raise_errors` is not set). A dataset existing in the database is never enough on its own. The
caller always names it.

## Nothing is written when the file carries a fault, and every fault is located

A fault is one of four things: a header that is not the official one, a value the model cannot
store, a controlled-vocabulary value the portal holds no concept for, or an empty mandatory model
field. If any row in either pass has one, nothing from the file is written — not just the faulty
row, the whole file, including every row that was otherwise clean:

```python
outcome = import_ghfdb_template(xlsx_bytes, dataset)

if outcome.has_errors():
    for row_number, errors in outcome.parent.row_errors():
        for error in errors:
            print(row_number, error.error)
    for invalid in outcome.child.invalid_rows:
        print(invalid.number, invalid.field_specific_errors)
```

`row_errors()` covers a value the model cannot store or a fault raised while a relation is being
set (a controlled-vocabulary value with no matching concept, for one); `invalid_rows` covers an
empty mandatory model field, reported by `full_clean()`. Both name the row; `invalid_rows`'
`field_specific_errors` additionally names the column. Every fault in the file is collected this
way rather than the import stopping at the first one.

### Three fields are excluded from row validation

Reporting an empty mandatory field needs `Meta.clean_model_instances` turned on, which makes
django-import-export run `full_clean()` on each row's instance before it is saved. Three fields are
not populated at that point: `sample`, `dataset` and `name`. Both resources fill those in on the way
to the database, in `before_save_instance()`, which runs later. Validating them at row-validation
time would refuse every row of every file on relations the resource is about to set correctly.

`ExcludeFieldsSetAfterValidation`, in `project/ghfdb/resources/validation.py`, is the one override
both resources share. It runs the same validation django-import-export would, minus those three
fields.

For `sample` and `dataset` the database's own constraint stays as the backstop: both are foreign
keys, so a failure to set one is reported as a database-level row error rather than a located
message naming the column. `name` has no such backstop. It is a required text field, and a field
left unset saves as an empty string that no constraint objects to, so both resources set it on
every row: a record's own identifier where the row carries one, and the site it belongs to where it
does not.

## The portal's own vocabulary decides, not the template's sheet

The template ships a "controlled vocabulary" sheet listing values it considers permitted for each
controlled-vocabulary column. The import never reads it. What a controlled-vocabulary column
accepts is decided entirely by the concepts the portal itself holds for that vocabulary: a value
the sheet lists but the portal holds no concept for is still refused, and a value the portal holds
a concept for but the sheet does not list is still accepted. The two are expected to disagree from
time to time; when they do, the portal's concepts are what matters, not the copy of the sheet
travelling with the file.

## Importing the same file again updates what is there

Re-sending a file the dataset already holds the contents of does not add a second copy of
everything. Unchanged, it changes nothing; with a value corrected, the existing record picks up the
correction rather than a new one being written beside it.

The published template carries neither an `ID` nor an `ID_parent` column, so this holds without the
caller ever supplying one. The parent pass matches an existing site (and the parent heat-flow value
beneath it) by coordinates; the child pass resolves its parent through those same coordinates, and
separately matches an existing determination by the site's coordinates, the determination's
publication reference, and the determination's position within the file. That third piece is what
lets correcting a depth interval (`q_top`/`q_bottom`) update the existing determination instead of
writing a second one at the same site: depth is no longer part of what identifies it.

This depends on a resent file presenting its rows in the same relative order as the file it is
correcting. A row that moves earlier or later in the file — because rows ahead of it were inserted,
removed or reordered — is matched as if it were a new determination rather than the one it is
meant to correct. Re-sending the same file with one cell changed, which is how corrections actually
arrive, keeps every row's position exactly where it was.
