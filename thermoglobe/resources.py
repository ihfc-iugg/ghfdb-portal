from .models import Site, Conductivity, HeatFlow,ThermalGradient, HeatGeneration, Temperature, Correction
from reference.models import Reference, Operator
from geomodels.models import Basin, TectonicEnvironment, GeologicalUnit, GeologicalProvince
from import_export.fields import Field
from import_export.widgets import FloatWidget, CharWidget, IntegerWidget, BooleanWidget, ForeignKeyWidget
import time
from import_export import resources
from . import widgets, choices
import sys
import bibtexparser as bib
from geomodels.utils import age_range
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

def get_references():
    with open('reference/ThermoGlobe.bib',encoding='utf8') as bibfile:
        # required to handle certain common strings
        parser = bib.bparser.BibTexParser(common_strings=True)
        refs = bib.load(bibfile,parser=parser)
    return refs

def add_reference(entry):
    entry = bib.loads(entry)
    with open('reference/ThermoGlobe.bib',encoding='utf8',mode='a+') as bibfile:
        bibfile.write(entry)

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
    if row.get('latitude'):
        row['latitude'] = format(float(row['latitude']),'.5f')
    if row.get('longitude'):
        row['longitude'] = format(float(row['longitude']),'.5f')
    return row

class ResourceMixin(resources.ModelResource):
    ref_dict = get_references().entries_dict

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Start import timer and initialize count for progress bar"""
        self.pbar = tqdm(total=len(dataset))

    def before_import_row(self,row=None,**kwargs):
        # add the current user to the row
        if kwargs.get('user'):
            row['added_by'] = kwargs['user']._wrapped.username

        row = format_coordinates(row) # converts lat and lon to 5 decimal place string
        row = fix_age(row) # convert any geo or stratigraphic ages to float values
        row = fix_depth(row) #fix depths reported as min = 0 and max = 0
        row['save_temp'] = True

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

    site_name = Field(attribute='site',column_name='site_name',
        widget=widgets.SiteWidget(Site,
            field='site_name',
            render_field='site_name',
            id_fields=['latitude','longitude','site_name'],
            ))
 

    latitude = Field(attribute='site__latitude',widget=FloatWidget(),readonly=True)
    longitude = Field(attribute='site__longitude',widget=FloatWidget(),readonly=True)
    elevation = Field(attribute='site__elevation',widget=FloatWidget())
    dip = Field(attribute='site__dip', widget=FloatWidget())
    # operator = Field(attribute='site__operator')
    operator = Field(attribute='site__operator', saves_null_values=global_saves_null, widget=widgets.CustomFK(Operator))
    site_type = Field(attribute='site__site_type',saves_null_values=global_saves_null)
    site_status = Field(attribute='site__site_status',saves_null_values=global_saves_null)

    cruise = Field(attribute='site__cruise')
    well_depth = Field(attribute='site__well_depth',widget=FloatWidget())
    #geology information
    sediment_thickness = Field(attribute='site__sediment_thickness',saves_null_values=global_saves_null,widget=FloatWidget())
    crustal_thickness = Field(attribute='site__crustal_thickness',saves_null_values=global_saves_null,widget=FloatWidget())
    basin = Field(attribute='site__basin', saves_null_values=global_saves_null, widget=widgets.CustomFK(Basin))
    sub_basin = Field(attribute='site__sub_basin', saves_null_values=global_saves_null, widget=widgets.CustomFK(Basin))
    tectonic_environment = Field(attribute='site__tectonic_environment', saves_null_values=global_saves_null, widget=widgets.CustomFK(TectonicEnvironment))
    geological_province = Field(attribute='site__geological_province', 
            saves_null_values=global_saves_null, 
            widget=widgets.CustomFK(GeologicalProvince))
    EOH_geo_unit = Field(attribute='site__EOH_geo_unit', 
            saves_null_values=global_saves_null, 
            widget=widgets.CustomFK(GeologicalUnit))
    EOH_rock_type = Field(attribute='site__EOH_rock_type', 
            saves_null_values=global_saves_null)


    seamount_distance = Field(attribute='site__seamount_distance',widget=FloatWidget(),saves_null_values=global_saves_null)
    # outcrop_distance = Field(attribute='site__',saves_null_values=global_saves_null,widget=FloatWidget())
    ruggedness = Field(attribute='site__ruggedness', saves_null_values=global_saves_null,widget=IntegerWidget())  

    USGS_code = Field(attribute='site__USGS_code',widget=CharWidget(),saves_null_values=global_saves_null)

    bottom_hole_temp = Field(attribute='site__bottom_hole_temp', 
                            widget=widgets.SitePropertyWidget(Temperature,
                            field='value',
                            exclude='lithology',
                            id_fields = ['site','value','reference'],
                            required_fields=['value'],
                            # specify the column to be mapped to each model field
                            varmap={'bottom_hole_temp':'value',
                                    'well_depth':'depth',
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

    age_min = Field(attribute='site__age_min',widget=FloatWidget(),saves_null_values=global_saves_null)
    age_max = Field(attribute='site__age_max',widget=FloatWidget(),saves_null_values=global_saves_null)
    age_method = Field(attribute='site__age_method',saves_null_values=global_saves_null)
    tectonothermal_min = Field(attribute='site__tectonothermal_min',widget=FloatWidget(),saves_null_values=global_saves_null)
    tectonothermal_max = Field(attribute='site__tectonothermal_max',widget=FloatWidget(),saves_null_values=global_saves_null)
    juvenile_age_min = Field(attribute='site__juvenile_age_min',widget=FloatWidget(),saves_null_values=global_saves_null)
    juvenile_age_max = Field(attribute='site__juvenile_age_max',widget=FloatWidget(),saves_null_values=global_saves_null)

    def __init__(self,bibtex=None):
        self.bibtex = bibtex

class CorrectionsMixin(resources.ModelResource):
    BooleanWidget.FALSE_VALUE = ''
    has_climatic = Field(attribute='correction__has_climatic',widget=BooleanWidget(),readonly=True)
    has_topographic = Field(attribute='correction__has_topographic',widget=BooleanWidget(),readonly=True)
    has_refraction = Field(attribute='correction__has_refraction',widget=BooleanWidget(),readonly=True)
    has_sedimentation = Field(attribute='correction__has_sedimentation',widget=BooleanWidget(),readonly=True)
    has_fluid = Field(attribute='correction__has_fluid',widget=BooleanWidget(),readonly=True)
    has_bottom_water_variation = Field(attribute='correction__has_bottom_water_variation',widget=BooleanWidget(),readonly=True)
    has_compaction = Field(attribute='correction__has_compaction',widget=BooleanWidget(),readonly=True)
    has_other = Field(attribute='correction__has_other',widget=BooleanWidget(),readonly=True)

class HeatFlowResource(CorrectionsMixin,SiteMixin):
    global_saves_null=True

    reliability = Field(attribute='reliability',
            saves_null_values=global_saves_null)
    heatflow_corrected = Field(attribute='corrected',
            widget=FloatWidget(),
            saves_null_values=global_saves_null)
    heatflow_corrected_uncertainty = Field(attribute='corrected_uncertainty',
            widget=FloatWidget(),
            saves_null_values=global_saves_null)
    heatflow_uncorrected = Field(attribute='uncorrected',
            widget=FloatWidget(),
            saves_null_values=global_saves_null)
    heatflow_uncorrected_uncertainty = Field(attribute='uncorrected_uncertainty',
            widget=FloatWidget(),
            saves_null_values=global_saves_null)
    thermal_conductivity = Field(attribute='conductivity',
            widget=FloatWidget(),
            saves_null_values=global_saves_null)

    correction__climatic = Field(attribute='correction',widget=widgets.CorrectionsWidget(field="climatic"))

    # needs to be before the site property fields below so that a reference is saved
    reference = Field(attribute='reference',
            column_name='bibtex', 
            widget=widgets.ReferenceWidget(Reference, field='bibtex', reference_dict=ResourceMixin.ref_dict))

    # Temperature gradient data associated with interval
    thermal_gradient_corrected = Field(attribute='thermalgradient',
                                widget=widgets.SitePropertyWidget(ThermalGradient,
                                field='corrected',
                                id_fields = ['site','depth_min','depth_max','reference'],
                                required_fields=['corrected','uncorrected'],
                                varmap={
                                    'thermal_gradient_corrected':'corrected',
                                    'gradient_corrected_uncertainty':'corrected_uncertainty',
                                    'gradient_uncorrected':'uncorrected',
                                    'gradient_uncorrected_uncertainty':'uncorrected_uncertainty',
                                    'reference':'reference'}))
    gradient_corrected_uncertainty = Field(attribute='thermalgradient__corrected_uncertainty',readonly=True)
    gradient_uncorrected = Field(attribute='thermalgradient__uncorrected',readonly=True)
    gradient_uncorrected_uncertainty = Field(attribute='thermalgradient__uncorrected_uncertainty',readonly=True)

    class Meta:
        model = HeatFlow
        import_id_fields = ['site','depth_min','depth_max','reference','thermal_conductivity']
        skip_unchanged = True
        # report_skipped=False
        fields = choices.HEAT_FLOW_EXPORT_ORDER
        export_order = fields.copy()

    def after_import_row(self,row,row_result,**kwargs):
        super().after_import_row(row,row_result,**kwargs)
        # decided not to associate heat generation with heat flow. However many uploads will contain a HG value. This will throw and error if listed as a field so need to put it here to save it to the site.
        hg_id, hg_fields = widgets.site_property(
                model=HeatGeneration,
                row=row,
                exclude=[],
                id_fields = ['site','value','reference','depth'],
                required_fields=['value'],
                varmap={'heat_generation':'value',
                        'heatgeneration__uncertainty': 'uncertainty',
                        'heatgeneration__number_of_measurements': 'number_of_measurements',
                        'heatgeneration__method':'method',}
                        )
        if hg_id:
            HeatGeneration.objects.update_or_create(**hg_id,defaults=hg_fields)
        
    def after_save_instance(self,instance, using_transactions, dry_run):   
        super().after_save_instance(instance,using_transactions,dry_run)
        # There's an issue where the new corrections (if they have changed (i think)) do not       
            # overwrite the old ones but instead create a new instance. Because its a 121     
            # relationship it must be unique andtherefore an error is thrown. This solution deletes 
            # the old relationship if it exists and then saves the new one. It is not elegant but it 
            # works.
        # if getattr(instance,'correction',False):
        #     try:
        #         Correction.objects.get(heatflow=instance.id).delete()
        #     except Correction.DoesNotExist:
        #         pass
        #     finally:
        #         instance.correction.save()

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
            ref, created = Reference.objects.get_or_create(bib_id=bib_id)
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
        # If a bib ID is supplied, check if an entry already exists and retrieve it
        try:
            ref = Reference.objects.get(bib_id=row['reference'])
        except Reference.DoesNotExist:
            db = BibDatabase()
            try:
                db.entries = [self.ref_dict[row['reference']]]
            except KeyError:
                ref = Reference.objects.create(bib_id=row['bibtex'])
            else:
                ref = Reference.objects.create(bibtex=bib.dumps(db))
        finally:
            return ref

class SitePropertyMixin(SiteMixin):
    global_saves_null = False

    site = Field(attribute='site',column_name='site_name',
        widget=widgets.SiteWidget(Site,
            field='site_name',
            render_field='site_name',
            id_fields=['latitude','longitude'],
            ))
    reference = Field(attribute='reference',
            column_name='reference', 
            widget=widgets.ReferenceWidget(Reference, field='bibtex', reference_dict=ResourceMixin.ref_dict))

    def before_import_row(self,row=None,**kwargs):
        super().before_import_row(row,**kwargs)
        row['site'] = None
        row['reference'] = init_reference_instance(row,self.bibtex)
        row['save_temp'] = False

class ConductivityResource(SitePropertyMixin):
    global_saves_null = False

    rock_group = Field(widget=widgets.ChoiceWidget(choices=choices.ROCK_GROUPS))
    rock_origin = Field(widget=widgets.ChoiceWidget(choices=choices.ROCK_ORIGIN))
    geo_unit = Field(attribute='geo_unit',column_name='geological_unit', saves_null_values=global_saves_null, widget=widgets.CustomFK(GeologicalUnit))

    class Meta:
        model = Conductivity
        fields = choices.PROPERTY_EXPORT_ORDER
        export_order = fields.copy()
        import_id_fields = ['site','sample_name','depth','reference']
        instance_loader_class = CustomInstanceLoader
        raise_errors = True

class HeatGenResource(SitePropertyMixin):
    global_saves_null = False

    rock_group = Field(widget=widgets.ChoiceWidget(choices=choices.ROCK_GROUPS))
    rock_origin = Field(widget=widgets.ChoiceWidget(choices=choices.ROCK_ORIGIN))
    geo_unit = Field(attribute='geo_unit',column_name='geological_unit', saves_null_values=global_saves_null, widget=widgets.CustomFK(GeologicalUnit))

    class Meta:
        model = HeatGeneration
        fields = choices.PROPERTY_EXPORT_ORDER
        export_order = fields.copy()
        import_id_fields = ['site','sample_name','depth','reference']

class TempResource(SitePropertyMixin):

    # geo_unit = Field(column_name='geological_unit')
    reference = Field(attribute='reference',
            column_name='reference', 
            widget=widgets.ReferenceWidget(Reference, field='bibtex', reference_dict=ResourceMixin.ref_dict))

    class Meta:
        model = Temperature
        fields = choices.TEMPERATURE_EXPORT_ORDER
        export_order = fields.copy()
        import_id_fields = ['site','depth','reference','operator']

    def before_import_row(self, row, **kwargs):
        super().before_import_row(row, **kwargs)
        row['reference'] = init_reference_instance(row,self.bibtex)
        depth = row.get('depth')
        well_depth = row.get('well_depth')
        if depth and well_depth:
            if float(depth) > float(well_depth) - 1/100*float(well_depth):
                row['is_bottom_of_hole'] = True