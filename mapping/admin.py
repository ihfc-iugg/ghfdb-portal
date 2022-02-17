from django.contrib.gis import admin
from .models import Country, Continent, Ocean, Political, Province, Ocean, Plate
from django.db.models import Count, Avg
from django.db.models.functions import Coalesce
from django.urls import path
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.encoding import force_str
from import_export.admin import ImportMixin
from django.utils.translation import gettext_lazy as _
from .forms import ConfirmImportForm, ImportForm
import zipfile as zf
from django.contrib.gis.utils import LayerMapping
from django.core.cache import caches
from import_export.admin import ImportExportActionModelAdmin

class MappingAbstract(ImportExportActionModelAdmin, admin.GeoModelAdmin):
    #: template for change_list view
    # change_list_template = 'admin/mapping/change_list_import.html'
    #: template for import view
    # import_template_name = 'admin/mapping/import.html'

    def get_queryset(self, request):
        return (super().get_queryset(request)
        # .filter(sites__isnull=False)
        .annotate(
            _number_of_sites=Count("sites"),
            _ave_heat_flow=Avg(
                Coalesce('sites__intervals__heat_flow_corrected',
                'sites__intervals__heat_flow_uncorrected')
                )
            )
        .order_by('-_number_of_sites')
        )

    def ave_heat_flow(self,obj):
        return obj._ave_heat_flow
    ave_heat_flow.admin_order_field = '_ave_heat_flow'

    def number_of_sites(self,obj):
        return obj._number_of_sites
    number_of_sites.admin_order_field = '_number_of_sites'

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        my_urls = [
            path('process_import/',
                self.admin_site.admin_view(self.load_data),
                name='%s_%s_process_import' % info),
        ]
        return my_urls + urls

    @method_decorator(require_POST)
    def load_data(self, request, *args, **kwargs):

        form_type = self.get_confirm_import_form()
        confirm_form = form_type(request.POST)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            tmp_storage = self.get_tmp_storage_class()(name=confirm_form.cleaned_data['import_file_name'])
            data = tmp_storage.read(input_format.get_read_mode())
            if not input_format.is_binary() and self.from_encoding:
                data = force_str(data, self.from_encoding)
            dataset = input_format.create_dataset(data)

            result = self.process_dataset(dataset, confirm_form, request, *args, **kwargs)

            tmp_storage.remove()

            return self.process_result(result, request)

    # def get_confirm_import_form(self):
    #     return ConfirmImportForm

    # def get_import_form(self):
    #     return ImportForm

@admin.register(Country)
class CountryAdmin(MappingAbstract):
    list_display = ['name','iso3','region','subregion','number_of_sites']
    search_fields = ['name','region','subregion',]
    list_filter = ['region']
    readonly_fields = ['name','region','subregion','iso3']
    fields = ['poly', ('iso3','name', 'region','subregion')]
    
@admin.register(Continent)
class ContinentAdmin(MappingAbstract):
    list_display = ['name','number_of_sites']
    readonly_fields = ['name']
    fields = ['name','poly']

@admin.register(Political)
class PoliticalAdmin(MappingAbstract):
    list_display = ['name','iso','number_of_sites']
    readonly_fields = ['iso','name']
    search_fields = ['iso','name']
    fields = ['poly',('iso','name')]

@admin.register(Province)
class ProvinceAdmin(MappingAbstract):
    list_display = ['name', 'type', 'group', 'last_orogen', 'crust', 'number_of_sites']
    search_fields = ['name',]
    list_filter = ['type','group','crust','last_orogen',]
    readonly_fields = ['name', 'type', 'group', 'last_orogen', 'crust']
    fields = ['poly',('name','group'), ('type', 'crust', 'last_orogen')]

@admin.register(Ocean)
class Ocean(MappingAbstract):
    list_display = ['name','number_of_sites']
    search_fields = ['name']
    readonly_fields = ['name']
    fields = ['poly','name']

@admin.register(Plate)
class Plate(MappingAbstract):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_display = [
        'id','name','plate','plate_id','poly_name','type',
        'crust_type','domain','number_of_sites']

    search_fields = ['name','plate','poly_name']

    list_filter = ['plate','type','crust_type','domain']
    fields =  ['poly',
        'id','name','plate','plate_id','poly_name','type',
        'crust_type','domain']