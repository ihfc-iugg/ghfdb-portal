from django.db import models
import plotly.graph_objects as go
import plotly.express as px
from django.utils.html import mark_safe
import numpy as np
from thermoglobe.utils import Hyperlink, Round
from django.db.models.functions import Coalesce
from django.db.models import Avg, Count, F, FloatField, Max, Min, Q, Value, Case, When, StdDev
import plotly.io as pio
import pandas as pd
from plotly.subplots import make_subplots
from collections import Counter

def options(file_name):
    return dict(
    include_plotlyjs=False,
    full_html=False,
    config={
        'responsive': True,
        'toImageButtonOptions': {
            'format': 'svg', # one of png, svg, jpeg, webp
            'filename': file_name,
            'height': None,
            'width': None,
            # 'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
            }
        }
    )




class SiteQS(models.QuerySet):

    def pie(self, field, n=5, include_other=True,**kwargs):
        """Generates a pie chart from the given dataset

        Args:
            groupby (str): Name of the dataframe column to group values by.
            property (str, optional): Name of the dataframe column to calculate statistical data from.
            n_to_include (int, optional): Number of groups to include in the final plot. Use to improve appearance when plotting data with lots of values (e.g. countries). Defaults to the 10.
            include_other (bool, optional): Whether to include a calculated field called 'other' to represent data not in the n_to_include number of items. Defaults to True.

        """
        data = (self.filter(**{f'{field}__isnull':False})
            .annotate(value=F(f'{field}__name'))
            .values_list('id','value')
        )
        data = Counter([x[1] for x in list(data)]).most_common()
        if not data:
            return ''

        vals = data[:n]
        if len(vals) == n and len(data) > n:
            vals.append(('Other',sum([x[1] for x in data[n:]])))

        fig = go.Figure(data=[go.Pie(
            labels=[x[0] for x in vals],
            values=[x[1] for x in vals], 
            textinfo='label,value')])

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(0,0,0,0)',
            showlegend=False,
            )
        
        return mark_safe(fig.to_html(**options('{}_pie_chart'.format(self.__class__.__name__))))

    def pie_country(self):
        return self.pie('country')

    def pie_sea(self):
        return self.pie('sea')

    def pie_data_counts(self):
        data = self.aggregate(
            Count('heat_flow'),
            Count('gradient'),
            Count('temperature'),
            Count('conductivity'),
            Count('heat_generation'),
        )

        data = {k:v for k,v in data.items() if v}

        fig = go.Figure(data=[go.Pie(
            labels=[key.split('__')[0] for key in data.keys()],
            values=list(data.values()), 
            textinfo='label,value')])

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(0,0,0,0)',
            showlegend=False,
            )
        
        return mark_safe(fig.to_html(**options('{}_pie_chart'.format(self.__class__.__name__))))

    def heat_flow(self):
        return self.annotate(**{           
            'heat_flow': Round(Avg(Coalesce('intervals__heat_flow_corrected', 'intervals__heat_flow_uncorrected'))),
            'depth_min': Min('intervals__depth_min'),
            'depth_max': Max('intervals__depth_min'),
        }).exclude(heat_flow__isnull=True)

    def gradient(self):
        return self.annotate(**{           
            'gradient': Round(Avg(Coalesce('intervals__gradient_corrected', 'intervals__gradient_uncorrected'))),
            'depth_min': Min('intervals__depth_min'),
            'depth_max': Max('intervals__depth_min'),
        }).exclude(gradient__isnull=True)
        # return self.annotate(value=F('gradient')).distinct()

    def temperature(self):
        return self.exclude(temperature__isnull=True).annotate(
            count=Count('temperature'),
            min_temperature=Min('temperature__temperature'),
            max_temperature=Max('temperature__temperature'),
            depth_min=Min('temperature__depth'),
            depth_max=Max('temperature__depth'),
            )

    def conductivity(self):
        return self.exclude(conductivity__isnull=True).annotate(
            count=Count('conductivity'),
            std=StdDev('conductivity__conductivity'),
            avg_conductivity=Round(Avg('conductivity__conductivity')),
            min_conductivity=Min('conductivity__conductivity'),
            max_conductivity=Max('conductivity__conductivity'),
            depth_min=Min('conductivity__depth'),
            depth_max=Max('conductivity__depth'),
            )

    def heat_generation(self):
        return self.exclude(heat_generation__isnull=True).annotate(
            count=Count('heat_generation'),
            avg_heat_generation=Round(Avg('heat_generation__heat_generation')),
            min_heat_generation=Min('heat_generation__heat_generation'),
            max_heat_generation=Max('heat_generation__heat_generation'),
            depth_min=Min('heat_generation__depth'),
            depth_max=Max('heat_generation__depth'),
            )

    def table(self,data_type):
        return getattr(self,data_type)()

    def intervals(self):
        return self.annotate(**{           
            'heat_flow': Round(Avg(Coalesce('intervals__heat_flow_corrected', 'intervals__heat_flow_uncorrected'))),
            'gradient': Round(Avg(Coalesce('intervals__gradient_corrected', 'intervals__gradient_uncorrected'))),
            'depth_min': Min('intervals__depth_min'),
            'depth_max': Max('intervals__depth_min'),
        })

class SiteManager(models.Manager):

    def get_queryset(self):
        return SiteQS(self.model, using=self._db).annotate(**{           
            'heat_flow': Round(Avg(Coalesce('intervals__heat_flow_corrected', 'intervals__heat_flow_uncorrected'))),
            'gradient': Round(Avg(Coalesce('intervals__gradient_corrected', 'intervals__gradient_uncorrected'))),
            'depth_min': Min('intervals__depth_min'),
            'depth_max': Max('intervals__depth_min'),
        })

    @property
    def heat_flow(self):
        return self.get_queryset().heat_flow()

    @property
    def gradient(self):
        return self.get_queryset().gradient()

    @property
    def temperature(self):
        return self.get_queryset().temperature()

    @property
    def conductivity(self):
        return self.get_queryset().conductivity()

    @property
    def heat_generation(self):
        return self.get_queryset().heat_generation()


class HeatFlowManager(models.Manager):

    def get_queryset(self):
        return (super().get_queryset()
        .annotate(heat_flow=Coalesce('heat_flow_corrected', 'heat_flow_uncorrected'))
        .exclude(heat_flow__isnull=True)
        )

class GradientManager(models.Manager):

    def get_queryset(self):
        return (super().get_queryset()
        .annotate(gradient=Coalesce('gradient_corrected', 'gradient_uncorrected'))
        .exclude(gradient__isnull=True)
        )
