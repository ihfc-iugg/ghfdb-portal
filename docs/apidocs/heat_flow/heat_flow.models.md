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

* - {py:obj}`HeatFlow <heat_flow.models.HeatFlow>`
  - ```{autodoc2-docstring} heat_flow.models.HeatFlow
    :summary:
    ```
* - {py:obj}`HeatFlowChild <heat_flow.models.HeatFlowChild>`
  - ```{autodoc2-docstring} heat_flow.models.HeatFlowChild
    :summary:
    ```
````

### API

``````{py:class} HeatFlow(*args, **kwargs)
:canonical: heat_flow.models.HeatFlow

Bases: {py:obj}`geoluminate.contrib.project.models.Measurement`

```{autodoc2-docstring} heat_flow.models.HeatFlow
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.models.HeatFlow.__init__
```

````{py:attribute} site
:canonical: heat_flow.models.HeatFlow.site
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.site
```

````

````{py:attribute} q
:canonical: heat_flow.models.HeatFlow.q
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.q
```

````

````{py:attribute} q_uncertainty
:canonical: heat_flow.models.HeatFlow.q_uncertainty
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.q_uncertainty
```

````

````{py:attribute} environment
:canonical: heat_flow.models.HeatFlow.environment
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.environment
```

````

````{py:attribute} corr_HP_flag
:canonical: heat_flow.models.HeatFlow.corr_HP_flag
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.corr_HP_flag
```

````

````{py:attribute} total_depth_MD
:canonical: heat_flow.models.HeatFlow.total_depth_MD
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.total_depth_MD
```

````

````{py:attribute} total_depth_TVD
:canonical: heat_flow.models.HeatFlow.total_depth_TVD
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.total_depth_TVD
```

````

````{py:attribute} explo_method
:canonical: heat_flow.models.HeatFlow.explo_method
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.explo_method
```

````

````{py:attribute} explo_purpose
:canonical: heat_flow.models.HeatFlow.explo_purpose
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.explo_purpose
```

````

`````{py:class} Meta
:canonical: heat_flow.models.HeatFlow.Meta

```{autodoc2-docstring} heat_flow.models.HeatFlow.Meta
```

````{py:attribute} verbose_name
:canonical: heat_flow.models.HeatFlow.Meta.verbose_name
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.Meta.verbose_name
```

````

````{py:attribute} verbose_name_plural
:canonical: heat_flow.models.HeatFlow.Meta.verbose_name_plural
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlow.Meta.verbose_name_plural
```

````

`````

````{py:method} __str__()
:canonical: heat_flow.models.HeatFlow.__str__

```{autodoc2-docstring} heat_flow.models.HeatFlow.__str__
```

````

````{py:method} get_site()
:canonical: heat_flow.models.HeatFlow.get_site

```{autodoc2-docstring} heat_flow.models.HeatFlow.get_site
```

````

````{py:property} name
:canonical: heat_flow.models.HeatFlow.name

```{autodoc2-docstring} heat_flow.models.HeatFlow.name
```

````

````{py:property} lat_NS
:canonical: heat_flow.models.HeatFlow.lat_NS

```{autodoc2-docstring} heat_flow.models.HeatFlow.lat_NS
```

````

````{py:property} long_EW
:canonical: heat_flow.models.HeatFlow.long_EW

```{autodoc2-docstring} heat_flow.models.HeatFlow.long_EW
```

````

````{py:property} elevation
:canonical: heat_flow.models.HeatFlow.elevation

```{autodoc2-docstring} heat_flow.models.HeatFlow.elevation
```

````

````{py:property} q_comment
:canonical: heat_flow.models.HeatFlow.q_comment

```{autodoc2-docstring} heat_flow.models.HeatFlow.q_comment
```

````

````{py:method} get_quality()
:canonical: heat_flow.models.HeatFlow.get_quality

```{autodoc2-docstring} heat_flow.models.HeatFlow.get_quality
```

````

``````

``````{py:class} HeatFlowChild(*args, **kwargs)
:canonical: heat_flow.models.HeatFlowChild

Bases: {py:obj}`geoluminate.contrib.project.models.Measurement`

```{autodoc2-docstring} heat_flow.models.HeatFlowChild
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.__init__
```

````{py:attribute} parent
:canonical: heat_flow.models.HeatFlowChild.parent
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.parent
```

````

````{py:attribute} qc
:canonical: heat_flow.models.HeatFlowChild.qc
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.qc
```

````

````{py:attribute} qc_uncertainty
:canonical: heat_flow.models.HeatFlowChild.qc_uncertainty
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.qc_uncertainty
```

````

````{py:attribute} q_method
:canonical: heat_flow.models.HeatFlowChild.q_method
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.q_method
```

````

````{py:attribute} q_top
:canonical: heat_flow.models.HeatFlowChild.q_top
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.q_top
```

````

````{py:attribute} q_bottom
:canonical: heat_flow.models.HeatFlowChild.q_bottom
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.q_bottom
```

````

````{py:attribute} expedition
:canonical: heat_flow.models.HeatFlowChild.expedition
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.expedition
```

````

````{py:attribute} relevant_child
:canonical: heat_flow.models.HeatFlowChild.relevant_child
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.relevant_child
```

````

````{py:attribute} probe_penetration
:canonical: heat_flow.models.HeatFlowChild.probe_penetration
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.probe_penetration
```

````

````{py:attribute} probe_type
:canonical: heat_flow.models.HeatFlowChild.probe_type
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.probe_type
```

````

````{py:attribute} probe_length
:canonical: heat_flow.models.HeatFlowChild.probe_length
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.probe_length
```

````

````{py:attribute} probe_tilt
:canonical: heat_flow.models.HeatFlowChild.probe_tilt
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.probe_tilt
```

````

````{py:attribute} water_temperature
:canonical: heat_flow.models.HeatFlowChild.water_temperature
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.water_temperature
```

````

````{py:attribute} T_grad_mean
:canonical: heat_flow.models.HeatFlowChild.T_grad_mean
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_grad_mean
```

````

````{py:attribute} T_grad_uncertainty
:canonical: heat_flow.models.HeatFlowChild.T_grad_uncertainty
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_grad_uncertainty
```

````

````{py:attribute} T_grad_mean_cor
:canonical: heat_flow.models.HeatFlowChild.T_grad_mean_cor
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_grad_mean_cor
```

````

````{py:attribute} T_grad_uncertainty_cor
:canonical: heat_flow.models.HeatFlowChild.T_grad_uncertainty_cor
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_grad_uncertainty_cor
```

````

````{py:attribute} T_method_top
:canonical: heat_flow.models.HeatFlowChild.T_method_top
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_method_top
```

````

````{py:attribute} T_method_bottom
:canonical: heat_flow.models.HeatFlowChild.T_method_bottom
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_method_bottom
```

````

````{py:attribute} T_shutin_top
:canonical: heat_flow.models.HeatFlowChild.T_shutin_top
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_shutin_top
```

````

````{py:attribute} T_shutin_bottom
:canonical: heat_flow.models.HeatFlowChild.T_shutin_bottom
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_shutin_bottom
```

````

````{py:attribute} T_correction_top
:canonical: heat_flow.models.HeatFlowChild.T_correction_top
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_correction_top
```

````

````{py:attribute} T_correction_bottom
:canonical: heat_flow.models.HeatFlowChild.T_correction_bottom
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_correction_bottom
```

````

````{py:attribute} T_number
:canonical: heat_flow.models.HeatFlowChild.T_number
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.T_number
```

````

````{py:attribute} tc_mean
:canonical: heat_flow.models.HeatFlowChild.tc_mean
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.tc_mean
```

````

````{py:attribute} tc_uncertainty
:canonical: heat_flow.models.HeatFlowChild.tc_uncertainty
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.tc_uncertainty
```

````

````{py:attribute} tc_source
:canonical: heat_flow.models.HeatFlowChild.tc_source
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.tc_source
```

````

````{py:attribute} tc_location
:canonical: heat_flow.models.HeatFlowChild.tc_location
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.tc_location
```

````

````{py:attribute} tc_method
:canonical: heat_flow.models.HeatFlowChild.tc_method
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.tc_method
```

````

````{py:attribute} tc_saturation
:canonical: heat_flow.models.HeatFlowChild.tc_saturation
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.tc_saturation
```

````

````{py:attribute} tc_pT_conditions
:canonical: heat_flow.models.HeatFlowChild.tc_pT_conditions
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.tc_pT_conditions
```

````

````{py:attribute} tc_pT_function
:canonical: heat_flow.models.HeatFlowChild.tc_pT_function
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.tc_pT_function
```

````

````{py:attribute} tc_strategy
:canonical: heat_flow.models.HeatFlowChild.tc_strategy
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.tc_strategy
```

````

````{py:attribute} tc_number
:canonical: heat_flow.models.HeatFlowChild.tc_number
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.tc_number
```

````

````{py:attribute} IGSN
:canonical: heat_flow.models.HeatFlowChild.IGSN
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.IGSN
```

````

````{py:attribute} corr_IS_flag
:canonical: heat_flow.models.HeatFlowChild.corr_IS_flag
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.corr_IS_flag
```

````

````{py:attribute} corr_T_flag
:canonical: heat_flow.models.HeatFlowChild.corr_T_flag
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.corr_T_flag
```

````

````{py:attribute} corr_S_flag
:canonical: heat_flow.models.HeatFlowChild.corr_S_flag
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.corr_S_flag
```

````

````{py:attribute} corr_E_flag
:canonical: heat_flow.models.HeatFlowChild.corr_E_flag
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.corr_E_flag
```

````

````{py:attribute} corr_TOPO_flag
:canonical: heat_flow.models.HeatFlowChild.corr_TOPO_flag
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.corr_TOPO_flag
```

````

````{py:attribute} corr_PAL_flag
:canonical: heat_flow.models.HeatFlowChild.corr_PAL_flag
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.corr_PAL_flag
```

````

````{py:attribute} corr_SUR_flag
:canonical: heat_flow.models.HeatFlowChild.corr_SUR_flag
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.corr_SUR_flag
```

````

````{py:attribute} corr_CONV_flag
:canonical: heat_flow.models.HeatFlowChild.corr_CONV_flag
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.corr_CONV_flag
```

````

````{py:attribute} corr_HR_flag
:canonical: heat_flow.models.HeatFlowChild.corr_HR_flag
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.corr_HR_flag
```

````

`````{py:class} Meta
:canonical: heat_flow.models.HeatFlowChild.Meta

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.Meta
```

````{py:attribute} verbose_name
:canonical: heat_flow.models.HeatFlowChild.Meta.verbose_name
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.Meta.verbose_name
```

````

````{py:attribute} verbose_name_plural
:canonical: heat_flow.models.HeatFlowChild.Meta.verbose_name_plural
:value: >
   None

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.Meta.verbose_name_plural
```

````

````{py:attribute} ordering
:canonical: heat_flow.models.HeatFlowChild.Meta.ordering
:value: >
   ['relevant_child', 'q_top']

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.Meta.ordering
```

````

`````

````{py:method} __str__()
:canonical: heat_flow.models.HeatFlowChild.__str__

````

````{py:method} clean(*args, **kwargs)
:canonical: heat_flow.models.HeatFlowChild.clean

````

````{py:method} interval(obj)
:canonical: heat_flow.models.HeatFlowChild.interval

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.interval
```

````

````{py:method} get_U_score()
:canonical: heat_flow.models.HeatFlowChild.get_U_score

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.get_U_score
```

````

````{py:method} get_M_score()
:canonical: heat_flow.models.HeatFlowChild.get_M_score

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.get_M_score
```

````

````{py:method} get_TC_score()
:canonical: heat_flow.models.HeatFlowChild.get_TC_score

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.get_TC_score
```

````

````{py:method} get_perturbation_effects()
:canonical: heat_flow.models.HeatFlowChild.get_perturbation_effects

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.get_perturbation_effects
```

````

````{py:method} get_quality()
:canonical: heat_flow.models.HeatFlowChild.get_quality

```{autodoc2-docstring} heat_flow.models.HeatFlowChild.get_quality
```

````

``````
