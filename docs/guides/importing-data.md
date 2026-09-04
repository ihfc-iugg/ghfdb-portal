# Importing a release

The admin site can read a full published release of the Global Heat Flow Database: the file GFZ
Data Services distributes with the release's DOI, one row per determination, with each site's own
columns repeated on every row that belongs to it.

## Where to import it

In the admin site, open the GHFDB Children page and use the Import action. The action is only
available to a user holding permission to add a determination; anyone else does not see it, and
opening the import page directly is refused.

Choose "GHFDB Release Format" from the file format list and upload the release file.

## What the check reports

Before anything is read, every column in the file's header is checked:

- Two published column names are known to appear misspelled in the distributed release. A file
  carrying either is refused, naming the misspelled column, the corrected name, and describing the
  file as following an outdated template.
- A column name the release format does not define is refused, naming that column.
- A column the release format requires, which the file's header does not carry, is refused, naming
  the missing column.

If the header passes, every row is checked next, and every fault found is reported together rather
than stopping at the first one. Each fault names the column as it appears in the file's header, the
line the row occupies in the file (counting the header line, so the first row of data is line 2),
the value that was rejected, and why.

Two further checks apply across rows: two rows describing the same site are refused if they
disagree about that site's own details, and two rows describing the same measured interval are
refused if they disagree about the probe that took the measurement. Both name the columns in
disagreement and the conflicting values.

## What happens when a file fails

Nothing is written. If even one value anywhere in the file is refused, the whole import is refused
and rolled back in full, including the rows that were themselves valid — the page reports the
failure rather than a success message.

Correct the file at the fault named and upload it again. Once every row passes, the import writes
everything at once.

## Very large files

Because a file is imported whole or not at all, the whole file is read into memory first, and the
database stays inside one transaction until the run finishes. A full release imports as one file.
If a particular file is large enough to make that slow, split it and import the pieces in turn.
Splitting is safe. A site or an interval that more than one piece describes is recognised as the
same one, and a row already imported is updated rather than duplicated.
