# ADR 0021 — A determination is served only through a parent that is served

**Status:** accepted

## Decision

Anything that serves the published structure outside the portal serves a determination only when
its parent is served to the same person. A parent lists only the determinations that would be served
on their own. A determination with no parent, or with a parent that has no published identifier, is
not part of the published structure and is not served.

The first place this applies is the read API over the published structure (FS-006): the parent,
determination and flat endpoints.

## Why

Whether a record can be seen depends on its own dataset. A determination and its parent can sit in
different datasets:

- The child import looks up `ID_parent` across every parent, whatever dataset it belongs to.
- When a row has no `ID_parent`, the import attaches the determination to whichever site is at its
  coordinates.

An uploaded dataset stays private until a curator approves it. So both mismatches can happen. A
determination still under review can name a public parent. A public determination can attach to a
site that isn't public yet.

The framework's visibility filter only looks at the records a view is serving. It does not look at
records reached through a relation. If each side of the pair were checked on its own, the unapproved
record would leak through the approved one. The first case would expose the unapproved
determination's columns on its parent's route. The second would expose the unapproved parent's
values, its coordinates among them, on every row of the determination.

Requiring both sides of the pair to be visible closes both paths with one rule. It also keeps the
structure consistent: every determination a consumer receives has a parent they can follow, and
every parent lists only determinations they can reach.

## Consequences

- A parent's `total_children` and `relevant_children` count every determination at the site. That
  can include determinations these rules keep from the consumer, and the consumer guide says so.
- A determination becomes visible only once both its own dataset and its parent's are visible.

## Revisit if

The import stops attaching determinations across datasets, so a determination and its parent always
share one. Their visibility would then always match, and this check would never exclude anything.
