# {py:mod}`heat_flow.tables`

```{py:module} heat_flow.tables
```

```{autodoc2-docstring} heat_flow.tables
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HeatFlowSiteTable <heat_flow.tables.HeatFlowSiteTable>`
  -
* - {py:obj}`ParentHeatFlowTable <heat_flow.tables.ParentHeatFlowTable>`
  -
* - {py:obj}`ChildHeatFlowTable <heat_flow.tables.ChildHeatFlowTable>`
  -
* - {py:obj}`GHFDBTable <heat_flow.tables.GHFDBTable>`
  -
````

### API

``````{py:class} HeatFlowSiteTable(data=None, order_by=None, orderable=None, empty_text=None, exclude=None, attrs=None, row_attrs=None, pinned_row_attrs=None, sequence=None, prefix=None, order_by_field=None, page_field=None, per_page_field=None, template_name=None, default=None, request=None, show_header=None, show_footer=True, extra_columns=None)
:canonical: heat_flow.tables.HeatFlowSiteTable

Bases: {py:obj}`earth_science.tables.PointTable`

`````{py:class} Meta
:canonical: heat_flow.tables.HeatFlowSiteTable.Meta

```{autodoc2-docstring} heat_flow.tables.HeatFlowSiteTable.Meta
```

````{py:attribute} model
:canonical: heat_flow.tables.HeatFlowSiteTable.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.tables.HeatFlowSiteTable.Meta.model
```

````

````{py:attribute} exclude
:canonical: heat_flow.tables.HeatFlowSiteTable.Meta.exclude
:value: >
   ['path', 'status', 'has_children', 'has_parent', 'site_icon']

```{autodoc2-docstring} heat_flow.tables.HeatFlowSiteTable.Meta.exclude
```

````

````{py:attribute} fields
:canonical: heat_flow.tables.HeatFlowSiteTable.Meta.fields
:value: >
   ['id', 'dataset', 'name', 'latitude', 'longitude', 'elevation', 'environment', 'explo_method', 'expl...

```{autodoc2-docstring} heat_flow.tables.HeatFlowSiteTable.Meta.fields
```

````

`````

``````

``````{py:class} ParentHeatFlowTable(data=None, order_by=None, orderable=None, empty_text=None, exclude=None, attrs=None, row_attrs=None, pinned_row_attrs=None, sequence=None, prefix=None, order_by_field=None, page_field=None, per_page_field=None, template_name=None, default=None, request=None, show_header=None, show_footer=True, extra_columns=None)
:canonical: heat_flow.tables.ParentHeatFlowTable

Bases: {py:obj}`geoluminate.contrib.core.tables.MeasurementTable`

````{py:attribute} site
:canonical: heat_flow.tables.ParentHeatFlowTable.site
:value: >
   'Column(...)'

```{autodoc2-docstring} heat_flow.tables.ParentHeatFlowTable.site
```

````

`````{py:class} Meta
:canonical: heat_flow.tables.ParentHeatFlowTable.Meta

```{autodoc2-docstring} heat_flow.tables.ParentHeatFlowTable.Meta
```

````{py:attribute} model
:canonical: heat_flow.tables.ParentHeatFlowTable.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.tables.ParentHeatFlowTable.Meta.model
```

````

````{py:attribute} fields
:canonical: heat_flow.tables.ParentHeatFlowTable.Meta.fields
:value: >
   ['site', 'lat_NS', 'heat_flow']

```{autodoc2-docstring} heat_flow.tables.ParentHeatFlowTable.Meta.fields
```

````

`````

``````

``````{py:class} ChildHeatFlowTable(data=None, order_by=None, orderable=None, empty_text=None, exclude=None, attrs=None, row_attrs=None, pinned_row_attrs=None, sequence=None, prefix=None, order_by_field=None, page_field=None, per_page_field=None, template_name=None, default=None, request=None, show_header=None, show_footer=True, extra_columns=None)
:canonical: heat_flow.tables.ChildHeatFlowTable

Bases: {py:obj}`geoluminate.contrib.core.tables.MeasurementTable`

````{py:attribute} id
:canonical: heat_flow.tables.ChildHeatFlowTable.id
:value: >
   'Column(...)'

```{autodoc2-docstring} heat_flow.tables.ChildHeatFlowTable.id
```

````

````{py:attribute} value
:canonical: heat_flow.tables.ChildHeatFlowTable.value
:value: >
   'Column(...)'

```{autodoc2-docstring} heat_flow.tables.ChildHeatFlowTable.value
```

````

````{py:attribute} uncertainty
:canonical: heat_flow.tables.ChildHeatFlowTable.uncertainty
:value: >
   'Column(...)'

```{autodoc2-docstring} heat_flow.tables.ChildHeatFlowTable.uncertainty
```

````

````{py:attribute} method
:canonical: heat_flow.tables.ChildHeatFlowTable.method
:value: >
   'Column(...)'

```{autodoc2-docstring} heat_flow.tables.ChildHeatFlowTable.method
```

````

````{py:attribute} probe_penetration
:canonical: heat_flow.tables.ChildHeatFlowTable.probe_penetration
:value: >
   'Column(...)'

```{autodoc2-docstring} heat_flow.tables.ChildHeatFlowTable.probe_penetration
```

````

````{py:attribute} relevant_child
:canonical: heat_flow.tables.ChildHeatFlowTable.relevant_child
:value: >
   'Column(...)'

```{autodoc2-docstring} heat_flow.tables.ChildHeatFlowTable.relevant_child
```

````

`````{py:class} Meta
:canonical: heat_flow.tables.ChildHeatFlowTable.Meta

```{autodoc2-docstring} heat_flow.tables.ChildHeatFlowTable.Meta
```

````{py:attribute} model
:canonical: heat_flow.tables.ChildHeatFlowTable.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.tables.ChildHeatFlowTable.Meta.model
```

````

````{py:attribute} exclude
:canonical: heat_flow.tables.ChildHeatFlowTable.Meta.exclude
:value: >
   ['created', 'modified', 'polymorphic_ctype', 'name', 'sample', 'parent', 'options', 'measurement_ptr...

```{autodoc2-docstring} heat_flow.tables.ChildHeatFlowTable.Meta.exclude
```

````

`````

``````

``````{py:class} GHFDBTable(data=None, order_by=None, orderable=None, empty_text=None, exclude=None, attrs=None, row_attrs=None, pinned_row_attrs=None, sequence=None, prefix=None, order_by_field=None, page_field=None, per_page_field=None, template_name=None, default=None, request=None, show_header=None, show_footer=True, extra_columns=None)
:canonical: heat_flow.tables.GHFDBTable

Bases: {py:obj}`django_tables2.Table`

````{py:attribute} parent__value
:canonical: heat_flow.tables.GHFDBTable.parent__value
:value: >
   'Column(...)'

```{autodoc2-docstring} heat_flow.tables.GHFDBTable.parent__value
```

````

````{py:attribute} parent__uncertainty
:canonical: heat_flow.tables.GHFDBTable.parent__uncertainty
:value: >
   'Column(...)'

```{autodoc2-docstring} heat_flow.tables.GHFDBTable.parent__uncertainty
```

````

`````{py:class} Meta
:canonical: heat_flow.tables.GHFDBTable.Meta

```{autodoc2-docstring} heat_flow.tables.GHFDBTable.Meta
```

````{py:attribute} model
:canonical: heat_flow.tables.GHFDBTable.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.tables.GHFDBTable.Meta.model
```

````

````{py:attribute} fields
:canonical: heat_flow.tables.GHFDBTable.Meta.fields
:value: >
   ['id', 'parent__sample__name', 'parent__value', 'parent__uncertainty', 'value', 'uncertainty']

```{autodoc2-docstring} heat_flow.tables.GHFDBTable.Meta.fields
```

````

`````

``````
