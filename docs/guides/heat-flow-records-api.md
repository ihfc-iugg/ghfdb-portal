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
| Depth interval | `top`, `bottom` and `vertical_depth` in `m`. Its `probe_metadata` has its own `units`: `penetration` and `length` in `m`, `tilt` in `deg` |
| Child heat flow | `value` and `uncertainty` in `mW/m²`, `surface_temperature` in `°C` |
| Thermal gradient | `value`, `uncertainty`, `corrected_value` and `corrected_uncertainty` in `K/km`, `shutin_top` and `shutin_bottom` in `h`, `temperature_top`, `temperature_bottom` and their uncertainties in `°C` |
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

The site below is cut to its first interval and that interval's first child.

```
GET /api/v1/samples/heat-flow-sites/sJkWMuWMhnS9i846rJtWrHN/
```

```json
{
  "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sJkWMuWMhnS9i846rJtWrHN/",
  "uuid": "sJkWMuWMhnS9i846rJtWrHN",
  "name": "Black Forest borehole",
  "local_id": "1",
  "status": {
    "name": "unknown",
    "label": "Unknown",
    "uri": "https://www.fairdm.org/vocabularies/unknown",
    "vocabulary": "fairdm-sample-status"
  },
  "dataset": {
    "uuid": "dkdeMQST7ux5RYv63mi775C",
    "url": "https://portal.heatflow.world/api/v1/datasets/dkdeMQST7ux5RYv63mi775C/"
  },
  "location": {
    "type": "Point",
    "coordinates": [
      8.21345,
      47.99012
    ]
  },
  "location_uncertainty": null,
  "added": "2026-10-16T09:14:27.609614Z",
  "modified": "2026-10-16T09:14:27.609624Z",
  "type": {
    "name": "unknown",
    "label": "Unknown",
    "uri": "http://vocabulary.odm2.org/sitetype/unknown",
    "vocabulary": "sitetype"
  },
  "elevation": 500.0,
  "elevation_datum": {
    "name": "MSL",
    "label": "MSL",
    "uri": "http://vocabulary.odm2.org/elevationdatum/MSL",
    "vocabulary": "elevationdatum"
  },
  "country": "Germany",
  "region": null,
  "continent": "Europe",
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
  "explo_method": null,
  "explo_purpose": [],
  "lithology": [],
  "age": [],
  "stratigraphy": [],
  "parent": {
    "url": "https://portal.heatflow.world/api/v1/measurements/parent-heat-flow/mNnoHFFHGMS2Cpo52hvDRKt/",
    "uuid": "mNnoHFFHGMS2Cpo52hvDRKt",
    "name": "1",
    "sample": {
      "uuid": "sJkWMuWMhnS9i846rJtWrHN",
      "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sJkWMuWMhnS9i846rJtWrHN/"
    },
    "dataset": {
      "uuid": "dkdeMQST7ux5RYv63mi775C",
      "url": "https://portal.heatflow.world/api/v1/datasets/dkdeMQST7ux5RYv63mi775C/"
    },
    "location": {
      "type": "Point",
      "coordinates": [
        8.21345,
        47.99012
      ]
    },
    "location_uncertainty": null,
    "added": "2026-10-16T09:14:27.626252Z",
    "modified": "2026-10-16T09:14:27.626259Z",
    "value": 70.0,
    "uncertainty": 5.0,
    "corr_HP_flag": false,
    "comment": "",
    "U_score": "U2",
    "M_score": "Mx",
    "quality": "U2.Mx.-------",
    "quality_scheme": "hfqa_tool 0.2",
    "ghfdb_id": 1,
    "site": {
      "uuid": "sJkWMuWMhnS9i846rJtWrHN",
      "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sJkWMuWMhnS9i846rJtWrHN/"
    },
    "units": {
      "value": "mW/m²",
      "uncertainty": "mW/m²"
    }
  },
  "units": {
    "elevation": "m",
    "azimuth": "deg",
    "inclination": "deg",
    "length": "m"
  },
  "intervals": [
    {
      "url": "https://portal.heatflow.world/api/v1/samples/depth-intervals/sKhtqx2D3MpBQP6a9FJTTfH/",
      "uuid": "sKhtqx2D3MpBQP6a9FJTTfH",
      "name": "",
      "local_id": null,
      "status": {
        "name": "unknown",
        "label": "Unknown",
        "uri": "https://www.fairdm.org/vocabularies/unknown",
        "vocabulary": "fairdm-sample-status"
      },
      "dataset": {
        "uuid": "dkdeMQST7ux5RYv63mi775C",
        "url": "https://portal.heatflow.world/api/v1/datasets/dkdeMQST7ux5RYv63mi775C/"
      },
      "location": {
        "type": "Point",
        "coordinates": [
          8.21345,
          47.99012
        ]
      },
      "location_uncertainty": null,
      "added": "2026-10-16T09:14:27.783820Z",
      "modified": "2026-10-16T09:14:27.783831Z",
      "top": 0.0,
      "bottom": 500.0,
      "vertical_depth": 500.0,
      "vertical_datum": "MSL",
      "lithology": [],
      "age": [],
      "stratigraphy": [],
      "site": {
        "uuid": "sJkWMuWMhnS9i846rJtWrHN",
        "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sJkWMuWMhnS9i846rJtWrHN/"
      },
      "units": {
        "top": "m",
        "bottom": "m",
        "vertical_depth": "m"
      },
      "children": [
        {
          "url": "https://portal.heatflow.world/api/v1/measurements/heat-flow/mk83wFcgUTynziyfjvgLp24/",
          "uuid": "mk83wFcgUTynziyfjvgLp24",
          "name": "1",
          "sample": {
            "uuid": "sKhtqx2D3MpBQP6a9FJTTfH",
            "url": "https://portal.heatflow.world/api/v1/samples/depth-intervals/sKhtqx2D3MpBQP6a9FJTTfH/"
          },
          "dataset": {
            "uuid": "dkdeMQST7ux5RYv63mi775C",
            "url": "https://portal.heatflow.world/api/v1/datasets/dkdeMQST7ux5RYv63mi775C/"
          },
          "location": {
            "type": "Point",
            "coordinates": [
              8.21345,
              47.99012
            ]
          },
          "location_uncertainty": null,
          "added": "2026-10-16T09:14:27.798722Z",
          "modified": "2026-10-16T09:14:27.798729Z",
          "value": 70.0,
          "uncertainty": 5.0,
          "surface_temperature": null,
          "date_acquired": null,
          "method": [],
          "expedition": "",
          "c_comment": "",
          "U_score": "U2",
          "M_score": "Mx",
          "T_score": null,
          "T_score_missing": false,
          "TC_score": null,
          "TC_score_missing": false,
          "quality": "U2.Mx.-------",
          "quality_scheme": "hfqa_tool 0.2",
          "ghfdb_id": 1,
          "is_relevant": true,
          "parent": {
            "uuid": "mNnoHFFHGMS2Cpo52hvDRKt",
            "url": "https://portal.heatflow.world/api/v1/measurements/parent-heat-flow/mNnoHFFHGMS2Cpo52hvDRKt/"
          },
          "thermal_gradient": null,
          "thermal_conductivity": {
            "uuid": "m5MQyqUMgxtJFMPGHh4p6r5",
            "url": "https://portal.heatflow.world/api/v1/measurements/thermal-conductivities/m5MQyqUMgxtJFMPGHh4p6r5/"
          },
          "site": {
            "uuid": "sJkWMuWMhnS9i846rJtWrHN",
            "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sJkWMuWMhnS9i846rJtWrHN/"
          },
          "units": {
            "value": "mW/m²",
            "uncertainty": "mW/m²",
            "surface_temperature": "°C"
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
`ghfdb_id`, a reference to its `site` and the site's coordinates as `location`. When the requester
may not see the site, `location` and `site` are `null`. The record at its own address adds `children`: a
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
      "location": {
        "type": "Point",
        "coordinates": [-179.43217, -79.87654]
      },
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
  "location": {
    "type": "Point",
    "coordinates": [-179.43217, -79.87654]
  },
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

A child is one heat flow value, made over one depth interval. Its list entry gives the value and
its uncertainty, the surface temperature and the date the data was acquired, and the scores the
portal calculated for it: `U_score`, `M_score`, the corrected `T_score` and `TC_score` with
`T_score_missing` and `TC_score_missing` saying whether an input was empty, the `quality` code and
the `quality_scheme` revision that calculated them. A score that could not be determined is `null`.
`ghfdb_id` is the identifier the record had in the original database, and `is_relevant` says
whether the child counted towards its parent. The scores, the quality code, the scheme revision
and `ghfdb_id` are read-only: a request that creates or changes a child cannot set them.

The entry refers to the child's interval as `sample`, and to its `parent`, `thermal_gradient`,
`thermal_conductivity` and `site`. It carries the coordinates of its site as `location`. When the
requester may not see the site, `location` and `site` are `null`. The record at the child's own
address gives the thermal gradient and the interval conductivity whole, in the shape of their own
records, in place of the references. It adds `corrections`, one entry for each correction recorded
against the child, whatever its status, with the type and the status each given as a `name` and a
`label`. A correction recorded with no status is in the list with `status` set to `null`, which
tells it from a correction type that was never recorded and is not in the list. A gradient or conductivity
the requester may not see is `null`.

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
      "url": "https://portal.heatflow.world/api/v1/measurements/heat-flow/mymJ5inhK9m89DkwZTvjEFS/",
      "html_url": "https://portal.heatflow.world/measurement/mymJ5inhK9m89DkwZTvjEFS/",
      "uuid": "mymJ5inhK9m89DkwZTvjEFS",
      "name": "Hole A-1, 200 m",
      "sample": {
        "uuid": "su4JiacdQpHDUD4wx32xbqL",
        "url": "https://portal.heatflow.world/api/v1/samples/depth-intervals/su4JiacdQpHDUD4wx32xbqL/"
      },
      "dataset": {
        "uuid": "db5GZfnvXHi2QFHN7NNE4P6",
        "url": "https://portal.heatflow.world/api/v1/datasets/db5GZfnvXHi2QFHN7NNE4P6/"
      },
      "location": {
        "type": "Point",
        "coordinates": [-179.43217, -79.87654]
      },
      "location_uncertainty": null,
      "added": "2026-10-20T20:58:10.366190Z",
      "modified": "2026-10-20T20:58:10.406596Z",
      "value": 70.5,
      "uncertainty": 5.5,
      "surface_temperature": 4.5,
      "date_acquired": "2019-06-12",
      "method": [
        {
          "name": "numerical",
          "label": "Other numerical computations",
          "uri": "https://heatflow.world/vocabularies/heat-flow-method/numerical",
          "vocabulary": "heat-flow-method"
        }
      ],
      "expedition": null,
      "c_comment": null,
      "U_score": "U2",
      "M_score": "M4",
      "T_score": 0.5,
      "T_score_missing": false,
      "TC_score": 0.4,
      "TC_score_missing": false,
      "quality": "U2.M4.-------",
      "quality_scheme": "hfqa_tool 0.2",
      "ghfdb_id": 1021,
      "is_relevant": true,
      "parent": {
        "uuid": "miTrRWyF2DEjPqyxJUYi2eC",
        "url": "https://portal.heatflow.world/api/v1/measurements/parent-heat-flow/miTrRWyF2DEjPqyxJUYi2eC/"
      },
      "thermal_gradient": {
        "uuid": "m9Lri4vWTof9DqfDCWjzv5V",
        "url": "https://portal.heatflow.world/api/v1/measurements/thermal-gradients/m9Lri4vWTof9DqfDCWjzv5V/"
      },
      "thermal_conductivity": {
        "uuid": "mogAH2nxj9YzJyjNbxYN955",
        "url": "https://portal.heatflow.world/api/v1/measurements/thermal-conductivities/mogAH2nxj9YzJyjNbxYN955/"
      },
      "site": {
        "uuid": "sEoijNefzuf7ySbQ9wR4qxb",
        "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sEoijNefzuf7ySbQ9wR4qxb/"
      },
      "descriptions": [],
      "dates": [],
      "identifiers": [],
      "keywords": [],
      "contributors": [],
      "units": {
        "value": "mW/m²",
        "uncertainty": "mW/m²",
        "surface_temperature": "°C"
      }
    }
  ]
}
```

At the child's own address, `thermal_gradient` and `thermal_conductivity` are the whole records
and `corrections` is added. The record's other fields are as in the list. Here the gradient is
shortened to a few of its fields:

```
GET /api/v1/measurements/heat-flow/mymJ5inhK9m89DkwZTvjEFS/
```

```json
{
  "uuid": "mymJ5inhK9m89DkwZTvjEFS",
  "thermal_gradient": {
    "uuid": "m9Lri4vWTof9DqfDCWjzv5V",
    "value": 25.5,
    "uncertainty": 1.25,
    "units": {
      "value": "K/km",
      "uncertainty": "K/km"
    }
  },
  "thermal_conductivity": null,
  "corrections": [
    {
      "correction_type": {
        "name": "IS",
        "label": "In-situ conditions"
      },
      "status": {
        "name": "present_corrected",
        "label": "Present and corrected"
      },
      "comment": "Corrected to in-situ pressure and temperature."
    },
    {
      "correction_type": {
        "name": "T",
        "label": "Temperature"
      },
      "status": {
        "name": "not_corrected",
        "label": "not corrected"
      },
      "comment": null
    }
  ]
}
```

## A depth interval

An interval is a stretch of a site's hole or profile, between a `top` and a `bottom` depth. Its
list entry gives the depths, the vertical depth and its datum, the lithology, age and stratigraphy,
and a reference to its `site`. It carries the coordinates of the site as `location`, because an
interval has no position of its own. When the requester may not see the site, `location` and `site`
are `null`.

The record at the interval's own address adds `probe_metadata`, which describes the marine heat flow
probe used and has its own `units`, and three lists of references: the `children` made over the
interval, its `thermal_gradients` and its `thermal_conductivities`. An interval with no probe
metadata has `probe_metadata: null`. A record the requester may not see is left out of its list.

```
GET /api/v1/samples/depth-intervals/
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "url": "https://portal.heatflow.world/api/v1/samples/depth-intervals/sAvai23dHxcyhKwmMz4sMZU/",
      "html_url": "https://portal.heatflow.world/samples/sAvai23dHxcyhKwmMz4sMZU/overview/",
      "uuid": "sAvai23dHxcyhKwmMz4sMZU",
      "name": "Hole A-1, 10 to 200 m",
      "local_id": "SAMPLE-0466",
      "status": {
        "name": "unknown",
        "label": "Unknown",
        "uri": "https://www.fairdm.org/vocabularies/unknown",
        "vocabulary": "fairdm-sample-status"
      },
      "dataset": {
        "uuid": "dSJt4XcaoCXHb8BfKdnVCAE",
        "url": "https://portal.heatflow.world/api/v1/datasets/dSJt4XcaoCXHb8BfKdnVCAE/"
      },
      "location": {
        "type": "Point",
        "coordinates": [-179.43217, -79.87654]
      },
      "location_uncertainty": null,
      "added": "2026-10-20T21:31:57.169995Z",
      "modified": "2026-10-20T21:31:57.183888Z",
      "top": 10.5,
      "bottom": 200.5,
      "vertical_depth": 190.0,
      "vertical_datum": "MSL",
      "lithology": [],
      "age": [],
      "stratigraphy": [],
      "site": {
        "uuid": "sufCcNuwVkhMwA8RJWumEft",
        "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sufCcNuwVkhMwA8RJWumEft/"
      },
      "descriptions": [],
      "dates": [],
      "identifiers": [],
      "keywords": [],
      "contributors": [],
      "units": {
        "top": "m",
        "bottom": "m",
        "vertical_depth": "m"
      }
    }
  ]
}
```

At the interval's own address the fields above are the same, and `probe_metadata` and the three
lists are added. Here the record is shortened to those fields:

```
GET /api/v1/samples/depth-intervals/sAvai23dHxcyhKwmMz4sMZU/
```

```json
{
  "uuid": "sAvai23dHxcyhKwmMz4sMZU",
  "probe_metadata": {
    "penetration": 3.5,
    "probe_type": [
      {
        "name": "outrigger_hybrid_lister_hylo",
        "label": "Outrigger probe (Hybrid Lister) HyLO",
        "uri": "https://heatflow.world/vocabularies/heat-flow-probes/outrigger_hybrid_lister_hylo",
        "vocabulary": "heat-flow-probes"
      }
    ],
    "length": 4.5,
    "tilt": 1.5,
    "units": {
      "penetration": "m",
      "length": "m",
      "tilt": "deg"
    }
  },
  "children": [
    {
      "uuid": "mPRRfWDjwicXHp6tuDZMUwR",
      "url": "https://portal.heatflow.world/api/v1/measurements/heat-flow/mPRRfWDjwicXHp6tuDZMUwR/"
    }
  ],
  "thermal_gradients": [
    {
      "uuid": "mprrvSq56QCmNiMAiVdmaKC",
      "url": "https://portal.heatflow.world/api/v1/measurements/thermal-gradients/mprrvSq56QCmNiMAiVdmaKC/"
    }
  ],
  "thermal_conductivities": [
    {
      "uuid": "mn67tXfcqEAVVzMqFoiSicR",
      "url": "https://portal.heatflow.world/api/v1/measurements/thermal-conductivities/mn67tXfcqEAVVzMqFoiSicR/"
    }
  ]
}
```

## A thermal gradient

A thermal gradient is the temperature gradient measured over one depth interval. Its list entry
gives the `value` and `uncertainty`, the `corrected_value` and `corrected_uncertainty`, the methods,
shut-in times and corrections for the top and the bottom of the interval, the number of
temperature readings it rests on (`number`), and the temperature at the `temperature_top` and
`temperature_bottom` of the interval with an uncertainty for each.

The portal calculates the gradient's own `score`, with `score_missing` saying whether an input was
empty and `quality_scheme` naming the scheme revision that calculated it. A score that could not be
determined is `null`. The score and the scheme revision are read-only: a request that creates or
changes a gradient cannot set them.

The entry refers to the gradient's interval as `sample` and to its `site`, and carries the site's
coordinates as `location`. When the requester may not see the site, `location` and `site` are
`null`. The record at the gradient's own address adds `children`, a reference to each child heat
flow calculated from the gradient. A child the requester may not see is left out.

```
GET /api/v1/measurements/thermal-gradients/
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "url": "https://portal.heatflow.world/api/v1/measurements/thermal-gradients/mprrvSq56QCmNiMAiVdmaKC/",
      "html_url": "https://portal.heatflow.world/measurement/mprrvSq56QCmNiMAiVdmaKC/",
      "uuid": "mprrvSq56QCmNiMAiVdmaKC",
      "name": "Hole A-1 gradient",
      "sample": {
        "uuid": "sAvai23dHxcyhKwmMz4sMZU",
        "url": "https://portal.heatflow.world/api/v1/samples/depth-intervals/sAvai23dHxcyhKwmMz4sMZU/"
      },
      "dataset": {
        "uuid": "dSJt4XcaoCXHb8BfKdnVCAE",
        "url": "https://portal.heatflow.world/api/v1/datasets/dSJt4XcaoCXHb8BfKdnVCAE/"
      },
      "location": {
        "type": "Point",
        "coordinates": [-179.43217, -79.87654]
      },
      "location_uncertainty": null,
      "added": "2026-10-20T21:31:57.201118Z",
      "modified": "2026-10-20T21:31:57.269387Z",
      "value": 25.5,
      "uncertainty": 1.25,
      "corrected_value": 26.5,
      "corrected_uncertainty": 1.5,
      "method_top": [
        {
          "name": "ODTT_PC",
          "label": "ODTT-PC",
          "uri": "https://heatflow.world/vocabularies/temperature-method/ODTT_PC",
          "vocabulary": "temperature-method"
        }
      ],
      "method_bottom": [],
      "shutin_top": 12,
      "shutin_bottom": 24,
      "correction_top": [],
      "correction_bottom": [],
      "number": 35,
      "temperature_top": 14.2,
      "temperature_top_uncertainty": null,
      "temperature_bottom": 19.8,
      "temperature_bottom_uncertainty": null,
      "score": 0.5,
      "score_missing": false,
      "quality_scheme": "hfqa_tool 0.2",
      "site": {
        "uuid": "sufCcNuwVkhMwA8RJWumEft",
        "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sufCcNuwVkhMwA8RJWumEft/"
      },
      "descriptions": [],
      "dates": [],
      "identifiers": [],
      "keywords": [],
      "contributors": [],
      "units": {
        "value": "K/km",
        "uncertainty": "K/km",
        "corrected_value": "K/km",
        "corrected_uncertainty": "K/km",
        "shutin_top": "h",
        "shutin_bottom": "h",
        "temperature_top": "°C",
        "temperature_top_uncertainty": "°C",
        "temperature_bottom": "°C",
        "temperature_bottom_uncertainty": "°C"
      }
    }
  ]
}
```

At the gradient's own address the record is the same, with `children` added:

```
GET /api/v1/measurements/thermal-gradients/mprrvSq56QCmNiMAiVdmaKC/
```

```json
{
  "uuid": "mprrvSq56QCmNiMAiVdmaKC",
  "children": [
    {
      "uuid": "mPRRfWDjwicXHp6tuDZMUwR",
      "url": "https://portal.heatflow.world/api/v1/measurements/heat-flow/mPRRfWDjwicXHp6tuDZMUwR/"
    }
  ]
}
```

## An interval conductivity

An interval conductivity is the mean thermal conductivity over one depth interval. Its list entry
gives the `value` and `uncertainty`, the `method`, `strategy`, `source`, `saturation`, pressure and
temperature conditions and function, the `conductivity_location` the samples came from and the
number of measurements it rests on (`number`).

Like a gradient, it carries the `score` the portal calculated for it, `score_missing` and the
`quality_scheme` revision, all read-only and `null` when the score could not be determined. It
refers to its interval as `sample` and to its `site`, and carries the site's coordinates as
`location`. When the requester may not see the site, `location` and `site` are `null`. The record
at its own address adds `children`, a reference to each child heat flow calculated from it. A child
the requester may not see is left out.

```
GET /api/v1/measurements/thermal-conductivities/
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "url": "https://portal.heatflow.world/api/v1/measurements/thermal-conductivities/mn67tXfcqEAVVzMqFoiSicR/",
      "html_url": "https://portal.heatflow.world/measurement/mn67tXfcqEAVVzMqFoiSicR/",
      "uuid": "mn67tXfcqEAVVzMqFoiSicR",
      "name": "Hole A-1 conductivity",
      "sample": {
        "uuid": "sAvai23dHxcyhKwmMz4sMZU",
        "url": "https://portal.heatflow.world/api/v1/samples/depth-intervals/sAvai23dHxcyhKwmMz4sMZU/"
      },
      "dataset": {
        "uuid": "dSJt4XcaoCXHb8BfKdnVCAE",
        "url": "https://portal.heatflow.world/api/v1/datasets/dSJt4XcaoCXHb8BfKdnVCAE/"
      },
      "location": {
        "type": "Point",
        "coordinates": [-179.43217, -79.87654]
      },
      "location_uncertainty": null,
      "added": "2026-10-20T21:31:57.289558Z",
      "modified": "2026-10-20T21:31:57.405852Z",
      "value": 2.5,
      "uncertainty": 0.25,
      "method": [],
      "strategy": [],
      "source": [
        {
          "name": "assumed_from_literature",
          "label": "Assumed from literature",
          "uri": "https://heatflow.world/vocabularies/conductivity-sources/assumed_from_literature",
          "vocabulary": "conductivity-sources"
        }
      ],
      "saturation": [],
      "pT_conditions": [],
      "pT_function": [],
      "conductivity_location": [
        {
          "name": "actual",
          "label": "Actual heat-flow location",
          "uri": "https://heatflow.world/vocabularies/conductivity-location/actual",
          "vocabulary": "conductivity-location"
        }
      ],
      "number": 12,
      "score": 0.4,
      "score_missing": false,
      "quality_scheme": "hfqa_tool 0.2",
      "site": {
        "uuid": "sufCcNuwVkhMwA8RJWumEft",
        "url": "https://portal.heatflow.world/api/v1/samples/heat-flow-sites/sufCcNuwVkhMwA8RJWumEft/"
      },
      "descriptions": [],
      "dates": [],
      "identifiers": [],
      "keywords": [],
      "contributors": [],
      "units": {
        "value": "W/mK",
        "uncertainty": "W/mK"
      }
    }
  ]
}
```

At the conductivity's own address the record is the same, with `children` added:

```
GET /api/v1/measurements/thermal-conductivities/mn67tXfcqEAVVzMqFoiSicR/
```

```json
{
  "uuid": "mn67tXfcqEAVVzMqFoiSicR",
  "children": [
    {
      "uuid": "mPRRfWDjwicXHp6tuDZMUwR",
      "url": "https://portal.heatflow.world/api/v1/measurements/heat-flow/mPRRfWDjwicXHp6tuDZMUwR/"
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
| `HeatFlowIntervalSerializer` | Depth interval |
| `HeatFlowSerializer` | Child heat flow |
| `ThermalGradientSerializer` | Thermal gradient |
| `IntervalConductivitySerializer` | Interval conductivity |
| `ParentHeatFlowSerializer` | Parent heat flow |

Every type has a longer single record than its list gives. Its serializer names the shorter shape
as `summary_serializer` (`HeatFlowSiteSummarySerializer`, `HeatFlowIntervalSummarySerializer`,
`HeatFlowSummarySerializer`, `ThermalGradientSummarySerializer`,
`IntervalConductivitySummarySerializer` and `ParentHeatFlowSummarySerializer`), and a list of it is
a `HeatFlowListSerializer` of that summary. A list of sites also reads the
parents of the whole page at once, and `RequesterVisibility.can_see` says whether the requester may
see one of them, by the same rule as the parent's own address. The site's single record builds its
intervals from `SiteIntervalSerializer`: the interval summary plus a `children` field, whose
entries are child summaries (`ChildSummaries` documents that field in the schema). The parent's
list entry on a site is `SiteParentSerializer`. `reference()` writes the `uuid` and `url` of a
record the requester has already been allowed to see, as the parent's `children` do.

A child's single record is `HeatFlowSerializer`. It gives the gradient and the conductivity
through `IntervalConductivitySummarySerializer` and `ThermalGradientSummarySerializer`, each read
only when the requester may see it, and lists the corrections with
`HeatFlowCorrectionSerializer`, whose type and status are `ChoiceLabelField`s.

The interval, child, gradient, conductivity and parent summaries all build on
`SitePlacedSerializer`. Its `location` is a `SiteLocationField` and its `site` is read through
`site_of`, which gives the site of a site, an interval, a parent, a child, a gradient or a
conductivity. A list of any of them asks `prime_sites` once which of the sites on the page the
requester may see, and the path to each record's site is prefetched with the page.

An interval's single record, `HeatFlowIntervalSerializer`, adds `probe_metadata` through
`ProbeMetadataSerializer` and lists the `children`, `thermal_gradients` and
`thermal_conductivities` made over it. A gradient's, `ThermalGradientSerializer`, and a
conductivity's, `IntervalConductivitySerializer`, add `children`. Each list is one query narrowed
to what the requester may see, and `references()` writes its entries.

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

`TermFieldSchema`, `TermRelatedFieldSchema`, `ChoiceLabelFieldSchema` and `UnitsFieldSchema`, in `project/heat_flow/schema.py`,
describe the term and `units` objects in the generated OpenAPI schema, with each term's
`vocabulary` limited to that field's vocabulary.

`HeatFlowRecordSchema`, in the same module, makes the generated schema give a list operation the
summary's component, so the site list's items have a `parent` and no `intervals`, and every other
operation the serializer's own.
