# Research — 010 heat flow API representations

Investigated against `origin/main` at `54509ad` (FS-011 merged), FairDM pinned at `f69c9cb`,
Django REST Framework 3.18.1, drf-spectacular 0.29.0, pint 0.26.1.

There is no `planning-notes.md` and no `sketch.md` for this feature.

## What the six routes do today

The router builds each type's endpoints from its registration
(`fairdm.api.router.FairDMAPIRouter.register_types`), at `samples/heat-flow-sites/`,
`samples/depth-intervals/`, `measurements/heat-flow/`, `measurements/thermal-gradients/`,
`measurements/thermal-conductivities/` and `measurements/parent-heat-flow/`. The serializer is
`config.get_serializer_class()`, which the registry builds from the configuration's `fields` on
`BaseSampleSerializer` or `BaseMeasurementSerializer`.

**Five of the six list routes answer 500 today.** On the development server:

| Route | Status | Error |
|---|---|---|
| `samples/heat-flow-sites/` | 200 | — |
| `samples/depth-intervals/` | 500 | `DimensionalityError` |
| `measurements/heat-flow/` | 500 | `DimensionalityError: Cannot convert from 'milliwatt / meter ** 2' to 'dimensionless'` |
| `measurements/thermal-gradients/` | 500 | `decimal.InvalidOperation` |
| `measurements/thermal-conductivities/` | 500 | `decimal.InvalidOperation` |
| `measurements/parent-heat-flow/` | 500 | `DimensionalityError` |

ModelSerializer maps a quantity field to a `FloatField`, `DecimalField` or `IntegerField`, whose
`to_representation` calls `float()` or `Decimal()` on a pint `Quantity`. No test covers these
routes. Serving quantities as numbers in their stored unit (FR-011) removes the failure, so it is
part of this feature rather than a separate fix.

The generated fields, per type:

- A single vocabulary field (`ConceptField`) becomes a writable `ChoiceField`: it takes the term's
  name and gives the bare name back.
- Every relation the base does not declare becomes read-only: a `StringRelatedField` (a
  many-valued vocabulary field, and `stratigraphy`, a plain many-to-many to `StratigraphicUnit`),
  or a `RecordReferenceField` for a record (`fairdm/registry/factories.py:961-984`). Nothing is
  written through them today.
- A quantity becomes a writable number field that cannot be read (above).
- `location` is FairDM's `GeoJSONPointField`, read-only, reading the record's own location. Only a
  site holds one (ADR 0023), so every other type would serve `null`.
- The scores, quality codes, scheme revisions, `ghfdb_id` and the gradient, conductivity, parent
  and relevance of a child are not in any configuration's `fields`, so they are not served.

## How a type gets its own serializer

A registration names its serializer with `serializer_class` (a class or a dotted path), and
`generate_viewset` requires it to build on the kind's base serializer, `BaseSampleSerializer` or
`BaseMeasurementSerializer`. The registry otherwise builds one from the configuration's `fields`
with those bases' `Meta.fields` plus the configured names.

**Chosen:** each of the six registrations names a serializer declared in
`project/heat_flow/serializers.py`, built on the kind's base serializer, whose `Meta.fields` holds
the same writable model fields the generated one holds today, plus this feature's read-only fields.
The same model fields through the same ModelSerializer give the same writable fields, so what is
accepted today is accepted after (FR-017), and FairDM's system check `fairdm.E600`, which reads
the registered serializer, keeps guarding it. A serializer declared in a module reads as a DRF
serializer and nothing else, where one built inside `get_serializer_class()` would not.

Rejected: overriding `get_serializer_class()` to subclass the generated serializer at runtime, as
`HeatFlowSiteConfig.get_form_class()` does for the form. Twelve classes built inside methods are
harder to read, import and document than twelve declared ones.

Rejected: registering our own viewsets at the same addresses. DRF's router refuses a second
registration under the same basename, and has no way to remove one, so the generated viewsets
cannot be replaced without editing the router's internal list.

## A list and a single record in different shapes

`generate_viewset` gives a type one serializer for every action. DRF documents two ways to change
what a list holds without a viewset of one's own; the one that fits is `many_init`, the classmethod
DRF calls to build the list serializer when a serializer is created with `many=True` ("Customizing
ListSerializer initialization behavior" in DRF's serializer documentation). Each type's full
serializer overrides `many_init` to build its list from the type's summary serializer. A list
request reaches it through `self.get_serializer(page, many=True)`; a single record never does.

The schema needs the same split. drf-spectacular builds a list's item from
`view.get_serializer_class()`, so on its own it would describe each list item as the full record.
Its documented extension point for one serializer class is `OpenApiSerializerExtension`
(`get_name` and `map_serializer`), which can give the list operation the summary serializer's
component. One extension, matching this feature's base class and its subclasses, covers all six
types. Extensions are found by import, so the module holding it is imported from the app's
`ready()`.

## Queries

`generate_viewset` builds the queryset once, as
`load_relations(serializer.load_related(queryset), serializer)`: our `load_related` classmethod
adds what both shapes read (the site behind a record's coordinates, the many-valued terms), and
`load_relations` already prefetches every many-to-many named in `Meta.fields`.

A list page is checked as a page. FairDM's `RecordListSerializer` calls `prime()` on every
`RecordReferenceField` with the whole page before serializing it, so a reference costs one
visibility query per page however many records it holds. The site list's parent summary and the
visibility of the sites whose coordinates a page carries are gathered the same way, in a list
serializer subclass that does its page-level work before calling the parent's
`to_representation`.

A single record's nested lists (a site's intervals and their children, a parent's children, an
interval's measurements) are read in the serializer for that one record, each as one query
narrowed by visibility, so the count does not grow with the number of related records.

## Visibility

- References: `RecordReferenceField` already returns `null` for a record the requester may not see,
  using FairDM's own list rule (`FairDMVisibilityFilter`).
- Lists of related records: `FairDMVisibilityFilter().filter_queryset`, the rule each record's own
  route applies (`fairdm/api/filters.py:102`) and the call `RecordReferenceField.visible_pks`
  makes. `visible_to` (`fairdm/core/managers.py:137`), which the overview pages use, admits on
  dataset permissions the API's filter does not read, so it is not the rule of the record's own
  route. A record the requester may not see is left out of the list, never given as `null`.
- Coordinates: a record carries its site's coordinates only when the requester may see the site,
  as `HeatFlowPage.site_location` does on the pages. Otherwise `location` is `null`.

## Vocabulary terms

Two kinds of value arrive at the serializer:

- A `ConceptField` gives a `research_vocabs.core.Concept`, read from the vocabulary's graph in
  memory: `name`, `label()` (a method) and `URI`. Reading its label costs no query.
- A `ConceptManyToManyField` gives `research_vocabs.models.Concept` rows: `name`, `label`, `uri`
  and `vocabulary`. FairDM's `KeywordSerializer` already gives a record's keywords from these rows
  as `{name, label, uri, vocabulary}`.

**Chosen:** a term is served as `{name, label, uri, vocabulary}`, the shape of FairDM's
`KeywordSerializer`, for both kinds. The class itself is not reused, because the schema has to name
each field's own vocabulary (FR-018) and `KeywordSerializer` describes every keyword alike. One
function gives a term's object from either kind. A single field gets a `ChoiceField` subclass that
still takes the term's name on write and gives the object on read. A many-valued field gets a
read-only `RelatedField` whose `many=True` form iterates the prefetched rows.

The two choice fields on a correction (`correction_type`, `status`) are Django choices, not
vocabulary terms. They are served as `{name, label}`.

## Units

Every quantity field (`fairdm.db.models.QuantityField`, `DecimalQuantityField`,
`PositiveIntegerQuantityField`, all from `quantityfield`) carries `base_units` and its unit
registry. A value read from the database is a `Quantity` in that unit.

**Chosen:** a quantity is served as a plain number in its stored unit, and the record carries a
`units` object naming the unit of each of its quantities, written in pint's compact form
(`f"{unit:~C}"`): `mW/m**2`, `K/km`, `°C`, `m`, `h`, `deg`. A value that is empty is `null`, and its
unit is still stated. A record's own quantities, its probe metadata's and its nested records' each
carry their own `units`.

Rejected: a `{magnitude, unit}` object per value, because an empty value would then carry no unit,
and every consumer would have to unwrap every number.

**Found:** the conductivity's unit is declared as `W/mK`. pint reads that as watts per
**millikelvin**, so the API states it as `W/mK`, which a person reads correctly and a unit library
does not. Every other part of the portal uses the same declaration consistently (import, quality
scoring, demo data), so the stored numbers are right. Correcting the declaration touches the model,
its migrations and the import, and is outside this feature. It is filed as an issue of its own, and
the API's unit text follows the declaration when it is corrected.

## Scores

Served as stored, read-only: on a child `U_score`, `M_score`, `T_score`, `T_score_missing`,
`TC_score`, `TC_score_missing`, `quality` and `quality_scheme`; on a parent `U_score`, `M_score`,
`quality`, `quality_scheme`; on a gradient or conductivity `score`, `score_missing`,
`quality_scheme`. A numeric score not determined is stored `NULL` and served `null`. `Ux` and `Mx`
are the scheme's own grades for "not determined" and are served as stored (SC-005).

## Writes

Every field this feature adds is `read_only`. The generated writable fields are kept, so what is
accepted today is accepted after. Scores, quality codes and `ghfdb_id` are `editable=False` on the
models and never writable. A single vocabulary field keeps taking the term's name.

## Documentation

`docs/guides/published-structure-api.md` documents the FS-006 endpoints. This feature adds
`docs/guides/heat-flow-records-api.md` beside it, listed in the same toctree in `docs/index.md`,
with the shape of each type and an example request and response (FR-019).

## What already exists

| Piece | Stopped at | Found |
|---|---|---|
| Per-type serializer hook | an installed package | the registration's `serializer_class` (FairDM) |
| A list in a different shape from one record | an installed package | DRF `Serializer.many_init` |
| Schema for the list shape | an installed package | drf-spectacular `OpenApiSerializerExtension` |
| Schema for a term's vocabulary and a record's units | an installed package | drf-spectacular `OpenApiSerializerFieldExtension` |
| References with visibility, one query per page | an installed package | FairDM `RecordReferenceField`, `RecordListSerializer.prime` |
| Visibility of related lists and of the site | an installed package | FairDM `FairDMVisibilityFilter.filter_queryset` |
| A page's sites and parents gathered once | new code | `HeatFlowListSerializer`, a `RecordListSerializer` subclass |
| The site a record is placed at | new code | `site_of`, one method over the model relations |
| A reference to an already-narrowed record | new code | `reference()`, built on `RecordReferenceField.route_name` |
| The unit object of a record | new code | `UnitsField`, reading each quantity field's `base_units` |
| A term with label and identifier | new code | one function and two small fields, in the shape of FairDM's `KeywordSerializer`, which cannot name a field's vocabulary in the schema and does not read a `core.Concept` |
| A record's address and page | an installed package | FairDM `RecordURLField`, `PortalPageField` (already on the base serializers) |
| GeoJSON point | an installed package | FairDM `GeoJSONPointField`, subclassed as `SiteLocationField` to read the site instead of the record |
| Quantity as a number in its stored unit | new code | number-field subclasses whose `to_representation` takes the magnitude in `base_units` |
| The unit of a quantity field | an installed package | `quantityfield` field's `base_units` and `ureg`, formatted by pint |
| Query-count assertions | an installed package | pytest-django `django_assert_num_queries`, as `tests/test_ghfdb/test_viewsets.py` uses it |
| Choice with its label | new code | a read-only field giving `{name, label}` from a model choice |
