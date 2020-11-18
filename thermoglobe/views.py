import json
from urllib.parse import parse_qs
import csv
from datetime import datetime
import time
import zipfile
from io import StringIO

from django import forms
from django.contrib import messages
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.core import serializers
from django.core.mail import send_mail
from django.core.serializers import deserialize, serialize
from django.db.models import Avg, Count, F, FloatField, Max, Min, Q, Value
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView, View
from django.db.models.functions import Cast, Coalesce
from django.utils.html import mark_safe
from django.apps import apps
from django.utils.text import slugify
from thermoglobe.mixins import DownloadMixin 
from thermoglobe.models import Publication
from tablib import Dataset

from main.utils import get_page_or_none
from main.views import PageMixin, PageMetaMixin
from main.models import Page
from users.models import CustomUser

from . import plots, resources, tables, choices
from .forms import BetterSiteForm, UploadForm, ConfirmUploadForm, SiteMultiForm, DownloadForm
from .models import Conductivity, Interval, HeatGeneration, Site, Temperature
from .utils import get_db_summary, Hyperlink
from .filters import WorldMapFilter
from tables.mixins import MultiTableMixin
import re
from tempfile import NamedTemporaryFile
from bs4 import BeautifulSoup

REFERENCE_FIELDS = [
    ('reference__bib_id','bib_id'),
    ('reference__doi','doi'),
    ]

HEATFLOW_FIELDS = [  

    ('reliability', 'heatflow_reliability'),
    ('corrected','heatflow_corrected'),
    ('corrected_uncertainty','heatflow_corrected_uncertainty'),
    ('uncorrected','heatflow_uncorrected'),
    ('uncorrected_uncertainty','heatflow_uncorrected_uncertainty'),
    ('thermalgradient__corrected','gradient_corrected'),
    ('thermalgradient__corrected_uncertainty','gradient_corrected_uncertainty'),
    ('thermalgradient__uncorrected','gradient_uncorrected'),
    ('thermalgradient__uncorrected_uncertainty','gradient_uncorrected_uncertainty'),
    ('conductivity','thermal_conductivity'),
    'conductivity_uncertainty',
    'number_of_conductivities',
    'conductivity_method',
    # ('heat_generation','heat_generation
    # ('heat_generation_uncertainty','heatgeneration__uncertainty'),
    # ('heat_generation_number_of_measurements','heatgeneration__number_of_measurements'),
    # ('heat_generation_method','heatgeneration__method'),
    'comment',
    ]

CONDUCTIVITY_FIELDS = [
    'sample_name',
    ('value','thermal_conductivity'),
    'uncertainty',
    'method',
    'depth',
    'rock_group',
    'rock_origin',
    'rock_type',
    ('geo_unit__name','geo_unit'),
    'age',
    'age_min',
    'age_max',
    'age_method',
    'comment',
 ]

def data(request):
    """Handles the filter request from map view"""
    t = time.time()
    query = dict(request.GET)
    data_type = query.pop('data_type')[0]
    model = apps.get_model('thermoglobe', data_type)
    sites = getattr(Site.objects,data_type)()
    result = WorldMapFilter(request.GET,queryset=sites)
    fields = ['site_slug','site_name','latitude','longitude','elevation','value','reference__bib_id']
    filtered_qs = result.qs.annotate(site_slug=F('slug'))

    t2 = time.time()
    print('Database queried in: ',t2 - t,'s')


    if request.GET.get('filter') == 'false':
        return download_queryset(request, model, filtered_qs)
    else:
        r = JsonResponse({
            'type': data_type,
            'columns': ['site_slug','Site Name','Latitude','Longitude','Elevation [m]','value','Reference'],
            'data': list(filtered_qs.values_list(*fields)[:100])
            })
        print('Response prepared in: ',time.time() - t2,'s')
        print('Size: ',len(r.content)/10**6,'MB')
        return r


# def get_download_fields(data_type):
#     if data_type == 'heat_flow':
#         return Interval, heat_flow_sites()
#     elif data_type == 'gradient':
#         return Interval, gradient_sites()
#     elif data_type == 'conductivity':
#         return Conductivity, conductivity_sites()
#     elif data_type == 'heat_generation':
#         return HeatGeneration, heat_generation_sites()
#     elif data_type == 'temperature':
#         return Temperature, temperature_sites()

def get_upload_template(request,template_name):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}_upload_template.csv"'.format(template_name)
    writer = csv.writer(response)
    fields = getattr(choices, data_type)
    writer.writerow([field[1] if len(field) == 2 else field for field in fields])
    return response


class WorldMap(TemplateView):
    template_name = 'thermoglobe/world_map.html'
    filter = WorldMapFilter
    options = dict(
        autoWidth=False,
        dom='<"top d-flex justify-content-around align-items-baseline"lpf>t<"bottom"ip><"clear">',
        pageLength=100,
        deferRender=True,
        responsive=True,
        )
    form = DownloadForm
    table_fields = ['site_slug','site_name','latitude','longitude','country','sea','province__source_id',]
    field_aliases = ['site_slug','Site Name','Latitude','Longitude','Country','Sea','province']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            filter = self.filter(),
            table = dict(
                id='dataTable',
                options=self.options,
                columns=self.table_fields + [mark_safe('Heat Flow<br>[mW m<sup>3</sup>]')],
            ),
            map = dict(
                ajax=True,
                display=True,
                cluster=True,
                color=True,
            ),
            form=self.form()
            )     
        context['options'] = mark_safe(json.dumps(self.options))
        return context
   
    def post(self, request):
        """This function controls the download of the csv file"""
        data_type = request.POST.get('data_type')

        if data_type in ['heat_flow','gradient']:
            model = apps.get_model('thermoglobe', 'interval')
        else:
            model = apps.get_model('thermoglobe', data_type.replace('_',''))

        sites = getattr(Site.objects,data_type)
        result = WorldMapFilter(request.POST,queryset=sites)

        if request.is_ajax():
            if data_type in ['heat_generation','conductivity']:
                value = f'avg_{data_type}'
            elif data_type == 'temperature':
                value = 'count'
            else:
                value = data_type

            return JsonResponse({
                'type': data_type,
                'options': self.options,
                'columns': self.field_aliases  + [value],
                'data': list(result.qs
                    .annotate(site_slug=F('slug'))
                    .values_list(*self.table_fields + [value])
                    )
            })
        else:
            return self.download(data_type, model, result.qs)


    def download(self, data_type, model, filtered_qs):
        export_fields = getattr(choices, data_type).get(self.request.POST.get('options')) + ['reference__bib_id']
        site_fields = [f.name for f in Site._meta.fields]
        
        query_fields = ['site__'+field if field in site_fields else field for field in export_fields ]

        data = model.objects.filter(site__in=filtered_qs).values_list(*query_fields)

        # get all references in the current dataset
        all_refs = data.values_list('reference__bib_id',flat=True)

        # get a list of bibtex data from unique references in the current dataset
        bibtex_list = Publication.objects.filter(bib_id__in=all_refs).values_list('bibtex',flat=True)

        return self.prepare_zipped_response(data, export_fields, bibtex_list)
        # return self.prepare_response(data,export_fields)


    def prepare_response(self, data, headers):
        # prepare the response for csv file
        filename = 'ThermoGlobe_{}.csv'.format(datetime.now().strftime('%d_%b_%Y'))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        writer = csv.writer(response)

        # write the header row;
        writer.writerow(headers)

        # write the rows to the csv file
        for i in data:
            writer.writerow(i)

        return response

    def prepare_zipped_response(self, data, headers, bibtex_list):
        # prepare the response for csv file
        filename = 'ThermoGlobe_{}'.format(datetime.now().strftime('%d_%b_%Y'))
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(filename)
        zf = zipfile.ZipFile(response,'w')

        # put csv data in zipfile object
        headers = [header.split('__')[-1] for header in headers]
        zf.writestr('{}.csv'.format(self.request.POST.get('data_type')),self.csv_to_bytes(data, headers))

        # put bibtext list into a zipfile object
        zf.writestr('bibliography.bib',self.bibtex_to_bytes(bibtex_list))


        return response

    def bibtex_to_bytes(self, bibtex_list):
        bib_buffer = StringIO()

        for bib_entry in bibtex_list:
            bib_buffer.write(bib_entry)

        return bib_buffer.getvalue()

    def csv_to_bytes(self, data, headers):
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        # write the header row;
        writer.writerow(headers)

        # write the rows to the csv file
        for i in data:
            writer.writerow(i)

        return csv_buffer.getvalue()

class UploadView(PageMetaMixin,TemplateView):
    template_name = 'main/upload.html'
    page_id = 12
    upload_form = UploadForm
    confirm_form = ConfirmUploadForm
    success_template = 'main/upload_success.html'
    has_errors_template = ''
    has_validation_errors_template = ''
    options = dict(
        autoWidth=False,
        dom='<"top d-flex justify-content-around align-items-baseline"lpf>t<"bottom"ip><"clear">',
        order_by='year',
        pageLength=100,
        deferRender=True,
        responsive=True,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.upload_form
        context['templates'] = ['heat_flow','gradient','temperature','conductivity','heat_generation']
        return context

    def post(self, request):
        form = self.upload_form(request.POST, request.FILES)
        if form.is_valid():
            if not form.cleaned_data['bibtex']:
                form.cleaned_data['bibtex'] = get_unpublished_bibtex(form.cleaned_data)
            response = self.process_data(request, form)
            return response
        args = {'form': form, 'response': "Something wen't wrong!"}
        return render(request, self.template_name, args)

    @method_decorator(require_POST)
    def process_data(self, request, form):
        resource = self.get_resource_class(form)
        data = self.read_import_file(form)
        if isinstance(data, HttpResponse):
            # reading the file encountered an error
            return data

        dataset = Dataset().load(data, format='csv')

        # result = resource.import_data(dataset=dataset, dry_run=True,raise_errors=True)
        result = resource.import_data(dataset=dataset, dry_run=True)
        context = {'table': self.prepare_output_table(result)}

        if result.has_errors():  # Something wen't wrong on our side         
            return self.get_template_response(request, context, 'errors')
        elif result.has_validation_errors():  # Something wen't wrong on the users side
            return self.get_template_response(request, context, 'validation_error')
        else:  # Import was succesful
            # with NamedTemporaryFile(mode='w+b') as temp:
            #     # Encode your text in order to write bytes
            #     temp.write('abcdefg'.encode())
            #     # put file buffer to offset=0
            #     temp.seek(0)

            #     # use the temp file
            #     cmd = "cat "+ str(temp.name)
            #     print(os.system(cmd))
            form.save()
            return self.get_template_response(request, context, 'success')

    def get_template_response(self, request, context, status):
        context.update(page=self.get_page_context(status))
        return render(request, 
            self.get_template(status), 
            context=context,
            )

    def get_template(self, template):
        templates = {
            'success': self.success_template,
            'errors': self.has_errors_template,
            'validation_error': self.has_validation_errors_template,
        }
        return templates.get(template)

    def get_page_context(self, page):
        try:
            return Page.objects.get(title__iexact=page)
        except Page.DoesNotExist:
            pass

    def get_resource_class(self, form):
        resource_switch = {
            '0': resources.HeatFlowResource(),
            '1': resources.HeatFlowResource(),
            '2': resources.TempResource(),
            '3': resources.ConductivityResource(form.cleaned_data['bibtex']),
            '4': resources.HeatGenResource(),
        }
        return resource_switch[str(form.cleaned_data['data_type'])]

    def read_import_file(self, form):
        data_file = form.cleaned_data['data']
        try:
            return data_file.read().decode('utf-8')
        except UnicodeDecodeError as e:
            return HttpResponse(_(u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
        except Exception as e:
            return HttpResponse(_(u"<h1>%s encountered while trying to read file: %s</h1>" % (type(e).__name__, import_file.name)))

    def get_html_tag(self, import_type):
        tags = {
            'new': '<span class="badge badge-success">{}</span>',
            'update': '<span class="badge badge-info">{}</span>',
            'error': '<span class="badge badge-danger">{}</span>', 
            'skip': '<span class="badge badge-warning">{}</span>', 
            }
        return tags[import_type].format(import_type)

    def prepare_output_table(self, result):
        # adds html icon to display import_type
        table = [[self.get_html_tag(row.import_type)] +
                 row.diff for row in result.rows]

        headers = result.diff_headers.copy()
        headers.insert(0, '_')

        # return [{key: val for key, val in zip(headers, row)} for row in table]
        return {
            'id': 'importResult',
            'data': mark_safe(json.dumps(dict(
                id = 'importResult',
                columns = headers,
                data = table,
            )))
        }



        # return dict(
        #         id='importResult',
        #         data=mark_safe(dict(
        #             columns=headers,
        #             data=table)),                
        #         )

class SiteView(DownloadMixin, DetailView):
    template_name = "thermoglobe/site_details.html"
    model = Site
    form = SiteMultiForm
    tables = dict(
        intervals=['depth_min','depth_max','heat_flow','gradient','average_conductivity','heat_generation'],
        conductivity=['log_id','depth','conductivity','uncertainty','method'],
        temperature=['log_id','depth','temperature','uncertainty','method','circ_time'],
        heat_generation=['log_id','depth','heat_generation','uncertainty','method'],
    )
    options = dict(
        autoWidth=False,
        dom='<"top d-flex justify-content-around align-items-baseline"lpf>t<"bottom"ip><"clear">',
        order_by='year',
        pageLength=50,
        deferRender=True,
        responsive=True,
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
        context['options'] = json.dumps(self.options)
        
        context['tables'] = {}

        for table, fields in self.tables.items():
            context['tables'][table.replace('_',' ')] = self.get_table(table, fields)

        for table in context['tables'].values():
            if table['data']:
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


    def post(self, request,  *args, **kwargs):
        SITE = self.get_object()

        # prepare the response for csv file
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(SITE.pk)
        zf = zipfile.ZipFile(response,'w')

        for key, qs in SITE.get_data().items():
            if qs.exists():
                export_fields = getattr(choices, key).get('detailed') + ['reference__bib_id']
                site_fields = [f.name for f in Site._meta.fields]
                query_fields = ['site__'+field if field in site_fields else field for field in export_fields ]
                # if key in ['temperature','conductivity','heat_generation']:
                #     query_fields[query_fields.index(key)] = 'value'

                # create a csv file an save it to the zip object
                zf.writestr('{}.csv'.format(key),self.csv_to_bytes(qs.values_list(*query_fields), export_fields))

        # add bibtex file to zip object
        zf.writestr('{}.bib'.format(SITE.pk), self.bibtex_to_bytes(SITE.reference.values_list('bibtex',flat=True)))

        return response

class Explore(PageMetaMixin, TemplateView):
    table = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        soup = BeautifulSoup(context['page'].content,features="html.parser")
        context["content"] = [x.prettify() for x in soup.find_all('div')]
        if self.table is not None:
            context['data'] = self.table()

        return context  

class ExploreHeatFlow(Explore):
    table = tables.HeatFlow
    template_name = 'thermoglobe/explore/heat_flow.html'
    page_id = 5

class ExploreGradient(Explore):
    table = tables.Gradient
    template_name = 'thermoglobe/explore/gradient.html'
    page_id = 6

class ExploreTemperature(Explore):
    table = tables.Temperature
    template_name = 'thermoglobe/explore/temperature.html'
    page_id = 7

class ExploreConductivity(Explore):
    table = tables.Conductivity
    template_name = 'thermoglobe/explore/conductivity.html'
    page_id = 8

class ExploreHeatGen(Explore):
    table = tables.HeatGeneration
    template_name = 'thermoglobe/explore/heat_gen.html'
    page_id = 9


def plots(request):
    table_map = {
        'heat_flow': tables.HeatFlow,
        'gradient': tables.Gradient,
        'temperature':tables.Temperature,
    }

    table = table_map[request.GET['data']]()
    plot_method = getattr(table,request.GET['type'])

    return JsonResponse({'result': plot_method()})

# def plots(request):
#     models = {
#         'heat_flow': tables.HeatFlow,
#         'gradient': tables.Gradient,
#         'temperature':tables.Temperature,
#     }

#     table = table_map[request.GET['data']]()
#     plot_method = getattr(table,request.GET['type'])

#     return JsonResponse({'result': plot_method()})

def get_site_fields():
    exclude = ['slug','id','uploaded_by','date_added','added_by','date_edited','edited_by','geom']
    foreign_keys = {f[0]:'__'.join(f) for f in
                    [
                    ('continent','name'),
                    ('country','name'),
                    ('sea','name'),
                    ('basin','name'),
                    ('operator','name'),
                    ('surface_temp','value'),
                    ('bottom_hole_temp','value'),
                    ]
        }

    site_fields = [field.name for field in Site._meta.fields if field.name not in exclude]

    new_site_fields = []
    for field in site_fields:
        if field in foreign_keys.keys():
            new_site_fields.append(foreign_keys[field])
        else:
            new_site_fields.append(field)

    return [('site__'+field,field.split('__')[0]) for field in new_site_fields]


def get_unpublished_bibtex(form):
    timestamp = datetime.now()
    return "@Unpublished{{{last_name}{year},\
        author    = {{{last_name}, {first_name}}},\
        title     = {{Unpublished data upload to Heatflow.org - {date}}},\
        month     = {{{month}}},\
        year      = {{{year}}},\
        timestamp = {{{date}}},\
        }}".format(
            last_name=form['last_name'],
            first_name=form['first_name'],
            month=timestamp.strftime('%b').lower(),
            year=timestamp.strftime('%Y'),
            date=timestamp.strftime('%Y-%m-%d'),
        )