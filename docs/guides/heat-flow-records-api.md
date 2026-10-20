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

A list of related records, such as a site's intervals or a parent's children, holds only the
records the requester may see. A hidden record is left out of the list. It is never a `null`
entry, so the list's length does not reveal that anything is missing.

## A heat flow site

A site is a named place where heat flow was measured. The list gives each site's position and its parent's
headline numbers, and leaves out its intervals. The record at the site's own address gives the
parent whole, then every depth interval, and under each interval all the child heat flows made
over it.

| Part | In the list | In the single record |
|---|---|---|
| `location` | The site's coordinates | The site's coordinates |
| `parent` | `uuid`, `url`, `value`, `uncertainty`, `quality` and `units`, or `null` | The whole parent record, or `null` |
| `intervals` | Not given | Each interval, with its `children` |

A site with no parent has `"parent": null` in both, and is still listed. A parent the requester may
not see is `null` too. An interval or a child they may not see is left out of `intervals`.

The examples leave out `html_url` and the empty lists of descriptions, dates, identifiers,
keywords and contributors that every record carries.

```
GET /api/v1/samples/heat-flow-sites/
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sQcrZXZsAnhtT5LyW55ALhs/",
      "uuid": "sQcrZXZsAnhtT5LyW55ALhs",
      "name": "Hole A-1",
      "local_id": "SAMPLE-2984",
      "status": {
        "name": "unknown",
        "label": "Unknown",
        "uri": "https://www.fairdm.org/vocabularies/unknown",
        "vocabulary": "fairdm-sample-status"
      },
      "dataset": {
        "uuid": "dGeJTczPv8dUTq6jGeMgE5Z",
        "url": "https://portal.heatflow.world/api/v1/datasets/dGeJTczPv8dUTq6jGeMgE5Z/"
      },
      "location": {
        "type": "Point",
        "coordinates": [
          -179.43217,
          -79.87654
        ]
      },
      "location_uncertainty": null,
      "added": "2026-10-20T20:16:02.306569Z",
      "modified": "2026-10-20T20:16:02.322409Z",
      "type": {
        "name": "unknown",
        "label": "Unknown",
        "uri": "http://vocabulary.odm2.org/sitetype/unknown",
        "vocabulary": "sitetype"
      },
      "elevation": 412.0,
      "elevation_datum": {
        "name": "MSL",
        "label": "MSL",
        "uri": "http://vocabulary.odm2.org/elevationdatum/MSL",
        "vocabulary": "elevationdatum"
      },
      "country": null,
      "region": null,
      "continent": null,
      "domain": null,
      "azimuth": null,
      "inclination": null,
      "length": null,
      "environment": {
        "name": "onshore_continental",
        "label": "Onshore (continental)",
        "uri": "https://heatflow.world/vocabularies/geographic-environments/onshore_continental",
        "vocabulary": "geographic-environments"
      },
      "explo_method": {
        "name": "drilling_clustering",
        "label": "Drilling-Clustering",
        "uri": "https://heatflow.world/vocabularies/exploration-methods/drilling_clustering",
        "vocabulary": "exploration-methods"
      },
      "explo_purpose": [],
      "lithology": [],
      "age": [],
      "stratigraphy": [],
      "parent": {
        "url": "https://portal.heatflow.world/api/v1/measurements/parent-heat-flow/mgLFmNMQmYsjQ26EsMTkScb/",
        "uuid": "mgLFmNMQmYsjQ26EsMTkScb",
        "value": 64.5,
        "uncertainty": 6.1,
        "quality": "U2.Mx.-------",
        "units": {
          "value": "mW/m²",
          "uncertainty": "mW/m²"
        }
      },
      "units": {
        "azimuth": "deg",
        "inclination": "deg",
        "length": "m",
        "elevation": "m"
      }
    }
  ]
}
```

```
GET /api/v1/samples/heat-flow-sites/sQcrZXZsAnhtT5LyW55ALhs/
```

```json
{
  "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sQcrZXZsAnhtT5LyW55ALhs/",
  "uuid": "sQcrZXZsAnhtT5LyW55ALhs",
  "name": "Hole A-1",
  "local_id": "SAMPLE-2984",
  "status": {
    "name": "unknown",
    "label": "Unknown",
    "uri": "https://www.fairdm.org/vocabularies/unknown",
    "vocabulary": "fairdm-sample-status"
  },
  "dataset": {
    "uuid": "dGeJTczPv8dUTq6jGeMgE5Z",
    "url": "https://portal.heatflow.world/api/v1/datasets/dGeJTczPv8dUTq6jGeMgE5Z/"
  },
  "location": {
    "type": "Point",
    "coordinates": [
      -179.43217,
      -79.87654
    ]
  },
  "location_uncertainty": null,
  "added": "2026-10-20T20:16:02.306569Z",
  "modified": "2026-10-20T20:16:02.322409Z",
  "type": {
    "name": "unknown",
    "label": "Unknown",
    "uri": "http://vocabulary.odm2.org/sitetype/unknown",
    "vocabulary": "sitetype"
  },
  "elevation": 412.0,
  "elevation_datum": {
    "name": "MSL",
    "label": "MSL",
    "uri": "http://vocabulary.odm2.org/elevationdatum/MSL",
    "vocabulary": "elevationdatum"
  },
  "country": null,
  "region": null,
  "continent": null,
  "domain": null,
  "azimuth": null,
  "inclination": null,
  "length": null,
  "environment": {
    "name": "onshore_continental",
    "label": "Onshore (continental)",
    "uri": "https://heatflow.world/vocabularies/geographic-environments/onshore_continental",
    "vocabulary": "geographic-environments"
  },
  "explo_method": {
    "name": "drilling_clustering",
    "label": "Drilling-Clustering",
    "uri": "https://heatflow.world/vocabularies/exploration-methods/drilling_clustering",
    "vocabulary": "exploration-methods"
  },
  "explo_purpose": [],
  "lithology": [],
  "age": [],
  "stratigraphy": [],
  "parent": {
    "url": "https://portal.heatflow.world/api/v1/measurements/parent-heat-flow/mgLFmNMQmYsjQ26EsMTkScb/",
    "uuid": "mgLFmNMQmYsjQ26EsMTkScb",
    "name": "Hole A-1 parent",
    "sample": {
      "uuid": "sQcrZXZsAnhtT5LyW55ALhs",
      "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sQcrZXZsAnhtT5LyW55ALhs/"
    },
    "dataset": {
      "uuid": "dGeJTczPv8dUTq6jGeMgE5Z",
      "url": "https://portal.heatflow.world/api/v1/datasets/dGeJTczPv8dUTq6jGeMgE5Z/"
    },
    "location": null,
    "location_uncertainty": null,
    "added": "2026-10-20T20:16:02.334121Z",
    "modified": "2026-10-20T20:16:02.344461Z",
    "value": 64.5,
    "uncertainty": 6.1,
    "corr_HP_flag": null,
    "comment": null,
    "U_score": "U2",
    "M_score": "Mx",
    "quality": "U2.Mx.-------",
    "quality_scheme": "hfqa_tool 0.2",
    "ghfdb_id": null,
    "site": {
      "uuid": "sQcrZXZsAnhtT5LyW55ALhs",
      "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sQcrZXZsAnhtT5LyW55ALhs/"
    },
    "units": {
      "value": "mW/m²",
      "uncertainty": "mW/m²"
    }
  },
  "units": {
    "azimuth": "deg",
    "inclination": "deg",
    "length": "m",
    "elevation": "m"
  },
  "intervals": [
    {
      "url": "https://portal.heatflow.world/api/v1/samples/depth-intervals/stemVCKGnvWzPRqqxXGuDRk/",
      "uuid": "stemVCKGnvWzPRqqxXGuDRk",
      "name": "Hole A-1 100-200 m",
      "local_id": "SAMPLE-1680",
      "status": {
        "name": "unknown",
        "label": "Unknown",
        "uri": "https://www.fairdm.org/vocabularies/unknown",
        "vocabulary": "fairdm-sample-status"
      },
      "dataset": {
        "uuid": "dGeJTczPv8dUTq6jGeMgE5Z",
        "url": "https://portal.heatflow.world/api/v1/datasets/dGeJTczPv8dUTq6jGeMgE5Z/"
      },
      "location": null,
      "location_uncertainty": null,
      "added": "2026-10-20T20:16:02.350163Z",
      "modified": "2026-10-20T20:16:02.363405Z",
      "top": 100.0,
      "bottom": 200.0,
      "vertical_depth": 100.0,
      "vertical_datum": "MSL",
      "lithology": [],
      "age": [],
      "stratigraphy": [],
      "units": {
        "top": "m",
        "bottom": "m",
        "vertical_depth": "m"
      },
      "children": [
        {
          "url": "https://portal.heatflow.world/api/v1/measurements/heat-flow/mevMsNs3mw3w6kFCmXQvMc4/",
          "uuid": "mevMsNs3mw3w6kFCmXQvMc4",
          "name": "Hole A-1 100-200 m heat flow",
          "sample": {
            "uuid": "stemVCKGnvWzPRqqxXGuDRk",
            "url": "https://portal.heatflow.world/api/v1/samples/depth-intervals/stemVCKGnvWzPRqqxXGuDRk/"
          },
          "dataset": {
            "uuid": "dGeJTczPv8dUTq6jGeMgE5Z",
            "url": "https://portal.heatflow.world/api/v1/datasets/dGeJTczPv8dUTq6jGeMgE5Z/"
          },
          "location": null,
          "location_uncertainty": null,
          "added": "2026-10-20T20:16:02.372638Z",
          "modified": "2026-10-20T20:16:02.401317Z",
          "value": 66.2,
          "uncertainty": 5.0,
          "method": [],
          "expedition": null,
          "c_comment": null,
          "units": {
            "value": "mW/m²",
            "uncertainty": "mW/m²"
          }
        }
      ]
    }
  ]
}
```

## A parent heat flow

A parent is the quality-controlled heat flow for one site. The list gives its value, uncertainty,
the two scores that make up its `quality` code, the scheme revision that calculated them, its
`ghfdb_id` and a reference to its `site`. The record at its own address adds `children`: a
reference to each child heat flow made towards it, with `is_relevant` saying whether that child
counted in the parent's value. A child that did not count is listed too. A child the requester may
not see is left out.

```
GET /api/v1/measurements/parent-heat-flow/
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "url": "https://portal.heatflow.world/api/v1/measurements/parent-heat-flow/mgLFmNMQmYsjQ26EsMTkScb/",
      "uuid": "mgLFmNMQmYsjQ26EsMTkScb",
      "name": "Hole A-1 parent",
      "sample": {
        "uuid": "sQcrZXZsAnhtT5LyW55ALhs",
        "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sQcrZXZsAnhtT5LyW55ALhs/"
      },
      "dataset": {
        "uuid": "dGeJTczPv8dUTq6jGeMgE5Z",
        "url": "https://portal.heatflow.world/api/v1/datasets/dGeJTczPv8dUTq6jGeMgE5Z/"
      },
      "location": null,
      "location_uncertainty": null,
      "added": "2026-10-20T20:16:02.334121Z",
      "modified": "2026-10-20T20:16:02.344461Z",
      "value": 64.5,
      "uncertainty": 6.1,
      "corr_HP_flag": null,
      "comment": null,
      "U_score": "U2",
      "M_score": "Mx",
      "quality": "U2.Mx.-------",
      "quality_scheme": "hfqa_tool 0.2",
      "ghfdb_id": null,
      "site": {
        "uuid": "sQcrZXZsAnhtT5LyW55ALhs",
        "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sQcrZXZsAnhtT5LyW55ALhs/"
      },
      "units": {
        "value": "mW/m²",
        "uncertainty": "mW/m²"
      }
    }
  ]
}
```

```
GET /api/v1/measurements/parent-heat-flow/mgLFmNMQmYsjQ26EsMTkScb/
```

```json
{
  "url": "https://portal.heatflow.world/api/v1/measurements/parent-heat-flow/mgLFmNMQmYsjQ26EsMTkScb/",
  "uuid": "mgLFmNMQmYsjQ26EsMTkScb",
  "name": "Hole A-1 parent",
  "sample": {
    "uuid": "sQcrZXZsAnhtT5LyW55ALhs",
    "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sQcrZXZsAnhtT5LyW55ALhs/"
  },
  "dataset": {
    "uuid": "dGeJTczPv8dUTq6jGeMgE5Z",
    "url": "https://portal.heatflow.world/api/v1/datasets/dGeJTczPv8dUTq6jGeMgE5Z/"
  },
  "location": null,
  "location_uncertainty": null,
  "added": "2026-10-20T20:16:02.334121Z",
  "modified": "2026-10-20T20:16:02.344461Z",
  "value": 64.5,
  "uncertainty": 6.1,
  "corr_HP_flag": null,
  "comment": null,
  "U_score": "U2",
  "M_score": "Mx",
  "quality": "U2.Mx.-------",
  "quality_scheme": "hfqa_tool 0.2",
  "ghfdb_id": null,
  "site": {
    "uuid": "sQcrZXZsAnhtT5LyW55ALhs",
    "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sQcrZXZsAnhtT5LyW55ALhs/"
  },
  "units": {
    "value": "mW/m²",
    "uncertainty": "mW/m²"
  },
  "children": [
    {
      "uuid": "mevMsNs3mw3w6kFCmXQvMc4",
      "url": "https://portal.heatflow.world/api/v1/measurements/heat-flow/mevMsNs3mw3w6kFCmXQvMc4/",
      "is_relevant": true
    }
  ]
}
```

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
| `HeatFlowSiteSerializer` | Heat flow site |
| `HeatFlowIntervalSummarySerializer` | Depth interval |
| `HeatFlowSummarySerializer` | Child heat flow |
| `ThermalGradientSummarySerializer` | Thermal gradient |
| `IntervalConductivitySummarySerializer` | Interval conductivity |
| `ParentHeatFlowSerializer` | Parent heat flow |

A site and a parent each have a longer single record than their list gives. Their serializer
names the shorter shape as `summary_serializer` (`HeatFlowSiteSummarySerializer` and
`ParentHeatFlowSummarySerializer`), and a list of it is a `HeatFlowListSerializer` of that summary. The other four give the same record in both. A list of sites also reads the
parents of the whole page at once, and `RequesterVisibility.can_see` says whether the requester may
see one of them, by the same rule as the parent's own address. The site's single record builds its
intervals from `SiteIntervalSerializer`: the interval summary plus a `children` field, whose
entries are child summaries (`ChildSummaries` documents that field in the schema). The parent's
list entry on a site is `SiteParentSerializer`. `reference()` writes the `uuid` and `url` of a
record the requester has already been allowed to see, as the parent's `children` do.

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

`HeatFlowRecordSchema`, in the same module, makes the generated schema give a list operation the
summary's component, so the site list's items have a `parent` and no `intervals`, and every other
operation the serializer's own.
