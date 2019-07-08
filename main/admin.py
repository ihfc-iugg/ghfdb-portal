from django.contrib import admin
from .models import Site, DepthInterval, HeatFlow, Conductivity, HeatGeneration, Temperature, TemperatureGradient 
from .mixins import BaseAdmin, DataCountsMixin
from django.db.models import Count
# from database.admin_inlines import CorrectionsInline, TemperatureInline, HeatFlowInline, HeatGenerationInline, ConductivityInline
from import_export.admin import ImportExportActionModelAdmin, ImportForm
from site_property.mixins import SitePropertyAdminMixin
from .resources import HeatFlowResource
from main.models import HeatFlow, TemperatureGradient, Conductivity, HeatGeneration

class HeatFlowInline(admin.TabularInline):
    model = HeatFlow
    fields = ['corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty','reliability']

class GradientInline(admin.TabularInline):
    model = TemperatureGradient
    fields = ['corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty']

class ConductivityInline(admin.TabularInline):
    model = Conductivity
    fields = ['value','uncertainty','method','number_of_measurements',]

class HeatGenerationInline(admin.TabularInline):
    model = HeatGeneration
    fields = ['value','uncertainty','method','number_of_measurements',]

# Register your models here.
@admin.register(Site)
class SiteAdmin(BaseAdmin):
    # resource_class = ThermoGlobeResource
    # counts = ['heat_flow','conductivity','heat_gen','temp']
    list_display = ['site_name', 'latitude', 'longitude', 'elevation', 'dip', 'well_depth', 'top_hole_temp','bottom_hole_temp','sediment_thickness','basin','sub_basin','domain','province','tectonic_environment','cruise','operator','added_by','date_added','edited_by','date_edited']
    fieldsets = [
        (None, 
            {'fields': [
                'site_name',
                ('latitude','longitude','elevation'),
                ('well_depth','dip','sediment_thickness'),]}),
        ('Geology',
            {'fields': [ 
                ('province','domain','basin','tectonic_environment')]}),
        (None,
            {'fields': [
                ('reference','operator','cruise')]})]

    # inlines = [HeatFlowInline, TemperatureInline, HeatGenerationInline, ]
    search_fields = ['site_name','cruise','reference__first_author__last_name']
    # list_filter = ['dip']


    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.annotate(
    #         _conductivity_count=Count("conductivity", distinct=True),
    #         _heat_gen_count=Count("heatgeneration", distinct=True),
    #         _temperature_count=Count("temperature", distinct=True),
    #         _heat_flow_count=Count("heatflow", distinct=True),)
    #     return queryset

    # def save_model(self, request, obj, form, change):    
    #     if change:
    #         if obj.geom.x != obj.longitude:
    #             obj.longitude = obj.geom.x
    #         if obj.geom.y != obj.latitude:
    #             obj.latitude = obj.geom.y
    #     super().save_model(request, obj, form, change)

@admin.register(DepthInterval)
class DepthIntervalAdmin(SitePropertyAdminMixin,ImportExportActionModelAdmin):
    resource_class = HeatFlowResource
    exclude = ['added_by','edited_by']
    list_display = ['site', 'latitude','longitude', 'depth_min','depth_max']
    fieldsets = [('Site', {'fields':[
                            'site',]}),
                ('Reference', {'fields': [
                            'reference',]}),
                (None, {'fields': [

                    ('depth_min','depth_max'),
                    ('age_min','age_max'),
                    ]})]
    inlines = [HeatFlowInline, GradientInline, ConductivityInline, HeatGenerationInline]

@admin.register(TemperatureGradient)
class GradientAdmin(DataCountsMixin):
    list_display = ['depth_interval','corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty','date_added','added_by','date_edited','edited_by']
    fieldsets = [
        ('Depth Interval', 
            {'fields': [
                'depth_interval']}),
        ('Temperature Gradient',
            {'fields': [
                ('corrected','corrected_uncertainty'),
                ('uncorrected','uncorrected_uncertainty'),]})]


@admin.register(HeatFlow)
class HeatFlowAdmin(DataCountsMixin):
    # resource_class = HeatFlowResource
    list_display = ['depth_interval','corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty','reliability','date_added','added_by','date_edited','edited_by']
    list_filter = ['reliability',]
    fieldsets = [
        ('Depth Interval', 
            {'fields': [
                'depth_interval']}),
        ('Heat Flow',
            {'fields': [
                'reliability',
                ('corrected','corrected_uncertainty'),
                ('uncorrected','uncorrected_uncertainty'),]})]

    # autocomplete_fields = ['site','reference','lithology']

    def save_model(self, request, obj, form, change):
        # #save the following fields to all of the related conductivity, temperature and heatgen objects
        # model_fields = ['site','depth','lithology','additional_lithology','age','age_method','reference']
        # fields = {field: getattr(obj,field) for field in model_fields if getattr(obj,field) is not None}  
        # for model in ['temperature','conductivity','heatgeneration']:
        #     getattr(obj,model+'_set').all().update(**fields)
        super().save_model(request, obj, form, change)

    # def _corrections(self,obj):
    #     return ", ".join([
    #         correction.correction_type for correction in obj.corrections.all()])

    def _corrected_heat_flow(self,obj):
        if obj.corrected:
            if obj.corrected_uncertainty:
                return '{} ({})'.format(obj.corrected,obj.corrected_uncertainty)
            else:
                return '{}'.format(obj.corrected)
    _corrected_heat_flow.admin_order_field = 'corrected_heatflow'

    def _uncorrected_heat_flow(self,obj):
        if obj.uncorrected:
            if obj.uncorrected_uncertainty:
                return '{} ({})'.format(obj.uncorrected, obj.uncorrected_uncertainty)
            else:
                return '{}'.format(obj.uncorrected)
    _uncorrected_heat_flow.admin_order_field = 'uncorrected_heatflow'

    def is_corrected(self,obj):
        return True if self.corrected else False
    is_corrected.boolean = True

@admin.register(Conductivity)
class ConductivityAdmin(SitePropertyAdminMixin):
    pass

@admin.register(HeatGeneration)
class HeatGenAdmin(SitePropertyAdminMixin):
    pass

@admin.register(Temperature)
class TemperatureAdmin(SitePropertyAdminMixin):
    pass

