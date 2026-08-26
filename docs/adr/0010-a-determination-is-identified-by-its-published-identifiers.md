# ADR 0010 — A determination is identified by its published identifiers

**Status:** accepted

## Decision

A heat flow determination is identified by the identifier the published release gives it, held in
the field named for that identifier. The same holds for the parent value a determination belongs
to. No identity is computed, and nothing is inferred from a record's other values.

The gradient and the conductivity a determination was derived from take that determination's
identifier as their own. Every record a row produces, apart from the depth interval, is therefore
reachable from the determination's identifier alone.

Two consequences follow and are part of the decision:

- A record's name is a label, never a key. A computed key stored in a name field is not identity
  and does not count as one.
- Nothing is matched on its value. Two rows giving the same gradient are two gradients unless the
  determination identifier says otherwise.

## Why

Reading the same release twice has to leave the portal unchanged, and that is only possible if
every record a row produces can be found again from something the row states. The published
identifiers are the only such thing. They are assigned by the people who assemble the release, they
are stable across editions, and a release always carries them.

The alternative that had to be ruled out is matching a dependent record on what it holds. A release
gives no distinction between a determination re-derived from a fresh measurement and one newly
added, and it does not need to: both arrive as a new row with a new identifier over an interval
that already exists, and what separates them is which publication reported each. Matching on value
would collapse those two cases, and it is the proximity reasoning this project rules out elsewhere
wearing a different hat.

Measured against the 2024 release, 43 per cent of the groups sharing one interval give different
gradients and 31 per cent give different conductivities. Treating a gradient as belonging to its
determination records what the file states. Treating it as belonging to the interval would assert
something the file never says.

The earlier reading, that the identifiers map to a record's general-purpose local identifier while
a computed key lives in its name, was rejected. It made identity depend on a field that means
something else, and it left a fallback that invented a key from coordinates whenever the identifier
columns were absent. A release always carries both identifiers, and the contributor upload template
is a separate format with its own rules.

## Revisit if

A release edition stops carrying determination identifiers, or begins reusing an identifier for a
different determination between editions.
