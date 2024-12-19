# {py:mod}`heat_flow.factories`

```{py:module} heat_flow.factories
```

```{autodoc2-docstring} heat_flow.factories
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HeatFlowSiteFactory <heat_flow.factories.HeatFlowSiteFactory>`
  -
* - {py:obj}`HeatFlowIntervalFactory <heat_flow.factories.HeatFlowIntervalFactory>`
  -
* - {py:obj}`ParentHeatFlowFactory <heat_flow.factories.ParentHeatFlowFactory>`
  -
* - {py:obj}`ChildHeatFlowFactory <heat_flow.factories.ChildHeatFlowFactory>`
  -
````

### API

``````{py:class} HeatFlowSiteFactory
:canonical: heat_flow.factories.HeatFlowSiteFactory

Bases: {py:obj}`earth_science.factories.location.BoreholeFactory`

````{py:attribute} environment
:canonical: heat_flow.factories.HeatFlowSiteFactory.environment
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.HeatFlowSiteFactory.environment
```

````

````{py:attribute} explo_method
:canonical: heat_flow.factories.HeatFlowSiteFactory.explo_method
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.HeatFlowSiteFactory.explo_method
```

````

````{py:attribute} explo_purpose
:canonical: heat_flow.factories.HeatFlowSiteFactory.explo_purpose
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.HeatFlowSiteFactory.explo_purpose
```

````

`````{py:class} Meta
:canonical: heat_flow.factories.HeatFlowSiteFactory.Meta

```{autodoc2-docstring} heat_flow.factories.HeatFlowSiteFactory.Meta
```

````{py:attribute} model
:canonical: heat_flow.factories.HeatFlowSiteFactory.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.factories.HeatFlowSiteFactory.Meta.model
```

````

`````

``````

``````{py:class} HeatFlowIntervalFactory
:canonical: heat_flow.factories.HeatFlowIntervalFactory

Bases: {py:obj}`earth_science.factories.location.GeoDepthIntervalFactory`

`````{py:class} Meta
:canonical: heat_flow.factories.HeatFlowIntervalFactory.Meta

```{autodoc2-docstring} heat_flow.factories.HeatFlowIntervalFactory.Meta
```

````{py:attribute} model
:canonical: heat_flow.factories.HeatFlowIntervalFactory.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.factories.HeatFlowIntervalFactory.Meta.model
```

````

`````

``````

``````{py:class} ParentHeatFlowFactory
:canonical: heat_flow.factories.ParentHeatFlowFactory

Bases: {py:obj}`geoluminate.factories.MeasurementFactory`

`````{py:class} Meta
:canonical: heat_flow.factories.ParentHeatFlowFactory.Meta

```{autodoc2-docstring} heat_flow.factories.ParentHeatFlowFactory.Meta
```

````{py:attribute} model
:canonical: heat_flow.factories.ParentHeatFlowFactory.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.factories.ParentHeatFlowFactory.Meta.model
```

````

`````

````{py:attribute} value
:canonical: heat_flow.factories.ParentHeatFlowFactory.value
:value: >
   'LazyAttribute(...)'

```{autodoc2-docstring} heat_flow.factories.ParentHeatFlowFactory.value
```

````

````{py:attribute} uncertainty
:canonical: heat_flow.factories.ParentHeatFlowFactory.uncertainty
:value: >
   'LazyAttribute(...)'

```{autodoc2-docstring} heat_flow.factories.ParentHeatFlowFactory.uncertainty
```

````

````{py:attribute} corr_HP_flag
:canonical: heat_flow.factories.ParentHeatFlowFactory.corr_HP_flag
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ParentHeatFlowFactory.corr_HP_flag
```

````

````{py:attribute} is_ghfdb
:canonical: heat_flow.factories.ParentHeatFlowFactory.is_ghfdb
:value: >
   'Faker(...)'

```{autodoc2-docstring} heat_flow.factories.ParentHeatFlowFactory.is_ghfdb
```

````

``````

``````{py:class} ChildHeatFlowFactory
:canonical: heat_flow.factories.ChildHeatFlowFactory

Bases: {py:obj}`geoluminate.factories.MeasurementFactory`

`````{py:class} Meta
:canonical: heat_flow.factories.ChildHeatFlowFactory.Meta

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.Meta
```

````{py:attribute} model
:canonical: heat_flow.factories.ChildHeatFlowFactory.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.Meta.model
```

````

`````

````{py:attribute} value
:canonical: heat_flow.factories.ChildHeatFlowFactory.value
:value: >
   'LazyAttribute(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.value
```

````

````{py:attribute} uncertainty
:canonical: heat_flow.factories.ChildHeatFlowFactory.uncertainty
:value: >
   'LazyAttribute(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.uncertainty
```

````

````{py:attribute} method
:canonical: heat_flow.factories.ChildHeatFlowFactory.method
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.method
```

````

````{py:attribute} expedition
:canonical: heat_flow.factories.ChildHeatFlowFactory.expedition
:value: >
   'Faker(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.expedition
```

````

````{py:attribute} relevant_child
:canonical: heat_flow.factories.ChildHeatFlowFactory.relevant_child
:value: >
   'Faker(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.relevant_child
```

````

````{py:attribute} probe_penetration
:canonical: heat_flow.factories.ChildHeatFlowFactory.probe_penetration
:value: >
   'Faker(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.probe_penetration
```

````

````{py:attribute} probe_type
:canonical: heat_flow.factories.ChildHeatFlowFactory.probe_type
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.probe_type
```

````

````{py:attribute} probe_length
:canonical: heat_flow.factories.ChildHeatFlowFactory.probe_length
:value: >
   'Faker(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.probe_length
```

````

````{py:attribute} probe_tilt
:canonical: heat_flow.factories.ChildHeatFlowFactory.probe_tilt
:value: >
   'Faker(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.probe_tilt
```

````

````{py:attribute} water_temperature
:canonical: heat_flow.factories.ChildHeatFlowFactory.water_temperature
:value: >
   'Faker(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.water_temperature
```

````

````{py:attribute} corr_IS_flag
:canonical: heat_flow.factories.ChildHeatFlowFactory.corr_IS_flag
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.corr_IS_flag
```

````

````{py:attribute} corr_T_flag
:canonical: heat_flow.factories.ChildHeatFlowFactory.corr_T_flag
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.corr_T_flag
```

````

````{py:attribute} corr_S_flag
:canonical: heat_flow.factories.ChildHeatFlowFactory.corr_S_flag
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.corr_S_flag
```

````

````{py:attribute} corr_E_flag
:canonical: heat_flow.factories.ChildHeatFlowFactory.corr_E_flag
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.corr_E_flag
```

````

````{py:attribute} corr_TOPO_flag
:canonical: heat_flow.factories.ChildHeatFlowFactory.corr_TOPO_flag
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.corr_TOPO_flag
```

````

````{py:attribute} corr_PAL_flag
:canonical: heat_flow.factories.ChildHeatFlowFactory.corr_PAL_flag
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.corr_PAL_flag
```

````

````{py:attribute} corr_SUR_flag
:canonical: heat_flow.factories.ChildHeatFlowFactory.corr_SUR_flag
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.corr_SUR_flag
```

````

````{py:attribute} corr_CONV_flag
:canonical: heat_flow.factories.ChildHeatFlowFactory.corr_CONV_flag
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.corr_CONV_flag
```

````

````{py:attribute} corr_HR_flag
:canonical: heat_flow.factories.ChildHeatFlowFactory.corr_HR_flag
:value: >
   'FuzzyChoice(...)'

```{autodoc2-docstring} heat_flow.factories.ChildHeatFlowFactory.corr_HR_flag
```

````

``````
