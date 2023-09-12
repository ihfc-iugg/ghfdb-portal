# {py:mod}`heat_flow.forms`

```{py:module} heat_flow.forms
```

```{autodoc2-docstring} heat_flow.forms
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HeatFlowParentForm <heat_flow.forms.HeatFlowParentForm>`
  -
* - {py:obj}`HeatFlowChildForm <heat_flow.forms.HeatFlowChildForm>`
  -
* - {py:obj}`ProbeSensingForm <heat_flow.forms.ProbeSensingForm>`
  -
* - {py:obj}`MetadataAndFlagsForm <heat_flow.forms.MetadataAndFlagsForm>`
  -
* - {py:obj}`TemperatureForm <heat_flow.forms.TemperatureForm>`
  -
* - {py:obj}`ConductivityForm <heat_flow.forms.ConductivityForm>`
  -
````

### API

``````{py:class} HeatFlowParentForm(**kwargs)
:canonical: heat_flow.forms.HeatFlowParentForm

Bases: {py:obj}`formset.fieldset.FieldsetMixin`, {py:obj}`django.forms.models.ModelForm`

````{py:attribute} label
:canonical: heat_flow.forms.HeatFlowParentForm.label
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.HeatFlowParentForm.label
```

````

````{py:attribute} help_text
:canonical: heat_flow.forms.HeatFlowParentForm.help_text
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.HeatFlowParentForm.help_text
```

````

`````{py:class} Meta
:canonical: heat_flow.forms.HeatFlowParentForm.Meta

```{autodoc2-docstring} heat_flow.forms.HeatFlowParentForm.Meta
```

````{py:attribute} model
:canonical: heat_flow.forms.HeatFlowParentForm.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.HeatFlowParentForm.Meta.model
```

````

````{py:attribute} fields
:canonical: heat_flow.forms.HeatFlowParentForm.Meta.fields
:value: >
   '__all__'

```{autodoc2-docstring} heat_flow.forms.HeatFlowParentForm.Meta.fields
```

````

`````

``````

``````{py:class} HeatFlowChildForm(**kwargs)
:canonical: heat_flow.forms.HeatFlowChildForm

Bases: {py:obj}`formset.fieldset.FieldsetMixin`, {py:obj}`django.forms.models.ModelForm`

````{py:attribute} label
:canonical: heat_flow.forms.HeatFlowChildForm.label
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.HeatFlowChildForm.label
```

````

````{py:attribute} help_text
:canonical: heat_flow.forms.HeatFlowChildForm.help_text
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.HeatFlowChildForm.help_text
```

````

`````{py:class} Meta
:canonical: heat_flow.forms.HeatFlowChildForm.Meta

```{autodoc2-docstring} heat_flow.forms.HeatFlowChildForm.Meta
```

````{py:attribute} model
:canonical: heat_flow.forms.HeatFlowChildForm.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.HeatFlowChildForm.Meta.model
```

````

````{py:attribute} fields
:canonical: heat_flow.forms.HeatFlowChildForm.Meta.fields
:value: >
   ['qc', 'qc_uncertainty', 'q_method', 'q_top', 'q_bottom', 'hf_pen', 'probe_type', 'hf_probeL', 'prob...

```{autodoc2-docstring} heat_flow.forms.HeatFlowChildForm.Meta.fields
```

````

`````

``````

``````{py:class} ProbeSensingForm(**kwargs)
:canonical: heat_flow.forms.ProbeSensingForm

Bases: {py:obj}`formset.fieldset.FieldsetMixin`, {py:obj}`django.forms.models.ModelForm`

````{py:attribute} label
:canonical: heat_flow.forms.ProbeSensingForm.label
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.ProbeSensingForm.label
```

````

````{py:attribute} help_text
:canonical: heat_flow.forms.ProbeSensingForm.help_text
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.ProbeSensingForm.help_text
```

````

`````{py:class} Meta
:canonical: heat_flow.forms.ProbeSensingForm.Meta

```{autodoc2-docstring} heat_flow.forms.ProbeSensingForm.Meta
```

````{py:attribute} model
:canonical: heat_flow.forms.ProbeSensingForm.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.ProbeSensingForm.Meta.model
```

````

````{py:attribute} fields
:canonical: heat_flow.forms.ProbeSensingForm.Meta.fields
:value: >
   ['hf_pen', 'probe_type', 'hf_probeL', 'probe_title']

```{autodoc2-docstring} heat_flow.forms.ProbeSensingForm.Meta.fields
```

````

`````

``````

``````{py:class} MetadataAndFlagsForm(**kwargs)
:canonical: heat_flow.forms.MetadataAndFlagsForm

Bases: {py:obj}`formset.fieldset.FieldsetMixin`, {py:obj}`django.forms.models.ModelForm`

````{py:attribute} label
:canonical: heat_flow.forms.MetadataAndFlagsForm.label
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.MetadataAndFlagsForm.label
```

````

````{py:attribute} help_text
:canonical: heat_flow.forms.MetadataAndFlagsForm.help_text
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.MetadataAndFlagsForm.help_text
```

````

`````{py:class} Meta
:canonical: heat_flow.forms.MetadataAndFlagsForm.Meta

```{autodoc2-docstring} heat_flow.forms.MetadataAndFlagsForm.Meta
```

````{py:attribute} model
:canonical: heat_flow.forms.MetadataAndFlagsForm.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.MetadataAndFlagsForm.Meta.model
```

````

````{py:attribute} fields
:canonical: heat_flow.forms.MetadataAndFlagsForm.Meta.fields
:value: >
   ['q_method', 'relevant_child']

```{autodoc2-docstring} heat_flow.forms.MetadataAndFlagsForm.Meta.fields
```

````

`````

``````

``````{py:class} TemperatureForm(**kwargs)
:canonical: heat_flow.forms.TemperatureForm

Bases: {py:obj}`formset.fieldset.FieldsetMixin`, {py:obj}`django.forms.models.ModelForm`

````{py:attribute} label
:canonical: heat_flow.forms.TemperatureForm.label
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.TemperatureForm.label
```

````

````{py:attribute} help_text
:canonical: heat_flow.forms.TemperatureForm.help_text
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.TemperatureForm.help_text
```

````

`````{py:class} Meta
:canonical: heat_flow.forms.TemperatureForm.Meta

```{autodoc2-docstring} heat_flow.forms.TemperatureForm.Meta
```

````{py:attribute} model
:canonical: heat_flow.forms.TemperatureForm.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.TemperatureForm.Meta.model
```

````

````{py:attribute} fields
:canonical: heat_flow.forms.TemperatureForm.Meta.fields
:value: >
   ['t_grad_mean', 'T_grad_uncertainty', 'T_grad_mean_cor', 'T_grad_uncertainty_cor', 'T_method_top', '...

```{autodoc2-docstring} heat_flow.forms.TemperatureForm.Meta.fields
```

````

`````

``````

``````{py:class} ConductivityForm(**kwargs)
:canonical: heat_flow.forms.ConductivityForm

Bases: {py:obj}`formset.fieldset.FieldsetMixin`, {py:obj}`django.forms.models.ModelForm`

````{py:attribute} label
:canonical: heat_flow.forms.ConductivityForm.label
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.ConductivityForm.label
```

````

````{py:attribute} help_text
:canonical: heat_flow.forms.ConductivityForm.help_text
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.ConductivityForm.help_text
```

````

`````{py:class} Meta
:canonical: heat_flow.forms.ConductivityForm.Meta

```{autodoc2-docstring} heat_flow.forms.ConductivityForm.Meta
```

````{py:attribute} model
:canonical: heat_flow.forms.ConductivityForm.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.forms.ConductivityForm.Meta.model
```

````

````{py:attribute} fields
:canonical: heat_flow.forms.ConductivityForm.Meta.fields
:value: >
   ['tc_mean', 'tc_uncertainty', 'tc_source', 'tc_method', 'tc_saturation', 'tc_pT_conditions', 'tc_pT_...

```{autodoc2-docstring} heat_flow.forms.ConductivityForm.Meta.fields
```

````

`````

``````
