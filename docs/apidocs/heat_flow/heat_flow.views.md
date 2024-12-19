# {py:mod}`heat_flow.views`

```{py:module} heat_flow.views
```

```{autodoc2-docstring} heat_flow.views
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`GHFDBPathDownloadView <heat_flow.views.GHFDBPathDownloadView>`
  -
* - {py:obj}`ReviewForm <heat_flow.views.ReviewForm>`
  -
* - {py:obj}`ReviewCRUDView <heat_flow.views.ReviewCRUDView>`
  -
* - {py:obj}`UploadForm <heat_flow.views.UploadForm>`
  -
* - {py:obj}`GHFDBUpload <heat_flow.views.GHFDBUpload>`
  -
````

### API

`````{py:class} GHFDBPathDownloadView(**kwargs)
:canonical: heat_flow.views.GHFDBPathDownloadView

Bases: {py:obj}`django_downloadview.PathDownloadView`

````{py:method} get_path()
:canonical: heat_flow.views.GHFDBPathDownloadView.get_path

````

`````

``````{py:class} ReviewForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None)
:canonical: heat_flow.views.ReviewForm

Bases: {py:obj}`django.forms.ModelForm`

`````{py:class} Meta
:canonical: heat_flow.views.ReviewForm.Meta

```{autodoc2-docstring} heat_flow.views.ReviewForm.Meta
```

````{py:attribute} model
:canonical: heat_flow.views.ReviewForm.Meta.model
:value: >
   None

```{autodoc2-docstring} heat_flow.views.ReviewForm.Meta.model
```

````

````{py:attribute} fields
:canonical: heat_flow.views.ReviewForm.Meta.fields
:value: >
   ['reviewers', 'comment', 'start_date', 'literature']

```{autodoc2-docstring} heat_flow.views.ReviewForm.Meta.fields
```

````

`````

``````

`````{py:class} ReviewCRUDView(**kwargs)
:canonical: heat_flow.views.ReviewCRUDView

Bases: {py:obj}`geoluminate.core.view_mixins.HTMXMixin`, {py:obj}`neapolitan.views.CRUDView`

````{py:attribute} model
:canonical: heat_flow.views.ReviewCRUDView.model
:value: >
   None

```{autodoc2-docstring} heat_flow.views.ReviewCRUDView.model
```

````

````{py:attribute} form_class
:canonical: heat_flow.views.ReviewCRUDView.form_class
:value: >
   None

```{autodoc2-docstring} heat_flow.views.ReviewCRUDView.form_class
```

````

````{py:method} get_form(data=None, files=None, **kwargs)
:canonical: heat_flow.views.ReviewCRUDView.get_form

````

````{py:method} form_valid(form)
:canonical: heat_flow.views.ReviewCRUDView.form_valid

```{autodoc2-docstring} heat_flow.views.ReviewCRUDView.form_valid
```

````

`````

`````{py:class} UploadForm(data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList, label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None, renderer=None)
:canonical: heat_flow.views.UploadForm

Bases: {py:obj}`django.forms.Form`

````{py:attribute} docfile
:canonical: heat_flow.views.UploadForm.docfile
:value: >
   'FileField(...)'

```{autodoc2-docstring} heat_flow.views.UploadForm.docfile
```

````

`````

`````{py:class} GHFDBUpload(**kwargs)
:canonical: heat_flow.views.GHFDBUpload

Bases: {py:obj}`geoluminate.core.view_mixins.HTMXMixin`, {py:obj}`meta.views.MetadataMixin`, {py:obj}`django.views.generic.edit.FormView`

````{py:attribute} title
:canonical: heat_flow.views.GHFDBUpload.title
:value: >
   '_(...)'

```{autodoc2-docstring} heat_flow.views.GHFDBUpload.title
```

````

````{py:attribute} template_name
:canonical: heat_flow.views.GHFDBUpload.template_name
:value: >
   'geoluminate/import.html'

```{autodoc2-docstring} heat_flow.views.GHFDBUpload.template_name
```

````

````{py:attribute} form_class
:canonical: heat_flow.views.GHFDBUpload.form_class
:value: >
   None

```{autodoc2-docstring} heat_flow.views.GHFDBUpload.form_class
```

````

````{py:attribute} extra_context
:canonical: heat_flow.views.GHFDBUpload.extra_context
:value: >
   None

```{autodoc2-docstring} heat_flow.views.GHFDBUpload.extra_context
```

````

````{py:attribute} importer_class
:canonical: heat_flow.views.GHFDBUpload.importer_class
:value: >
   None

```{autodoc2-docstring} heat_flow.views.GHFDBUpload.importer_class
```

````

````{py:method} process_import(dataset, import_file)
:canonical: heat_flow.views.GHFDBUpload.process_import

```{autodoc2-docstring} heat_flow.views.GHFDBUpload.process_import
```

````

````{py:method} get_form(form_class=None)
:canonical: heat_flow.views.GHFDBUpload.get_form

````

````{py:method} form_valid(form)
:canonical: heat_flow.views.GHFDBUpload.form_valid

````

````{py:method} get_success_url()
:canonical: heat_flow.views.GHFDBUpload.get_success_url

````

`````
