from .models import Site, Conductivity, Interval, HeatGeneration, Temperature, Correction, Publication
from import_export.fields import Field
from import_export.widgets import FloatWidget, CharWidget, IntegerWidget, BooleanWidget, ForeignKeyWidget, DecimalWidget
import time
from import_export import resources
from . import widgets, import_choices as choices
from .utils import ACCEPTED_PLOT_TYPES
import sys
import bibtexparser as bib
from thermoglobe.utils import age_range
from import_export.instance_loaders import BaseInstanceLoader
from django.db import IntegrityError
from django import VERSION
from import_export.instance_loaders import ModelInstanceLoader
from django.utils.html import mark_safe
from tqdm import tqdm
# from django.contrib.admin.models import LogEntry, ContentType
from thermoglobe import plots
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str
from mapping import update
from django.core.cache import caches

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

def fix_depth(row):
    if row.get('depth_min') and row.get('depth_max'):
        if float(row['depth_min']) == float(row['depth_max']) == 0:
            row['depth_min'] = None
            row['depth_max'] = None
    return row

class ResourceMixin(resources.ModelResource):
    # ref_dict = get_references().entries_dict

    def __init__(self,bibtex=None):
        self.bibtex = bibtex

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        """ Start import timer and initialize count for progress bar"""
        self.pbar = tqdm(total=len(dataset))

    def before_import_row(self,row=None,**kwargs):
        row = self.format_coordinates(row) # converts lat and lon to 5 decimal place string
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

    def after_import(self, dataset, result, using_transactions, dry_run,**kwargs):
        self.clean_result(result)

        has_errors = result.has_validation_errors() or result.has_errors()
        if not dry_run and not has_errors:  
            #import was a success! spread the news!
            self.create_news(result, kwargs['user'])

            # These take too long for the production server
            #update all gis categories
            #self.update_gis()

            #update plot cache with new data
            #self.update_plot_cache()
            self.clear_cache()

        print('Import Summary:')
        for key, count in result.totals.items():
            if count:
                print('\t',key,': ',count)


    def update_gis(self):
        for i in ['continents','countries','seas','basins','province','political']:
            getattr(update,i)()

    def clear_cache(self):
        caches['plots'].clear()

    def update_plot_cache(self):
        pass

    def get_html_publications_list(self,result):
        objects = [row.object_id for row in result.rows]
        affected_pubs = Publication.objects.filter(intervals__in=objects).distinct()    

        # construct an html list of linked publications
        return "".join([f'<li><a href="{pub.get_absolute_url()}">{pub}</a></li>' for pub in affected_pubs])

    def create_news(self,result, user):
        totals = result.totals
        html_pubs = self.get_html_publications_list(result)
        # News.objects.create(
        #         headline = "New data added!",
        #         content =  f"<p>This new upload features {totals['new']} new and {totals['update']} updated entries in the {self._meta.model._meta.verbose_name} table. Check out the new data below:</p><div><ul>{html_pubs}</ul></div>",
        #         published_by = user,
        #     )

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

    def format_coordinates(self,row):
        """Converts lat an lon to a string formatted number no longer than 5 decimals places. This combats rounding errors when converting from degrees:minute:seconds to decimal degrees and prevents incorrect precision by rounding to too many decimal places."""
        for i in ['latitude','longitude']:
            val = row.get(i).split('.')[-1]
            if len(val) > 5:
                formatted = format(float(row[i]),'.5f')
                row[i] = formatted

        return row

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
    year_drilled = Field(attribute='site__year_drilled', widget=FloatWidget(),readonly=True)

    cruise = Field(attribute='site__cruise')
    well_depth = Field(attribute='site__well_depth',widget=FloatWidget())

    sediment_thickness = Field(attribute='site__sediment_thickness',saves_null_values=global_saves_null,widget=FloatWidget())
    sediment_thickness_type = Field(attribute='site__sediment_thickness_type')

    crustal_thickness = Field(attribute='site__crustal_thickness',saves_null_values=global_saves_null,widget=FloatWidget())

    seamount_distance = Field(attribute='site__seamount_distance',widget=FloatWidget(),saves_null_values=global_saves_null)

    bottom_water_temp = Field(attribute='site__bottom_water_temp',widget=FloatWidget(),saves_null_values=global_saves_null)

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
    
    bwv_correction = Field(attribute='corrections__bwv',widget=FloatWidget(),readonly=True)
    bwv_flag = Field(attribute='corrections__bwv_flag',widget=BooleanWidget(),readonly=True)
        
    compaction_correction = Field(attribute='corrections__compaction',widget=FloatWidget(),readonly=True)
    compaction_flag = Field(attribute='corrections__compaction_flag',widget=BooleanWidget(),readonly=True)
        
    other_correction = Field(attribute='corrections__other',widget=FloatWidget(),readonly=True)
    other_flag = Field(attribute='corrections__other_flag',widget=BooleanWidget(),readonly=True)
    other_type = Field(attribute='corrections__other_type',readonly=True)

class IntervalResource(CorrectionsMixin,SiteMixin):
    global_saves_null=True

    class Meta:
        model = Interval
        import_id_fields = ['site_name','depth_min','depth_max','reference','heat_flow_corrected','heat_flow_uncorrected']
        skip_unchanged = True
        fields = ['reference'] + choices.heat_flow
        export_order = fields.copy()
        instance_loader_class = CustomInstanceLoader
        # clean_model_instances = True

    def import_obj(self, obj, data, dry_run):
        """
        Traverses every field in this Resource and calls
        :meth:`~import_export.resources.Resource.import_field`. If
        ``import_field()`` results in a ``ValueError`` being raised for
        one of more fields, those errors are captured and reraised as a single,
        multi-field ValidationError."""
        data['hf_id'] = obj.pk
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

    def after_save_instance(self,instance, using_transactions, dry_run):   
        super().after_save_instance(instance,using_transactions,dry_run)
        # if getattr(instance,'corrections',False):
        #     instance.corrections.save()

    def create_news(self,result, user):
        totals = result.totals
        html_pubs = self.get_html_publications_list(result)
        # News.objects.create(
        #         headline = "New data added!",
        #         content =  f"<p>This new upload features {totals['new']} new and {totals['update']} updated heat flow and/or thermal gradient entries in the {self._meta.model._meta.verbose_name} table. Check out the new data below:</p><div><ul>{html_pubs}</ul></div>",
        #         published_by = user,
        #     )

    def update_plot_cache(self):
        # return
        for data_type in ['heat_flow','gradient']:
            qs = getattr(self.Meta.model,data_type)
            for plot_specs in getattr(plots,data_type):
                plot = getattr(qs,plot_specs['type'])
                if plot_specs.get('fields'):
                    for field in plot_specs['fields']:
                        plot(plots.field_mapping.get(field),force_update=True)
                else:
                    plot(force_update=True)
        # pass


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

    class Meta:
        model = Conductivity
        fields = choices.conductivity
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

    class Meta:
        model = HeatGeneration
        fields = choices.heat_generation
        export_order = fields.copy()
        import_id_fields = ['site_name','sample_name','depth','reference']

class TempResource(SiteMixin):
    temperature = Field(attribute='temperature',
            column_name='temperature',
            widget=FloatWidget())

    class Meta:
        model = Temperature
        fields = choices.temperature
        export_order = fields.copy()
        import_id_fields = ['site_name','depth','temperature','log_id','reference']



class SiteResource(resources.ModelResource):

    class Meta:
        model = Site
        import_id_fields = ['id']
        fields = ['id','latitude','longitude']
