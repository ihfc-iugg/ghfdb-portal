# {py:mod}`heat_flow.utils`

```{py:module} heat_flow.utils
```

```{autodoc2-docstring} heat_flow.utils
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`GHFDB <heat_flow.utils.GHFDB>`
  - ```{autodoc2-docstring} heat_flow.utils.GHFDB
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`GHFDB_field_map <heat_flow.utils.GHFDB_field_map>`
  - ```{autodoc2-docstring} heat_flow.utils.GHFDB_field_map
    :summary:
    ```
* - {py:obj}`GHFDB_db_fields <heat_flow.utils.GHFDB_db_fields>`
  - ```{autodoc2-docstring} heat_flow.utils.GHFDB_db_fields
    :summary:
    ```
* - {py:obj}`GHFDB_csv_fields <heat_flow.utils.GHFDB_csv_fields>`
  - ```{autodoc2-docstring} heat_flow.utils.GHFDB_csv_fields
    :summary:
    ```
````

### API

````{py:data} GHFDB_field_map
:canonical: heat_flow.utils.GHFDB_field_map
:value: >
   [('parent_id', 'parent__id'), ('q', 'parent__value'), ('q_uncertainty', 'parent__uncertainty'), ('na...

```{autodoc2-docstring} heat_flow.utils.GHFDB_field_map
```

````

````{py:data} GHFDB_db_fields
:canonical: heat_flow.utils.GHFDB_db_fields
:value: >
   None

```{autodoc2-docstring} heat_flow.utils.GHFDB_db_fields
```

````

````{py:data} GHFDB_csv_fields
:canonical: heat_flow.utils.GHFDB_csv_fields
:value: >
   None

```{autodoc2-docstring} heat_flow.utils.GHFDB_csv_fields
```

````

`````{py:class} GHFDB
:canonical: heat_flow.utils.GHFDB

Bases: {py:obj}`django_pandas.managers.DataFrameManager`

```{autodoc2-docstring} heat_flow.utils.GHFDB
```

````{py:method} get_queryset()
:canonical: heat_flow.utils.GHFDB.get_queryset

```{autodoc2-docstring} heat_flow.utils.GHFDB.get_queryset
```

````

````{py:method} to_dataframe(fieldnames=(), verbose=False, index=None, coerce_float=False, datetime_index=False)
:canonical: heat_flow.utils.GHFDB.to_dataframe

```{autodoc2-docstring} heat_flow.utils.GHFDB.to_dataframe
```

````

`````
