# ADR 0014 — An unmatched publication reference creates a bibliographic record, and an ambiguous one is refused

**Status:** accepted

## Decision

Each distinct publication reference in a release becomes one dataset. The reference is matched
against the portal's bibliographic records by citation key, ignoring case and surrounding
whitespace, and matched in the database rather than only within the file being read.

The three outcomes are fixed:

- **One match.** The dataset links to that record and takes its title.
- **No match.** A bibliographic record is created carrying the citation key and nothing else.
- **More than one match.** Every row carrying that reference is refused, and the refusal names the
  reference and the records it matched.

## Why

A release cites a century of literature, most of which the portal has never held. Requiring every
publication to exist before a release can be read would make the reader unusable. The portal's
bibliographic records need only a citation key and a type to be valid, so a record holding just the
key is a legitimate record that someone can complete later. The alternative, attaching
determinations to no publication at all, loses the one piece of provenance the release always
supplies.

Citation keys are deliberately not unique in the portal's records, so two matches is a real
outcome rather than a defensive branch. Choosing between them would attach a determination to a
publication on a guess, and a wrong attribution is harder to find later than a refused import is to
fix now.

The comparison ignores case and surrounding whitespace because the release supplies both variations
for what is plainly one reference. It does not go further than that: two keys differing in any
other way are two references.

## Revisit if

Citation keys become unique across the portal's bibliographic records, which would remove the
ambiguous case entirely.
