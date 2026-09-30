# ADR 0022 — Stored quality scores are recalculated when their inputs are written

**Status:** accepted

## Decision

Quality scores are stored on the records they describe:

- a thermal gradient's T-score and an interval conductivity's TC-score
- a child's U-score, corrected sub-scores, M-score and quality code
- the quality a parent inherits

A page, an export or the API reads the stored value and never calculates one.

A stored score is recalculated at the moment one of its inputs is written:

- Signal receivers on every model that holds an input (the gradient, the conductivity, the
  interval, the probe metadata, the site, the child and its corrections) refresh the scores that
  read it.
- The refresh runs upward: the measurement first, then the children that use it, then their
  parents.
- A refresh writes with a queryset `update`, so it never triggers another refresh.
- A delete collects what it affects and refreshes once, when the transaction commits, and only for
  records that still exist.
- A file import holds recalculation back while it runs and scores everything it wrote once, at the
  end and inside its own transaction.

Every stored score also records the revision of the scheme that produced it. The `refresh_quality`
management command recalculates every record whose revision is not the current one, or every
record with `--all`. The container runs it after migrating, on every start.

## Why

ADR 0004 makes the portal's calculated scores authoritative. Its objection to supplied codes is
that they go stale silently. A stored score that goes stale is exposed to the same objection.
Calculating on read would avoid staleness, but it would make the corrected sub-scores impossible
to query (FS-007 D4), and every list and export would pay for the calculation.

Recalculating on write keeps a stored value that is never knowingly stale. The cost falls on the
write that changed an input, where it belongs. Holding recalculation back during an import, and
collecting deletes until commit, stop that cost from multiplying: an imported row writes a child
through a dozen saves, and a dataset delete cascades through every correction.

Scoring existing records at deploy could have been a data migration. But a migration sees
historical models, which do not carry the scoring code, and calling the live code from a migration
breaks as soon as a later migration changes a field. A command keyed on the stored revision avoids
both. It is a single count when everything is current, and it is also how a later revision of the
scheme will be adopted: bump the revision, deploy, and every record is recalculated.

## Consequences

- A new model field that the scheme reads needs a receiver, or its changes will not reach the
  scores.
- A queryset `update` or `bulk_create` bypasses the receivers, as it bypasses every Django signal.
  `refresh_quality --all` is the repair.
- The first start after this change scores every record one at a time before the site serves, and
  an error in that run stops the container from starting.

## Revisit if

Recalculation on write becomes too slow for interactive edits, or imports grow to the point where
scoring them at the end of the transaction is not acceptable. Moving the refresh to a background
task queue would then keep the same stored values and revision tracking with a different trigger.
