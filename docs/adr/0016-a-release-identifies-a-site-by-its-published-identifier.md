# ADR 0016 — A release import identifies a site by its published identifier

**Status:** accepted. Narrows [ADR 0006](0006-a-site-is-its-coordinates.md), which continues to
hold for the contributor upload template.

## Decision

When a published release is imported, a site is the site its published site identifier names. Two
rows carrying the same identifier describe one site, whatever coordinates they give, and a row
carrying an identifier already in the database updates that site rather than creating a second one.

Coordinates no longer decide identity on this path. Where two rows sharing an identifier give
different coordinates, or differ on any other column belonging to the site, the file is refused and
the disagreement is named. Neither value wins.

A site's name plays no part in identity, and a row that names no site still describes one. The name
is stored exactly as the file gives it, including when that is a number, a question mark, or
nothing at all.

The contributor upload template is unchanged. It carries no published site identifier, so it still
resolves a site by its coordinates as ADR 0006 describes.

## Why

A release carries a published identifier for every site, and the people who assemble it use that
identifier to mean the site. ADR 0006 chose coordinates because they were the only thing every row
of the contributor template carries. That reason does not apply to a release, which carries the
identifier as well.

The identifier is also the safer of the two on this path. Coordinate identity would merge two rows
that fall on the same coordinate pair but carry different identifiers, which in a release is the
publishers saying they are different sites. It would equally split one site in two on a coordinate
that differs in its last decimal place, and either error would happen without a word.

The same reasoning already settled the determination's identity (ADR 0010), including removing a
fallback that computed a key from coordinates when an identifier was missing. A release always
carries both identifiers.

Refusing a coordinate disagreement rather than choosing between the values follows the standing
constraint that the portal does not guess at supplied data. A disagreement inside one file is a
fault in the file, and the curator who prepared it is the person who can settle it.

## Revisit if

The contributor upload template gains a site identifier column, which would leave the portal with
one identity rule rather than two.
