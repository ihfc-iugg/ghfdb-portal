import json, zipfile
from django import forms
from django.contrib import messages
from django.core.serializers import deserialize, serialize
from django.db.models import Avg, Count, F, FloatField, Max, Min, Q, Value
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView, View, ListView
from django.db.models.functions import Cast, Coalesce
from django.utils.html import mark_safe
from django.apps import apps
from thermoglobe.mixins import TableMixin, DownloadMixin
import pandas as pd
from django_pandas.io import read_frame
from django.utils.text import slugify
from thermoglobe.forms import DownloadForm
from thermoglobe import choices
from djgeojson.serializers import Serializer as to_geojson
from meta.views import Meta, MetadataMixin

class Describe(TableMixin, TemplateView):
    template_name = 'describe.html'
    groupby_options = dict(
        country=['name','region','subregion'],
        continent=['name'],
        sea=['name'],
        basin=['name','region','province','location','sub_regime','sub_regime_group'],
        province=['name','type','group','last_orogen','continent','plate'],
        political=['name','territory','sovereign'],
        )

    def get_context_data(self, **kwargs):
        if self.kwargs.get('model',None) == 'favicon.ico':
            return {}
        context = super().get_context_data(**kwargs)
        context['page'] = {
            'heading':self.verbose_name_plural.title(),
            }
        context['description'] = mark_safe(self.model.model_description)
        context['table'] = self.get_table()
        context['data_types'] = self.get_data_types()
        context['groupby_options'] = self.groupby_to_select()
        context['table_title'] = ' '.join(self.data_type.split('_')).title()
        context['meta'] = Meta(
            title=f"{self.verbose_name.title()} | HeatFlow.org",
            keywords=[self.verbose_name, 'heat flow', 'thermal gradient','heat generation','thermal conductivity','temperature'],
            description=self.description(),
        )
        return context
    
    def groupby_to_select(self):
        return [[x,x.replace('_',' ').title()] for x in self.groupby_options.get(self.model_name)]
        
    def get_data_types(self):
        return [
            ['heat_flow', 'Heat Flow'],
            ['gradient', 'Thermal Gradient'],
            ['temperature', 'Temperature'],
            ['conductivity', 'Thermal Conductivity'],
            ['heatgeneration', 'Heat Generation'],
        ]

    @property
    def model_name(self):
        return self.kwargs.get('model')

    @property
    def data_type(self):
        return self.request.GET.get('data_type','heat_flow')

    @property
    def group_by(self):
        return self.request.GET.get('group_by','name')

    @property
    def model(self):
        return apps.get_model('mapping',self.model_name)

    @property
    def choices(self):
        choices = self.model._meta.get_field(self.group_by).choices
        if choices:
            return dict(choices)

    @property
    def verbose_name(self):
        return self.model._meta.verbose_name

    @property
    def verbose_name_plural(self):
        return self.model._meta.verbose_name_plural

    def get_queryset(self):
        if self.data_type in ['heat_flow','gradient']:
            qs = getattr(apps.get_model('thermoglobe','interval'),self.data_type)
        else:
            qs = apps.get_model('thermoglobe',self.data_type).objects
        return qs.filter(**{f"site__{self.model_name}__isnull":False})

    def apply_hyperlink(self, row):
        return mark_safe(f"<a href='{reverse('mapping:describe_field', kwargs={'model':self.model_name,'slug':row['slug']})}'>{row[self.group_by]}</a>")
        # else:
            # return row[self.group_by]

    def get_table(self):
        # get the queryset as a list of value/name
        # qs = list(self.get_queryset().values_list(self.data_type,f"site__{self.model_name}__{self.group_by}").distinct())
        qs = list(self.get_queryset().values_list(self.data_type,f"site__{self.model_name}__{self.group_by}"))

        # turn into a pandas dataframe, stats are way easier to caluclate this way
        data = pd.DataFrame(qs, columns=[self.data_type,self.group_by])

        # groupby "name", calculate stats and round to 2 decimal places
        groups = data.groupby(self.group_by)
        data = groups.describe()[self.data_type].round(2)
        data['median'] = groups.median()[self.data_type].round(2)

        # pulls the target group by function out of the index and into a column
        data.reset_index(level=0, inplace=True)

        # add the name (converted to an index during groupby) as a column
        if self.choices:
            data[self.group_by] = data[self.group_by].map(lambda x: self.choices.get(x,'undefined'))

        # add slugs to data
        if self.group_by == 'name':
            slugs = pd.DataFrame(list(self.model.objects.values_list(self.group_by,'slug')),  columns=[self.group_by,'slug'])
            data = pd.merge(data,slugs,on=self.group_by)

            # apply hyperlinks to first columns
            data[self.group_by] = data[[self.group_by,'slug']].apply(self.apply_hyperlink,axis=1)
            data.drop('slug',inplace=True,axis=1)

        # explicitly define our columns and rearrange the dataset
        columns = [self.group_by,'count','median','mean','std','min','25%','50%','75%','max']
        data = data[columns]

        # replace Nan values with blanks
        data.fillna('',inplace=True)

        return dict(
            id=self.model_name,
            data=json.dumps(data.values.tolist()),
            columns = [d.title() for d in columns]
            )

    def description(self):
        return f'An interactive table of descriptive statistics covering all {self.verbose_name_plural} of the world. Compute statistics for heat flow, thermal gradient, temperature, thermal conductivity and heat generation.'

class DescribeField(TableMixin,  DownloadMixin, DetailView):
    template_name = 'describe_field.html'
    # options = {'pageLength':50}
    tables = dict(
        intervals=['depth_min','depth_max','heat_flow','gradient'],
        conductivity=['count','depth_min','depth_max','min_conductivity','max_conductivity'],
        temperature=['count','depth_min','depth_max','min_temperature','max_temperature'],
        heat_generation=['count','depth_min','depth_max','min_heat_generation','max_heat_generation'],
    )
    download_form = DownloadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_object().name

        context['meta'] = Meta(
            title=f"{self.get_object().name} | HeatFlow.org",
            keywords=[self.get_object().name, self.model._meta.verbose_name,'download','access','data','datsets','heat flow', 'thermal gradient','heat generation','thermal conductivity','temperature'],
            description=self.description(),
        )


        context['tables'] = {}
        for table, fields in self.tables.items():
            context['tables'][table.replace('_',' ')] = self.get_table(table, fields)

        for table in context['tables'].values():
            if table['data']:
                table['active'] = True
                break
        return context
    
    def get(self,request,*args, **kwargs):
        if request.is_ajax():
            """plots are generated here through ajax requests"""
            map_data = to_geojson().serialize(
                queryset=self.get_object().sites.all(), 
                properties='')              
            return JsonResponse({'data': map_data})

        return super().get(request,*args, **kwargs)

    def get_queryset(self):
        if self.data_type in ['heat_flow','gradient']:
            qs = getattr(apps.get_model('thermoglobe','interval'),self.data_type)
        else:
            qs = apps.get_model('thermoglobe',self.data_type).objects
        return qs.filter(**{f"site__{self.model_name}__isnull":False})

    def get_object(self):
        qs = self.model.objects.filter(slug=self.slug)
        if qs.count() == 1:
            return qs[0]
    
    def get_table(self,data_type, fields):
        fields = ['slug','site_name','latitude','longitude'] + fields
        qs = (apps.get_model('thermoglobe','Site')
                .objects.filter(**{self.model_name:self.get_object()})
                .table(data_type)
                .values_list(*fields)
        )
        return dict(
            id=slugify(data_type),
            data=json.dumps(list(qs)),
            columns=[field.replace('_',' ') for field in fields],
            )

    @property
    def slug(self):
        return self.kwargs.get('slug')

    @property
    def model_name(self):
        return self.kwargs.get('model')

    @property
    def model(self):
        return apps.get_model('mapping',self.model_name)

    @property
    def choices(self):
        choices = self.model._meta.get_field(self.group_by).choices
        if choices:
            return dict(choices)

    def description(self):
        return f"View and download all thermal data related to the {self.model._meta.verbose_name} {self.get_object().name.title()} from the ThermoGlobe database."