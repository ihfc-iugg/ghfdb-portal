from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView
from .forms import DownloadForm, UploadForm, ContactForm
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
from django.db.models import Avg, Max, Min, Count, F, Value, Q, FloatField
from reference.models import FileStorage
from .utils import get_db_summary
from users.models import CustomUser
from django.core.mail import send_mail
from reference.models import Reference

# Create your views here.
class UploadView(TemplateView):
    template_name = 'main/upload.html'
    form = UploadForm
    resource = HeatFlowResource

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form  
        # print(context['form'].__dict__.items())
        return context

    def post(self, request):
        form = self.form(request.POST, request.FILES)
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
        # resource = HeatFlowResource()

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

class SiteView(DetailView):
    template_name = "main/site_details.html"
    model = Site
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['depth_intervals'] = context['object'].depthinterval_set.order_by('depth_min','depth_max')
        context['points'] = serialize('geojson',[context['object']],geometry_field='geom',)
        return context




















