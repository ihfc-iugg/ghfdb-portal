from .models import Site, DepthInterval, Conductivity, HeatFlow,TemperatureGradient, HeatGeneration, HeatFlowCorrection, Temperature
from reference.models import Reference
from geomodels.models import Lithology
from import_export.fields import Field
from import_export.widgets import FloatWidget
import time
from import_export import resources
from main import widgets
import sys

# This data needs to be included in all import_export resources
class SiteResourceMixin(resources.ModelResource):

    site_name = Field(attribute='site',widget=widgets.SiteWidget(Site,field='site',render_field='site_name'))
    latitude = Field(attribute='site__latitude',widget=FloatWidget(),readonly=True)
    longitude = Field(attribute='site__longitude',widget=FloatWidget(),readonly=True)
    elevation = Field(attribute='site__elevation',widget=FloatWidget(),readonly=True)
    dip = Field(attribute='site__dip', widget=FloatWidget(),readonly=True)
    operator = Field(attribute='site__operator',readonly=True)
    cruise = Field(attribute='site__cruise', readonly=True)
    well_depth = Field(attribute='site__well_depth', readonly=True)
    sediment_thickness = Field(attribute='site__sediment_thickness', widget=FloatWidget(), readonly=True)

    bottom_hole_temp = Field(attribute='site__bottom_hole_temp',
                            widget=widgets.SitePropertyWidget(Temperature,
                                field='value',
                                exclude='lithology',
                                id_fields = ['site','value'],
                                required_fields=['value'],
                                # specify the column to be mapped to each model field
                                varmap={'bottom_hole_temp':'value',
                                        'temperature_method':'method'}))

    top_hole_temp = Field(attribute='site__top_hole_temp',
                            widget=widgets.SitePropertyWidget(Temperature,
                                field='value',
                                exclude='lithology',
                                id_fields = ['site','value'],
                                required_fields=['value'],
                                varmap={'top_hole_temp':'value',
                                        'temperature_method':'method'}))

    province = Field(attribute='site__province', readonly=True)
    domain = Field(attribute='site__domain', readonly=True)
    basin = Field(attribute='site__basin', readonly=True)
    sub_basin = Field(attribute='site__sub_basin', readonly=True)
    tectonic_environment = Field(attribute='site__tectonic_environment', readonly=True)    

    # Reference data
    authors = Field(attribute='reference', widget=widgets.ReferenceWidget(Reference, field='reference',))
    year = Field(attribute='reference__year', readonly=True)

class HeatFlowResource(SiteResourceMixin):

    # Heatflow data associated with interval
    heatflow__corrected = Field(attribute='heatflow',widget=widgets.SitePropertyWidget(HeatFlow,
                                    field='corrected',
                                    required_fields=['corrected','uncorrected'],
                                    varmap={
                                        'heatflow__corrected':'corrected',
                                        'heatflow__corrected_uncertainty':'corrected_uncertainty',
                                        'heatflow__uncorrected':'uncorrected',
                                        'heatflow__uncorrected_uncertainty':'uncorrected_uncertainty',
                                        'heatflow__reliability':'reliability',}))
    
    correction_type = Field(attribute='heatflow__corrections', widget=widgets.CorrectionsWidget(HeatFlowCorrection, field='correction'))
    correction_value = Field(attribute='heatflow__corrections',readonly=True, widget=widgets.CorrectionsWidget(HeatFlowCorrection, field='value'))

    # Temperature gradient data associated with interval
    temperaturegradient__corrected = Field(attribute='temperaturegradient',
                            widget=widgets.SitePropertyWidget(TemperatureGradient,
                                field='corrected',
                                column_name = 'temperaturegradient__corrected',
                                required_fields=['corrected','uncorrected'],
                                varmap={
                                    'temperaturegradient__corrected':'corrected',
                                    'temperaturegradient__corrected_uncertainty':'corrected_uncertainty',
                                    'temperaturegradient__uncorrected':'uncorrected',
                                    'temperaturegradient__uncorrected_uncertainty':'uncorrected_uncertainty',}))

    # Conductivity data associated with depth interval
    thermal_conductivity = Field(attribute='conductivity',
                                widget=widgets.SitePropertyWidget(Conductivity,
                                    field='value',
                                    id_fields = ['site','value','depth_interval',],
                                    required_fields=['value'],
                                    exclude='lithology',
                                    varmap={'thermal_conductivity':'value',
                                            'conductivity__uncertainty': 'uncertainty',
                                            'conductivity__number_of_measurements': 'number_of_measurements',
                                            'conductivity__method':'method',}))

    # Conductivity data associated with depth interval
    heat_generation = Field(attribute='heatgeneration',
                            widget=widgets.SitePropertyWidget(HeatGeneration,
                                field='value',
                                exclude='lithology',
                                id_fields = ['site','value','depth_interval',],
                                required_fields=['value'],
                                varmap={'heat_generation':'value',
                                        'heatgeneration__uncertainty': 'uncertainty',
                                        'heatgeneration__number_of_measurements': 'number_of_measurements',
                                        'heatgeneration__method':'method',}))

    lithology = Field(attribute='lithology', widget=widgets.M2MWidget(Lithology, field='lithology'))

    class Meta:
        model = DepthInterval
        exclude = ['id','date_added', 'added_by', 'date_edited','edited_by','geom','slug','reference','site','heat_flow','gradient','conductivity','heatgeneration','uploaded_by']
        import_id_fields = ['site_name','latitude','longitude','depth_min','depth_max','heatflow__corrected']

        fields = [
            # Site fields
            'site_name','latitude','longitude','elevation','dip', 'well_depth',
            # Site geo
            'sediment_thickness','basin','sub_basin','domain','province','tectonic_environment',
            # temp
            'bottom_hole_temp', 'top_hole_temp',
            # depth interval fields
            'depth_min','depth_max','age_min','age_max', 'age_method',
            # heat flow fields
            'heatflow__reliability','heatflow__corrected','heatflow__corrected_uncertainty','heatflow__uncorrected','heatflow__uncorrected_uncertainty','correction_type','correction_value',
            # temperature gradient fields
            'temperaturegradient__corrected','temperaturegradient__corrected_uncertainty','temperaturegradient__uncorrected','temperaturegradient__uncorrected_uncertainty',
            # conductivity fields
            'thermal_conductivity','conductivity__uncertainty','conductivity__number_of_measurements','conductivity__method',
            # heat generation measurements
            'heat_generation','heatgeneration__uncertainty','heatgeneration__number_of_measurements','heatgeneration__method',
            # lithology
            'lithology',
            # reference fields
            'authors','year','operator','cruise', 'comment']

        export_order = fields.copy()

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.now = time.time()  
        self.number_of_rows = len(dataset)
        self.row_number = 0
        print('')

    def before_import_row(self,row=None,**kwargs):

        for field,value in row.items():
            if isinstance(value,str):
                row[field] = value.strip(' ')

        user = kwargs['user']._wrapped
        row['added_by'] = '{},{}'.format(user.last_name,user.first_name[0])


        row['reference'] = widgets.get_reference(Reference, row, id_fields = ['first_author','year'])

        row['site'] = widgets.update_or_create_object(Site, row, 
                                        id_fields=['site_name','latitude','longitude'],
                                        exclude=['bottom_hole_temp','top_hole_temp'],
                                        recursive=True)          

    def after_import_row(self, row, row_result, **kwargs):
        self.row_number +=1
        progress_bar(self.row_number,self.number_of_rows)

    def after_save_instance(self,instance, using_transactions, dry_run):
        # reverse OneToOne relationship need to be saved AFTER the parent model. This is quite possibly going to make this very slow but I don't see another way
        
        # required to save the bottom and top of hole temps to the site object 
        instance.site.save()      
        for i in ['conductivity','heatgeneration','heatflow','temperaturegradient']:
            if getattr(instance,i,False):
                getattr(instance,i).save()

    def after_import(self, dataset,result,using_transactions, dry_run,**kwargs):
        print('\n\nTIME ELAPSED: {}m'.format((time.time()-self.now)/60)) 
        print('Failed row count: {}\n'.format(len(dataset)-self.row_number)) 

def progress_bar(i, total, message='', decimals=0, bar_length=25):
    """Creates a terminal progress bar

    :param i: i number
    :type controlfile: int/float

    :param message: message to be displayed on the right of the progress bar
    :type message: str
    """

    str_format = "{0:." + str(decimals) + "f}"
    percentage = str_format.format(100 * (i / float(total)))
    filled_length = int(round(bar_length * i / float(total)))
    bar = '#' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\rPopulating database |{}| {}% {}             '.format(bar, percentage,'- '+message))

    if i == total:
        sys.stdout.write('')
    sys.stdout.flush()