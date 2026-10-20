# ADR 0025 — A heat flow type serves a summary in a list and the whole record on its own

**Status:** accepted

## Decision

Each of the six heat flow types (site, depth interval, child, thermal gradient, interval
conductivity, parent) names its API serializer in its registration with `serializer_class`. The
serializers are declared in `heat_flow/serializers.py` and build on FairDM's
`BaseSampleSerializer` or `BaseMeasurementSerializer`.

- A type has a **summary**, which a list serves, and may have a **full record**, which a single
  record serves. The full serializer sets `summary_serializer`, and the shared base,
  `HeatFlowRecordSerializer`, overrides DRF's `many_init` so a list is built from the summary.
- The routes stay FairDM's generated viewsets, so addresses, paging, ordering, filtering and
  visibility are the framework's. The project registers no viewsets of its own for these types.
- A drf-spectacular extension, `HeatFlowRecordSchema` in `heat_flow/schema.py`, gives a list
  operation the summary's component and a single record the full one.
- Every related record, nested or referred to, passes `FairDMVisibilityFilter`, the rule of that
  record's own route. A hidden record is left out of a list, and is `null` where it would be a
  single value.
- A serializer keeps every writable field the generated one had. What it adds is read-only.

## Why

FairDM generates one viewset per type from its registration, with one serializer for every
action. A list of sites that carried every interval and child of every site would grow by an order
of magnitude, while a single site without them would cost a consumer one request per interval.
The published-structure endpoints already make the same split (a determination links to its
parent in a list and nests it on its own route).

`many_init` is DRF's documented hook for building the list serializer, so the split needs no
viewset of the project's own. DRF's router refuses a second registration under a basename and has
no way to remove one, so replacing the generated viewsets would mean editing the router's internal
list. Declared serializers named in the registration read as ordinary DRF code, which serializers
built at runtime inside `get_serializer_class()` would not.

## Revisit if

FairDM lets a registration give a list and a single record different serializers, or lets a
project replace a generated viewset. Either makes the `many_init` override and the schema
extension unnecessary.
