from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView
from .forms import UploadForm, SiteForm
from . import resources
from tablib import Dataset
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.conf import settings
from .models import Site, HeatFlow, Conductivity, HeatGeneration, ThermalGradient
from django.core.serializers import serialize, deserialize
from django.contrib.gis.db.models.functions import AsGeoJSON
from urllib.parse import parse_qs
import json
from django.db.models import Avg, Max, Min, Count, F, Value, Q, FloatField
from reference.models import Upload
from .utils import get_db_summary
from users.models import CustomUser
from django.core.mail import send_mail
from reference.models import Reference
from main.utils import get_page_or_none
from django.core import serializers
from django import forms
from . import plots
from main.models import Page

class UploadView(TemplateView):
    template_name = 'main/upload.html'
    form = UploadForm
    page_id = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form  
        context['page'] = get_page_or_none(self.page_id)
        return context

    def post(self, request):
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            context = self.dry_run(request,form)
            return render(request, 'main/upload_success.html', context)

        args = {'form':form,'response':"Something wen't wrong!"}
        return render(request, self.template_name, args)

    @method_decorator(require_POST)
    def dry_run(self,request,form):
        resource_switch = {
            '0':resources.HeatFlowResource(),
            '1':resources.HeatFlowResource(),
            '2':resources.TempResource(),
            '3':resources.ConductivityResource(form.cleaned_data['bibtex']),
            '4':resources.HeatGenResource(),
            }

        resource = resource_switch[request.POST['data_type']]
        data_file = request.FILES['data']
        data = data_file.read().decode('utf-8')
        dataset = Dataset().load(data,format='csv')

        # result = resource.import_data(dataset=dataset, dry_run=True,raise_errors=True)
        result = resource.import_data(dataset=dataset, dry_run=True)


        import_type_html = {
            'new': '<span class="badge badge-success">{}</span>',
            'update': '<span class="badge badge-info">{}</span>',
            'error': '<span class="badge badge-info">{}</span>',
        }



        table = [[import_type_html[row.import_type].format(row.import_type)]+ row.diff for row in result.rows]
        headers = result.diff_headers.copy()
        headers.insert(0,'_')

        table = [{key:val for key,val in zip(headers,row)} for row in table]

        if result.has_errors(): # Something wen't wrong on our side
            page = get_page_or_none(3)       
        elif result.has_validation_errors(): # Something wen't wrong on the users side
            page = get_page_or_none(11)
        else: # Import was succesful
            page = get_page_or_none(10)
            form.save()
        return {'table':table,'page':page}

class SiteView(DetailView):
    template_name = "main/site_details.html"
    model = Site
    form = SiteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = context['object']
        context['form'] = self.form(instance=site)
        context['tables'] = {
            'heat_flow': list(site.heatflow_set.values('depth_min','depth_max','corrected','corrected_uncertainty',      'uncorrected','uncorrected_uncertainty','reliability')),
            'thermal_gradient': list(site.thermalgradient_set.values('depth_min','depth_max','corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty')),
            'thermal_conductivity': list(site.conductivity_set.values('depth','value','uncertainty')),
            'temperature': list(site.temperature_set.values('depth','value')),
            'heat_generation': list(site.heatgeneration_set.values('depth','value','uncertainty')),
            }
        return context

class About(TemplateView):
    template_name = 'thermoglobe/about.html'
    page_id = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = get_page_or_none(self.page_id)

        context['data_counts'] = list(plots.data_counts().values())
        context['data_labels'] = ['Heat Flow','Thermal Gradient','Temperature','Thermal Conductivity','Heat Generation']

        context['ContributionsPerYear'] = plots.contributions_per_year()
        context['HeatFlowHist'] = plots.heat_flow_histogram()

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

    # context['heat_flow_histogram'] = plots.heat_flow_histogram()

        return context

def chart_resources(request):
    template= 'main/resource_charts.html'

    context = {'reference':plots.get_year_counts()}

    context['country_labels'],context['country_data'] = plots.get_country_counts()

    context['data_counts'] = list(plots.data_counts().values())
    context['data_labels'] = ['Heat Flow','Thermal Gradient','Temperature','Thermal Conductivity','Heat Generation']

    context['ContributionsPerYear'] = plots.contributions_per_year()
    context['HeatFlowHist'] = plots.heat_flow_histogram()



    context['gradient_pie'] = ['Thermal Gradient by Country',
        plots.entries_by(
            model=ThermalGradient,
            model_filters={'site__country__isnull':False},
            model_values='site__country__name'),
        ]

    context['heat_flow_pie'] = ['Heat Flow by Country',
        plots.entries_by(
            model=HeatFlow,
            model_filters={'site__country__isnull':False},
            model_values='site__country__name'),
        ]
  
    context['heat_flow_sea_pie'] = ['Heat Flow by Sea/Ocean',
        plots.entries_by(
            model=HeatFlow,
            model_filters={'site__sea__isnull':False},
            model_values='site__sea__name'),
        ]



    context['page'] = Page.objects.get(id=9)
    # context['heat_flow_histogram'] = plots.heat_flow_histogram()


    return render(request,template,context)
   


















