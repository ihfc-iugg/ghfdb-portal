# ADR 0023 — A site holds the location, and its elevation stays its own

**Status:** accepted

## Decision

A heat flow site is a named location, a station. It is the one record in the portal that holds
coordinates:

- The site's latitude and longitude are its `location`, the WGS 84 point FairDM declares on every
  sample.
- A depth interval and the measurements made over it hold no location of their own. They are
  placed at their site, and every table, export and API response reads their coordinates through
  the interval's `site`.

A site's elevation is `HeatFlowSite.elevation`, a quantity with its `elevation_datum`, and it is
the only one. FairDM's `location_elevation` and `location_uncertainty` stay empty on every record:
nothing in the portal writes them, and the GHFDB `elevation` column reads and writes
`HeatFlowSite.elevation` as it did before.

## Why

FairDM holds a location as a value on each record, so that a sample and a measurement each say
where they are. The GHFDB has no such thing. Its coordinates and its elevation are site columns,
and an interval or a determination is only ever where its site is. Copying the site's point onto
every interval and measurement would keep several copies of one fact that could drift apart, and
the published structure has nowhere to report a difference between them.

The site's elevation is a quantity with a unit and a datum, which the published structure carries.
`location_elevation` is a bare number of metres above mean sea level. Filling both would leave two
elevations that can disagree, and only one of them is published. Keeping `elevation` and leaving
FairDM's field empty means the published value and the stored one are the same field.
`location_uncertainty` has no counterpart in the published structure, so there is nothing to put
in it.

## Consequences

- A site's form shows FairDM's location input. Its elevation and uncertainty inputs are left
  unused.
- Measurement listings that show coordinates read them from the site and show them only to a
  viewer who may see that site.
- FairDM features that read `location_elevation` see no elevation for any record in this portal.
