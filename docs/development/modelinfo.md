# heat_flow.HeatFlowSite

## Model Info

| Key | Value |
|---|-----|
| Model Name | HeatFlowSite |
| Verbose Name | Heat Flow Site |
| Verbose Name Plural | Heat Flow Sites |
| Docstring | <p>HeatFlowSite(polymorphic\_ctype, image, name, created, modified, options, dataset, id, local\_id, status, location, sample\_ptr, azimuth, inclination, length, top, bottom, vertical\_depth, vertical\_datum, type, elevation\_datum, elevation, environment, explo\_method, explo\_purpose)</p> |
| Is Abstract | False |
| Is Proxy | False |
| Is Managed | True |
| Ordering | [] |
| Permissions | [] |
| Default Permissions | ('add', 'change', 'delete', 'view') |
| Indexes | [] |
| Constraints | [] |
| Database Table | heat_flow_heatflowsite |
| Database Table Comment | A geographic location where heat flow data has been collected. Multiple heat flow measurements may be associated with a single site. |
| Base Manager | None |
| Default Manager | None |
| File | C:\Users\jennings\Documents\repos\global-heat-flow-database\heat_flow\models\samples.py |
| Starting Line Number | 19 |
| Method Resolution Order | (<class 'heat_flow.models.samples.HeatFlowSite'>, <class 'fairdm_geo.models.features.sites.Borehole'>, <class 'fairdm_geo.models.samples.intervals.GeoDepthInterval'>, <class 'fairdm_geo.models.samples.intervals.VerticalDepthInterval'>, <class 'fairdm_geo.models.samples.intervals.VerticalInterval'>, <class 'fairdm_geo.models.samples.generic.GenericHole'>, <class 'fairdm_geo.models.features.sites.SamplingLocation'>, <class 'fairdm_geo.models.samples.generic.GenericEarthSample'>, <class 'fairdm.core.models.sample.Sample'>, <class 'polymorphic.models.PolymorphicModel'>, <class 'fairdm.core.models.abstract.BaseModel'>, <class 'django.db.models.base.Model'>, <class 'django.db.models.utils.AltersData'>, <class 'object'>) |

## Fields

| Field Name | Field Type | Database Column | Database Type | Verbose Name |
|----------|----------|---------------|-------------|------------|
| `HeatFlowSite_age+` | ManyToOneRel |  | varchar(23) |  |
| `HeatFlowSite_lithology+` | ManyToOneRel |  | varchar(23) |  |
| `HeatFlowSite_stratigraphy+` | ManyToOneRel |  | varchar(23) |  |
| `Sample_keywords+` | ManyToOneRel |  | varchar(23) |  |
| `action_object_actions` | GenericRelation | None | None | action object actions |
| `actor_actions` | GenericRelation | None | None | actor actions |
| `age` | ManyToManyField | age | through heat_flow.HeatFlowSite_age | geologic age |
| `azimuth` | QuantityField | azimuth | real | azimuth |
| `bottom` | QuantityField | bottom | real | bottom |
| `contributors` | GenericRelation | None | None | contributors |
| `contributors` | GenericRelation | None | None | contributors |
| `contributors` | GenericRelation | None | None | contributors |
| `created` | DateTimeField | created | datetime | Created |
| `dataset` | ForeignKey | dataset_id | varchar(23) | dataset |
| `dates` | ManyToOneRel |  | varchar(23) |  |
| `descriptions` | ManyToOneRel |  | varchar(23) |  |
| `elevation` | QuantityField | elevation | real | elevation |
| `elevation_datum` | ConceptField | elevation_datum | varchar(7) |  |
| `environment` | ConceptField | environment | varchar(20) | basic geographical environment |
| `explo_method` | ConceptField | explo_method | varchar(16) | exploration method |
| `explo_purpose` | ConceptField | explo_purpose | varchar(19) | exploration purpose |
| `id (pk)` | ShortUUIDField | id | varchar(23) | UUID |
| `identifiers` | ManyToOneRel |  | varchar(23) |  |
| `image` | ThumbnailerImageField | image | varchar(100) | image |
| `inclination` | QuantityField | inclination | real | inclination |
| `keywords` | ManyToManyField | keywords | through fairdm_core.Sample_keywords | keywords |
| `length` | QuantityField | length | real | hole length |
| `lithology` | ManyToManyField | lithology | through heat_flow.HeatFlowSite_lithology | lithology |
| `local_id` | CharField | local_id | varchar(255) | Local ID |
| `location` | ForeignKey | location_id | bigint | location |
| `measurements` | ManyToOneRel |  | varchar(23) |  |
| `modified` | DateTimeField | modified | datetime | Modified |
| `name` | CharField | name | varchar(255) | name |
| `options` | JSONField | options | text | options |
| `polymorphic_ctype` | ForeignKey | polymorphic_ctype_id | integer | polymorphic ctype |
| `related_samples` | ManyToOneRel |  | varchar(23) |  |
| `related_to` | ManyToOneRel |  | varchar(23) |  |
| `sample_ptr (pk)` | OneToOneField | sample_ptr_id | varchar(23) | sample ptr |
| `status` | ConceptField | status | varchar(8) | status |
| `stratigraphy` | ManyToManyField | stratigraphy | through heat_flow.HeatFlowSite_stratigraphy | stratigraphy |
| `tagged_items` | GenericRelation | None | None | tagged items |
| `tagged_items` | GenericRelation | None | None | tagged items |
| `tagged_items` | GenericRelation | None | None | tagged items |
| `tags` | TaggableManager | tags | through generic.TaggedItem | Tags |
| `target_actions` | GenericRelation | None | None | target actions |
| `top` | QuantityField | top | real | top |
| `type` | ConceptField | type | varchar(33) | type |
| `vertical_datum` | CharField | vertical_datum | varchar(255) | vertical datum |
| `vertical_depth` | QuantityField | vertical_depth | real | vertical depth |

## Relations

| Field Name | Field Type | Database Column | Database Type | Related Model | Related Name |
|----------|----------|---------------|-------------|-------------|------------|
| `action_object_actions` | GenericRelation | None | None | actstream.Action | actions_with_heat_flow_heatflowsite_as_action_object |
| `actor_actions` | GenericRelation | None | None | actstream.Action | actions_with_heat_flow_heatflowsite_as_actor |
| `age` | ManyToManyField | age | through heat_flow.HeatFlowSite_age | geologic_time.GeologicalTimescale | heatflowsite_set |
| `contributors` | GenericRelation | None | None | contributors.Contribution | + |
| `contributors` | GenericRelation | None | None | contributors.Contribution | + |
| `contributors` | GenericRelation | None | None | contributors.Contribution | + |
| `dataset` | ForeignKey | dataset_id | varchar(23) | fairdm_core.Dataset | samples |
| `keywords` | ManyToManyField | keywords | through fairdm_core.Sample_keywords | research_vocabs.Concept | samples |
| `lithology` | ManyToManyField | lithology | through heat_flow.HeatFlowSite_lithology | lithology.SimpleLithology | heatflowsite_set |
| `location` | ForeignKey | location_id | bigint | fairdm_location.Point | samples |
| `polymorphic_ctype` | ForeignKey | polymorphic_ctype_id | integer | contenttypes.ContentType | polymorphic_fairdm_core.sample_set+ |
| `sample_ptr (pk)` | OneToOneField | sample_ptr_id | varchar(23) | fairdm_core.Sample | heatflowsite_set |
| `stratigraphy` | ManyToManyField | stratigraphy | through heat_flow.HeatFlowSite_stratigraphy | stratigraphy.StratigraphicUnit | heatflowsite_set |
| `tagged_items` | GenericRelation | None | None | generic.TaggedItem | + |
| `tagged_items` | GenericRelation | None | None | generic.TaggedItem | + |
| `tagged_items` | GenericRelation | None | None | generic.TaggedItem | + |
| `tags` | TaggableManager | tags | through generic.TaggedItem | taggit.Tag | heatflowsite_set |
| `target_actions` | GenericRelation | None | None | actstream.Action | actions_with_heat_flow_heatflowsite_as_target |

fields_reverse_relation=[FieldReverseRelation(name='measurements', field_type='ManyToOneRel', field_db_type='varchar(23)', related_model='fairdm_core.Measurement', field_name_on_related_model='sample', field_type_on_related_model='ForeignKey'), FieldReverseRelation(name='Sample_keywords+ (no reverse relation allowed)', field_type='ManyToOneRel', field_db_type='varchar(23)', related_model='fairdm_core.Sample_keywords', field_name_on_related_model='sample', field_type_on_related_model='ForeignKey'), FieldReverseRelation(name='descriptions', field_type='ManyToOneRel', field_db_type='varchar(23)', related_model='fairdm_core.SampleDescription', field_name_on_related_model='related', field_type_on_related_model='ForeignKey'), FieldReverseRelation(name='dates', field_type='ManyToOneRel', field_db_type='varchar(23)', related_model='fairdm_core.SampleDate', field_name_on_related_model='related', field_type_on_related_model='ForeignKey'), FieldReverseRelation(name='identifiers', field_type='ManyToOneRel', field_db_type='varchar(23)', related_model='fairdm_core.SampleIdentifier', field_name_on_related_model='related', field_type_on_related_model='ForeignKey'), FieldReverseRelation(name='related_samples', field_type='ManyToOneRel', field_db_type='varchar(23)', related_model='fairdm_core.SampleRelation', field_name_on_related_model='source', field_type_on_related_model='ForeignKey'), FieldReverseRelation(name='related_to', field_type='ManyToOneRel', field_db_type='varchar(23)', related_model='fairdm_core.SampleRelation', field_name_on_related_model='target', field_type_on_related_model='ForeignKey'), FieldReverseRelation(name='HeatFlowSite_lithology+ (no reverse relation allowed)', field_type='ManyToOneRel', field_db_type='varchar(23)', related_model='heat_flow.HeatFlowSite_lithology', field_name_on_related_model='heatflowsite', field_type_on_related_model='ForeignKey'), FieldReverseRelation(name='HeatFlowSite_age+ (no reverse relation allowed)', field_type='ManyToOneRel', field_db_type='varchar(23)', related_model='heat_flow.HeatFlowSite_age', field_name_on_related_model='heatflowsite', field_type_on_related_model='ForeignKey'), FieldReverseRelation(name='HeatFlowSite_stratigraphy+ (no reverse relation allowed)', field_type='ManyToOneRel', field_db_type='varchar(23)', related_model='heat_flow.HeatFlowSite_stratigraphy', field_name_on_related_model='heatflowsite', field_type_on_related_model='ForeignKey')]

## Reverse Relations

| Field Name | Field Type | Database Type | Related Model | Field Name on Related Model | Field Type on Related Model |
|----------|----------|-------------|-------------|---------------------------|---------------------------|
| `HeatFlowSite_age+ (no reverse relation allowed)` | ManyToOneRel | varchar(23) | heat_flow.HeatFlowSite_age | heatflowsite | ForeignKey |
| `HeatFlowSite_lithology+ (no reverse relation allowed)` | ManyToOneRel | varchar(23) | heat_flow.HeatFlowSite_lithology | heatflowsite | ForeignKey |
| `HeatFlowSite_stratigraphy+ (no reverse relation allowed)` | ManyToOneRel | varchar(23) | heat_flow.HeatFlowSite_stratigraphy | heatflowsite | ForeignKey |
| `Sample_keywords+ (no reverse relation allowed)` | ManyToOneRel | varchar(23) | fairdm_core.Sample_keywords | sample | ForeignKey |
| `dates` | ManyToOneRel | varchar(23) | fairdm_core.SampleDate | related | ForeignKey |
| `descriptions` | ManyToOneRel | varchar(23) | fairdm_core.SampleDescription | related | ForeignKey |
| `identifiers` | ManyToOneRel | varchar(23) | fairdm_core.SampleIdentifier | related | ForeignKey |
| `measurements` | ManyToOneRel | varchar(23) | fairdm_core.Measurement | sample | ForeignKey |
| `related_samples` | ManyToOneRel | varchar(23) | fairdm_core.SampleRelation | source | ForeignKey |
| `related_to` | ManyToOneRel | varchar(23) | fairdm_core.SampleRelation | target | ForeignKey |

## Methods

### Other Methods

| Method Name | Signature | Docstring | File | Line Number |
|-----------|---------|---------|----|-----------|
| `add_contributor` | `(self, contributor, with_roles=None)` | <p>Adds a new contributor the object with the specified roles.</p> | repos\fairdm\fairdm\core\models\abstract.py | 69 |
| `base_class` | `()` |  | repos\fairdm\fairdm\core\models\sample.py | 90 |
| `get_abstract` | `(self)` | <p>Returns the abstract description of the project.</p> | repos\fairdm\fairdm\core\models\abstract.py | 95 |
| `get_api_url` | `(self)` |  | repos\fairdm\fairdm\core\models\abstract.py | 66 |
| `get_dates_in_order` | `(self)` | <p>Returns the dates in the correct order specified by the DATE\_TYPES vocabulary.</p> | repos\fairdm\fairdm\core\models\abstract.py | 89 |
| `get_descriptions_in_order` | `(self)` | <p>Returns the descriptions in the correct order specified by the DESCRIPTION\_TYPES vocabulary.</p> | repos\fairdm\fairdm\core\models\abstract.py | 83 |
| `get_elevation_datum_display` | `(self, *, field=<research_vocabs.fields.ConceptField: elevation_datum>)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `get_environment_display` | `(self, *, field=<research_vocabs.fields.ConceptField: environment>)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `get_explo_method_display` | `(self, *, field=<research_vocabs.fields.ConceptField: explo_method>)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `get_explo_purpose_display` | `(self, *, field=<research_vocabs.fields.ConceptField: explo_purpose>)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `get_meta_description` | `(self)` |  | repos\fairdm\fairdm\core\models\abstract.py | 102 |
| `get_next_by_created` | `(self, *, field=<django.db.models.fields.DateTimeField: created>, is_next=True, **kwargs)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `get_next_by_modified` | `(self, *, field=<django.db.models.fields.DateTimeField: modified>, is_next=True, **kwargs)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `get_previous_by_created` | `(self, *, field=<django.db.models.fields.DateTimeField: created>, is_next=False, **kwargs)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `get_previous_by_modified` | `(self, *, field=<django.db.models.fields.DateTimeField: modified>, is_next=False, **kwargs)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `get_real_concrete_instance_class` | `(self)` |  | virtualenvs\global-heat-flow-database-GuOryC2t-py3.11\Lib\site-packages\polymorphic\models.py | 141 |
| `get_real_concrete_instance_class_id` | `(self)` |  | virtualenvs\global-heat-flow-database-GuOryC2t-py3.11\Lib\site-packages\polymorphic\models.py | 131 |
| `get_real_instance` | `(self)` | <p>Upcast an object to it's actual type.</p><p>If a non-polymorphic manager (like base\_objects) has been used to<br>retrieve objects, then the complete object with it's real class/type<br>and all fields may be retrieved with this method.</p><p>.. note::<br>    Each method call executes one db query (if necessary).<br>    Use the :meth:`~polymorphic.managers.PolymorphicQuerySet.get\_real\_instances`<br>    to upcast a complete list in a single efficient query.</p> | virtualenvs\global-heat-flow-database-GuOryC2t-py3.11\Lib\site-packages\polymorphic\models.py | 151 |
| `get_real_instance_class` | `(self)` | <p>Return the actual model type of the object.</p><p>If a non-polymorphic manager (like base\_objects) has been used to<br>retrieve objects, then the real class/type of these objects may be<br>determined using this method.</p> | virtualenvs\global-heat-flow-database-GuOryC2t-py3.11\Lib\site-packages\polymorphic\models.py | 89 |
| `get_status_display` | `(self, *, field=<research_vocabs.fields.ConceptField: status>)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `get_template_name` | `(self)` |  | repos\fairdm\fairdm\core\models\sample.py | 98 |
| `get_type_display` | `(self, *, field=<research_vocabs.fields.ConceptField: type>)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `get_vertical_datum_display` | `(self, *, field=<django.db.models.fields.CharField: vertical_datum>)` |  | Local\Programs\Python\Python311\Lib\functools.py | 386 |
| `is_contributor` | `(self, user)` | <p>Returns true if the user is a contributor.</p> | repos\fairdm\fairdm\core\models\abstract.py | 78 |
| `pre_save_polymorphic` | `(self, using='default')` | <p>Make sure the ``polymorphic\_ctype`` value is correctly set on this model.</p> | virtualenvs\global-heat-flow-database-GuOryC2t-py3.11\Lib\site-packages\polymorphic\models.py | 65 |
| `total_depth_MD` | `(self)` |  | Documents\repos\global-heat-flow-database\heat_flow\models\samples.py | 44 |
| `total_depth_TVD` | `(self)` |  | Documents\repos\global-heat-flow-database\heat_flow\models\samples.py | 47 |
| `translate_polymorphic_Q_object` | `(q)` |  | virtualenvs\global-heat-flow-database-GuOryC2t-py3.11\Lib\site-packages\polymorphic\models.py | 61 |
| `verbose_name` | `(self)` |  | repos\fairdm\fairdm\core\models\abstract.py | 115 |
| `verbose_name_plural` | `(self)` |  | repos\fairdm\fairdm\core\models\abstract.py | 118 |


### Private Methods

| Method Name | Signature | Docstring | File | Line Number |
|-----------|---------|---------|----|-----------|
| `_get_inheritance_relation_fields_and_models` | `(self)` | <p>helper function for \_\_init\_\_:<br>determine names of all Django inheritance accessor member functions for type(self)</p> | virtualenvs\global-heat-flow-database-GuOryC2t-py3.11\Lib\site-packages\polymorphic\models.py | 217 |


### Dunder Methods

| Method Name | Signature | Docstring | File | Line Number |
|-----------|---------|---------|----|-----------|
| `__class__` | `(model_name, bases, attrs, **kwargs)` | <p>Manager inheritance is a pretty complex topic which may need<br>more thought regarding how this should be handled for polymorphic<br>models.</p><p>In any case, we probably should propagate 'objects' and 'base\_objects'<br>from PolymorphicModel to every subclass. We also want to somehow<br>inherit/propagate \_default\_manager as well, as it needs to be polymorphic.</p><p>The current implementation below is an experiment to solve this<br>problem with a very simplistic approach: We unconditionally<br>inherit/propagate any and all managers (using \_copy\_to\_model),<br>as long as they are defined on polymorphic models<br>(the others are left alone).</p><p>Like Django ModelBase, we special-case \_default\_manager:<br>if there are any user-defined managers, it is set to the first of these.</p><p>We also require that \_default\_manager as well as any user defined<br>polymorphic managers produce querysets that are derived from<br>PolymorphicQuerySet.</p> | virtualenvs\global-heat-flow-database-GuOryC2t-py3.11\Lib\site-packages\polymorphic\base.py | 30 |
| `__delattr__` | `(self, name, /)` | <p>Implement delattr(self, name).</p> |  |  |
| `__dir__` | `(self, /)` | <p>Default dir() implementation.</p> |  |  |
| `__eq__` | `(self, other)` | <p>Return self==value.</p> | Lib\site-packages\django\db\models\base.py | 593 |
| `__format__` | `(self, format_spec, /)` | <p>Default object formatter.</p> |  |  |
| `__ge__` | `(self, value, /)` | <p>Return self>=value.</p> |  |  |
| `__getattribute__` | `(self, name, /)` | <p>Return getattr(self, name).</p> |  |  |
| `__getstate__` | `(self)` | <p>Hook to allow choosing the attributes to pickle.</p> | Lib\site-packages\django\db\models\base.py | 614 |
| `__gt__` | `(self, value, /)` | <p>Return self>value.</p> |  |  |
| `__hash__` | `(self)` | <p>Return hash(self).</p> | Lib\site-packages\django\db\models\base.py | 603 |
| `__init__` | `(self, *args, **kwargs)` | <p>Replace Django's inheritance accessor member functions for our model<br>(self.\_\_class\_\_) with our own versions.<br>We monkey patch them until a patch can be added to Django<br>(which would probably be very small and make all of this obsolete).</p><p>If we have inheritance of the form ModelA -> ModelB ->ModelC then<br>Django creates accessors like this:<br>- ModelA: modelb<br>- ModelB: modela\_ptr, modelb, modelc<br>- ModelC: modela\_ptr, modelb, modelb\_ptr, modelc</p><p>These accessors allow Django (and everyone else) to travel up and down<br>the inheritance tree for the db object at hand.</p><p>The original Django accessors use our polymorphic manager.<br>But they should not. So we replace them with our own accessors that use<br>our appropriate base\_objects manager.</p> | virtualenvs\global-heat-flow-database-GuOryC2t-py3.11\Lib\site-packages\polymorphic\models.py | 169 |
| `__init_subclass__` | `()` | <p>This method is called when a class is subclassed.</p><p>The default implementation does nothing. It may be<br>overridden to extend subclasses.</p> | repos\fairdm\fairdm\core\models\sample.py | 87 |
| `__le__` | `(self, value, /)` | <p>Return self<=value.</p> |  |  |
| `__lt__` | `(self, value, /)` | <p>Return self<value.</p> |  |  |
| `__ne__` | `(self, value, /)` | <p>Return self!=value.</p> |  |  |
| `__new__` | `(*args, **kwargs)` | <p>Create and return a new object.  See help(type) for accurate signature.</p> |  |  |
| `__reduce__` | `(self)` | <p>Helper for pickle.</p> | Lib\site-packages\django\db\models\base.py | 608 |
| `__reduce_ex__` | `(self, protocol, /)` | <p>Helper for pickle.</p> |  |  |
| `__repr__` | `(self)` | <p>Return repr(self).</p> | Lib\site-packages\django\db\models\base.py | 587 |
| `__setattr__` | `(self, name, value, /)` | <p>Implement setattr(self, name, value).</p> |  |  |
| `__setstate__` | `(self, state)` |  | Lib\site-packages\django\db\models\base.py | 631 |
| `__sizeof__` | `(self, /)` | <p>Size of object in memory, in bytes.</p> |  |  |
| `__str__` | `(self)` | <p>Return str(self).</p> | repos\fairdm\fairdm\core\models\abstract.py | 56 |
| `__subclasshook__` | `No signature found` | <p>Abstract classes can override this to customize issubclass().</p><p>This is invoked early on by abc.ABCMeta.\_\_subclasscheck\_\_().<br>It should return True, False or NotImplemented.  If it returns<br>NotImplemented, the normal algorithm is used.  Otherwise, it<br>overrides the normal algorithm (and the outcome is cached).</p> |  |  |


### Common Django Methods

| Method Name | Signature | Docstring | File | Line Number |
|-----------|---------|---------|----|-----------|
| `_check_column_name_clashes` | `()` |  | Lib\site-packages\django\db\models\base.py | 1956 |
| `_check_constraints` | `(databases)` |  | Lib\site-packages\django\db\models\base.py | 2421 |
| `_check_db_table_comment` | `(databases)` |  | Lib\site-packages\django\db\models\base.py | 1750 |
| `_check_default_pk` | `()` |  | Lib\site-packages\django\db\models\base.py | 1718 |
| `_check_field_name_clashes` | `()` | <p>Forbid field shadowing in multi-table inheritance.</p> | Lib\site-packages\django\db\models\base.py | 1886 |
| `_check_fields` | `(**kwargs)` | <p>Perform all field checks.</p> | Lib\site-packages\django\db\models\base.py | 1821 |
| `_check_id_field` | `()` | <p>Check if `id` field is a primary key.</p> | Lib\site-packages\django\db\models\base.py | 1867 |
| `_check_indexes` | `(databases)` | <p>Check fields, names, and conditions of indexes.</p> | Lib\site-packages\django\db\models\base.py | 2070 |
| `_check_local_fields` | `(fields, option)` |  | Lib\site-packages\django\db\models\base.py | 2161 |
| `_check_long_column_names` | `(databases)` | <p>Check that any auto-generated column names are shorter than the limits<br>for each database in which the model will be created.</p> | Lib\site-packages\django\db\models\base.py | 2325 |
| `_check_m2m_through_same_relationship` | `()` | <p>Check if no relationship model is used by more than one m2m field.</p> | Lib\site-packages\django\db\models\base.py | 1831 |
| `_check_managers` | `(**kwargs)` | <p>Perform all manager checks.</p> | Lib\site-packages\django\db\models\base.py | 1813 |
| `_check_model` | `()` |  | Lib\site-packages\django\db\models\base.py | 1800 |
| `_check_model_name_db_lookup_clashes` | `()` |  | Lib\site-packages\django\db\models\base.py | 1981 |
| `_check_ordering` | `()` | <p>Check "ordering" option -- is it a list of strings and do all fields<br>exist?</p> | Lib\site-packages\django\db\models\base.py | 2216 |
| `_check_property_name_related_field_accessor_clashes` | `()` |  | Lib\site-packages\django\db\models\base.py | 2005 |
| `_check_single_primary_key` | `()` |  | Lib\site-packages\django\db\models\base.py | 2026 |
| `_check_swappable` | `()` | <p>Check if the swapped model exists.</p> | Lib\site-packages\django\db\models\base.py | 1773 |
| `_check_unique_together` | `()` | <p>Check the value of "unique\_together" option.</p> | Lib\site-packages\django\db\models\base.py | 2040 |
| `_do_insert` | `(self, manager, using, fields, returning_fields, raw)` | <p>Do an INSERT. If returning\_fields is defined then this method should<br>return the newly created data for the model.</p> | Lib\site-packages\django\db\models\base.py | 1197 |
| `_do_update` | `(self, base_qs, using, pk_val, values, update_fields, forced_update)` | <p>Try to update the model. Return True if the model was updated (if an<br>update query was done and a matching row was found in the DB).</p> | Lib\site-packages\django\db\models\base.py | 1169 |
| `_get_FIELD_display` | `(self, field)` |  | Lib\site-packages\django\db\models\base.py | 1285 |
| `_get_expr_references` | `(expr)` |  | Lib\site-packages\django\db\models\base.py | 2405 |
| `_get_field_expression_map` | `(self, meta, exclude=None)` |  | Lib\site-packages\django\db\models\base.py | 1337 |
| `_get_next_or_previous_by_FIELD` | `(self, field, is_next, **kwargs)` |  | Lib\site-packages\django\db\models\base.py | 1293 |
| `_get_next_or_previous_in_order` | `(self, is_next)` |  | Lib\site-packages\django\db\models\base.py | 1314 |
| `_get_pk_val` | `(self, meta=None)` |  | Lib\site-packages\django\db\models\base.py | 653 |
| `_get_unique_checks` | `(self, exclude=None, include_meta_constraints=False)` | <p>Return a list of checks to perform. Since validate\_unique() could be<br>called from a ModelForm, some fields may have been excluded; we can't<br>perform a unique check on a model that is missing fields involved<br>in that check. Fields that did not validate should also be excluded,<br>but they need to be passed in via the exclude argument.</p> | Lib\site-packages\django\db\models\base.py | 1387 |
| `_parse_params` | `(self, *args, method_name, **kwargs)` |  | Lib\site-packages\django\db\models\base.py | 781 |
| `_perform_date_checks` | `(self, date_checks)` |  | Lib\site-packages\django\db\models\base.py | 1499 |
| `_perform_unique_checks` | `(self, unique_checks)` |  | Lib\site-packages\django\db\models\base.py | 1450 |
| `_prepare_related_fields_for_save` | `(self, operation_name, fields=None)` |  | Lib\site-packages\django\db\models\base.py | 1210 |
| `_save_parents` | `(self, cls, using, update_fields, force_insert, updated_parents=None)` | <p>Save all the parents of cls using values from self.</p> | Lib\site-packages\django\db\models\base.py | 1024 |
| `_save_table` | `(self, raw=False, cls=None, force_insert=False, force_update=False, using=None, update_fields=None)` | <p>Do the heavy-lifting involved in saving. Update or insert the data<br>for a single table.</p> | Lib\site-packages\django\db\models\base.py | 1071 |
| `_set_pk_val` | `(self, value)` |  | Lib\site-packages\django\db\models\base.py | 657 |
| `_validate_force_insert` | `(force_insert)` |  | Lib\site-packages\django\db\models\base.py | 932 |
| `adelete` | `(self, using=None, keep_parents=False)` |  | Lib\site-packages\django\db\models\base.py | 1277 |
| `arefresh_from_db` | `(self, using=None, fields=None, from_queryset=None)` |  | Lib\site-packages\django\db\models\base.py | 758 |
| `asave` | `(self, *args, force_insert=False, force_update=False, using=None, update_fields=None)` |  | Lib\site-packages\django\db\models\base.py | 905 |
| `check` | `(**kwargs)` |  | Lib\site-packages\django\db\models\base.py | 1681 |
| `clean` | `(self)` | <p>Hook for doing any extra model-wide validation after clean() has been<br>called on every field by self.clean\_fields. Any ValidationError raised<br>by this method will not be associated with a particular field; it will<br>have a special-case association with the field defined by NON\_FIELD\_ERRORS.</p> | Lib\site-packages\fairdm_geo\models\samples\generic.py | 52 |
| `clean_fields` | `(self, exclude=None)` | <p>Clean all fields and raise a ValidationError containing a dict<br>of all validation errors if any occur.</p> | Lib\site-packages\django\db\models\base.py | 1653 |
| `date_error_message` | `(self, lookup_type, field_name, unique_for)` |  | Lib\site-packages\django\db\models\base.py | 1530 |
| `delete` | `(self, using=None, keep_parents=False)` |  | Lib\site-packages\django\db\models\base.py | 1264 |
| `from_db` | `(db, field_names, values)` |  | Lib\site-packages\django\db\models\base.py | 574 |
| `full_clean` | `(self, exclude=None, validate_unique=True, validate_constraints=True)` | <p>Call clean\_fields(), clean(), validate\_unique(), and<br>validate\_constraints() on the model. Raise a ValidationError for any<br>errors that occur.</p> | Lib\site-packages\django\db\models\base.py | 1606 |
| `get_absolute_url` | `(self)` |  | repos\fairdm\fairdm\core\models\sample.py | 95 |
| `get_constraints` | `(self)` |  | Lib\site-packages\django\db\models\base.py | 1579 |
| `get_deferred_fields` | `(self)` | <p>Return a set containing names of deferred fields for this instance.</p> | Lib\site-packages\django\db\models\base.py | 665 |
| `prepare_database_save` | `(self, field)` |  | Lib\site-packages\django\db\models\base.py | 1355 |
| `refresh_from_db` | `(self, using=None, fields=None, from_queryset=None)` | <p>Reload field values from the database.</p><p>By default, the reloading happens from the database this instance was<br>loaded from, or by the read router if this instance wasn't loaded from<br>any database. The using parameter will override the default.</p><p>Fields can be used to specify which fields to reload. The fields<br>should be an iterable of field attnames. If fields is None, then<br>all non-deferred fields are reloaded.</p><p>When accessing deferred fields of an instance, the deferred loading<br>of the field will call this method.</p> | Lib\site-packages\django\db\models\base.py | 675 |
| `save` | `(self, *args, **kwargs)` | <p>Calls :meth:`pre\_save\_polymorphic` and saves the model.</p> | Documents\repos\global-heat-flow-database\heat_flow\models\samples.py | 55 |
| `save_base` | `(self, raw=False, force_insert=False, force_update=False, using=None, update_fields=None)` | <p>Handle the parts of saving which should be done only once per save,<br>yet need to be done in raw saves, too. This includes some sanity<br>checks and signal sending.</p><p>The 'raw' argument is telling save\_base not to save any parent<br>models and not to do any changes to the values before save. This<br>is used by fixture loading.</p> | Lib\site-packages\django\db\models\base.py | 952 |
| `serializable_value` | `(self, field_name)` | <p>Return the value of the field name for this instance. If the field is<br>a foreign key, return the id value instead of the object. If there's<br>no Field object with this name on the model, return the model<br>attribute's value.</p><p>Used to serialize a field's value (in the serializer, or form output,<br>for example). Normally, you would just access the attribute directly<br>and not use this method.</p> | Lib\site-packages\django\db\models\base.py | 763 |
| `unique_error_message` | `(self, model_class, unique_check)` |  | Lib\site-packages\django\db\models\base.py | 1547 |
| `validate_constraints` | `(self, exclude=None)` |  | Lib\site-packages\django\db\models\base.py | 1586 |
| `validate_unique` | `(self, exclude=None)` | <p>Check unique constraints on the model and raise ValidationError if any<br>failed.</p> | Lib\site-packages\django\db\models\base.py | 1371 |


## Custom Managers

### default

**Class:** `PolymorphicManager`

**Module:** `fairdm.core.managers`

*Manager for PolymorphicModel

Usually not explicitly needed, except if a custom manager or
a custom queryset class is to be used.*

#### Custom Methods

##### `get_real_instances(self, base_result_objects=None)`


##### `get_type_counts(self)`

*Returns a dictionary with counts of each polymorphic child type in the queryset.*

##### `instance_of(self, *args)`


##### `non_polymorphic(self)`


##### `not_instance_of(self, *args)`


### objects

**Class:** `PolymorphicManager`

**Module:** `fairdm.core.managers`

*Manager for PolymorphicModel

Usually not explicitly needed, except if a custom manager or
a custom queryset class is to be used.*

#### Custom Methods

##### `get_real_instances(self, base_result_objects=None)`


##### `get_type_counts(self)`

*Returns a dictionary with counts of each polymorphic child type in the queryset.*

##### `instance_of(self, *args)`


##### `non_polymorphic(self)`


##### `not_instance_of(self, *args)`


### tags

**Class:** `_TaggableManager`

**Module:** `taggit.managers`

#### Custom Methods

##### `add(self, *tags, through_defaults=None, tag_kwargs=None, **kwargs)`


##### `clear(self)`


##### `get_prefetch_queryset(self, instances, queryset=None)`


##### `get_prefetch_querysets(self, instances, querysets=None)`


##### `is_cached(self, instance)`


##### `most_common(self, min_count=None, extra_filters=None)`


##### `names(self)`


##### `remove(self, *tags)`


##### `set(self, tags, *, through_defaults=None, **kwargs)`

*Set the object's tags to the given n tags. If the clear kwarg is True
then all existing tags are removed (using `.clear()`) and the new tags
added. Otherwise, only those tags that are not present in the args are
removed and any new tags added.

Any kwarg apart from 'clear' will be passed when adding tags.*

##### `similar_objects(self)`


##### `slugs(self)`



---
