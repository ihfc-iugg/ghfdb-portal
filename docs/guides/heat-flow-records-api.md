# The heat flow records through the API

Each type of heat flow record has its own list and its own record address under `/api/v1/`. Anyone
can read them without signing in. A record is public when the dataset it belongs to is public and
published, and signing in adds the records the person is listed on.

| Record | Address |
|---|---|
| Heat flow site | `/api/v1/samples/heat-flow-sites/` |
| Depth interval | `/api/v1/samples/depth-intervals/` |
| Child heat flow | `/api/v1/measurements/heat-flow/` |
| Thermal gradient | `/api/v1/measurements/thermal-gradients/` |
| Interval conductivity | `/api/v1/measurements/thermal-conductivities/` |
| Parent heat flow | `/api/v1/measurements/parent-heat-flow/` |

A single record is at the list address followed by its identifier, for example
`/api/v1/measurements/heat-flow/<uuid>/`. Lists are paged the way [the published structure
endpoints](published-structure-api.md) are: the records are under `results`, beside `count`,
`next` and `previous`.

## Terms

A value chosen from a vocabulary is an object with the term's name, its label, its identifier and
the vocabulary it belongs to:

```json
"environment": {
  "name": "onshore_continental",
  "label": "Onshore (continental)",
  "uri": "https://heatflow.world/vocabularies/geographic-environments/onshore_continental",
  "vocabulary": "geographic-environments"
}
```

A field that can hold several terms is a list with one such object for each term. When a record
is created or changed, a single-term field still takes the term's `name` as a plain string.

## Quantities and units

A quantity is a plain JSON number. It is always given in the unit the field is stored in, whatever
unit it was entered in, and that unit is named in the record's `units` object. Every quantity field
in the record has an entry there, including those with no value:

```json
"value": 70.5,
"uncertainty": null,
"units": {
  "value": "mW/m²",
  "uncertainty": "mW/m²"
}
```

Here are the units each type uses:

| Record | Quantities and their units |
|---|---|
| Heat flow site | `azimuth` and `inclination` in `deg`, `length` in `m` |
| Depth interval | `top`, `bottom` and `vertical_depth` in `m` |
| Child heat flow | `value` and `uncertainty` in `mW/m²` |
| Thermal gradient | `value`, `uncertainty`, `corrected_value` and `corrected_uncertainty` in `K/km`, `shutin_top` and `shutin_bottom` in `h` |
| Interval conductivity | `value` and `uncertainty` in `W/mK` |
| Parent heat flow | `value` and `uncertainty` in `mW/m²` |

## Empty values

A field with no value is still in the record. A single value, a quantity or a term is `null`, and a
field that holds several values is an empty list, `[]`.

## References

A reference to another record, such as the dataset a record belongs to or the interval a
measurement was made over, is an object with that record's `uuid` and the `url` of its address:

```json
"dataset": {
  "uuid": "d2aeBjVfSGfEbYXgTSCiYrF",
  "url": "https://portal.heatflow.world/api/v1/datasets/d2aeBjVfSGfEbYXgTSCiYrF/"
}
```

## Hidden records

A reference to a record the requester may not see is `null`, so a reader can tell that a value is
there without learning anything about it. A record is hidden when its dataset is private or not yet
published, unless the person asking is listed on it.

## A child heat flow

```
GET /api/v1/measurements/heat-flow/
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "url": "https://portal.heatflow.world/api/v1/measurements/heat-flow/mDthW8u8wnCEooYj9TWieLi/",
      "html_url": "https://portal.heatflow.world/measurement/mDthW8u8wnCEooYj9TWieLi/",
      "uuid": "mDthW8u8wnCEooYj9TWieLi",
      "name": "Interval 1",
      "sample": {
        "uuid": "s4NLZQRe9mECKWY5GC3Xiun",
        "url": "https://portal.heatflow.world/api/v1/samples/depth-intervals/s4NLZQRe9mECKWY5GC3Xiun/"
      },
      "dataset": {
        "uuid": "da7HMUn55WPRbMfxKumMJBG",
        "url": "https://portal.heatflow.world/api/v1/datasets/da7HMUn55WPRbMfxKumMJBG/"
      },
      "location": null,
      "location_uncertainty": null,
      "added": "2026-10-20T19:45:35.609999Z",
      "modified": "2026-10-20T19:45:35.663494Z",
      "value": 70.5,
      "uncertainty": 5.5,
      "method": [
        {
          "name": "unspecified",
          "label": "Unspecified",
          "uri": "https://heatflow.world/vocabularies/heat-flow-method/unspecified",
          "vocabulary": "heat-flow-method"
        }
      ],
      "expedition": null,
      "c_comment": null,
      "descriptions": [],
      "dates": [],
      "identifiers": [],
      "keywords": [],
      "contributors": [],
      "units": {
        "value": "mW/m²",
        "uncertainty": "mW/m²"
      }
    }
  ]
}
```

## For developers: how the serializers are built

The serializers are in `project/heat_flow/serializers.py`, and each type's registration in
`project/heat_flow/config.py` names its own with `serializer_class`.

| Serializer | Record |
|---|---|
| `HeatFlowSiteSummarySerializer` | Heat flow site |
| `HeatFlowIntervalSummarySerializer` | Depth interval |
| `HeatFlowSummarySerializer` | Child heat flow |
| `ThermalGradientSummarySerializer` | Thermal gradient |
| `IntervalConductivitySummarySerializer` | Interval conductivity |
| `ParentHeatFlowSummarySerializer` | Parent heat flow |

All six build on `HeatFlowRecordSerializer`, which chooses the field for each model field:

- A single vocabulary field becomes a `TermChoiceField`. It reads as a term object and writes the
  term's name.
- A many-valued vocabulary field becomes a read-only `TermRelatedField`, one term object for each
  entry. `term()` builds the object for either kind of stored concept.
- A quantity field becomes a `QuantityFloatField`, `QuantityDecimalField` or
  `QuantityIntegerField`, all built on `QuantityNumber`. They give the number in the unit the
  model field is stored in.
- `UnitsField` collects those units into the record's `units` object.
- Any other many-valued relation, such as a site's `stratigraphy`, stays read-only text.

`TermFieldSchema`, `TermRelatedFieldSchema` and `UnitsFieldSchema`, in `project/heat_flow/schema.py`,
describe the term and `units` objects in the generated OpenAPI schema, with each term's
`vocabulary` limited to that field's vocabulary.
