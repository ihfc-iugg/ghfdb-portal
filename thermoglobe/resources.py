from .models import Site, Conductivity, Interval, HeatGeneration, Temperature, Correction, Publication
# from publications.models import Operator
from import_export.fields import Field
from import_export.widgets import FloatWidget, CharWidget, IntegerWidget, BooleanWidget, ForeignKeyWidget, DecimalWidget
import time
from import_export import resources
from . import widgets, import_choices as choices
import sys
import bibtexparser as bib
from thermoglobe.utils import age_range
from import_export.instance_loaders import BaseInstanceLoader
from django.db import IntegrityError
from django import VERSION
from import_export.instance_loaders import ModelInstanceLoader
from django.utils.html import mark_safe
from tqdm import tqdm

class CustomInstanceLoader(ModelInstanceLoader):
    """
    Instance loader for Django model.

    Lookup for model instance by ``import_id_fields``.
    """
    def get_queryset(self):
        return self.resource.get_queryset()

    def get_instance(self, row):
        try:
            params = {}
            for key in self.resource.get_import_id_fields():
                field = self.resource.fields[key]
                params[field.attribute] = field.clean(row)
            if params:
                return self.get_queryset().get(**params)
            else:
                return None
        except self.resource._meta.model.DoesNotExist:
            return None

def fix_age(row):
    # handles the case where a geochronological or stratigraphic age is given
    age_values = ['age','age_min','age_max']

    for age in age_values:
        # if age is supplied as a string, check to see if it matches with known geological ages
        if not row.get(age):
            continue
        try: 
            row[age] = float(row[age])
        except ValueError:
            found_age_range = age_range(row[age])
            if not found_age_range:
                row[age] = ''
                continue
            if 'min' in age:
                row[age] = found_age_range[0]
            elif 'max' in age:
                row[age] = found_age_range[1]
            else:
                row['age'] = ''
                row['age_min'],row['age_max'] = found_age_range
            if not row.get('age_method'):
                row['age_method'] = 'Calculated from stratigraphic age'
        except TypeError:
            # Do nothing if none type
            pass
        # finally:

    return row

def fix_depth(row):
    if row.get('depth_min') and row.get('depth_max'):
        if float(row['depth_min']) == float(row['depth_max']) == 0:
            row['depth_min'] = None
            row['depth_max'] = None
    return row

def format_coordinates(row):
    """The point of this function is to convert coordinates to a string formatted number no longer than 5 decimals places. 
    This combats rounding errors when converting from degrees:minute:seconds to decimal degrees. 
    """
    for i in ['latitude','longitude']:
        val = row.get(i).split('.')[-1]
        if len(val) > 5:
            formatted = format(float(row[i]),'.5f')
            row[i] = formatted

    return row

class ResourceMixin(resources.ModelResource):
    # ref_dict = get_references().entries_dict

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Start import timer and initialize count for progress bar"""
        self.pbar = tqdm(total=len(dataset))

    def before_import_row(self,row=None,**kwargs):
        # add the current user to the row
        if kwargs.get('user'):
            row['added_by'] = kwargs['user']._wrapped.username

        row = format_coordinates(row) # converts lat and lon to 5 decimal place string
        # row = fix_age(row) # convert any geo or stratigraphic ages to float values
        row = fix_depth(row) #fix depths reported as min = 0 and max = 0
        row['save_temp'] = True

    def before_save_instance(self, instance, using_transactions, dry_run):
        """
        Override to add additional logic. Does nothing by default.
        """
        pass

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        """
        Takes care of saving the object to the database.

        Keep in mind that this is done by calling ``instance.save()``, so
        objects are not created in bulk!
        """
        self.before_save_instance(instance, using_transactions, dry_run)
        if not using_transactions and dry_run:
            # we don't have transactions and we want to do a dry_run
            pass
        else:
            instance.save()
        self.after_save_instance(instance, using_transactions, dry_run)

    def after_save_instance(self,instance, using_transactions, dry_run):
        if getattr(instance,'site',False):
            reference = getattr(instance,'reference',False)
            if reference:
                # If theres a reference, add it to the site__reference field
                instance.site.reference.add(reference)   
            instance.site.save() #required to save relational fields to site obj
        # pass

    def after_import_row(self, row, row_result, **kwargs):
        """ Updates the progress bar"""
        self.pbar.update(1)

    def after_import(self, dataset,result,using_transactions, dry_run,**kwargs):
        self.clean_result(result)
        print('Import Summary:')
        for key, count in result.totals.items():
            if count:
                print('\t',key,': ',count)

    def clean_result(self,result):
        """Cleans up the result preview"""
        # find the columns that do not contain any data and store the index
        remove_these = []
        if result.has_validation_errors():
            # loop through each column of the result
            for i, header in enumerate(result.diff_headers.copy()):
                has_data = False
                # look at each value in the column
                for row in result.invalid_rows: 
                    if row.values:
                        # Applies a html background to field specific errors to help user identify issues
                        if header in row.field_specific_errors.keys():
                            row.values = list(row.values)
                            row.values[i] = mark_safe('<span class="bg-danger">{}</span>'.format(row.values[i]))
                        # if a values is found in this column then mark it as containing data
                        if row.values[i] and row.values[i] != '---':
                            has_data = True
                            break
                # if no data was found in the column, delete it
                if not has_data:
                    remove_these.append(i)
                    # result.diff_headers.remove(header)

            # result.diff_headers.pop()
            for i in sorted(remove_these,reverse=True):
                result.diff_headers.pop(i)
                for row in result.invalid_rows:

                    row.values = list(row.values)
                    row.values.pop(i)
                    # row.values.pop()


        else:
            for i, header in enumerate(result.diff_headers.copy()):
                has_data = False
                for row in result.rows: 
                    if row.diff:
                        if row.diff[i]:
                            has_data = True
                            break
                if not has_data:
                    remove_these.append(i)
 
            for i in sorted(remove_these,reverse=True):
                result.diff_headers.pop(i)
                for row in result.rows:
                # remove stored indices from each row of the result
                    if row.diff:
                        del row.diff[i]


        result.diff_headers = [h.replace('_',' ').capitalize() for h in result.diff_headers]

class SiteMixin(ResourceMixin):
    global_saves_null=True

    # needs to be before the site property fields below so that a reference is saved
    reference = Field(attribute='reference',
            column_name='reference', 
            widget=widgets.PublicationWidget(Publication, field='reference',
            # reference_dict=ResourceMixin.ref_dict
            ))

    site_name = Field(attribute='site',column_name='site_name',
        widget=widgets.SiteWidget(Site,
            field='site_name',
            render_field='site_name',
            id_fields=['latitude','longitude','site_name'],
            ))

    latitude = Field(attribute='site__latitude',widget=DecimalWidget(),readonly=True)
    longitude = Field(attribute='site__longitude',widget=DecimalWidget(),readonly=True)
    elevation = Field(attribute='site__elevation',widget=FloatWidget(),readonly=True)
    tilt = Field(attribute='site__tilt', widget=FloatWidget(),readonly=True)

    cruise = Field(attribute='site__cruise')
    well_depth = Field(attribute='site__well_depth',widget=FloatWidget())
    #geology information
    sediment_thickness = Field(attribute='site__sediment_thickness',saves_null_values=global_saves_null,widget=FloatWidget())
    sediment_thickness_type = Field(attribute='site__sediment_thickness_type')

    crustal_thickness = Field(attribute='site__crustal_thickness',saves_null_values=global_saves_null,widget=FloatWidget())

    seamount_distance = Field(attribute='site__seamount_distance',widget=FloatWidget(),saves_null_values=global_saves_null)

    bottom_water_temp = Field(attribute='site__bottom_water_temp', 
                            widget=widgets.SitePropertyWidget(Temperature,
                            field='value',
                            exclude='lithology',
                            id_fields = ['site','value','reference'],
                            required_fields=['value'],
                            # specify the column to be mapped to each model field
                            varmap={'bottom_water_temp':'value',
                                    'temperature_method':'method',
                                    'reference':'reference'}))
    surface_temp = Field(attribute='site__surface_temp', 
                            widget=widgets.SitePropertyWidget(Temperature,
                                field='value',
                                exclude='lithology',
                                id_fields = ['site','value','reference'],
                                required_fields=['value'],
                                varmap={'surface_temp':'value',
                                        'temperature_method':'method',
                                        'reference':'reference'}))

    tectonothermal_min = Field(attribute='site__tectonothermal_min',widget=FloatWidget(),saves_null_values=global_saves_null)
    tectonothermal_max = Field(attribute='site__tectonothermal_max',widget=FloatWidget(),saves_null_values=global_saves_null)
    juvenile_age_min = Field(attribute='site__juvenile_age_min',widget=FloatWidget(),saves_null_values=global_saves_null)
    juvenile_age_max = Field(attribute='site__juvenile_age_max',widget=FloatWidget(),saves_null_values=global_saves_null)

    def __init__(self,bibtex=None):
        self.bibtex = bibtex

class CorrectionsMixin(resources.ModelResource):
    """Slightly annoying having to type these all out but it needs to be done to make sure the column names are output as expected. Ordering is done via the HEAT_FLOW_FIELDS variable in thermoglobe.choices.
    """

    # corrections are actually imported on this field
    climate_correction = Field(attribute='corrections',widget=widgets.CorrectionsWidget(field="climate"))

    # the following fields are for output puposes only
    climate_flag = Field(attribute='corrections__climate_flag',widget=BooleanWidget(),readonly=True)

    topographic_correction = Field(attribute='corrections__topographic',widget=FloatWidget(),readonly=True)
    topographic_flag = Field(attribute='corrections__topographic_flag',widget=BooleanWidget(),readonly=True)

    refraction_correction = Field(attribute='corrections__refraction',widget=FloatWidget(),readonly=True)
    refraction_flag = Field(attribute='corrections__refraction_flag',widget=BooleanWidget(),readonly=True)
    
    sed_erosion_correction = Field(attribute='corrections__sed_erosion',widget=FloatWidget(),readonly=True)
    sed_erosion_flag = Field(attribute='corrections__sed_erosion_flag',widget=BooleanWidget(),readonly=True)
    
    fluid_correction = Field(attribute='corrections__fluid',widget=FloatWidget(),readonly=True)
    fluid_flag = Field(attribute='corrections__fluid_flag',widget=BooleanWidget(),readonly=True)
    
    bottom_water_variation_correction = Field(attribute='corrections__bottom_water_variation',widget=FloatWidget(),readonly=True)
    bottom_water_variation_flag = Field(attribute='corrections__bottom_water_variation_flag',widget=BooleanWidget(),readonly=True)
        
    compaction_correction = Field(attribute='corrections__compaction',widget=FloatWidget(),readonly=True)
    compaction_flag = Field(attribute='corrections__compaction_flag',widget=BooleanWidget(),readonly=True)
        
    other_correction = Field(attribute='corrections__other',widget=FloatWidget(),readonly=True)
    other_flag = Field(attribute='corrections__other_flag',widget=BooleanWidget(),readonly=True)
    other_type = Field(attribute='corrections__other_type',readonly=True)

class HeatFlowResource(CorrectionsMixin,SiteMixin):
    global_saves_null=True

    class Meta:
        model = Interval
        import_id_fields = ['site_name','depth_min','depth_max','reference','heat_flow_corrected','heat_flow_uncorrected']
        skip_unchanged = True

        fields = ['reference'] + choices.HEAT_FLOW_EXPORT

        export_order = fields.copy()
        instance_loader_class = CustomInstanceLoader
        # use_bulk = True
        # skip_diff = True

    def import_obj(self, obj, data, dry_run):
        """
        Traverses every field in this Resource and calls
        :meth:`~import_export.resources.Resource.import_field`. If
        ``import_field()`` results in a ``ValueError`` being raised for
        one of more fields, those errors are captured and reraised as a single,
        multi-field ValidationError."""
        errors = {}
        for field in self.get_import_fields():
            if isinstance(field.widget, widgets.ManyToManyWidget):
                continue
            try:
                self.import_field(field, obj, data)
            except ValueError as e:
                errors[field.attribute] = ValidationError(
                    force_str(e), code="invalid")
        if errors:
            raise ValidationError(errors)

    def after_import_row(self,row,row_result,**kwargs):
        super().after_import_row(row,row_result,**kwargs)
        # decided not to associate heat generation with heat flow. However many uploads will contain a HG value. This will throw and error if listed as a field so need to put it here to save it to the site.
        # hg_id, hg_fields = widgets.site_property(
        #         model=HeatGeneration,
        #         row=row,
        #         exclude=[],
        #         id_fields = ['site','value','reference','depth'],
        #         required_fields=['value'],
        #         varmap={'heat_gen':'value',
        #                 'heat_gen_unc': 'uncertainty',
        #                 'number_of_heat_gen': 'number_of_measurements',
        #                 'heat_gen_method':'method',}
        #                 )
        # if hg_id:
        #     HeatGeneration.objects.update_or_create(**hg_id,defaults=hg_fields)

    def after_save_instance(self,instance, using_transactions, dry_run):   
        super().after_save_instance(instance,using_transactions,dry_run)
        if getattr(instance,'corrections',False):
            instance.corrections.save()

def init_site_instance(row,id_fields):
    params = {k:row[k] for k in id_fields}
    if not params['latitude'] or not params['longitude']:
        return None
    return Site.objects.get_or_create(**params)[0]

def init_reference_instance(row, bibtex):
    if bibtex:
        # If an actual bibtex string is provided
        try:
            entry = bib.loads(bibtex).entries[0]
        except IndexError:
            pass
        else:
            bib_id = entry.get('ID','')
            ref, created = Publication.objects.get_or_create(bib_id=bib_id)
            if created:
                # save new bibtex entry to bibtex file on server
                pass
            else:
                # save the existing reference entry with the new bibtex file
                ref.bibtex = bibtex
                ref.save()
                row['bibtex'] = ref.bib_id

            return ref
    else:
        # # If a bib ID is supplied, check if an entry already exists and retrieve it
        # try:
        #     ref = Publication.objects.get(bib_id=row['reference'])
        # except Publication.DoesNotExist:
        #     db = BibDatabase()
        #     try:
        #         db.entries = [self.ref_dict[row['reference']]]
        #     except KeyError:
        #         ref = Publication.objects.create(bib_id=row['bibtex'])
        #     else:
        #         ref = Publication.objects.create(bibtex=bib.dumps(db))
        # finally:
        #     return ref
        pass

class ConductivityResource(SiteMixin):
    global_saves_null = False
    conductivity = Field(attribute='conductivity',
            column_name='conductivity',
            widget=FloatWidget())
    rock_group = Field('rock_group',widget=widgets.ChoiceWidget(choices=choices.ROCK_GROUPS))
    rock_origin = Field('rock_origin',widget=widgets.ChoiceWidget(choices=choices.ROCK_ORIGIN))

    class Meta:
        model = Conductivity
        fields = choices.CONDUCTIVITY_EXPORT
        export_order = fields.copy()
        import_id_fields = ['site_name','depth','conductivity','log_id','reference']

    def import_field(self, field, obj, data, is_m2m=False):
        """
        Calls :meth:`import_export.fields.Field.save` if ``Field.attribute``
        and ``Field.column_name`` are found in ``data``.
        """
        if field.attribute and field.column_name in data:
            field.save(obj, data, is_m2m)

class HeatGenResource(SiteMixin):
    global_saves_null = False
    heat_generation = Field(attribute='heat_generation',
            column_name='heat_generation',
            widget=FloatWidget())
    rock_group = Field(widget=widgets.ChoiceWidget(choices=choices.ROCK_GROUPS))
    rock_origin = Field(widget=widgets.ChoiceWidget(choices=choices.ROCK_ORIGIN))

    class Meta:
        model = HeatGeneration
        fields = choices.HEAT_GEN_EXPORT
        export_order = fields.copy()
        import_id_fields = ['site_name','sample_name','depth','reference']

class TempResource(SiteMixin):
    temperature = Field(attribute='temperature',
            column_name='temperature',
            widget=FloatWidget())

    class Meta:
        model = Temperature
        fields = choices.TEMPERATURE_EXPORT
        export_order = fields.copy()
        import_id_fields = ['site_name','depth','temperature','log_id','reference']



