import json
from urllib.parse import parse_qs

from django.conf import settings
from django.contrib import messages
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.core.mail import send_mail
from django.core.serializers import deserialize, serialize
from django.db.models import Avg, Count, F, FloatField, Max, Min, Q, Value
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.html import mark_safe
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView
from meta.views import Meta, MetadataMixin
from publications.models import Publication
from tablib import Dataset

from thermoglobe import models, forms, choices
from thermoglobe.resources import HeatFlowResource
from thermoglobe.utils import get_db_summary
from users.models import CustomUser

from . import utils
from .forms import ContactForm
from .models import Field, Page


class PageMixin():

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.get_page().exists():
            context.update(page=self.get_page()[0])
        return context

    def get_page(self):
        try:
            return Page.objects.filter(title__iexact=self.title)
        except Page.DoesNotExist:
            pass


class PageMetaMixin(PageMixin, MetadataMixin):

    def get_meta_title(self, context):
        if self.get_page().exists():
            return self.get_page()[0].title + ' | Heatflow.org'
        else:
            return 'Heatflow.org'

    def get_meta_keywords(self, context):
        if self.get_page().exists():
            return self.get_page()[0].keywords.split(',')


    def get_meta_description(self, context):
        if self.get_page().exists():
            return mark_safe(self.get_page()[0].description)


class HomeView(PageMetaMixin, TemplateView):
    template_name = 'main/home.html'
    model = models.Site
    title = 'Home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sites = models.Site.objects.all()
        context['counts'] = {
            'individual sites': sites.count(),
            'heat flow estimates': models.HeatFlow.objects.all().count(),
            'temperature measurements': models.Temperature.objects.all().count(),
            'thermal conductivities': models.Conductivity.objects.all().count(),
            'heat generation': models.HeatGeneration.objects.all().count(),
            'references': Publication.objects.all().count(),
        }

        years = Publication.objects.aggregate(years=Max(
            'year', ouput_field=FloatField()) - Min('year', ouput_field=FloatField()))

        context.update(
            recently_added=Publication.objects.all().order_by(
                '-date_added')[:5],
            # 'page': utils.get_page_or_none(self.page_id),
            cards=[('publications', 'publications:publication_list'),
                    ('upload', 'thermoglobe:upload'),
                    ('resources', 'main:resources'), ],
            # ('cite','thermoglobe:upload'),],
        )

        return context


class ContactView(TemplateView):
    title = 'Contact Us'
    template_name = 'main/contact.html'
    model = CustomUser
    form = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = self.get_staff()
        context['form'] = self.form
        return context

    def get_staff(self):
        return self.model.objects.filter(is_staff=True)

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            sender_name = form.cleaned_data['name']
            sender_email = form.cleaned_data['email']

            message = "{0} has sent you a new message:\n\n{1}".format(
                sender_name, form.cleaned_data['message'])
            send_mail('New Enquiry', message,
                      sender_email, ['info@heatflow.org'])
            return HttpResponse('Thanks for contacting us!')

        return HttpResponse('Failed')


class AboutView(TemplateView):
    template_name = 'main/about.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ResourcesView(PageMetaMixin, TemplateView):
    template_name = 'main/resources.html'
    page_id = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = utils.get_page_or_none(self.page_id)

        return context


class FieldDescriptionsView(PageMetaMixin, TemplateView):
    template_name = 'main/field_descriptions.html'
    title = 'Field Descriptions'
    forms = {
        'site': forms.SiteForm,
        'heat_flow': forms.HeatFlowForm,
        # 'thermal_gradient': forms.GradientForm,
        'corrections': forms.CorrectionForm,
        'thermal_conductivity': forms.ConductivityForm,
        'heat_generation': forms.HeatGenForm,
        'temperature': forms.TemperatureForm,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = self.forms
        return context