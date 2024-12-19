# {py:mod}`heat_flow.importer`

```{py:module} heat_flow.importer
```

```{autodoc2-docstring} heat_flow.importer
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CustomChoiceField <heat_flow.importer.CustomChoiceField>`
  - ```{autodoc2-docstring} heat_flow.importer.CustomChoiceField
    :summary:
    ```
* - {py:obj}`CustomSelect <heat_flow.importer.CustomSelect>`
  - ```{autodoc2-docstring} heat_flow.importer.CustomSelect
    :summary:
    ```
* - {py:obj}`CustomModelMultipleSelect <heat_flow.importer.CustomModelMultipleSelect>`
  - ```{autodoc2-docstring} heat_flow.importer.CustomModelMultipleSelect
    :summary:
    ```
* - {py:obj}`GHFDBImporterMixin <heat_flow.importer.GHFDBImporterMixin>`
  - ```{autodoc2-docstring} heat_flow.importer.GHFDBImporterMixin
    :summary:
    ```
* - {py:obj}`HeatFlowParentImporter <heat_flow.importer.HeatFlowParentImporter>`
  - ```{autodoc2-docstring} heat_flow.importer.HeatFlowParentImporter
    :summary:
    ```
* - {py:obj}`ChildHeatFlowImporter <heat_flow.importer.ChildHeatFlowImporter>`
  - ```{autodoc2-docstring} heat_flow.importer.ChildHeatFlowImporter
    :summary:
    ```
````

### API

`````{py:class} CustomChoiceField(*args, **kwargs)
:canonical: heat_flow.importer.CustomChoiceField

Bases: {py:obj}`django.forms.ChoiceField`

```{autodoc2-docstring} heat_flow.importer.CustomChoiceField
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.importer.CustomChoiceField.__init__
```

````{py:method} to_python(value)
:canonical: heat_flow.importer.CustomChoiceField.to_python

````

`````

`````{py:class} CustomSelect(attrs=None, choices=())
:canonical: heat_flow.importer.CustomSelect

Bases: {py:obj}`django.forms.Select`

```{autodoc2-docstring} heat_flow.importer.CustomSelect
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.importer.CustomSelect.__init__
```

````{py:method} value_from_datadict(data, files, name)
:canonical: heat_flow.importer.CustomSelect.value_from_datadict

```{autodoc2-docstring} heat_flow.importer.CustomSelect.value_from_datadict
```

````

`````

`````{py:class} CustomModelMultipleSelect(attrs=None, choices=())
:canonical: heat_flow.importer.CustomModelMultipleSelect

Bases: {py:obj}`django.forms.SelectMultiple`

```{autodoc2-docstring} heat_flow.importer.CustomModelMultipleSelect
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.importer.CustomModelMultipleSelect.__init__
```

````{py:method} value_from_datadict(data, files, name)
:canonical: heat_flow.importer.CustomModelMultipleSelect.value_from_datadict

````

`````

`````{py:class} GHFDBImporterMixin
:canonical: heat_flow.importer.GHFDBImporterMixin

```{autodoc2-docstring} heat_flow.importer.GHFDBImporterMixin
```

````{py:attribute} df_init_kwargs
:canonical: heat_flow.importer.GHFDBImporterMixin.df_init_kwargs
:value: >
   None

```{autodoc2-docstring} heat_flow.importer.GHFDBImporterMixin.df_init_kwargs
```

````

````{py:attribute} multi_value_fields
:canonical: heat_flow.importer.GHFDBImporterMixin.multi_value_fields
:value: >
   ['geo_lithology', 'geo_stratigraphy']

```{autodoc2-docstring} heat_flow.importer.GHFDBImporterMixin.multi_value_fields
```

````

````{py:method} read_dataframe()
:canonical: heat_flow.importer.GHFDBImporterMixin.read_dataframe

```{autodoc2-docstring} heat_flow.importer.GHFDBImporterMixin.read_dataframe
```

````

````{py:method} modify_row(row, model, options)
:canonical: heat_flow.importer.GHFDBImporterMixin.modify_row

```{autodoc2-docstring} heat_flow.importer.GHFDBImporterMixin.modify_row
```

````

````{py:method} get_model_form(model, form_kwargs)
:canonical: heat_flow.importer.GHFDBImporterMixin.get_model_form

```{autodoc2-docstring} heat_flow.importer.GHFDBImporterMixin.get_model_form
```

````

`````

`````{py:class} HeatFlowParentImporter(io, dataset=None)
:canonical: heat_flow.importer.HeatFlowParentImporter

Bases: {py:obj}`heat_flow.importer.GHFDBImporterMixin`, {py:obj}`earth_science.imports.SampleLocationImporterMixin`, {py:obj}`geoluminate.imports.GeoluminateBaseImporter`

```{autodoc2-docstring} heat_flow.importer.HeatFlowParentImporter
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.importer.HeatFlowParentImporter.__init__
```

````{py:attribute} location_fields
:canonical: heat_flow.importer.HeatFlowParentImporter.location_fields
:value: >
   None

```{autodoc2-docstring} heat_flow.importer.HeatFlowParentImporter.location_fields
```

````

````{py:attribute} models
:canonical: heat_flow.importer.HeatFlowParentImporter.models
:value: >
   None

```{autodoc2-docstring} heat_flow.importer.HeatFlowParentImporter.models
```

````

`````

`````{py:class} ChildHeatFlowImporter(io, dataset=None)
:canonical: heat_flow.importer.ChildHeatFlowImporter

Bases: {py:obj}`heat_flow.importer.GHFDBImporterMixin`, {py:obj}`geoluminate.imports.GeoluminateBaseImporter`

```{autodoc2-docstring} heat_flow.importer.ChildHeatFlowImporter
```

```{rubric} Initialization
```

```{autodoc2-docstring} heat_flow.importer.ChildHeatFlowImporter.__init__
```

````{py:attribute} models
:canonical: heat_flow.importer.ChildHeatFlowImporter.models
:value: >
   None

```{autodoc2-docstring} heat_flow.importer.ChildHeatFlowImporter.models
```

````

`````
