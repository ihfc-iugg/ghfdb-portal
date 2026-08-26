# ADR 0015 — A site reported by several publications belongs to the earliest one

**Status:** accepted

## Decision

A site belongs to the dataset of the earliest publication year among the determinations reported
for it.

Its determinations do not move with it. Each stays with the dataset of the publication that
reported it.

Ownership is compared as each import runs, not resolved from the whole file in advance. When a
publication with an earlier year is imported after a later one, the site moves to it. When the
later one arrives second, the site stays where it is. A site created by the row being read is
already in the right dataset and is never reassigned.

## Why

Sites are shared far more often than the model's one-dataset relationship suggests. In the 2024
release, 4,817 of 71,934 sites carry determinations cited to more than one publication. Site
identity itself is never in doubt, since a release names every site by its published site
identifier (ADR 0016), so this is purely a question of which dataset holds it.

Earliest-publication ownership matches how the framework describes the relationship: the dataset a
sample first appeared in. It is also the only rule that is stable. Any rule keyed on import order,
including simply leaving the site where it first landed, gives a different answer depending on
which file a curator happened to load first.

Comparing per import rather than per file is what makes the rule hold however the work is divided.
A curator may import one publication today and another next year, and the answer has to be the same
as if both had arrived together.

Determinations stay put because the publication that reported a determination is a fact about that
determination, not about the site it sits under. Moving them would erase provenance to tidy a
relationship.

## Revisit if

The model gains a way for a site to belong to more than one dataset, which would make the choice
unnecessary.
