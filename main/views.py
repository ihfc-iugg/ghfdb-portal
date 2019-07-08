from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
# from .forms import DownloadForm, UploadForm
from .resources import HeatFlowResource
# from .filters import SiteFilter, HeatflowFilter, ConductivityFilter, HeatGenFilter, ReferenceFilter
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

def form_setup(form=None,menu_title=None):
    return {'form':form,'menu_title':menu_title}

# Create your views here.
class DatabaseView(TemplateView):
    template_name = 'database/database.html'
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
        context['points'] = serialize('geojson',self.get_queryset(), geometry_field='geom')
        return context

    def get_queryset(self):
        return Site.objects.all()
    
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
    template_name = 'database/upload.html'

    def get(self, request):
        form = UploadForm()
        return render(request,self.template_name,{'form':form})

    def post(self, request):
        form = UploadForm(request.POST)
        if form.is_valid():
            result = self.dry_run(request)
            return render(request, 'database/upload_confirm.html', {'result':result})

        args = {'form':form,'text':text,'response':"Something wen't wrong!"}
        return render(request, self.template_name, args)

    @method_decorator(require_POST)
    def dry_run(self,request):
        resource = HFResource()
        data_file = request.FILES['dataFile']
        dataset = Dataset().load(data_file.read().decode('utf-8'))
        result = resource.import_data(dataset=dataset, dry_run=True)  # Test the data import
        # print(result.has_errors())
        # if not result.has_errors():
        #     hf_resource.import_data(dataset, dry_run=False)  # Actually import now
        return result

class ConfirmUploadView(TemplateView):
    template_name = 'database/confirm_upload.html'

    def get(self, request):
        return render(request,self.template_name)

class SiteView(TemplateView):
    template_name = "database/site_details.html"

    def get(self, request, site_id=None,  site_name=None):
        site = get_object_or_404(Site, pk=site_id)
        all_heatflow = site.heatflow_set.order_by('depth__depth','depth__minimum')

        point = serialize('geojson',[site],
                    geometry_field='geom',)

        return render(request,self.template_name,{'site':site,'mapbox_access_token':settings.MAPBOX_ACCESS_TOKEN,'point':point,'all_heatflow':all_heatflow})




def filter_data(request):

    q = parse_qs(request.GET['myform'])
    q = {k:v[0] if v[0] != 'on' else True for k,v in q.items()}



    if 'heat_generation_toggle' not in q.keys():
        q['heatgeneration__isnull'] = False

    # Site.objects.filter(Q(heatgeneration__isnull=True) & )


    for k,v in q.items():
        print(k,': ',v)
    return HttpResponse(serialize('geojson', Site.objects.filter(**q), geometry_field='geom',))


