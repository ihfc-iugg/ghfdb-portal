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

* - {py:obj}`UploadForm <heat_flow.admin.UploadForm>`
  -
* - {py:obj}`HeatFlowDatasetAdmin <heat_flow.admin.HeatFlowDatasetAdmin>`
  -
* - {py:obj}`HeatFlowAdmin <heat_flow.admin.HeatFlowAdmin>`
  -
* - {py:obj}`ChildHeatFlowAdmin <heat_flow.admin.ChildHeatFlowAdmin>`
  -
* - {py:obj}`HeatFlowIntervalAdmin <heat_flow.admin.HeatFlowIntervalAdmin>`
  -
* - {py:obj}`HeatFlowSiteAdmin <heat_flow.admin.HeatFlowSiteAdmin>`
  -
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`admin_urlname <heat_flow.admin.admin_urlname>`
  - ```{autodoc2-docstring} heat_flow.admin.admin_urlname
    :summary:
    ```
````

### API

`````{py:class} UploadForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList, label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None, renderer=None)
:canonical: heat_flow.admin.UploadForm

Bases: {py:obj}`django.forms.Form`

````{py:attribute} docfile
:canonical: heat_flow.admin.UploadForm.docfile
:value: >
   'FileField(...)'

```{autodoc2-docstring} heat_flow.admin.UploadForm.docfile
```

````

`````

````{py:function} admin_urlname(opts, name)
:canonical: heat_flow.admin.admin_urlname

```{autodoc2-docstring} heat_flow.admin.admin_urlname
```
````

`````{py:class} HeatFlowDatasetAdmin(model, admin_site)
:canonical: heat_flow.admin.HeatFlowDatasetAdmin

Bases: {py:obj}`admin_extra_buttons.api.ExtraButtonsMixin`, {py:obj}`geoluminate.contrib.core.admin.DatasetAdmin`

````{py:attribute} actions_detail
:canonical: heat_flow.admin.HeatFlowDatasetAdmin.actions_detail
:value: >
   ['custom_detail_action']

```{autodoc2-docstring} heat_flow.admin.HeatFlowDatasetAdmin.actions_detail
```

````

````{py:method} upload(request, pk=None)
:canonical: heat_flow.admin.HeatFlowDatasetAdmin.upload

```{autodoc2-docstring} heat_flow.admin.HeatFlowDatasetAdmin.upload
```

````

`````

`````{py:class} HeatFlowAdmin(model, admin_site, *args, **kwargs)
:canonical: heat_flow.admin.HeatFlowAdmin

Bases: {py:obj}`geoluminate.contrib.core.admin.MeasurementAdmin`

````{py:attribute} list_display
:canonical: heat_flow.admin.HeatFlowAdmin.list_display
:value: >
   ['value', 'uncertainty', 'corr_HP_flag']

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.list_display
```

````

````{py:attribute} fields
:canonical: heat_flow.admin.HeatFlowAdmin.fields
:value: >
   ('sample', ('value', 'uncertainty'), 'corr_HP_flag')

```{autodoc2-docstring} heat_flow.admin.HeatFlowAdmin.fields
```

````

`````

`````{py:class} ChildHeatFlowAdmin(model, admin_site)
:canonical: heat_flow.admin.ChildHeatFlowAdmin

Bases: {py:obj}`django.contrib.admin.ModelAdmin`

````{py:attribute} list_display
:canonical: heat_flow.admin.ChildHeatFlowAdmin.list_display
:value: >
   ['parent', 'value', 'uncertainty']

```{autodoc2-docstring} heat_flow.admin.ChildHeatFlowAdmin.list_display
```

````

````{py:attribute} fieldsets
:canonical: heat_flow.admin.ChildHeatFlowAdmin.fieldsets
:value: >
   (('',), ('Heat Flow',), ('Probe Sensing',), ('Temperature',), ('Thermal Conductivity',), ('Correctio...

```{autodoc2-docstring} heat_flow.admin.ChildHeatFlowAdmin.fieldsets
```

````

````{py:attribute} formfield_overrides
:canonical: heat_flow.admin.ChildHeatFlowAdmin.formfield_overrides
:value: >
   None

```{autodoc2-docstring} heat_flow.admin.ChildHeatFlowAdmin.formfield_overrides
```

````

`````

`````{py:class} HeatFlowIntervalAdmin(model, admin_site)
:canonical: heat_flow.admin.HeatFlowIntervalAdmin

Bases: {py:obj}`geoluminate.contrib.core.admin.SampleAdmin`

````{py:attribute} list_display
:canonical: heat_flow.admin.HeatFlowIntervalAdmin.list_display
:value: >
   ['top', 'bottom']

```{autodoc2-docstring} heat_flow.admin.HeatFlowIntervalAdmin.list_display
```

````

````{py:attribute} formfield_overrides
:canonical: heat_flow.admin.HeatFlowIntervalAdmin.formfield_overrides
:value: >
   None

```{autodoc2-docstring} heat_flow.admin.HeatFlowIntervalAdmin.formfield_overrides
```

````

`````

`````{py:class} HeatFlowSiteAdmin(model, admin_site)
:canonical: heat_flow.admin.HeatFlowSiteAdmin

Bases: {py:obj}`geoluminate.contrib.core.admin.SampleAdmin`

````{py:attribute} list_display
:canonical: heat_flow.admin.HeatFlowSiteAdmin.list_display
:value: >
   ['top', 'bottom']

```{autodoc2-docstring} heat_flow.admin.HeatFlowSiteAdmin.list_display
```

````

````{py:attribute} formfield_overrides
:canonical: heat_flow.admin.HeatFlowSiteAdmin.formfield_overrides
:value: >
   None

```{autodoc2-docstring} heat_flow.admin.HeatFlowSiteAdmin.formfield_overrides
```

````

````{py:attribute} fieldsets
:canonical: heat_flow.admin.HeatFlowSiteAdmin.fieldsets
:value: >
   ((),)

```{autodoc2-docstring} heat_flow.admin.HeatFlowSiteAdmin.fieldsets
```

````

````{py:method} get_fieldsets(request, obj=None)
:canonical: heat_flow.admin.HeatFlowSiteAdmin.get_fieldsets

````

`````
