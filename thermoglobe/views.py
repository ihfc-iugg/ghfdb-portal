import zipfile
from datetime import datetime as dt
from django.db.models import F
from django.http import HttpResponse,  JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView, TemplateView
from django.utils.html import mark_safe
from django.apps import apps
from thermoglobe.mixins import DownloadMixin 

from .models import Site
from .filters import MapFilter
from .forms import DownloadBasicForm, DownloadWithChoicesForm
from mapping.forms import MapSettingsForm
from meta.views import Meta
from django.http import JsonResponse
from thermoglobe.tables import heat_flow, heat_production, conductivity, temperature
from django.views.decorators.http import require_POST

def quick_sites(request):
    """Very quick transfer of all site data for web mapping."""
    site_filter = MapFilter(request.GET, queryset=Site.objects.all())
    sites = site_filter.qs.values_list('id','latitude','longitude',)[:100]
    return JsonResponse(list(sites),safe=False)


class WorldMap(DownloadMixin, TemplateView):
    template_name = 'mapping/application.html'
    filter = MapFilter
    download_form = DownloadWithChoicesForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dict(
            filter=self.filter(),
            settings=MapSettingsForm(),
            ))

        context['meta'] = Meta(
            title='World Map | ThermoGlobe',
            description='Interactive search and download of all data within the ThermoGlobe database. The fastest wasy to find published and unpublished thermal data related to studies of the Earth.',
            keywords=['heat flow',' thermal gradient', 'thermal conductivity','temperature','heat production','ThermoGlobe','data','access']
        )
        return context
   
    @property
    def data_type(self):    
        """Convenience method"""
        return self.request.POST.get('data_type','heat_flow')

    def post(self, request):
        """This function controls the download of the csv file"""
        # PREFER TO HANDLE THIS IN SEPERATE VIEW
        data_type = request.POST.get('data_type')

        if request.is_ajax() and self.get_filtered_queryset().is_valid():
            if data_type in ['heat_production','conductivity','temperature']:
                value = 'count'
            else:
                value = data_type

            return JsonResponse({
                'type': data_type,
                'options': self.table_options(),
                'columns': self.field_aliases  + [value],
                'data': list(self.get_filtered_queryset().qs
                    .annotate(site_slug=F('slug'))
                    .values_list(*self.table_fields + [value])
                    )
            })
        else:
            return self.download()

    def get_filtered_queryset(self):
        return self.filter(self.request.POST, queryset=self.get_sites())

    def get_sites(self):
        # m = apps.get_model('thermoglobe',key)
        return getattr(Site.objects,self.data_type)()

    def download(self):
        
        options = self.download_form(self.request.POST)
        if options.is_valid():
            download_type = options.cleaned_data['download_type']
            data_select = options.cleaned_data['data_select']

            # prepare the response for csv file
            response = HttpResponse(content_type='application/zip')
            dt_format = '%d_%b_%Y'
            response['Content-Disposition'] = f'attachment; filename="Thermoglobe_{dt.now().strftime(dt_format)}.zip"'

            zf = zipfile.ZipFile(response,'w')

            publications = apps.get_model('thermoglobe','publication').objects
            sites = apps.get_model('thermoglobe.Site').objects.all()

            # reference_list = set()
            reference_list = publications.none()
            for key in data_select:
                #get the download fields
                csv_headers = self.get_csv_headers(key, download_type)

                # make site fields are appropriate for query
                formatted_fields = self.format_query_fields(key, download_type)

                if key == 'intervals':
                    qs = apps.get_model('thermoglobe','interval').heat_flow.filter(site__in=self.get_filtered_queryset().qs)
                else:
                    qs = apps.get_model('thermoglobe',key).objects.filter(site__in=self.get_filtered_queryset().qs)
              
                zf.writestr(f'{key}.csv',self.csv_to_bytes(
                            data=qs.values_list(*formatted_fields), 
                            headers=csv_headers))


                sites = sites.filter(**{f"{key}__in":qs})
                reference_list = reference_list | publications.filter(sites__in=sites).distinct()

                # reference_list.update(list(qs.exclude(reference__bibtex__isnull=True).values_list('reference__bibtex',flat=True).distinct()))

            reference_list = reference_list.distinct().exclude(bibtex__isnull=True).values_list('bibtex',flat=True)

            if reference_list:
                zf.writestr(f'Thermoglobe_{dt.now().strftime(dt_format)}.bib', self.bibtex_to_bytes(reference_list))
                return response
            else:
                context = self.get_context_data(*args, **kwargs)
                context['download_form'] = options
                return render(request, template_name=self.template_name, context=context)

class SiteView(DownloadMixin, DetailView):
    template_name = "thermoglobe/site_details.html"
    model = Site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = [heat_flow, heat_production, conductivity, temperature]
        context['meta'] = self.get_object().as_meta(self.request)
        return context

@require_POST
def download(request):
    """This should be a simple view that handles download reuqests from the application"""
    data_type = request.POST.get('data_type')

    if request.is_ajax() and self.get_filtered_queryset().is_valid():
        if data_type in ['heat_production','conductivity','temperature']:
            value = 'count'
        else:
            value = data_type

        return JsonResponse({
            'type': data_type,
            'options': self.table_options(),
            'columns': self.field_aliases  + [value],
            'data': list(self.get_filtered_queryset().qs
                .annotate(site_slug=F('slug'))
                .values_list(*self.table_fields + [value])
                )
        })
    else:
        return self.download()
