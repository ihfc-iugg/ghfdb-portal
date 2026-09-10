# Decisions — 004 Import a completed upload template into a dataset

Rationale too long to sit inside `spec.md`, plus every ambiguity resolved without asking.

## D1 — The portal's vocabularies are the authority, the template's sheet is not

**Ambiguous because** the upload template ships a `controlled vocabulary` sheet listing permitted
values, and the portal separately holds its own concepts for the same columns. Either could have
been treated as the thing an import validates against, and the sheet is the more convenient of the
two because it travels with the file.

**Chosen**: the portal's concepts decide. The sheet is guidance for whoever fills the spreadsheet in
and is never read by the import. A value the sheet permits but the portal holds no concept for still
refuses the file.

**Defensible because** it is the standing ruling for this portal, given during grilling on
2026-09-10: the vocabularies in the portal app are canon and are what matters. It also has the better
failure mode. Validating against the file lets a stale or edited copy of the sheet decide what enters
the database, which puts the authority inside the artefact being checked.

**Consequence accepted**: the two will disagree, and a file that a data provider believes is correct
will be refused. That is worked out as real datasets are imported, not by reconciliation code
written now.

## D2 — Only failures the portal cannot absorb refuse a file

**Ambiguous because** the template carries three separate contracts of its own: the obligation row
(M/R/O), the allowed-range row, and the vocabulary sheet. Enforcing all three at import would have
been a defensible reading of "validate the file".

**Chosen**: the obligation row and the allowed-range row are not enforced. What refuses a file is a
header that is not the official one, a value the model cannot store, a vocabulary value with no
matching concept, or an empty mandatory model field.

**Defensible because** those two rows are data reporting contracts rather than storage constraints,
and the aim is for a good file to import smoothly with errors raised only where the database or the
application genuinely cannot accept what it is given. They become checks at a later point.

Note the asymmetry with D1: the vocabulary sheet is not a deferred check. It is simply not the
authority, while vocabulary validation against the portal's own concepts is in scope from the start.

## D3 — The official template is the fixture

**Ambiguous because** three spreadsheet fixtures already exist in the test suite and could have been
extended.

**Chosen**: the work is built and tested against an unmodified copy of the published template. The
existing fixtures are hand-built hybrids, and the column constants in the code disagree with the
template on ten names, so the current tests establish nothing about a real upload.

**Defensible because** the feature's whole claim is that the file the assessment team fills in can be
read. A fixture nobody uses cannot support that claim.

## D4 — No revision marker, so the header is the detection

**Ambiguous because** nothing inside the template says which revision of it a file is, so a revised
template that renames, adds or drops a column would be discovered only when a header stopped
matching.

**Chosen**: accepted as-is. The header check is the detection.

**Defensible because** a revision handling scheme has no requirement behind it yet, and the failure
it would guard against is loud rather than silent: the file is refused, naming the header.

## D5 — Roadmap corrections this feature carries

R3 and R5 are struck through, with an ADR recording that the data assessment team ended the release
import direction. R6 gains a note that this feature delivers its programmatic half and the page
follows separately. Recorded here because they are decisions this run took, and they land on this
branch.
