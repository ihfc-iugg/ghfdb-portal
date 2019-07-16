from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .forms import DownloadForm, UploadForm
from .resources import HeatFlowResource
from .filters import SiteFilter, HeatflowFilter, ConductivityFilter, HeatGenFilter, ReferenceFilter
from tablib import Dataset
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import Site
from django.core.serializers import serialize, deserialize
from django.contrib.gis.db.models.functions import AsGeoJSON
from urllib.parse import parse_qs
import json
from django.db.models import Count, F, Value
from django.db.models import Max, Min
from django.db.models import Q
from reference.models import FileStorage


def form_setup(form=None,menu_title=None):
    return {'form':form,'menu_title':menu_title}

# Create your views here.
class HomeView(TemplateView):
    template_name= 'main/home.html'
    model = Site


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sites = Site.objects.all()

        context['db'] = sites.aggregate(Max('reference__year'),
                                        Min('reference__year'),
                                        Count('heatflow',distinct=True),
                                        Count('conductivity',distinct=True),
                                        Count('heatgeneration',distinct=True),
                                        Count('temperature',distinct=True),
                                        Count('reference', distinct=True))
        return context

class AboutView(TemplateView):
    template_name= 'main/about.html'

class ContactView(TemplateView):
    template_name= 'main/contact.html'


def download_success(request):
    return render(request,'main/download_success.html')

def resources(request):
      form = UserCreationForm
      return render(request,
                    'main/resources.html',
                    context={'form':form})

def geojson_serializer(qs):
    qs = qs.values('latitude','longitude','site_name','reference__first_author__last_name','reference__year')
    return {
        'type': 'FeatureCollection',
        'features': [{
            "type":"Feature",
            "geometry":{"type": "Point",
                        "coordinates":[q['longitude'], q['latitude']]},
            # "properties": {'site_name':form['site_name'],
            #             #    'author':form['reference__first_author__last_name'],
            #                'year':form['reference__year']
            # }
        } for q in qs]
    }

class DatabaseView(TemplateView):
    template_name = 'mapping/fullmap.html'
    forms = [
            form_setup(SiteFilter, 'site'),
            form_setup(HeatflowFilter, 'heat flow'),
            form_setup(ConductivityFilter, 'thermal conductivity'),
            form_setup(HeatGenFilter, 'heat generation'),
            form_setup(ReferenceFilter,'reference'),
             ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = self.forms
        qs = self.get_queryset()[:100]
        context['points'] = geojson_serializer(qs)
  
        return context

    def get_queryset(self):
        return Site.objects.select_related('reference').all()
    
    def post(self, request):
        form = DownloadForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['file_type']
            response = self.download(text)
            return response

        args = {'form':form,'text':text,'response':"Something wen't wrong!"}
        return render(request, self.template_name, args)

    def download(self,text):
        # dataset = Resource.Site().export()
        dataset = None #TODO add site resource here
        if text == 'csv':
            response = HttpResponse(dataset.csv,content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="heatflow.csv"'
        elif text == 'xls':
            response = HttpResponse(dataset.xls,content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="heatflow.xls"'
        elif text == 'json':
            response = HttpResponse(dataset.json,content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="heatflow.json"'

        return response

class UploadView(TemplateView):
    template_name = 'main/upload.html'

    def get(self, request):
        form = UploadForm()
        return render(request,self.template_name,{'form':form,})

    def post(self, request):
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            result = self.dry_run(request)

            # print(result.errors)

            if not result.has_errors():
                form.save()

            return render(request, 'main/confirm_upload.html', {'result':result,})

        args = {'form':form,'response':"Something wen't wrong!"}
        return render(request, self.template_name, args)

    @method_decorator(require_POST)
    def dry_run(self,request):
        resource = HeatFlowResource()

        data_file = request.FILES['data']
        dataset = Dataset().load(data_file.read().decode('utf-8'))

        # headers = dataset.headers.copy()
        # for header in dataset.headers.copy():
        #     if header == 'heatflow__corrected' or header == 'heatflow__uncorrected':
        #         continue
        #     has_data = False


        #     for cell in dataset[header]:
        #         if cell:
        #             has_data = True
        #             break
        #     if not has_data:
        #         del dataset[header]
        #         resource.Meta.export_order.remove(header)
        #         resource.Meta.fields.remove(header)
        #         # del resource.fields[header]
        #         resource.Meta.exclude.append(header)




        return resource.import_data(dataset=dataset, dry_run=True)


class ConfirmUploadView(TemplateView):
    template_name = 'main/confirm_upload.html'

    def get(self, request):
        return render(request,self.template_name)

class SiteView(TemplateView):
    template_name = "main/site_details.html"

    def get(self, request, site_id=None,  site_name=None):
        site = get_object_or_404(Site, pk=site_id)
        depth_intervals = site.depthinterval_set.order_by('depth_min','depth_max')

        point = serialize('geojson',[site],
                    geometry_field='geom',)

        return render(request,self.template_name,{'site':site,'mapbox_access_token':settings.MAPBOX_ACCESS_TOKEN,'point':point,'depth_intervals':depth_intervals})

def filter_data(request):

    form = parse_qs(request.GET['myform'])
    form = {k:v[0] if v[0] != 'on' else True for k,v in form.items()}

    qs = Site.objects.all()

    if form.get('heatflow__gte'):
        if form.get('hf_uncorrected') and form.get('hf_corrected'):
            qs = qs.filter(
                Q(heatflow__corrected__gte=form['heatflow__gte']) |
                Q(heatflow__uncorrected__gte=form['heatflow__gte'])
                ).distinct()
        elif form.get('hf_uncorrected') and not form.get('hf_corrected'):
            form['heatflow__uncorrected__gte'] = form['heatflow__gte']
        elif form.get('hf_corrected') and not form.get('hf_uncorrected'):
            form['heatflow__corrected__gte'] = form['heatflow__gte']

    if form.get('heatflow__lte'):
        if form.get('hf_uncorrected') and form.get('hf_corrected'):
            qs = qs.filter(
                Q(heatflow__corrected__lte=form['heatflow__lte']) |
                Q(heatflow__uncorrected__lte=form['heatflow__lte'])
                ).distinct()

        elif form.get('hf_uncorrected') and not form.get('hf_corrected'):
            form['heatflow__uncorrected__lte'] = form['heatflow__lte']

        elif form.get('hf_corrected') and not form.get('hf_uncorrected'):
            form['heatflow__corrected__lte'] = form['heatflow__lte']

    # delete logical form field because they cannot be used in filter
    for k in ['heatflow__gte','hf_uncorrected','hf_corrected']:
        if form.get(k):
            del form[k]

    for k,v in form.items():
        print(k,': ',v)

    qs = qs.filter(**form).distinct()

    print(qs.count())

    return JsonResponse(geojson_serializer(qs))


