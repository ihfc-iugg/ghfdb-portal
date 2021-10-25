import json, zipfile
from datetime import datetime as dt
from django.db.models import F
from django.http import HttpResponse,  JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView, TemplateView,  ListView
from django.utils.html import mark_safe
from django.apps import apps
from django.utils.text import slugify
from thermoglobe.mixins import DownloadMixin 
from meta.views import MetadataMixin
from publications.models import Publication

from .forms import SiteMultiForm, DownloadForm
from .models import Site
from .utils import Hyperlink
from .filters import WorldMapFilter
from thermoglobe.mixins import TableMixin
from meta.views import Meta
from djgeojson.serializers import Serializer as to_geojson

# for handling temporary file uploads before confirmation
class WorldMap(DownloadMixin, TableMixin, TemplateView):
    template_name = 'world_map.html'
    filter = WorldMapFilter
    download_form = DownloadForm
    table_fields = ['site_slug','site_name','latitude','longitude','country','sea','province__id',]
    field_aliases = ['site_slug','Site Name','Latitude','Longitude','Country','Sea','province']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            filter = self.filter(),
            table = dict(
                id='dataTable',
                options=self.table_options(),
                columns=self.table_fields + [mark_safe('Heat Flow<br>[mW m<sup>3</sup>]')],
            ),
            map = dict(
                ajax=True,
                display=True,
                cluster=True,
                color=True,
            ),
            )
        context['meta'] = Meta(
            title='World Map | HeatFlow.org',
            description='Interactive search and download of all data within the ThermoGlobe database. The fastest wasy to find published and unpublished thermal data related to studies of the Earth.',
            keywords=['heat flow',' thermal gradient', 'thermal conductivity','temperature','heat production','download','ThermoGlobe','data','access']
        )
        return context
   
    @property
    def data_type(self):    
        """Convenience method"""
        return self.request.POST.get('data_type','heat_flow')

    def post(self, request):
        """This function controls the download of the csv file"""
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

class SiteView(TableMixin, DownloadMixin, DetailView):
    template_name = "site_details.html"
    model = Site
    form = SiteMultiForm
    tables = dict(
        intervals=['depth_min','depth_max','heat_flow_corrected','heat_flow_uncorrected','gradient_corrected','gradient_uncorrected'],
        conductivity=['log_id','depth','conductivity','uncertainty','method'],
        temperature=['log_id','depth','temperature','uncertainty','method','circ_time'],
        heat_production=['log_id','depth','heat_production','uncertainty','method'],
    )
    options = dict(
        pageLength=50,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.form(instance={
            'Site': self.get_object(),
            'Country': self.get_object().country,
            'Sea': self.get_object().sea,
            'Geological Province': self.get_object().province,
            'CGG Basins and Plays': self.get_object().basin,
            })
        context['meta'] = self.get_object().as_meta(self.request)

        context['tables'] = {}
        for table, fields in self.tables.items():
            context['tables'][table.replace('_',' ')] = self.get_table(table, fields)

        for table in context['tables'].values():
            if not table['data'] == '[]':   #cant check for truth because data is a json string
                table['active'] = True
                break

        return context

    def get_table(self, data_type, fields):
        qs = getattr(self.get_object(),data_type).all().values_list(*fields)
        return dict(
            id=slugify(data_type),
            data=json.dumps(list(qs)),
            columns=[field.replace('_',' ').capitalize() for field in fields],
            )

class PublicationListView(TableMixin,  ListView):
    page_id = 10
    model = Publication
    template_name = "publication_list.html"
    column_headers = ['slug', 'doi', 'type', 'title', 'year', 'journal','publisher']
    options = {'pageLength':50}
    mark_safe = True

    def get_queryset(self):
        return super().get_queryset().exclude(bibtex__exact='').values('slug','bibtex')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['table'] = dict(
            id='publicationTable',
            columns = self.column_headers,
            )
        return context

    def get(self,request,*args, **kwargs):
        if request.is_ajax():
            return JsonResponse({'data':list(self.get_queryset())})
        return super().get(request,*args, **kwargs)

class PublicationDetailsView(TableMixin, DownloadMixin, MetadataMixin, DetailView):
    template_name = "publication_details.html"
    download_form = DownloadForm
    model = Publication
    options = {'pageLength':50}
    tables = dict(
        intervals=['depth_min','depth_max','heat_flow','gradient'],
        conductivity=['count','depth_min','depth_max','min_conductivity','max_conductivity'],
        temperature=['count','depth_min','depth_max','min_temperature','max_temperature'],
        heat_production=['count','depth_min','depth_max','min_heat_production','max_heat_production'],
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bibtex'] = json.dumps(self.get_object().bibtex)
        context['meta'] = self.get_object().as_meta(self.request)
        context['sidebar'] = 'active'
        context['tables'] = {}

        for table, fields in self.tables.items():
            context['tables'][table.replace('_',' ')] = self.get_table(table, fields)

        for table in context['tables'].values():
            if table['data']:
                table['active'] = True
                break


        popup_fields = ['id','site_name','latitude','longitude','elevation',]

        context['geojson'] = to_geojson().serialize(
                queryset= self.get_object().sites.annotate(
                    link=Hyperlink('/thermoglobe/publications/','slug',icon='view')
                    ), 
                properties=','.join(popup_fields)
        )  


        return context

    def get_table(self,data_type, fields):
        fields = ['slug','site_name','latitude','longitude'] + fields
        qs = (apps.get_model('thermoglobe','Site')
                .objects.filter(reference=self.get_object())
                .table(data_type)
                .values_list(*fields)
        )
        return dict(
            id=slugify(data_type),
            data=json.dumps(list(qs)),
            columns=[field.replace('_',' ') for field in fields],
            )
