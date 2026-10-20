# ADR 0026 — A quantity is a number in its stored unit, and the record names the unit

**Status:** accepted

## Decision

Through the API, every quantity field of a heat flow record is a plain JSON number in the unit the
model declares as its `base_units`. The record carries a `units` object that maps the name of each
of its quantity fields to that unit, written in pint's compact form (`mW/m²`, `K/km`, `°C`, `m`).
A nested record carries its own `units`.

- An empty quantity is `null`, and its unit is still named in `units`.
- A decimal quantity is a number too, never a string.
- Units are not converted on request.

## Why

A record that names its own units can be read without the schema, which the constitution's FAIR
and labelling articles ask for. A `{magnitude, unit}` object per value was weighed and not
adopted. An empty value would then carry no unit at all, and every consumer would have to unwrap
every number. Giving each number in its declared unit keeps one canonical unit per field, the one
the portal stores and computes quality scores in.

## Revisit if

A consumer needs values in a unit other than the stored one, or a unit string a unit library can
parse without its compact notation.
