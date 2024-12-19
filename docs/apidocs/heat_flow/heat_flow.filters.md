# {py:mod}`heat_flow.filters`

```{py:module} heat_flow.filters
```

```{autodoc2-docstring} heat_flow.filters
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HeatFlowSiteFilter <heat_flow.filters.HeatFlowSiteFilter>`
  -
* - {py:obj}`ChildHeatFlowFilter <heat_flow.filters.ChildHeatFlowFilter>`
  - ```{autodoc2-docstring} heat_flow.filters.ChildHeatFlowFilter
    :summary:
    ```
````

### API

``````{py:class} HeatFlowSiteFilter(data=None, queryset=None, *, request=None, prefix=None)
:canonical: heat_flow.filters.HeatFlowSiteFilter

Bases: {py:obj}`geoluminate.contrib.core.filters.SampleFilter`

`````{py:class} Meta
:canonical: heat_flow.filters.HeatFlowSiteFilter.Meta

```{autodoc2-docstring} heat_flow.filters.HeatFlowSiteFilter.Meta
```

````{py:attribute} model
:canonical: heat_flow.filters.HeatFlowSiteFilter.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.filters.HeatFlowSiteFilter.Meta.model
```

````

````{py:attribute} fields
:canonical: heat_flow.filters.HeatFlowSiteFilter.Meta.fields
:value: >
   ['name', 'environment', 'explo_method', 'explo_purpose', 'lithology', 'age', 'stratigraphy']

```{autodoc2-docstring} heat_flow.filters.HeatFlowSiteFilter.Meta.fields
```

````

`````

``````

``````{py:class} ChildHeatFlowFilter(data=None, queryset=None, *, request=None, prefix=None)
:canonical: heat_flow.filters.ChildHeatFlowFilter

Bases: {py:obj}`django_filters.FilterSet`

```{autodoc2-docstring} heat_flow.filters.ChildHeatFlowFilter
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.filters.ChildHeatFlowFilter.__init__
```

`````{py:class} Meta
:canonical: heat_flow.filters.ChildHeatFlowFilter.Meta

```{autodoc2-docstring} heat_flow.filters.ChildHeatFlowFilter.Meta
```

````{py:attribute} model
:canonical: heat_flow.filters.ChildHeatFlowFilter.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.filters.ChildHeatFlowFilter.Meta.model
```

````

````{py:attribute} exclude
:canonical: heat_flow.filters.ChildHeatFlowFilter.Meta.exclude
:value: >
   ['created', 'modified', 'polymorphic_ctype', 'options', 'measurement_ptr', 'image']

```{autodoc2-docstring} heat_flow.filters.ChildHeatFlowFilter.Meta.exclude
```

````

`````

``````
