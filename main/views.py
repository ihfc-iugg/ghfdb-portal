from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView
from .forms import DownloadForm, UploadForm, ContactForm
from thermoglobe.resources import HeatFlowResource
from tablib import Dataset
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.conf import settings
from thermoglobe.models import Site, DepthInterval
from django.core.serializers import serialize, deserialize
from django.contrib.gis.db.models.functions import AsGeoJSON
from urllib.parse import parse_qs
import json
from django.db.models import Avg, Max, Min, Count, F, Value, Q, FloatField
from reference.models import FileStorage
from thermoglobe.utils import get_db_summary
from users.models import CustomUser
from django.core.mail import send_mail
from reference.models import Reference
from .models import Page

# Create your views here.
class HomeView(TemplateView):
    template_name= 'main/home.html'
    model = Site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sites = Site.objects.all()

        num_years = (Max('reference__year', ouput_field=FloatField()) - 
            Min('reference__year', ouput_field=FloatField()))

        context['db'] = sites.aggregate(
            Count('heatflow',distinct=True),
            Count('conductivity',distinct=True),
            Count('heatgeneration',distinct=True),
            Count('temperature',distinct=True),
            Count('reference', distinct=True),
            years=num_years,)
        
        context['recently_added'] = Reference.objects.all().order_by('-date_added')[:5]

        context['page'] = Page.objects.get(name='Home')

        context['nav_images'] = [   ('publications','.jpg','reference:reference_list'),
                                    ('upload','.jpg','thermoglobe:upload'),
                                    ('resources','.jpg','main:resources'),
                                    ('cite','.jpg','thermoglobe:upload'),]

        return context

class ContactView(TemplateView):
    template_name= 'main/contact.html'
    model = CustomUser
    form = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contacts"] = self.get_superusers() 
        context['form'] = self.form  
        return context
    
    def get_superusers(self):
        return self.model.objects.filter(is_staff=True)

    def post(self,request):
        form = self.form(request.POST)
        if form.is_valid():
            sender_name = form.cleaned_data['name']
            sender_email = form.cleaned_data['email']

            message = "{0} has sent you a new message:\n\n{1}".format(sender_name, form.cleaned_data['message'])
            send_mail('New Enquiry', message, sender_email, ['info@heatflow.org'])
            return HttpResponse('Thanks for contacting us!')

        return HttpResponse('Failed')

class AboutView(TemplateView):
    template_name= 'main/about.html'

class ResourcesView(TemplateView):
    template_name = 'main/resources.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context[""] = 
        return context
    





















