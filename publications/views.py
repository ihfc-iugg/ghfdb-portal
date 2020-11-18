import csv
import json
import zipfile
from io import StringIO
from datetime import datetime

import bibtexparser as bib
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers import serialize
from django.db.models import (Avg, Count, F, FloatField, Func, Max, Min, Q,
                              Sum, Value)
from django.apps import apps
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone, text
from django.views.generic import DetailView, ListView, TemplateView
from django_filters.views import FilterView
from meta.views import Meta, MetadataMixin
import numpy as np
from django.utils.html import mark_safe

from main.utils import get_page_or_none
from main.views import PageMixin, PageMetaMixin
from thermoglobe.views import HEATFLOW_FIELDS 
from thermoglobe import plots, tables, utils, choices
from thermoglobe.models import Interval, Site, Temperature, Conductivity, HeatGeneration, Author, Publication
from thermoglobe.mixins import DownloadMixin 
from .filters import PublicationFilter
from .forms import PublicationForm
from .mixins import CustomListView
from djgeojson.views import GeoJSONSerializer, GeoJSONResponseMixin
from tables.mixins import TableMixin, MultiTableMixin

class TableMetaMixin(TableMixin, PageMetaMixin):

    def get_dataset(self):
        return json.dumps(list(self.get_queryset()))


class PublicationListView(TableMetaMixin, ListView):
    page_id = 10
    model = Publication
    template_name = "publications/publication_list.html"
    column_headers = ['slug', 'doi', 'type','author', 'title', 'year', 'journal','publisher']

    # table options to pass to dataTables.js Table constructor
    options = dict(
        autoWidth=False,
        dom='<"top d-flex justify-content-around align-items-baseline"lpf>t<"bottom"ip><"clear">',
        order_by='year',
        pageLength=50,
        deferRender=True,
        responsive=True,
    )

    def get_queryset(self):
        return super().get_queryset().exclude(bibtex__exact='').values('slug','bibtex')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['table'] = dict(id='publicationTable',
            # data = list(self.get_queryset()),
            columns = self.column_headers,
            )
        context['options'] = mark_safe(json.dumps(self.options))

        return context

    def get(self,request,*args, **kwargs):
        if request.is_ajax():
            return JsonResponse({'data':list(self.get_queryset())})
        return super().get(request,*args, **kwargs)


class PublicationDetailsView(DownloadMixin, MetadataMixin, DetailView):
    template_name = "publications/publication_details.html"
    model = Publication

    # table options to pass to dataTables.js Table constructor
    options = dict(
        autoWidth=False,
        dom='<"top d-flex justify-content-around align-items-baseline"lpf>t<"bottom"ip><"clear">',
        order_by='year',
        pageLength=50,
        deferRender=True,
        responsive=True,
    )
    tables = dict(
        heat_flow=['depth_min','depth_max','heat_flow'],
        gradient=['depth_min','depth_max','gradient'],
        conductivity=['count','depth_min','depth_max','min_conductivity','max_conductivity'],
        temperature=['count','depth_min','depth_max','min_temperature','max_temperature'],
        heat_generation=['count','depth_min','depth_max','min_heat_generation','max_heat_generation'],
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bibtex'] = json.dumps(self.get_object().bibtex)
        context['meta'] = self.get_object().as_meta(self.request)
        context['options'] = json.dumps(self.options)
        context['tables'] = {}

        for table, fields in self.tables.items():
            context['tables'][table.replace('_',' ')] = self.get_table(table, fields)

        for table in context['tables'].values():
            if table['data']:
                table['active'] = True
                break


        return context


    def post(self, request,  *args, **kwargs):
        # prepare the response for csv file
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(self.get_object().pk)
        zf = zipfile.ZipFile(response,'w')

        for key, qs in self.get_object().get_data().items():
            if qs.exists():
                export_fields = getattr(choices, key).get('detailed') + ['reference__bib_id']
                site_fields = [f.name for f in Site._meta.fields]
                query_fields = ['site__'+field if field in site_fields else field for field in export_fields ]
                # if key in ['temperature','conductivity','heat_generation']:
                #     query_fields[query_fields.index(key)] = 'value'

                # create a csv file an save it to the zip object
                zf.writestr('{}.csv'.format(key),self.csv_to_bytes(qs.values_list(*query_fields), export_fields))

        # add bibtex file to zip object
        zf.writestr('{}.bib'.format(self.get_object().bib_id),self.bibtex_to_bytes([self.get_object().bibtex]))

        return response

    def get_table(self,data_type, fields):
        fields = ['slug','site_name','latitude','longitude'] + fields
        qs = (apps.get_model('thermoglobe','Site')
                .objects.filter(reference=self.get_object())
                .table(data_type)
                .values_list(*fields)
        )
        return dict(
            id=text.slugify(data_type),
            data=json.dumps(list(qs)),
            columns=[field.replace('_',' ') for field in fields],
            )


# class PublicationDetailsView(DownloadMixin, MultiTableMixin, MetadataMixin, DetailView):
#     template_name = "publications/publication_details.html"
#     model = Publication

#     # table options to pass to dataTables.js Table constructor
#     options = dict(
#         autoWidth=False,
#         dom='<"top d-flex justify-content-around align-items-baseline"lpf>t<"bottom"ip><"clear">',
#         order_by='year',
#         pageLength=50,
#         deferRender=True,
#         responsive=True,
#     )

#     # tables = [  tables.Site,
#     #             tables.Interval,
#     #             tables.Temperature,
#     #             tables.Conductivity,
#     #             tables.HeatGeneration,
#     #             ]

#     tables = ['heat_flow','gradient','conductivity','temperature','heat_generation']

#     filter_object_on = 'reference'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['bibtex'] = json.dumps(self.get_object().bibtex)
#         context['meta'] = self.get_object().as_meta(self.request)
#         return context


#     def post(self, request,  *args, **kwargs):
#         # prepare the response for csv file
#         response = HttpResponse(content_type='application/zip')
#         response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(self.get_object().pk)
#         zf = zipfile.ZipFile(response,'w')

#         for key, qs in self.get_object().get_data().items():
#             if qs.exists():
#                 export_fields = getattr(choices, key).get('detailed') + ['reference__bib_id']
#                 site_fields = [f.name for f in Site._meta.fields]
#                 query_fields = ['site__'+field if field in site_fields else field for field in export_fields ]
#                 if key in ['temperature','conductivity','heat_generation']:
#                     query_fields[query_fields.index(key)] = 'value'

#                 # create a csv file an save it to the zip object
#                 zf.writestr('{}.csv'.format(key),self.csv_to_bytes(qs.values_list(*query_fields), export_fields))

#         # add bibtex file to zip object
#         zf.writestr('{}.bib'.format(self.get_object().bib_id),self.bibtex_to_bytes([self.get_object().bibtex]))

#         return response

class AuthorDetailsView(DownloadMixin, TableMixin, MetadataMixin, DetailView):
    template_name = "publications/author_details.html"
    model = Author
    column_headers = ['slug', 'doi', 'year', 'reference']
    options = dict(
        autoWidth=False,
        dom='<"top d-flex justify-content-end align-items-baseline"f>t<"bottom"i><"clear">',
        order_by='year',
        pageLength=100,
        deferRender=True,
        responsive=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = dict(id='publicationTable',
            columns = self.column_headers,
            )
        context['options'] = mark_safe(json.dumps(self.options))
        context['meta'] = self.get_object().as_meta(self.request)
        return context
    
    def get_sites(self, context):
        return Site.objects.filter(reference__first_author=context['author'])

    def get(self,request,*args, **kwargs):
        if request.is_ajax():
            return JsonResponse({'data':list(self.get_publications())})
        return super().get(request,*args, **kwargs)

    def post(self, request,  *args, **kwargs):
        # prepare the response for csv file
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(self.get_object().slug)
        zf = zipfile.ZipFile(response,'w')

        for key, qs in self.get_object().get_data().items():
            if qs.exists():
                export_fields = getattr(choices, key).get('detailed') + ['reference__bib_id']
                site_fields = [f.name for f in Site._meta.fields]
                query_fields = ['site__'+field if field in site_fields else field for field in export_fields ]
                if key in ['temperature','conductivity','heat_generation']:
                    query_fields[query_fields.index(key)] = 'value'

                # create a csv file an save it to the zip object
                zf.writestr('{}.csv'.format(key),self.csv_to_bytes(qs.values_list(*query_fields), export_fields))

        # add bibtex file to zip object
        zf.writestr('{}.bib'.format(self.get_object().slug),self.bibtex_to_bytes(
            self.get_publications().values_list('bibtex',flat=True)
            ))

        return response

    def get_publications(self):
        return self.get_object().get_publications().exclude(bibtex__exact='').values('slug','bibtex')


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
