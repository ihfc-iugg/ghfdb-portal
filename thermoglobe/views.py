import json
from urllib.parse import parse_qs
import csv
from datetime import datetime
import time

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
from django.views.generic import DetailView, TemplateView
from django.db.models.functions import Cast, Coalesce
from django.utils.html import mark_safe

from publications.models import Publication
from tablib import Dataset

from main.utils import get_page_or_none
from main.views import PageMixin
from main.models import Page
from users.models import CustomUser

from . import plots, resources, tables, choices
from .forms import BetterSiteForm, SiteForm, UploadForm, ConfirmUploadForm, SiteMultiForm
from .models import Conductivity, HeatFlow, HeatGeneration, Site
from .utils import get_db_summary
from .filters import (SiteFilter, HeatflowFilter, ConductivityFilter, 
HeatGenFilter, PublicationFilter, map_filter_forms)
from tables.mixins import MultiTableMixin
from .utils import Hyperlink
import re
from tempfile import NamedTemporaryFile

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
    qs = filter_request(request.GET, Site)
    data_type = request.GET.get('dataType','heatflow')

    if data_type == 'heatflow':
        # Average of either corrected or uncorrected heat flow values at a particular site. 
        annotation = {
            'heat_flow': Avg(Coalesce('heatflow__corrected', 'heatflow__uncorrected'))
            }
    elif data_type == 'conductivity':
        annotation = {'_conductivity':Avg('conductivity__value'),}
    elif data_type == 'heatgeneration':
        annotation = {'_heat_generation':Avg('heatgeneration__value'),}
    elif data_type == 'temperature':
        annotation = {'_temperature':Avg('temperature__value'),}

    fields = ['site_slug','site_name','latitude','longitude','elevation'] + list(annotation.keys()) + ['reference__bib_id']

    # qs = qs.annotate(**annotation, **link_fields)
    qs = qs.annotate(**annotation, site_slug=F('slug'))[:1000]
    t2 = time.time()

    r = JsonResponse({
        'columns': ['site_slug','Site Name','Latitude','Longitude','Elevation [m]','Heat Flow','Reference'],
        'data': list(qs.values_list(*fields))
    })

    print('Response prepared in: ',time.time() - t2,'s')
    print('Size: ',len(r.content)/10**6,'MB')
    return r


def filter_request(query_dict, model):
    """Filters data based on either the Site model (for ajax filtering) or the DepthInterval model (for download)"""
    query_dict = {k:v for k,v in query_dict.items() if v}

    # convert 'on'/'off' to True or False
    query_dict = {k:v if v != 'on' else True for k,v in query_dict.items()}       
    
    qs = model.objects.filter(**{'{}__isnull'.format(query_dict.get('dataType','heatflow')):False})

    if query_dict.get('value__gte') or query_dict.get('value__lte'):
        value_range = (query_dict.get('value__gte',0),query_dict.get('value__lte',10**6))
        if query_dict['dataType'] == 'heatflow':
            qs = qs.filter( 
                Q(heatflow__corrected__range=value_range)|
                Q(heatflow__uncorrected__range=value_range)
                        ).distinct()
        else:
            qs = qs.filter( 
                Q(**{'{}__value__range'.format(query_dict['dataType']):value_range})
            )

    # delete logical query_dict field because they cannot be used in filter
    for k in ['heatflow__gte','heatflow__lte','hf_uncorrected','hf_corrected','csrfmiddlewaretoken','dataType','value__gte','value__lte']:
        if k in query_dict.keys():
            del query_dict[k]

    # FOR DEBUGGING
    if query_dict:
        print('Current query:')
        for k,v in query_dict.items():
            print(k,': ',v)
        print(' ')

    return qs.filter(**query_dict).distinct()


class WorldMap(TemplateView):
    template_name = 'thermoglobe/world_map.html'
    filters = [SiteFilter]
    table_options = dict(
            order = [[6,'desc'],],
            pageLength = 25,
            link_url='/thermoglobe/sites/',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dict(
            filters = self.filters,
            # table_options = self.table_options, 
        ))     

        context['table'] = dict(
            id='worldmap',
            options=self.table_options,
        )

        context['map'] = dict(
            ajax=True,
            display=True,
            cluster=True,
            color=True,
        )

        return context

    def get_queryset(self):
        return Site.objects.select_related('reference').all()
    
    def post(self, request):
        """This method controls the download of the csv file"""
        sites = filter_request(request.POST,Site)
        data_type = request.POST.get('dataType')
        site_fields = get_site_fields()

        if data_type == 'heatflow':
            model = HeatFlow
            fields = site_fields + HEATFLOW_FIELDS + REFERENCE_FIELDS
        elif data_type == 'conductivity':
            model = Conductivity
            fields = site_fields + CONDUCTIVITY_FIELDS + REFERENCE_FIELDS
        elif data_type == 'heatgeneration':
            model = HeatGeneration
        elif data_type == 'temperature':
            model = Temperature

        qs = model.objects.filter(site__in=sites)
        my_csv = qs.values_list(*[field[0] if len(field) == 2 else field for field in fields])

        # prepare the response for csv file
        filename = 'ThermoGlobe_{}.csv'.format(datetime.now().strftime('%d_%b_%Y'))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        writer = csv.writer(response)

        # write the header row; remove "site__" prefix for some fields for clarity
        writer.writerow([field[1] if len(field) == 2 else field for field in fields])

        # write the rows to the csv file
        for i in my_csv:
            writer.writerow(i)

        return response


class UploadView(TemplateView):
    template_name = 'main/upload.html'
    # title = 'Upload'
    upload_form = UploadForm
    confirm_form = ConfirmUploadForm
    success_template = 'main/upload_success.html'
    has_errors_template = ''
    has_validation_errors_template = ''
    table_options = dict(
            order = [[6,'desc'],],
            pageLength = 25,
            link_url='/thermoglobe/sites/',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.upload_form
        return context

    def post(self, request):
        form = self.upload_form(request.POST, request.FILES)
        # form_data = self.upload_form(request.POST)
        if form.is_valid():
            if not form.cleaned_data['bibtex']:
                form.cleaned_data['bibtex'] = get_unpublished_bibtex(form.cleaned_data)
            #     request.session['form_data'] = form.cleaned_data
            # # if form_data.is_valid():
            # #     request.session['form_data'] = form_data.cleaned_data
            response = self.dry_run(request, form)
            return response

        args = {'form': form, 'response': "Something wen't wrong!"}
        return render(request, self.template_name, args)

    @method_decorator(require_POST)
    def dry_run(self, request, form):
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


class SiteView(MultiTableMixin, DetailView):
    template_name = "thermoglobe/site_details.html"
    model = Site
    form = BetterSiteForm
    # form = SiteMultiForm
    tables = [  tables.HeatFlow,
                # tables.ThermalGradient,
                tables.Temperature,
                tables.Conductivity,
                tables.HeatGeneration,
                ]
    filter_object_on = 'site'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form(instance=self.get_object())
        context['map'] = dict(
            ajax=False,
            display=True,
            cluster=False,
            color=True,
        )

        return context


class About(MultiTableMixin, TemplateView):
    template_name = 'thermoglobe/about.html'
    page_id = 9
    tables = [  tables.HeatFlow(headers=['site__latitude','site__longitude','corrected','uncorrected','site__elevation','site__country__name','site__continent__name','site__CGG_basin__name']),
                # tables.ThermalGradient(),
                tables.Temperature(),
                tables.Conductivity(),
                tables.HeatGeneration(),
                ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = get_page_or_none(self.page_id)
        context['data_labels'] = ['Heat Flow', 'Thermal Gradient',
                                  'Temperature', 'Thermal Conductivity', 'Heat Generation']

        # context['ContributionsPerYear'] = plots.contributions_per_year()
        # context['HeatFlowHist'] = plots.heat_flow_histogram()

        # context['test'] = plots.contributions_per_year()

        # context.update(dict(
        #     figures={
        #         'historical_heat_flow':
        #             {'id': 'historical_heat_flow',
        #              'data': plots.contributions_per_year(),
        #              },
        #         'heat_flow_hist':
        #             {'id': 'HeatFlowHist',
        #              'data': plots.heat_flow_histogram(),
        #              },





        #     },
        # )
        # )
        # context['gradient_pie'] = ['Thermal Gradient by Country',
        #     plots.entries_by(
        #         model=ThermalGradient,
        #         model_filters={'site__country__isnull':False},
        #         model_values='site__country__name'),
        #     ]

        # context['heat_flow_pie'] = ['Heat Flow by Country',
        #     plots.entries_by(
        #         model=HeatFlow,
        #         model_filters={'site__country__isnull':False},
        #         model_values='site__country__name'),
        #     ]

        # context['heat_flow_sea_pie'] = ['Heat Flow by Sea/Ocean',
        #     plots.entries_by(
        #         model=HeatFlow,
        #         model_filters={'site__sea__isnull':False},
        #         model_values='site__sea__name'),
        #     ]

        return context


def get_site_fields():
    exclude = ['slug','id','uploaded_by','date_added','added_by','date_edited','edited_by','geom']
    foreign_keys = {f[0]:'__'.join(f) for f in
                    [
                    ('continent','name'),
                    ('country','name'),
                    ('sea','name'),
                    ('CGG_basin','name'),
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


def chart_resources(request):
    template = 'main/resource_charts.html'

    context = {'reference': plots.get_year_counts()}

    context['country_labels'], context['country_data'] = plots.get_country_counts()

    context['data_counts'] = list(plots.data_counts().values())
    context['data_labels'] = ['Heat Flow', 'Thermal Gradient',
                              'Temperature', 'Thermal Conductivity', 'Heat Generation']

    context['ContributionsPerYear'] = plots.contributions_per_year()
    context['HeatFlowHist'] = plots.heat_flow_histogram()

    # context['gradient_pie'] = ['Thermal Gradient by Country',
    #                            plots.entries_by(
    #                                model=ThermalGradient,
    #                                model_filters={
    #                                    'site__country__isnull': False},
    #                                model_values='site__country__name'),
    #                            ]

    context['heat_flow_pie'] = ['Heat Flow by Country',
                                plots.entries_by(
                                    model=HeatFlow,
                                    model_filters={
                                        'site__country__isnull': False},
                                    model_values='site__country__name'),
                                ]

    context['heat_flow_sea_pie'] = ['Heat Flow by Sea/Ocean',
                                    plots.entries_by(
                                        model=HeatFlow,
                                        model_filters={
                                            'site__sea__isnull': False},
                                        model_values='site__sea__name'),
                                    ]

    context['page'] = Page.objects.get(id=9)
    # context['heat_flow_histogram'] = plots.heat_flow_histogram()

    return render(request, template, context)


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