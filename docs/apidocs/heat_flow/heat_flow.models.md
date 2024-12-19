# {py:mod}`heat_flow.models`

```{py:module} heat_flow.models
```

```{autodoc2-docstring} heat_flow.models
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`GHFDBDataset <heat_flow.models.GHFDBDataset>`
  -
* - {py:obj}`HeatFlowSite <heat_flow.models.HeatFlowSite>`
  -
* - {py:obj}`HeatFlowInterval <heat_flow.models.HeatFlowInterval>`
  -
* - {py:obj}`ParentHeatFlow <heat_flow.models.ParentHeatFlow>`
  - ```{autodoc2-docstring} heat_flow.models.ParentHeatFlow
    :summary:
    ```
* - {py:obj}`ChildHeatFlow <heat_flow.models.ChildHeatFlow>`
  - ```{autodoc2-docstring} heat_flow.models.ChildHeatFlow
    :summary:
    ```
* - {py:obj}`Review <heat_flow.models.Review>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`default_metadata <heat_flow.models.default_metadata>`
  - ```{autodoc2-docstring} heat_flow.models.default_metadata
    :summary:
    ```
````

### API

````{py:data} default_metadata
:canonical: heat_flow.models.default_metadata
:value: >
   None

```{autodoc2-docstring} heat_flow.models.default_metadata
```

````

```{py:class} GHFDBDataset(*args, **kwargs)
:canonical: heat_flow.models.GHFDBDataset

Bases: {py:obj}`geoluminate.contrib.core.models.Dataset`

```

``````{py:class} HeatFlowSite(*args, **kwargs)
:canonical: heat_flow.models.HeatFlowSite

Bases: {py:obj}`earth_science.models.features.Borehole`

````{py:attribute} environment
:canonical: heat_flow.models.HeatFlowSite.environment
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.environment
```

````

````{py:attribute} explo_method
:canonical: heat_flow.models.HeatFlowSite.explo_method
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.explo_method
```

````

````{py:attribute} explo_purpose
:canonical: heat_flow.models.HeatFlowSite.explo_purpose
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.explo_purpose
```

````

````{py:attribute} total_depth_MD
:canonical: heat_flow.models.HeatFlowSite.total_depth_MD
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.total_depth_MD
```

````

````{py:attribute} total_depth_TVD
:canonical: heat_flow.models.HeatFlowSite.total_depth_TVD
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.total_depth_TVD
```

````

`````{py:class} Meta
:canonical: heat_flow.models.HeatFlowSite.Meta

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.Meta
```

````{py:attribute} verbose_name
:canonical: heat_flow.models.HeatFlowSite.Meta.verbose_name
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.Meta.verbose_name
```

````

````{py:attribute} verbose_name_plural
:canonical: heat_flow.models.HeatFlowSite.Meta.verbose_name_plural
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.Meta.verbose_name_plural
```

````

````{py:attribute} db_table_comment
:canonical: heat_flow.models.HeatFlowSite.Meta.db_table_comment
:value: >
   'Represents a heat flow site in the Global Heat Flow Database (GHFDB) to which multiple parent heat f...'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.Meta.db_table_comment
```

````

`````

`````{py:class} Config
:canonical: heat_flow.models.HeatFlowSite.Config

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.Config
```

````{py:attribute} metadata
:canonical: heat_flow.models.HeatFlowSite.Config.metadata
:value: >
   'Metadata(...)'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.Config.metadata
```

````

````{py:attribute} filterset_class
:canonical: heat_flow.models.HeatFlowSite.Config.filterset_class
:value: >
   'heat_flow.filters.HeatFlowSiteFilter'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.Config.filterset_class
```

````

````{py:attribute} form_class
:canonical: heat_flow.models.HeatFlowSite.Config.form_class
:value: >
   'heat_flow.forms.HeatFlowSiteForm'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.Config.form_class
```

````

````{py:attribute} table_class
:canonical: heat_flow.models.HeatFlowSite.Config.table_class
:value: >
   'heat_flow.tables.HeatFlowSiteTable'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.Config.table_class
```

````

````{py:attribute} importer_class
:canonical: heat_flow.models.HeatFlowSite.Config.importer_class
:value: >
   'heat_flow.importers.HeatFlowSiteImporter'

```{autodoc2-docstring} heat_flow.models.HeatFlowSite.Config.importer_class
```

````

`````

````{py:method} save(*args, **kwargs)
:canonical: heat_flow.models.HeatFlowSite.save

````

``````

``````{py:class} HeatFlowInterval(*args, **kwargs)
:canonical: heat_flow.models.HeatFlowInterval

Bases: {py:obj}`earth_science.models.samples.intervals.GeoDepthInterval`

````{py:attribute} ALLOWED_PARENTS
:canonical: heat_flow.models.HeatFlowInterval.ALLOWED_PARENTS
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowInterval.ALLOWED_PARENTS
```

````

`````{py:class} Meta
:canonical: heat_flow.models.HeatFlowInterval.Meta

```{autodoc2-docstring} heat_flow.models.HeatFlowInterval.Meta
```

````{py:attribute} verbose_name
:canonical: heat_flow.models.HeatFlowInterval.Meta.verbose_name
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.models.HeatFlowInterval.Meta.verbose_name
```

````

````{py:attribute} verbose_name_plural
:canonical: heat_flow.models.HeatFlowInterval.Meta.verbose_name_plural
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.models.HeatFlowInterval.Meta.verbose_name_plural
```

````

`````

`````{py:class} Config
:canonical: heat_flow.models.HeatFlowInterval.Config

```{autodoc2-docstring} heat_flow.models.HeatFlowInterval.Config
```

````{py:attribute} metadata
:canonical: heat_flow.models.HeatFlowInterval.Config.metadata
:value: >
   'Metadata(...)'

```{autodoc2-docstring} heat_flow.models.HeatFlowInterval.Config.metadata
```

````

````{py:attribute} filterset_fields
:canonical: heat_flow.models.HeatFlowInterval.Config.filterset_fields
:value: >
   ['lithology', 'stratigraphy']

```{autodoc2-docstring} heat_flow.models.HeatFlowInterval.Config.filterset_fields
```

````

````{py:attribute} table_class
:canonical: heat_flow.models.HeatFlowInterval.Config.table_class
:value: >
   'heat_flow.tables.HeatFlowIntervalTable'

```{autodoc2-docstring} heat_flow.models.HeatFlowInterval.Config.table_class
```

````

`````

````{py:method} save(*args, **kwargs)
:canonical: heat_flow.models.HeatFlowInterval.save

````

``````

``````{py:class} ParentHeatFlow(*args, **kwargs)
:canonical: heat_flow.models.ParentHeatFlow

Bases: {py:obj}`geoluminate.contrib.core.models.Measurement`

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.__init__
```

````{py:attribute} ALLOWED_SAMPLE_TYPES
:canonical: heat_flow.models.ParentHeatFlow.ALLOWED_SAMPLE_TYPES
:value: >
   None

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.ALLOWED_SAMPLE_TYPES
```

````

````{py:attribute} value
:canonical: heat_flow.models.ParentHeatFlow.value
:value: >
   'QuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.value
```

````

````{py:attribute} uncertainty
:canonical: heat_flow.models.ParentHeatFlow.uncertainty
:value: >
   'QuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.uncertainty
```

````

````{py:attribute} corr_HP_flag
:canonical: heat_flow.models.ParentHeatFlow.corr_HP_flag
:value: >
   'BooleanField(...)'

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.corr_HP_flag
```

````

````{py:attribute} is_ghfdb
:canonical: heat_flow.models.ParentHeatFlow.is_ghfdb
:value: >
   'BooleanField(...)'

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.is_ghfdb
```

````

`````{py:class} Meta
:canonical: heat_flow.models.ParentHeatFlow.Meta

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.Meta
```

````{py:attribute} verbose_name
:canonical: heat_flow.models.ParentHeatFlow.Meta.verbose_name
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.Meta.verbose_name
```

````

````{py:attribute} verbose_name_plural
:canonical: heat_flow.models.ParentHeatFlow.Meta.verbose_name_plural
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.Meta.verbose_name_plural
```

````

````{py:attribute} db_table_comment
:canonical: heat_flow.models.ParentHeatFlow.Meta.db_table_comment
:value: >
   'Global Heat Flow Database (GHFDB) parent table.'

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.Meta.db_table_comment
```

````

`````

`````{py:class} Config
:canonical: heat_flow.models.ParentHeatFlow.Config

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.Config
```

````{py:attribute} metadata
:canonical: heat_flow.models.ParentHeatFlow.Config.metadata
:value: >
   'Metadata(...)'

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.Config.metadata
```

````

````{py:attribute} filterset_fields
:canonical: heat_flow.models.ParentHeatFlow.Config.filterset_fields
:value: >
   ['name', 'value', 'uncertainty', 'corr_HP_flag']

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.Config.filterset_fields
```

````

````{py:attribute} table_class
:canonical: heat_flow.models.ParentHeatFlow.Config.table_class
:value: >
   'heat_flow.tables.ParentHeatFlowTable'

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.Config.table_class
```

````

`````

````{py:method} save(*args, **kwargs)
:canonical: heat_flow.models.ParentHeatFlow.save

````

````{py:method} __str__()
:canonical: heat_flow.models.ParentHeatFlow.__str__

````

````{py:property} site
:canonical: heat_flow.models.ParentHeatFlow.site

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.site
```

````

````{py:method} get_quality()
:canonical: heat_flow.models.ParentHeatFlow.get_quality

```{autodoc2-docstring} heat_flow.models.ParentHeatFlow.get_quality
```

````

``````

``````{py:class} ChildHeatFlow(*args, **kwargs)
:canonical: heat_flow.models.ChildHeatFlow

Bases: {py:obj}`geoluminate.contrib.core.models.Measurement`

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.__init__
```

````{py:attribute} ALLOWED_SAMPLE_TYPES
:canonical: heat_flow.models.ChildHeatFlow.ALLOWED_SAMPLE_TYPES
:value: >
   None

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.ALLOWED_SAMPLE_TYPES
```

````

````{py:attribute} ghfdb
:canonical: heat_flow.models.ChildHeatFlow.ghfdb
:value: >
   'GHFDB(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.ghfdb
```

````

````{py:attribute} parent
:canonical: heat_flow.models.ChildHeatFlow.parent
:value: >
   'ForeignKey(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.parent
```

````

````{py:attribute} value
:canonical: heat_flow.models.ChildHeatFlow.value
:value: >
   'QuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.value
```

````

````{py:attribute} uncertainty
:canonical: heat_flow.models.ChildHeatFlow.uncertainty
:value: >
   'QuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.uncertainty
```

````

````{py:attribute} method
:canonical: heat_flow.models.ChildHeatFlow.method
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.method
```

````

````{py:attribute} expedition
:canonical: heat_flow.models.ChildHeatFlow.expedition
:value: >
   'CharField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.expedition
```

````

````{py:attribute} relevant_child
:canonical: heat_flow.models.ChildHeatFlow.relevant_child
:value: >
   'BooleanField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.relevant_child
```

````

````{py:attribute} probe_penetration
:canonical: heat_flow.models.ChildHeatFlow.probe_penetration
:value: >
   'DecimalQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.probe_penetration
```

````

````{py:attribute} probe_type
:canonical: heat_flow.models.ChildHeatFlow.probe_type
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.probe_type
```

````

````{py:attribute} probe_length
:canonical: heat_flow.models.ChildHeatFlow.probe_length
:value: >
   'DecimalQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.probe_length
```

````

````{py:attribute} probe_tilt
:canonical: heat_flow.models.ChildHeatFlow.probe_tilt
:value: >
   'DecimalQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.probe_tilt
```

````

````{py:attribute} water_temperature
:canonical: heat_flow.models.ChildHeatFlow.water_temperature
:value: >
   'QuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.water_temperature
```

````

````{py:attribute} T_grad_mean
:canonical: heat_flow.models.ChildHeatFlow.T_grad_mean
:value: >
   'DecimalQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_grad_mean
```

````

````{py:attribute} T_grad_uncertainty
:canonical: heat_flow.models.ChildHeatFlow.T_grad_uncertainty
:value: >
   'DecimalQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_grad_uncertainty
```

````

````{py:attribute} T_grad_mean_cor
:canonical: heat_flow.models.ChildHeatFlow.T_grad_mean_cor
:value: >
   'DecimalQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_grad_mean_cor
```

````

````{py:attribute} T_grad_uncertainty_cor
:canonical: heat_flow.models.ChildHeatFlow.T_grad_uncertainty_cor
:value: >
   'DecimalQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_grad_uncertainty_cor
```

````

````{py:attribute} T_method_top
:canonical: heat_flow.models.ChildHeatFlow.T_method_top
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_method_top
```

````

````{py:attribute} T_method_bottom
:canonical: heat_flow.models.ChildHeatFlow.T_method_bottom
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_method_bottom
```

````

````{py:attribute} T_shutin_top
:canonical: heat_flow.models.ChildHeatFlow.T_shutin_top
:value: >
   'PositiveIntegerQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_shutin_top
```

````

````{py:attribute} T_shutin_bottom
:canonical: heat_flow.models.ChildHeatFlow.T_shutin_bottom
:value: >
   'PositiveIntegerQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_shutin_bottom
```

````

````{py:attribute} T_corr_top
:canonical: heat_flow.models.ChildHeatFlow.T_corr_top
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_corr_top
```

````

````{py:attribute} T_corr_bottom
:canonical: heat_flow.models.ChildHeatFlow.T_corr_bottom
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_corr_bottom
```

````

````{py:attribute} T_number
:canonical: heat_flow.models.ChildHeatFlow.T_number
:value: >
   'PositiveSmallIntegerField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.T_number
```

````

````{py:attribute} tc_mean
:canonical: heat_flow.models.ChildHeatFlow.tc_mean
:value: >
   'DecimalQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.tc_mean
```

````

````{py:attribute} tc_uncertainty
:canonical: heat_flow.models.ChildHeatFlow.tc_uncertainty
:value: >
   'DecimalQuantityField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.tc_uncertainty
```

````

````{py:attribute} tc_source
:canonical: heat_flow.models.ChildHeatFlow.tc_source
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.tc_source
```

````

````{py:attribute} tc_location
:canonical: heat_flow.models.ChildHeatFlow.tc_location
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.tc_location
```

````

````{py:attribute} tc_method
:canonical: heat_flow.models.ChildHeatFlow.tc_method
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.tc_method
```

````

````{py:attribute} tc_saturation
:canonical: heat_flow.models.ChildHeatFlow.tc_saturation
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.tc_saturation
```

````

````{py:attribute} tc_pT_conditions
:canonical: heat_flow.models.ChildHeatFlow.tc_pT_conditions
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.tc_pT_conditions
```

````

````{py:attribute} tc_pT_function
:canonical: heat_flow.models.ChildHeatFlow.tc_pT_function
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.tc_pT_function
```

````

````{py:attribute} tc_strategy
:canonical: heat_flow.models.ChildHeatFlow.tc_strategy
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.tc_strategy
```

````

````{py:attribute} tc_number
:canonical: heat_flow.models.ChildHeatFlow.tc_number
:value: >
   'PositiveSmallIntegerField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.tc_number
```

````

````{py:attribute} corr_IS_flag
:canonical: heat_flow.models.ChildHeatFlow.corr_IS_flag
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.corr_IS_flag
```

````

````{py:attribute} corr_T_flag
:canonical: heat_flow.models.ChildHeatFlow.corr_T_flag
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.corr_T_flag
```

````

````{py:attribute} corr_S_flag
:canonical: heat_flow.models.ChildHeatFlow.corr_S_flag
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.corr_S_flag
```

````

````{py:attribute} corr_E_flag
:canonical: heat_flow.models.ChildHeatFlow.corr_E_flag
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.corr_E_flag
```

````

````{py:attribute} corr_TOPO_flag
:canonical: heat_flow.models.ChildHeatFlow.corr_TOPO_flag
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.corr_TOPO_flag
```

````

````{py:attribute} corr_PAL_flag
:canonical: heat_flow.models.ChildHeatFlow.corr_PAL_flag
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.corr_PAL_flag
```

````

````{py:attribute} corr_SUR_flag
:canonical: heat_flow.models.ChildHeatFlow.corr_SUR_flag
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.corr_SUR_flag
```

````

````{py:attribute} corr_CONV_flag
:canonical: heat_flow.models.ChildHeatFlow.corr_CONV_flag
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.corr_CONV_flag
```

````

````{py:attribute} corr_HR_flag
:canonical: heat_flow.models.ChildHeatFlow.corr_HR_flag
:value: >
   'ConceptField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.corr_HR_flag
```

````

````{py:attribute} c_comment
:canonical: heat_flow.models.ChildHeatFlow.c_comment
:value: >
   'TextField(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.c_comment
```

````

`````{py:class} Meta
:canonical: heat_flow.models.ChildHeatFlow.Meta

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.Meta
```

````{py:attribute} verbose_name
:canonical: heat_flow.models.ChildHeatFlow.Meta.verbose_name
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.Meta.verbose_name
```

````

````{py:attribute} verbose_name_plural
:canonical: heat_flow.models.ChildHeatFlow.Meta.verbose_name_plural
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.Meta.verbose_name_plural
```

````

````{py:attribute} ordering
:canonical: heat_flow.models.ChildHeatFlow.Meta.ordering
:value: >
   ['parent', 'relevant_child']

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.Meta.ordering
```

````

````{py:attribute} db_table_comment
:canonical: heat_flow.models.ChildHeatFlow.Meta.db_table_comment
:value: >
   'Global Heat Flow Database (GHFDB) child table.'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.Meta.db_table_comment
```

````

`````

`````{py:class} Config
:canonical: heat_flow.models.ChildHeatFlow.Config

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.Config
```

````{py:attribute} metadata
:canonical: heat_flow.models.ChildHeatFlow.Config.metadata
:value: >
   'Metadata(...)'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.Config.metadata
```

````

````{py:attribute} table_class
:canonical: heat_flow.models.ChildHeatFlow.Config.table_class
:value: >
   'heat_flow.tables.ChildHeatFlowTable'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.Config.table_class
```

````

````{py:attribute} filterset_class
:canonical: heat_flow.models.ChildHeatFlow.Config.filterset_class
:value: >
   'heat_flow.filters.ChildHeatFlowFilter'

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.Config.filterset_class
```

````

`````

````{py:method} __str__()
:canonical: heat_flow.models.ChildHeatFlow.__str__

````

````{py:property} interval
:canonical: heat_flow.models.ChildHeatFlow.interval

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.interval
```

````

````{py:method} get_U_score()
:canonical: heat_flow.models.ChildHeatFlow.get_U_score

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.get_U_score
```

````

````{py:method} get_M_score()
:canonical: heat_flow.models.ChildHeatFlow.get_M_score

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.get_M_score
```

````

````{py:method} get_TC_score()
:canonical: heat_flow.models.ChildHeatFlow.get_TC_score

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.get_TC_score
```

````

````{py:method} get_perturbation_effects()
:canonical: heat_flow.models.ChildHeatFlow.get_perturbation_effects

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.get_perturbation_effects
```

````

````{py:method} get_quality()
:canonical: heat_flow.models.ChildHeatFlow.get_quality

```{autodoc2-docstring} heat_flow.models.ChildHeatFlow.get_quality
```

````

``````

``````{py:class} Review(*args, **kwargs)
:canonical: heat_flow.models.Review

Bases: {py:obj}`django.db.models.Model`

````{py:attribute} reviewers
:canonical: heat_flow.models.Review.reviewers
:value: >
   'ManyToManyField(...)'

```{autodoc2-docstring} heat_flow.models.Review.reviewers
```

````

````{py:attribute} dataset
:canonical: heat_flow.models.Review.dataset
:value: >
   'OneToOneField(...)'

```{autodoc2-docstring} heat_flow.models.Review.dataset
```

````

````{py:attribute} literature
:canonical: heat_flow.models.Review.literature
:value: >
   'OneToOneField(...)'

```{autodoc2-docstring} heat_flow.models.Review.literature
```

````

````{py:attribute} start_date
:canonical: heat_flow.models.Review.start_date
:value: >
   'PartialDateField(...)'

```{autodoc2-docstring} heat_flow.models.Review.start_date
```

````

````{py:attribute} completion_date
:canonical: heat_flow.models.Review.completion_date
:value: >
   'PartialDateField(...)'

```{autodoc2-docstring} heat_flow.models.Review.completion_date
```

````

````{py:attribute} status
:canonical: heat_flow.models.Review.status
:value: >
   'IntegerField(...)'

```{autodoc2-docstring} heat_flow.models.Review.status
```

````

````{py:attribute} comment
:canonical: heat_flow.models.Review.comment
:value: >
   'TextField(...)'

```{autodoc2-docstring} heat_flow.models.Review.comment
```

````

`````{py:class} Meta
:canonical: heat_flow.models.Review.Meta

```{autodoc2-docstring} heat_flow.models.Review.Meta
```

````{py:attribute} verbose_name
:canonical: heat_flow.models.Review.Meta.verbose_name
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.models.Review.Meta.verbose_name
```

````

````{py:attribute} verbose_name_plural
:canonical: heat_flow.models.Review.Meta.verbose_name_plural
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.models.Review.Meta.verbose_name_plural
```

````

````{py:attribute} ordering
:canonical: heat_flow.models.Review.Meta.ordering
:value: >
   ['-start_date']

```{autodoc2-docstring} heat_flow.models.Review.Meta.ordering
```

````

`````

````{py:method} save(*args, **kwargs)
:canonical: heat_flow.models.Review.save

````

``````
