from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .forms import DownloadForm, UploadForm
from .resources import HeatFlowResource
from tablib import Dataset
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import Site, DepthInterval
from django.core.serializers import serialize, deserialize
from django.contrib.gis.db.models.functions import AsGeoJSON
from urllib.parse import parse_qs
import json
from django.db.models import Avg, Max, Min, Count, F, Value, Q
from reference.models import FileStorage
from .utils import get_db_summary

# Create your views here.
class HomeView(TemplateView):
    template_name= 'main/home.html'
    model = Site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sites = Site.objects.all()

        context['db'] = sites.aggregate(
            Max('reference__year'),
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

class UploadView(TemplateView):
    template_name = 'main/upload.html'

    def get(self, request):
        form = UploadForm()
        return render(request,self.template_name,{'form':form,})

    def post(self, request):
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            result = self.dry_run(request)

            """UNCOMMENT TO SAVE FILES TO SERVER"""
            # if not result.has_errors():
            #     form.save()

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






















