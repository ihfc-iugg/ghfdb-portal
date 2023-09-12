# {py:mod}`heat_flow.admin`

```{py:module} heat_flow.admin
```

```{autodoc2-docstring} heat_flow.admin
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HeatFlowChildInline <heat_flow.admin.HeatFlowChildInline>`
  -
* - {py:obj}`HeatFlowAdmin <heat_flow.admin.HeatFlowAdmin>`
  -
* - {py:obj}`HeatFlowChildAdmin <heat_flow.admin.HeatFlowChildAdmin>`
  -
````

### API

`````{py:class} HeatFlowChildInline(parent_model, admin_site)
:canonical: heat_flow.admin.HeatFlowChildInline

Bases: {py:obj}`django.contrib.admin.StackedInline`

````{py:attribute} model
:canonical: heat_flow.admin.HeatFlowChildInline.model
:value: >
   None

```{autodoc2-docstring} heat_flow.admin.HeatFlowChildInline.model
```

````

````{py:attribute} max_num
:canonical: heat_flow.admin.HeatFlowChildInline.max_num
:value: >
   0

```{autodoc2-docstring} heat_flow.admin.HeatFlowChildInline.max_num
```

````

`````

`````{py:class} HeatFlowAdmin(*args, **kwargs)
:canonical: heat_flow.admin.HeatFlowAdmin

Bases: {py:obj}`geoluminate.contrib.gis.admin.SiteAdminMixin`

````{py:attribute} list_display
:canonical: heat_flow.admin.HeatFlowAdmin.list_display
:value: >
   ['id', 'q', 'q_uncertainty']

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.list_display
```

````

````{py:attribute} readonly_fields
:canonical: heat_flow.admin.HeatFlowAdmin.readonly_fields
:value: >
   ['id']

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.readonly_fields
```

````

````{py:attribute} list_filter
:canonical: heat_flow.admin.HeatFlowAdmin.list_filter
:value: >
   ['environment', 'explo_method', 'explo_purpose']

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.list_filter
```

````

````{py:attribute} inlines
:canonical: heat_flow.admin.HeatFlowAdmin.inlines
:value: >
   None

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.inlines
```

````

````{py:attribute} fieldsets
:canonical: heat_flow.admin.HeatFlowAdmin.fieldsets
:value: >
   [('Geographic',), ('Heat Flow',), ('Marine',), ('References',), ('Comment',)]

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.fieldsets
```

````

````{py:attribute} search_fields
:canonical: heat_flow.admin.HeatFlowAdmin.search_fields
:value: >
   ['id']

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.search_fields
```

````

````{py:attribute} point_zoom
:canonical: heat_flow.admin.HeatFlowAdmin.point_zoom
:value: >
   8

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.point_zoom
```

````

````{py:attribute} map_width
:canonical: heat_flow.admin.HeatFlowAdmin.map_width
:value: >
   900

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.map_width
```

````

````{py:attribute} modifiable
:canonical: heat_flow.admin.HeatFlowAdmin.modifiable
:value: >
   True

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.modifiable
```

````

`````

`````{py:class} HeatFlowChildAdmin(model, admin_site)
:canonical: heat_flow.admin.HeatFlowChildAdmin

Bases: {py:obj}`django.contrib.admin.ModelAdmin`

````{py:attribute} list_display
:canonical: heat_flow.admin.HeatFlowChildAdmin.list_display
:value: >
   ['relevant_child', 'q_top', 'q_bottom', 'qc', 'qc_uncertainty', 'q_method', 'water_temperature', 'tc...

```{autodoc2-docstring} heat_flow.admin.HeatFlowChildAdmin.list_display
```

````

````{py:attribute} list_filter
:canonical: heat_flow.admin.HeatFlowChildAdmin.list_filter
:value: >
   ['q_method', 'probe_type', 'tc_source', 'tc_strategy']

```{autodoc2-docstring} heat_flow.admin.HeatFlowChildAdmin.list_filter
```

````

````{py:attribute} fieldsets
:canonical: heat_flow.admin.HeatFlowChildAdmin.fieldsets
:value: >
   [(), (), (), ()]

```{autodoc2-docstring} heat_flow.admin.HeatFlowChildAdmin.fieldsets
```

````

`````
