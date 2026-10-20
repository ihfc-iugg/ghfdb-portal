# Implementation Plan: API representations of heat flow sites and measurements

**Branch**: `010-heat-flow-api` | **Spec**: [spec.md](spec.md) | **Research**: [research.md](research.md)

## Summary

Each of the six registrations (`project/heat_flow/config.py`) names its own serializer with
`serializer_class`. The serializers live in a new module, `project/heat_flow/serializers.py`, two
per type: a **summary** that a list serves, and the **full record** a single record serves, which
builds on the summary and adds the related records. The full serializer's `many_init` hands a list
to the summary, so the generated viewsets, their addresses, paging, ordering, filtering and
visibility stay FairDM's own. A drf-spectacular extension gives a list operation the summary's
schema. Quantities are served as numbers in their stored unit with a `units` object beside them;
vocabulary terms as objects with their label, identifier and vocabulary; scores as stored. This
also ends the 500 that five of the six lists answer today (research.md).

## Technical context

Python 3.13, Django 5, Django REST Framework 3.18, drf-spectacular 0.29, FairDM at `f69c9cb`.
Tests: pytest-django against PostGIS. No new dependency. No migration.

## Constitution check

- Article XI (FAIR) and XII (labelled data): every term carries its label and identifier, every
  quantity its unit. Pass.
- Article XIII (computed quality): scores are read-only and served as stored. Pass.
- ADR 0021 (served only through what is served): every related record passes the requester's
  visibility before it is nested, listed or referred to. Pass.
- ADR 0023 (a site holds the location): coordinates are read from the site, nothing is stored.
  Pass.

## Module layout

```
project/heat_flow/serializers.py      new: fields, base, twelve serializers
project/heat_flow/schema.py           new: drf-spectacular extensions
project/heat_flow/apps.py             import heat_flow.schema in ready()
project/heat_flow/config.py           serializer_class on each of the six registrations
docs/guides/heat-flow-records-api.md  new, listed in docs/index.md beside the published-structure guide
tests/test_heat_flow/test_serializers.py   new, one class per serializer and field
tests/test_heat_flow/test_schema.py        new
```

Tests go through the API routes with `client` (anonymous) and a signed-in client, as
`tests/test_ghfdb/test_viewsets.py` does, so they test the composition the portal serves: the
generated viewset, the registered serializer, FairDM's visibility filter and pagination. Records
come from `tests/factories.py`. Test classes mirror the serializer classes they exercise.

## The fields (`serializers.py`, top of the module)

- **`term(concept)`**: a function giving `{"name", "label", "uri", "vocabulary"}` for either kind
  of concept. A `research_vocabs.core.Concept` gives `name`, `label()`, `str(URI)` and its
  vocabulary's scheme name. A `research_vocabs.models.Concept` row gives `name`, `label`, `uri`,
  `vocabulary.name`. `None` gives `None`.
- **`TermChoiceField(ChoiceField)`**: a single vocabulary field. Writes the term's name exactly as
  the generated `ChoiceField` does today. `to_representation` gives `term(value)`. It is used for
  every `ConceptField` by overriding `build_standard_field` in the base serializer.
- **`TermRelatedField(RelatedField)`**: read-only, `to_representation` gives `term(concept)`. A
  many-valued vocabulary field is `TermRelatedField(many=True, read_only=True)`, so each term is its
  own entry and the prefetched rows are read through `.all()`. It is used for every
  `ConceptManyToManyField` named in `Meta.fields`, through `build_relational_field`.
- **Quantity number fields**: `QuantityFloatField(FloatField)`, `QuantityDecimalField(DecimalField)`
  with `coerce_to_string=False`, `QuantityIntegerField(IntegerField)`. Each writes as its parent does
  today and gives, on read, the magnitude in the model field's `base_units`
  (`value.to(field.base_units).magnitude`), or `None`. They replace the generated number fields
  for every `quantityfield` field through `serializer_field_mapping`.
- **`UnitsField(Field)`**: read-only, `source="*"`. Gives `{name: unit}` for every quantity field
  among the serializer's own fields, the unit written `f"{field.ureg(field.base_units).units:~C}"`.
  Present whatever the values are.
- **`ChoiceLabelField(ChoiceField)`**: read-only, gives `{"name": value, "label": display}` for a
  Django choice (a correction's type and status).
- **`reference(record, request)`**: a function giving `{"uuid", "url"}` for a record, the address
  built with `RecordReferenceField.route_name(record)`. Used for lists of references that have
  already been narrowed to what the requester may see.
- **`SiteLocationField(GeoJSONPointField)`**: gives the GeoJSON point of the record's site, read
  through the serializer's `site_of(record)`, or `None` when the record has no site or the requester
  may not see it.

## The base (`HeatFlowRecordSerializer`)

A mixin placed before the kind's base serializer
(`class HeatFlowSiteSummarySerializer(HeatFlowRecordSerializer, BaseSampleSerializer)`).

- `serializer_field_mapping`, `build_standard_field` and `build_relational_field` as above.
- `units = UnitsField()`.
- `summary_serializer = None`. `many_init` builds the list from `cls.summary_serializer` when it is
  set, and from `cls` otherwise.
- `Meta.list_serializer_class = HeatFlowListSerializer`.
- `site_of(record)`: the site a record is placed at. A site is its own, an interval's is
  `record.site`, a parent's is its sample, a child's, gradient's or conductivity's is its interval's
  site.
- `can_see(record)`: whether the requester may see a sample or measurement, answered from the page
  set the list serializer primed into `self.context` when there is one, and with one query when there
  is not. Built on `Sample.objects.visible_to(user)` and `Measurement.objects.visible_to(user)`, the
  rule `HeatFlowPage.split` uses.

**`HeatFlowListSerializer(RecordListSerializer)`**: before FairDM's own priming, gathers in one
query each the sites the page's records are placed at that the requester may see, and the parents of
a page of sites (with their visibility), and keeps both in the shared serializer context.

**`visible(queryset, request)`**: a function narrowing a queryset of samples or measurements to what
the requester may see, in one query. Used for every nested or listed related record on a single
record.

## The shapes

Every serializer keeps its kind's common fields (`url`, `html_url`, `uuid`, `name`, `dataset`,
`location`, `location_uncertainty`, `added`, `modified`, the five metadata lists, and `local_id`
and `status` for a sample, `sample` for a measurement), every field its registration lists today,
and `units`. A field with no value is present and `null`, a list with nothing in it `[]`.

| Type | Summary adds | Full record adds |
|---|---|---|
| Site | `type`, `elevation`, `elevation_datum`; `parent` as `{uuid, url, value, uncertainty, quality, units}` or `null` | `parent` as the whole parent summary; `intervals`: each interval's summary with `children`, each a child summary |
| Parent | `U_score`, `M_score`, `quality`, `quality_scheme`, `ghfdb_id`; `site` reference; `location` from the site | `children`: `{uuid, url, is_relevant}` for each child |
| Child | `surface_temperature`, `date_acquired`, the eight score fields, `ghfdb_id`, `is_relevant`; references `parent`, `thermal_gradient`, `thermal_conductivity`, `site`; `location` from the site | `thermal_gradient` and `thermal_conductivity` as their whole summaries; `corrections`: `{correction_type, status, comment}` each |
| Interval | `site` reference; `location` from the site | `probe_metadata` as `{penetration, probe_type, length, tilt, units}` or `null`; references `children`, `thermal_gradients`, `thermal_conductivities` |
| Gradient | `temperature_top`, `temperature_bottom` and their uncertainties; `score`, `score_missing`, `quality_scheme`; `site` reference; `location` from the site | references `children` (`heat_flow_children`) |
| Conductivity | `conductivity_location`, `number`; `score`, `score_missing`, `quality_scheme`; `site` reference; `location` from the site | references `children` (`heat_flow_children`) |

Every added field is read-only. A reference to a record the requester may not see is `null`, as
`RecordReferenceField` gives it. A list of related records or references holds only what the
requester may see, and never a `null` in place of one (spec, edge cases). A site's children are
nested under the interval they were made over (FR-001), all of them, never one picked.

## Queries

- Each summary's `load_related` classmethod extends the base's with the `select_related` path to
  the site (`site` for an interval, `sample__heatflowinterval__site` for a measurement made over an
  interval, `sample__heatflowsite` for a parent) and the prefetches its many-valued terms need.
  FairDM's `load_relations` adds the rest.
- A list costs the same number of queries for a page of one record as for a full page: the page
  priming above, FairDM's reference priming, the prefetches.
- A single record's related lists are each one query narrowed by `visible`, with their own terms
  prefetched, so a site with more intervals and children costs the same number of queries.

## Schema (`schema.py`)

- **`HeatFlowRecordSchema(OpenApiSerializerExtension)`**, `target_class` the base,
  `match_subclasses=True`: for a list operation on a serializer whose `summary_serializer` is set,
  `get_name` gives the summary's component name and `map_serializer` maps the summary. Every other
  case maps the serializer itself (`bypass_extensions=True`).
- **`TermFieldSchema(OpenApiSerializerFieldExtension)`** for `TermChoiceField` and
  `TermRelatedField`: an object with `name`, `label`, `uri` and `vocabulary`, the last given
  `enum: [<the field's vocabulary name>]`, nullable for a single field.
- **`UnitsFieldSchema(OpenApiSerializerFieldExtension)`**: an object with one property per quantity
  field, each `enum: [<unit>]`.
- Nested shapes are annotated on their method fields with `extend_schema_field`.
- `HeatFlowSchemaConfig.ready()` (`project/heat_flow/apps.py`) imports `heat_flow.schema`, which
  is how drf-spectacular finds extensions.

## Writes

Unchanged. `Meta.fields` keeps every writable model field the registration lists today, through the
same ModelSerializer mapping, so a request accepted today is accepted after. Scores, quality codes,
scheme revisions and `ghfdb_id` are `editable=False` on the models and read-only here. A test posts
each of them and asserts the stored values are the portal's (US2 scenario 7).

## Documentation

`docs/guides/heat-flow-records-api.md`: how a term, a quantity and its unit, an empty value, a
reference and a hidden record appear, then one section per type with its list and single-record
shape and one example request and response. Each story writes the sections for the names it
introduces.

## Order

US4 first: it builds the fields, the base, a summary for each of the six types and the schema for
terms and units, so every list answers 200 with readable terms and stated units. Then US1 (site and
parent, with the list/single split and its schema), US2 (child), US3 (interval, gradient,
conductivity). Each story edits `serializers.py`, its test module and the guide, so they run one
after another on the branch.

## Risks

- `many_init` is called for any `many=True` use of a full serializer. Nested lists in this feature
  use the summary serializers directly, so nothing else reaches it.
- A list page of sites still prefetches their parents. That is one query per page, and is what
  FR-002 asks a list to carry.
- The conductivity's declared unit, `W/mK`, is stated as declared (research.md). The API follows
  the declaration when it is corrected.
