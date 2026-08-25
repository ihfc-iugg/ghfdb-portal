# Research — 003 a published release read into the portal

Written 2026-08-24, against `django-import-export` 4.3.9 as installed, the published 2024 release
file, and the portal's own models. Every claim here was read out of the source or measured from the
file rather than recalled.

Paths below are relative to the installed package unless stated otherwise.

## R1 — The release file, measured

`assets/ghfdb/IHFC_2024_GHFDB.zip` holds `IHFC_2024_GHFDB.csv`: 91,182 data rows, 74 columns,
header on line 1, comma separated, UTF-8 with a byte-order mark.

- The header is the published parent and determination columns in order, then `Reviewer_name`,
  `Reviewer_comment`, `Review_date`, `Review_status`, `Country`, `Region`, `Continent`, `Domain`,
  `Year`, `Quality_Code`, `ID_parent`, `ID`.
- **The identifiers are the last two columns, not the first.**
- Two column names are the misspelled published forms. The file carries no correct spelling of
  either.
- Six names in the portal's canonical lists are absent from the file, all of them quality columns.
  The portal computes quality, so their absence is correct rather than a gap.
- The published absent-value marker is `[Unspecified]`. It appears in numeric columns 651 times in
  `elevation`, 494 in `q_top` and 564 in `q_bottom`, and is the only non-numeric value any numeric
  column holds.
- `q`, `qc`, `lat_NS` and `long_EW` are populated and numeric on every row.

Counts the design depends on: 1,586 distinct publication references, none empty; 71,934 sites, each
with exactly one coordinate pair; 91,182 distinct determination identifiers, one per row; 8,145
intervals carrying more than one determination; 4,687 site groups with no depth at all; 974 shared
intervals whose rows contradict each other about the probe.

**Consequence.** The stock `CSV` format reads this layout without modification — see R2. The two
formats the portal has today cannot: both are spreadsheet-only, open a sheet named `data list`, and
take headers from row 6.

## R2 — Reading a comma-separated file

`formats/base_formats.py:136` defines `CSV(TextFormat)`, delegating to tablib. Tablib's CSV reader
defaults to `headers=True, skip_lines=0`, so line 1 is the header and line 2 begins the data —
exactly the release layout.

Two behaviours to guard against, both in tablib's reader:

- A short row is right-padded with empty strings to the dataset width rather than refused.
- `resources.py:889` builds each row with an unguarded `zip(dataset.headers, data_row)`, so a row
  with surplus columns silently loses the surplus.

Neither raises. A row whose column count does not match the header is therefore invisible unless we
check it ourselves, which is what FR-003's header check and FR-015's "every row is imported or
reported" together require.

`get_title()` returns the bare string `csv`, which is what the format dropdown renders. A subclass
supplying a readable title is worth the four lines.

## R3 — There is no true "abort before row one"

`Resource.before_import(dataset, **kwargs)` (`resources.py:595`, called at `:875`) is the only hook
that runs after the dataset is loaded and before any row. It receives the live dataset, so
`dataset.headers` is available there.

**Raising inside it does not stop the import.** The call sits in a `try` whose handler is
`handle_import_error(result, e, raise_errors)` (`resources.py:672`), and with `raise_errors=False` —
the admin's setting — that appends to `result.base_errors` and returns. Control falls straight
through to the row loop and **every row is still processed**.

What makes the file genuinely stop is emptying the dataset. The library re-reads its length
immediately afterwards, with a comment saying why (`resources.py:882`):

```python
# Update the total in case the dataset was altered by before_import()
result.total_rows = len(dataset)
```

So the header check is: append a base error naming the fault, then wipe the dataset. The user sees
the error, the confirm form is never offered (`admin.py:533` only builds it when the result has no
errors), and no row is read.

The library's own header check, `_check_import_id_fields` (`resources.py:1141`), is not a substitute.
It returns without checking anything while `import_id_fields` is the default `["id"]`
(`resources.py:1153`), and even when configured it only checks the identifier columns. A missing
ordinary column is silently skipped per row at `resources.py:417`.

## R4 — The admin already runs two passes, and the second one re-reads the file

`import_action` (`admin.py:436`) writes the upload to temporary storage, parses it, and calls
`import_data(dry_run=True, raise_errors=False)` (`admin.py:523`). If the result is clean it offers a
confirm form carrying only the temporary file's name in a hidden field (`admin.py:391`, `forms.py:82`).

`process_import` (`admin.py:150`) re-reads and re-parses that file (`admin.py:173`) and calls
`import_data(dry_run=False)` through `process_dataset` (`admin.py:204`). It carries no state from the
first pass.

This is the check-then-write shape the specification asks for, already built. What it costs is
parsing the file twice, which is a size concern and out of scope.

**Two resources are constructed, one per pass** (`admin.py:514`, `admin.py:200`), so anything
`before_import` creates on the dry run is a different object from the one the real pass creates —
and the dry run's is rolled back anyway. Nothing may cache a primary key across passes.

## R5 — The default admin flow violates FR-011, and must be overridden

This is the finding with the most consequence.

Rollback is decided after the row loop, on the outer atomic block (`resources.py:851`):

```python
if using_transactions and (
    dry_run
    or result.has_errors()
    or (rollback_on_validation_errors and result.has_validation_errors())
):
    set_rollback(True, using=db_connection)
```

`has_errors()` covers hard exceptions only. A value the portal refuses is a *validation* error, and
`rollback_on_validation_errors` defaults to `False` (`resources.py:790`). `process_dataset`
(`admin.py:204`) does not pass it.

**So on the confirmed pass, valid rows commit and refused rows are silently skipped.** The library's
own skip-confirm branch sets the flag to `True` and says why (`admin.py:461`): "If this is not done
validation errors would be silently skipped." The two-step flow does not.

Worse, `process_result` (`admin.py:212`) redirects with a success message without checking the
result at all, so a partly-written import reports as a success.

The specification requires the opposite: nothing is written unless every row passes. The fix is to
override `process_dataset` to pass `rollback_on_validation_errors=True`, and to check the confirmed
pass's result before reporting success. Both belong to US-1 and both need a test that fails without
them.

Transactions are otherwise sound: `use_transactions` defaults to `True` (`resources.py:129`), a dry
run is transactional regardless (`resources.py:835`), and there is a per-row savepoint
(`resources.py:890`).

## R6 — Where a fault's row and column come from

`Error` (`results.py:15`) carries the row number and the whole row, **and no field name**. Field
identity survives only for validation errors, through `InvalidRow.error_dict` (`results.py:161`).

The route that keeps the field is a `ValueError` raised inside a widget. `import_instance`
(`resources.py:472`) catches it and re-tags it:

```python
except ValueError as e:
    errors[field.attribute] = ValidationError(force_str(e), code="invalid")
```

Two things follow.

- **A widget must raise `ValueError`, never `ValidationError`.** A `ValidationError` bypasses that
  handler, lands in the catch-all at `resources.py:768`, and is filed under `NON_FIELD_ERRORS` with
  the field name lost.
- The key is `field.attribute`, the model attribute, **not** the published column name the file
  used. FR-010 asks for the column as it appears in the header, so the column name has to reach the
  reader another way. The cheapest route that does not fight the library is the message itself: a
  widget knows its own column, so it names it. Some of the portal's widgets already do this.

**Row numbers are 1-based over data rows and exclude the header** (`resources.py:888`). For a
comma-separated file with a header line, the file's line number is that number plus one. The stock
template labels the column "Line number" (`templates/admin/import_export/import.html:100`), which is
off by one against the file the curator is looking at. FR-010 says the row number as it appears in
the file, so this needs correcting rather than inheriting.

Continuing past a failure is already the default: the loop aborts early only when `raise_errors` is
true (`resources.py:945`), and the admin sets it false on both passes. FR-009 needs no work.

## R7 — Identity, and what the library gives us

`Meta.import_id_fields` drives which existing record a row updates. The published determination
identifier is unique across every row of the release, so it is the determination's identifier
directly.

Everything else follows from relationships rather than from columns in the file:

| Record | Identified by | Where that comes from |
|---|---|---|
| Site | published site identifier | column, 71,934 distinct |
| Site-level determination | its site | one per site |
| Interval | its site and the depth range the row gives | columns, or the indeterminate interval |
| Determination | published determination identifier | column, unique per row |
| Gradient, conductivity | the determination's identifier | D16 |
| Correction | its determination and correction type | `unique_together` already on the model |
| Probe metadata | its interval | one-to-one already on the model |

The two model facts were read from the portal: `HeatFlowCorrection` declares
`unique_together = [("heat_flow", "correction_type")]`, and `ProbeMetadata.interval` is a
`OneToOneField`. Neither needs changing.

`Measurement.sample` is an ordinary foreign key, so an interval can carry many determinations. That
is what makes D15 expressible without a model change.

## R8 — Creating the datasets and the bibliographic records

`before_import` is the once-per-run hook (`resources.py:595`), and the resource instance lives for
the whole run, so it can resolve every publication reference in the file up front and stash the map
for the row pass. `after_import` (`resources.py:606`) is its counterpart.

It must branch on `dry_run`, which the admin passes explicitly on both calls, because the hook runs
on both passes against two different resource instances.

`get_import_resource_kwargs()` (`mixins.py:136`) is the supported route for handing the resource a
value chosen on the import form. The repository already uses it to require a target dataset, in the
change awaiting merge as #183 — which this feature supersedes for the release path, since a release
import chooses its datasets from the file rather than from the form.

The portal's bibliographic record requires only a citation key and a type, and its citation key is
documented as not unique. So a stub is creatable, and a lookup can legitimately return more than one
row, which is why FR-020 refuses rather than picks.

## R9 — The confirm page's columns

The diff table's headers and values both come from `resource.get_import_fields()`
(`resources.py:589`, `resources.py:66`), ordered by `_get_ordered_field_names("import_order")`
(`resources.py:1118`): `Meta.import_order` first, then `Meta.fields`, then the remaining declared
fields in declaration order.

So the confirm page follows published order by setting `Meta.import_order` to the release format's
column list. This is the same mechanism the export side got wrong, and the reason it went wrong —
entries that match no field name are dropped silently (`resources.py:1040`) — is worth carrying
across as a test rather than a comment.

## R10 — What we are not doing, and why

- **Streaming.** Nothing in the library streams: the upload is concatenated into one bytes object
  (`admin.py:421`), re-read whole (`tmp_storages.py:30`), parsed into one in-memory dataset
  (`admin.py:496`, whose own comment reads "warning, big files may exceed memory"), and a
  `RowResult` is retained for every row (`results.py:234`). `Meta.chunk_size` is export-only. Size
  is the operator's concern by ruling, so this is recorded and left alone.
- **`collect_failed_rows`.** It would build a second copy of every failed row. The reporting FR-010
  asks for is per-fault, not a rejected-rows file, so it stays off.
- **Reusing the two existing import resources.** They read a different file, split parent and
  determination across two user actions, and carry the natural-key fallback D10 removes. The release
  path is a third resource that shares the widget layer and the column definitions, and nothing
  else.
