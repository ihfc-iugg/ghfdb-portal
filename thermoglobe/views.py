import json, csv, time, zipfile, re
from urllib.parse import parse_qs
from datetime import datetime as dt
from io import StringIO
from itertools import zip_longest
from django import forms
from django.contrib import messages
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.core import serializers
from django.core.serializers import deserialize, serialize
from django.db.models import Avg, Count, F, FloatField, Max, Min, Q, Value
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView, View, ListView
from django.db.models.functions import Cast, Coalesce
from django.utils.html import mark_safe
from django.apps import apps
from django.utils.text import slugify
from thermoglobe.mixins import DownloadMixin 
from thermoglobe.models import Publication
from tablib import Dataset
from meta.views import MetadataMixin

from main.utils import get_page_or_none
from main.views import PageMetaMixin
from main.models import Page
from users.models import CustomUser

from . import resources, tables, choices, import_choices
from .forms import UploadForm, SiteMultiForm, DownloadForm, ConfirmUploadForm
from .models import Conductivity, Interval, HeatGeneration, Site, Temperature, Author, Publication
from .utils import Hyperlink, ACCEPTED_PLOT_TYPES
from .filters import WorldMapFilter
from tempfile import NamedTemporaryFile
from bs4 import BeautifulSoup
from import_export.forms import ConfirmImportForm
from thermoglobe.mixins import TableMixin
from meta.views import Meta
from thermoglobe import plots

# for handling temporary file uploads before confirmation
from django.core.cache import caches
cache = caches['file_cache']

def get_upload_template(request,template_name):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}_upload_template.csv"'.format(template_name)
    writer = csv.writer(response)
    fields = getattr(import_choices, template_name)
    writer.writerow([field[1] if len(field) == 2 else field for field in fields])
    return response

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
            keywords=['heat flow',' thermal gradient', 'thermal conductivity','temperature','heat generation','download','ThermoGlobe','data','access']
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
            if data_type in ['heat_generation','conductivity','temperature']:
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

class UploadView(TableMixin, PageMetaMixin,TemplateView):
    template_name = 'upload.html'
    confirm_template_name = 'upload_confirm.html'
    page_id = 12
    form = UploadForm
    # options = dict(autoWidth=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['templates'] = ['heat_flow','gradient','temperature','conductivity','heat_generation']
        context['upload_success'] = self.request.session.pop('upload_success',False)
        return context

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            # submitted form is valid so temporarily save data to cache for later use
            import_file = form.cleaned_data.pop('data')

            # read in the dataset
            dataset = self.get_dataset(import_file)
            # A HTTPResponse will be returned if an error is enounctered reading the file
            if isinstance(dataset, HttpResponse):
                return dataset 

            # get the relevant resource
            resource = self.get_resource_class(form)

            #import the data
            result = resource.import_data(dataset, dry_run=True, user=request.user)

            # Something wen't wrong on our side      
            if result.has_errors():     
                context.update(
                    table= self.prepare_output_table(result, errors='error'),
                    page= self.get_page(15),
                    errors = result.rows,
                )
            # User did something wrong
            elif result.has_validation_errors():  
                context.update(
                    table= self.prepare_output_table(result, errors='validation'),
                    page = self.get_page(15),
                    validation_errors = result.invalid_rows,
                )
            else:
                # save to cache so we can redirect and load in another view
                cache.set(request.session.get('session_key'), import_file)
                context.update(
                    confirm_form = self.form(initial=form.cleaned_data,hidden=True),
                    table = self.prepare_output_table(result),
                    page = self.get_page(14),
                    sidebar='inactive',
                )
            return render(request, self.confirm_template_name,context=context)

        else:
            context['form'] = form
            return render(request, self.template_name,context=context)


    def get_bibtex_data(form):
        if not form.cleaned_data['bibtex']:
            form.cleaned_data['bibtex'] = get_unpublished_bibtex(form.cleaned_data)
        return form

    def get_template_response(self, request, context, status):
        context.update(page=self.get_page_context(status))
        return render(request, 
            self.get_template(status), 
            context=context,
            )

    def get_page_context(self, page):
        try:
            return Page.objects.get(title__iexact=page)
        except Page.DoesNotExist:
            pass

    def get_resource_class(self, form):
        resource_switch = {
            '0': resources.IntervalResource(),
            '1': resources.IntervalResource(),
            '2': resources.TempResource(),
            '3': resources.ConductivityResource(form.cleaned_data['bibtex']),
            '4': resources.HeatGenResource(),
        }
        return resource_switch[str(form.cleaned_data['data_type'])]

    def get_dataset(self, data_file):
        try:
            data = data_file.read().decode('utf-8')
        except UnicodeDecodeError as e:
            return HttpResponse(_(u"<h1>Imported file has a wrong encoding: {}</h1>".format(e)))
        except Exception as e:
            return HttpResponse(_(u"<h1>{} encountered while trying to read file: {}</h1>".format(type(e).__name__, import_file.name)))

        return Dataset().load(data, format='csv')

    def get_html_tag(self, import_type, id=None):
        tags = {
            'new': '<i class="fas fa-check-circle text-success"></i>',
            'update': '<i class="fas fa-pen-square text-info"></i>',
            # 'error': '<i class="fas fa-times-circle text-danger"></i>',
            'skip': '<i class="fas fa-forward text-info"></i>',
            'error': f'<i class="fas fa-exclamation-triangle text-warning" data-toggle="modal" data-target="#{id}"></i>',
            # 'new': '<span class="badge badge-success">{}</span>',
            # 'update': '<span class="badge badge-info">{}</span>',
            # 'error': '<span class="badge badge-danger">{}</span>', 
            # 'invalid': '<span class="badge badge-warning">{}</span>', 
            # 'skip': '<span class="badge badge-skip">{}</span>', 
            }
        return tags[import_type].format(import_type)

    def prepare_output_table(self, result, errors=False):
        # adds html icon to display import_type
        if errors == 'validation':
            table = [[self.get_html_tag('error',f"row-{id_num}")] + [str(r) for r in row.values] for id_num, row in enumerate(result.invalid_rows)]
        elif errors == 'error':
            table = [[self.get_html_tag('error',f"row-{id_num}")] + self.get_values_from_row(row) for id_num, row in enumerate(result.rows) if row.errors]
        else:
            table = [[self.get_html_tag(row.import_type)] + row.diff for row in result.rows]

        headers = result.diff_headers.copy()
        headers.insert(0, '_')

        return dict(
            id='importResult',
            data=json.dumps(table),
            columns=[field.replace('_',' ') for field in headers],
            )

    def get_values_from_row(self, row):
        # what a cunt of a thing this is!
        return [str(val) for val in row.errors[0].row.values()]

class SiteView(TableMixin, DownloadMixin, DetailView):
    template_name = "site_details.html"
    model = Site
    form = SiteMultiForm
    tables = dict(
        intervals=['depth_min','depth_max','heat_flow_corrected','heat_flow_uncorrected','gradient_corrected','gradient_uncorrected'],
        conductivity=['log_id','depth','conductivity','uncertainty','method'],
        temperature=['log_id','depth','temperature','uncertainty','method','circ_time'],
        heat_generation=['log_id','depth','heat_generation','uncertainty','method'],
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

class Explore(PageMetaMixin, ListView):
    model = None
    template_name = 'explore.html'
    accepted_plot_types = ACCEPTED_PLOT_TYPES
    field_mapping = plots.field_mapping

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        soup = BeautifulSoup(context['page'].content,features="html.parser")
        context['lead_paragraph'] = self.get_soup_until(soup.find_all('p')[0],'header')
        context['content'] = self.parse_content(soup)
        context['content'] = zip_longest(context['content'],self.plots)
        return context  

    def parse_content(self,soup):
        headers = soup.find_all('header')
        content = []
        for h in headers:
            content.append(self.get_soup_until(h, 'header'))
        return content

    def get_soup_until(self, element, stop_on):
        html = element.prettify()
        el = element.find_next_sibling()
        while el is not None and el.name != stop_on:
            html += el.prettify()
            el = el.find_next_sibling()
        return html

    def get(self,request,*args, **kwargs):
        if request.is_ajax():
            """plots are generated here through ajax requests"""
            field = request.GET.get('field',None)
            data_type = request.GET['type']
            if not data_type in self.accepted_plot_types:
                return JsonResponse({
                    "status_code" : 404,
                    "error" : "The resource was not found",
                })
            plot = getattr(self.get_queryset(), data_type)
            if field:
                plot = plot(self.field_mapping.get(field))
            else:
                plot = plot()
            return JsonResponse({'result': plot})

        return super().get(request,*args, **kwargs)

class ExploreHeatFlow(Explore):
    page_id = 5
    model = Interval
    plots = plots.heat_flow

    def get_queryset(self, *args, **kwargs):
        return self.model.heat_flow.all()

class ExploreGradient(Explore):
    page_id = 6
    model = Interval
    plots = plots.gradient

    def get_queryset(self, *args, **kwargs):
        return self.model.gradient.all()

class PublicationListView(TableMixin, PageMetaMixin, ListView):
    page_id = 10
    model = Publication
    template_name = "publication_list.html"
    column_headers = ['slug', 'doi', 'type','author', 'title', 'year', 'journal','publisher']
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
        heat_generation=['count','depth_min','depth_max','min_heat_generation','max_heat_generation'],
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

class AuthorDetailsView(TableMixin, DownloadMixin, MetadataMixin, DetailView):
    template_name = "author_details.html"
    model = Author
    column_headers = ['slug', 'doi', 'year', 'publication']
    options = dict(dom='')
    mark_safe=True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = dict(
            id='publicationTable',
            columns=self.column_headers,
            )
        context['meta'] = self.get_object().as_meta(self.request)
        return context
    
    def get_sites(self, context):
        return Site.objects.filter(reference__first_author=context['author'])

    def get(self,request,*args, **kwargs):
        if request.is_ajax():
            return JsonResponse({'data':list(self.get_publications())})
        return super().get(request,*args, **kwargs)

    def get_publications(self):
        return self.get_object().get_publications().exclude(bibtex__exact='').values('slug','bibtex')


@require_POST
def upload_confirm(request):
    data = cache.get(request.session.get('session_key'))
    if request.POST.get('bibtex') == '':
        updated = request.POST.copy()
        updated.update(bibtex=get_unpublished_bibtex(request.POST))
        form = ConfirmUploadForm(updated, {'data':data})
    else:
        form = ConfirmUploadForm(request.POST, {'data':data})
        
    if form.is_valid():
        form.save()
        request.session['upload_success'] = True
    return redirect(reverse("thermoglobe:upload"))


def get_site_fields():
    exclude = ['slug','id','uploaded_by','date_added','added_by','date_edited','edited_by','geom']
    foreign_keys = {f[0]:'__'.join(f) for f in
                    [
                    ('continent','name'),
                    ('country','name'),
                    ('sea','name'),
                    ('basin','name'),
                    ('operator','name'),
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
    timestamp = dt.now()
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