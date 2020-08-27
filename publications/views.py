import csv
import json

import bibtexparser as bib
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers import serialize
from django.db.models import (Avg, Count, F, FloatField, Func, Max, Min, Q,
                              Sum, Value)
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView
from django_filters.views import FilterView
from meta.views import Meta
import numpy as np
from django.utils.html import mark_safe

from main.utils import get_page_or_none
from main.views import PageMixin, PageMetaMixin
from thermoglobe.views import HEATFLOW_FIELDS 
from thermoglobe import plots, tables, utils
from thermoglobe.models import HeatFlow, Site

from .filters import PublicationFilter
from .forms import PublicationForm
from .mixins import CustomListView
from .models import Author, Operator, Publication
from tables.mixins import TableMixin, MultiTableMixin

class TableMetaMixin(TableMixin, PageMetaMixin):

    def get_dataset(self):
        return json.dumps(list(self.get_queryset()))


class PublicationListView(TableMetaMixin, ListView):
    title = 'Publications'
    model = Publication
    template_name = "publications/table.html"
    table_headers = ['slug', 'bibtex','doi', 'type','author', 'title', 'year', 'journal','publisher']
    counts = ['sites','heatflow','thermalgradient','temperature','conductivity','heatgeneration']


    def get_queryset(self):
        return super().get_queryset().exclude(bibtex__exact='').prefetch_related('authors').values('slug','bibtex')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['bibtex_headers'] = ['doi', 'author', 'title', 'year', 'journal']
        x = 1 if 'slug' in self.table_headers else 0
        context['complex_headers'] = [[len(context['bibtex_headers']) + x, ''], [5, 'Data Counts']]

        context['table'] = self.table(
                headers = self.table_headers,
                options = {
                    'dom': '<"top d-flex justify-content-around align-items-center"lpf>t<"bottom"ip><"clear">',
                    'order': [[4, 'desc'], [1, 'asc']],
                    'pageLength': 50,
                    'link_url': '/thermoglobe/publications/',
                    },
                link = '/thermoglobe/publications/',
                ID= 'publicationTable',
                )

        return context

    def combine_counts(self):
        result = [
            self.get_queryset().annotate(Count(c)).values_list(c+'__count') for c in self.counts
        ]
        result = np.concatenate([self.get_queryset(),np.array(result).transpose()[0]],axis=1).tolist()
        return [{a:b for a,b in zip(self.table_headers,x)} for x in result]


class PublicationDetailsView(MultiTableMixin, DetailView):
    template_name = "publications/publication_details.html"
    model = Publication
    tables = [  tables.Site,
                tables.HeatFlow,
                # tables.ThermalGradient,
                tables.Temperature,
                tables.Conductivity,
                tables.HeatGeneration,
                ]
    filter_object_on = 'reference'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['figures'] = {
            'temp_profile': context['tables'].get('temperature').plot_profile()

        }
        for i, fig in enumerate(context['figures'].values()):
            fig.number = i+1

        context['bibtex'] = json.dumps(self.get_object().bibtex)
        context['meta'] = self.get_object().as_meta(self.request)
        context['sites'] = self.get_object().sites.count()
        context['map'] = dict(
            display=True,
            cluster=True,
            color=True,
        )
        return context

    def post(self, request, pk):
        my_csv = HeatFlow.objects.filter(reference=pk).values_list(
            *[field[0] for field in HEATFLOW_FIELDS])
        filename = '{}.csv'.format(self.model.objects.get(id=pk))

        # prepare the response for csv file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            filename)
        writer = csv.writer(response)

        # write the header row; remove "site__" prefix for some fields for clarity
        writer.writerow([field[1] for field in HEATFLOW_FIELDS])

        # write the rows to the csv file
        for i in my_csv:
            writer.writerow(i)
        return response


class AuthorListView(TableMetaMixin, ListView):
    model = Author
    title = 'Authors'
    template_name = "publications/table.html"
    table_link_url = 'reference:author_list'
    table_fields = ['last_name', 'first_name', 'total_publications', 'slug']
    table_options = dict(
        order=[[4, 'desc']],
        pageLength=50,
        columnDefs=[dict(
            targets=2,
            visible=False,
            searchable=False
        ), ]
    )

    def get_queryset(self):
        return super().get_queryset().annotate(
            total_publications=Count('publications')
        ).values_list(*self.table_fields)


class AuthorDetailsView(DetailView):
    details_url = 'reference:publication_list'
    template_name = "publications/author_details.html"
    model = Author
    site_lookup = 'reference__first_author'
    details_url = 'reference:publication_list'
    table_fields = ['slug', 'bibtex', '_heat_flow', '_thermal_gradient',
                    '_temperature', '_thermal_conductivity', '_heat_generation', ]
    table_options = json.dumps(dict(
        order=[[4, 'desc'], ],
        pageLength=100,
        dom='<"top d-flex justify-content-between align-content-center"fi>t<"bottom"><"clear">',
    ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        x = 1 if 'slug' in self.table_fields else 0
        context.update(dict(
            object_url=self.details_url,
            table_options=self.table_options,
            table_fields=self.table_fields,
            dataset=list(context['object'].get_publications().values(
                *self.table_fields)),
            bibtex_headers=['doi', 'author', 'title', 'year', 'journal'],
            figures={
                'contributions':    {
                    'id': 'ContributionsPerYear',
                    'data': [plots.publications_per_year(context['object'].get_publications())],
                },
                'counts': {
                    'id': 'data_counts',
                    'data': context['object'].data_counts(),
                }
            }
        ))
        context['complex_headers'] = [
            [len(context['bibtex_headers']) + x, ''], [5, 'Data Counts']]

        return context

    def get_sites(self, context):
        return Site.objects.filter(**{self.site_lookup: context['author']})


def annotate_data_average(qs):
    return qs.annotate(
        _heat_flow=utils.Round(Avg('heatflow__corrected')),
        _thermal_gradient=utils.Round(Avg('thermalgradient__corrected')),
        _temperature=utils.Round(Avg('temperature__value')),
        _thermal_conductivity=utils.Round(Avg('conductivity__value')),
        _heat_generation=utils.Round(Avg('heatgeneration__value')),
    )


def publication_data(request, slug):
    fields = ['latitude', 'longitude']
    r = JsonResponse({
        'columns': ['Site Name','Latitude','Longitude','Heat Flow'],
        'data': list(Site.objects.filter(reference__slug=slug).annotate(heat_flow=utils.Round(Avg('heatflow__corrected'))).values_list(*fields))
    })
    return r
