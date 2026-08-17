# ADR 0006 — A heat flow site is identified by its coordinates

**Status:** accepted

## Decision

A heat flow site is defined by its latitude and longitude, reported to five decimal places. One
site per coordinate pair. Two boreholes a hundred metres apart are two sites.

Coordinates are taken exactly as supplied. The portal performs no rounding, no tolerance matching
and no merging of sites that are near each other but not identical.

"Site" and "location" are synonyms and are used interchangeably.

## Why

Coordinates are the only identifier that every contributor supplies and that means the same thing
across a century of publications. Anything richer, such as a borehole name or an operator's well
identifier, is present in some records and absent from most.

The alternative reading, that a site is an access point such as one borehole or one probe
deployment, is defensible from the model, which carries borehole geometry and total depth. It was
rejected because it introduces a distinction the assessment team does not make, and a shared
vocabulary with the people supplying the data is worth more here than a finer-grained one.

Proximity matching was considered and rejected as out of scope. The same borehole can legitimately
arrive with slightly different coordinates from two publications, one digitised from a map and one
read from an instrument, and deciding whether two nearby records describe one physical location is
a judgement about the source literature. That judgement belongs to data assessment. A tolerance
window would also introduce the opposite error, silently collapsing genuinely distinct sites that
happen to fall within it.

Note that a coordinate's stated precision is not its actual precision: values are supplied to five
decimal places regardless of how precisely they were determined, so a coordinate originally known
to two decimal places arrives padded with zeros. Any future work that reasons about precision has
to account for this rather than trusting the digits.

## Revisit if

Coordinate uncertainty is captured as data rather than implied by formatting, which would make
proximity reasoning sound rather than speculative.
