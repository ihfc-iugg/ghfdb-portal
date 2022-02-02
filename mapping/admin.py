from django.contrib.gis import admin
from .models import Country, Continent, Sea, Political, Province
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

class MappingAbstract(ImportMixin, admin.GeoModelAdmin):
    #: template for change_list view
    change_list_template = 'admin/mapping/change_list_import.html'
    #: template for import view
    import_template_name = 'admin/mapping/import.html'

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
            path('import/',
                self.admin_site.admin_view(self.import_action),
                name='%s_%s_import' % info),
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

    def import_action(self, request, *args, **kwargs):
        context = self.get_import_context_data()
        form_type = self.get_import_form()
        form_kwargs = self.get_form_kwargs(form_type, *args, **kwargs)
        form = form_type(request.POST or None,
                         request.FILES or None,
                         **form_kwargs)

        if request.POST and form.is_valid():
            import_file = form.cleaned_data['import_file']
            # handle zip file and possibly save to disk
            with zf.Zipfile(import_file,'r') as zipped:
                shp_file = [f for f in zipped.infolist() if f.filename.endswith('.shp')]

                if len(shp_file) == 1:
                    lm = LayerMapping(self.model, 
                        shp_file[0], 
                        self.model.mapping, 
                        transform=False)
                    lm.save(strict=True, verbose=True)
                elif len(shp_file) > 1:
                    raise ValueError('Multiple shapefiles found in directory')
                else:
                    raise ValueError('No shapefiles found in directory')

            # import data

            # return import messages as context

            # if not result.has_errors() and not result.has_validation_errors():
            #     initial = {
            #         'import_file_name': tmp_storage.name,
            #         'original_file_name': import_file.name,
            #         'input_format': form.cleaned_data['input_format'],
            #     }
            #     confirm_form = self.get_confirm_import_form()
            #     initial = self.get_form_kwargs(form=form, **initial)
            #     context['confirm_form'] = confirm_form(initial=initial)
        else:
            res_kwargs = self.get_import_resource_kwargs(request, form=form, *args, **kwargs)
            resource = self.get_import_resource_class()(**res_kwargs)

        context.update(self.admin_site.each_context(request))

        context['title'] = _("Import")
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]

        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name],
                                context)

    def get_confirm_import_form(self):
        return ConfirmImportForm

    def get_import_form(self):
        return ImportForm

@admin.register(Country)
class CountryAdmin(MappingAbstract):
    list_display = ['name','region','subregion','number_of_sites']
    search_fields = ['name','region','subregion',]
    list_filter = ['region']
    # readonly_fields = ['name','region','subregion','iso3'],

    fields = [
        'poly',
        'name',
        ('region','subregion'),
        'iso3',
    ]
    
@admin.register(Continent)
class ContinentAdmin(MappingAbstract):
    list_display = ['name','number_of_sites']
    fields = [
        'name',
        'poly',
        ('shape_area','sqkm'),
    ]

@admin.register(Sea)
class SeaAdmin(MappingAbstract):
    list_display = ['name','number_of_sites']
    fields = [
        'name',
        'poly',
        ('longitude','latitude'),
        ('min_x','max_x'),
        ('min_y','max_y'),
    ]

@admin.register(Political)
class PoliticalAdmin(MappingAbstract):
    list_display = ['name','territory','sovereign','area_km2',]
    search_fields = ['name','territory','sovereign',]

    fields = [
        'name',
        'poly',
    ]

@admin.register(Province)
class ProvinceAdmin(MappingAbstract):
    list_display = ['id','name','type','group','juvenile_age_min','juvenile_age_max','thermotectonic_age_min','thermotectonic_age_max','last_orogen','continent','plate','number_of_sites','ave_heat_flow']
    search_fields = ['name','type','group','continent']
    list_filter = ['continent','type','group','last_orogen','plate']
    fields = [
        'name',
        'poly',
    ]
