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
from django.urls import reverse
from django.apps import apps
from meta.views import Meta, MetadataMixin
from thermoglobe.models import Publication
from tablib import Dataset

from thermoglobe import models, forms, choices, tables
from thermoglobe.resources import IntervalResource
from users.models import CustomUser

from . import utils
from .forms import ContactForm
from .models import Field, Page, News, FAQ
from django.views.generic import ListView
from bs4 import BeautifulSoup

class PageMetaMixin(MetadataMixin):
    page_id = None
    image = 'assets/main/images/equi_300.webp'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.get_page():
            context.update(page=self.get_page())
        return context

    def get_page(self, page_id=None):
        if page_id is None:
            page_id = self.page_id
        try:
            return Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return

    def get_meta_title(self, context):
        if self.get_page():
            if self.get_page().title:
                return self.get_page().title  + ' | Heatflow.org'
            else:
                return self.get_page().heading + ' | Heatflow.org'
        else:
            return 'Heatflow.org'

    def get_meta_keywords(self, context):
        if self.get_page():
            return self.get_page().keywords.split(',')

    def get_meta_description(self, context):
        if self.get_page():
            return mark_safe(self.get_page().description)


class HomeView(PageMetaMixin, TemplateView):
    template_name = 'home.html'
    model = models.Site
    page_id = 13

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        soup = BeautifulSoup(context['page'].content,features="html.parser")

        context.update(
            recently_added=Publication.objects.all().order_by(
                '-added')[:5],
            cards={
                'heat flow': {
                    'icon': 'HF',
                    'content': 'Heres some test heat flow content. This will come from the heat flow page eventually.',
                    'counts': self.heat_flow_counts(),
                    'link': reverse('thermoglobe:heat_flow'),
                },
                'thermal gradient': {
                    'icon': 'TG',
                    'content': 'Heres some test gradient content. This will come from the heat flow page eventually.',
                    'counts': self.gradient_counts(),
                    'link': reverse('thermoglobe:gradient'),
                },
                'temperature': {
                    'icon': 'T',
                    'content': 'Heres some test temperature content. This will come from the heat flow page eventually.',
                    'counts': self.temp_counts(),
                    # 'link': reverse('thermoglobe:temperature'),
                },
                'thermal conductivity': {
                    'icon': 'TC',
                    'content': 'Heres some test conductivity content. This will come from the heat flow page eventually.',
                    'counts': self.conductivity_counts(),
                    # 'link': reverse('thermoglobe:conductivity'),
                },
                'heat generation': {
                    'icon': 'HG',
                    'content': 'Heres some test heat generation content. This will come from the heat flow page eventually.',
                    'counts': self.heat_gen_counts(),
                    # 'link': reverse('thermoglobe:heat_gen'),
                },
            },
            content=[x.prettify() for x in soup.find_all('div')],
            publications = Publication.objects.all(),
        )

        return context

    def temp_counts(self):
        sites = models.Site.objects.all()
        return {
            'sites': models.Site.objects.temperature().count(),
            'measurements': models.Temperature.objects.count(),
            'temperature logs': models.Site.objects.annotate(temp_count=Count('temperature')).filter(temp_count__gte=3).distinct().count(),
        }

    def heat_flow_counts(self):
        return models.Interval.heat_flow.aggregate(**{
            'sites':Count('site',distinct=True),
            'corrected estimates':Count('heat_flow_corrected'),
            'uncorrected estimates':Count('heat_flow_uncorrected'),
        })

    def gradient_counts(self):
        return models.Interval.gradient.aggregate(**{
            'sites':Count('site',distinct=True),
            'corrected gradient':Count('gradient_corrected'),
            'uncorrected gradient':Count('gradient_uncorrected'),
        })

    def conductivity_counts(self):
        return {
                'sites': apps.get_model('thermoglobe','Site').objects.conductivity().count(),
                'measurements': models.Conductivity.objects.count(),
                'conductivity logs': models.Site.objects.annotate(cond_count=Count('conductivity')).filter(cond_count__gte=3).distinct().count(),
            }

    def heat_gen_counts(self):
        return {
                'sites': apps.get_model('thermoglobe','Site').objects.heat_generation().distinct().count(),
                'measurements': models.HeatGeneration.objects.count(),
                'heat generation logs': models.Site.objects.annotate(heat_gen_count=Count('heat_generation')).filter(heat_gen_count__gte=3).distinct().count(),

        }


class FieldDescriptionsView(PageMetaMixin, ListView):
    template_name = 'field_descriptions.html'
    model = Field
    page_id = 11

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_types'] = {choice[1]:Field.objects.filter(table=choice[0]) for choice in self.model.table_choices}
        return context


class PaginatorMixin(ListView):
    pag_neighbours = 4
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['range'] = self.paginator_fix(context['paginator'],context['page_obj'].number)
        return context

    def paginator_fix(self,paginator,page):
        if paginator.num_pages > 2*self.pag_neighbours:
            start_index = max(1, page-self.pag_neighbours)
            end_index = min(paginator.num_pages, page + self.pag_neighbours)
            if end_index < start_index + 2*self.pag_neighbours:
                end_index = start_index + 2*self.pag_neighbours
            elif start_index > end_index - 2*self.pag_neighbours:
                start_index = end_index - 2*self.pag_neighbours
            if start_index < 1:
                end_index -= start_index
                start_index = 1
            elif end_index > paginator.num_pages:
                start_index -= (end_index-paginator.num_pages)
                end_index = paginator.num_pages
            page_list = [f for f in range(start_index, end_index+1)]
            return page_list[:(2*self.pag_neighbours + 1)]
        else:
            return list(range(1,paginator.num_pages+1))


class NewsView(PageMetaMixin, PaginatorMixin):
    template_name = 'news.html'
    model = News
    page_id = 2


class FAQView(PageMetaMixin, PaginatorMixin):
    template_name = 'faqs.html'
    model = FAQ
    page_id = 4


class LandingPage(PageMetaMixin,TemplateView):
    template_name = 'landing_page.html'
    page_id = 16
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar'] = 'inactive'
        return context

