from reference.models import Reference
from . import utils, forms
from .models import Field
from thermoglobe import models
from thermoglobe.resources import HeatFlowResource
from reference.models import Upload
from thermoglobe.utils import get_db_summary
from users.models import CustomUser
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from tablib import Dataset
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.conf import settings
from thermoglobe import models
from django.core.serializers import serialize, deserialize
from django.contrib.gis.db.models.functions import AsGeoJSON
from urllib.parse import parse_qs
import json
from django.db.models import Avg, Max, Min, Count, F, Value, Q, FloatField

from django.core.mail import send_mail


# Create your views here.
class HomeView(TemplateView):
    template_name= 'main/home.html'
    model = models.Site
    page_id = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sites = models.Site.objects.all()
        context['counts'] = {
            'individual sites': sites.count(),
            'heat flow estimates': models.HeatFlow.objects.all().count(),
            'temperature measurements': models.Temperature.objects.all().count(),
            'thermal conductivities': models.Conductivity.objects.all().count(),
            'heat generation': models.HeatGeneration.objects.all().count(),
            'references': Reference.objects.all().count(),
        }

        
        years = Reference.objects.aggregate(years = Max('year', ouput_field=FloatField()) - Min('year', ouput_field=FloatField()))

        context.update({
            'recently_added': Reference.objects.all().order_by('-date_added')[:5],
            'page': utils.get_page_or_none(self.page_id),
            'cards': [  ('publications','reference:publication_list'),
                        ('upload','thermoglobe:upload'),
                        ('resources','main:resources'),],
                        # ('cite','thermoglobe:upload'),],
        })

        return context

class ContactView(TemplateView):
    template_name= 'main/contact.html'
    model = CustomUser
    form = forms.ContactForm
    page_id = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = self.get_staff() 
        context['form'] = self.form  
        context['page'] = utils.get_page_or_none(self.page_id)

        return context
    
    def get_staff(self):
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
    page_id = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = utils.get_page_or_none(self.page_id)
        # context['contacts'] = self.get_staff() 
        return context

    # def get_staff(self):
    #     return self.model.objects.filter(is_staff=True)

class ResourcesView(TemplateView):
    template_name = 'main/resources.html'
    page_id = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = utils.get_page_or_none(self.page_id)

        return context
    
class FieldDescriptionsView(ListView):
    template_name = 'main/field_descriptions.html'
    model = Field
    page_id = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = utils.get_page_or_none(self.page_id)

        return context




















