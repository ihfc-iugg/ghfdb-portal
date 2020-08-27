from . import models
from tables.tables import Table
import plotly.graph_objects as go
import plotly.express as px
from django.utils.html import mark_safe
# import plotly.figure_factory as ff
import numpy as np
from thermoglobe.utils import Hyperlink

def options(file_name):
    return dict(
    include_plotlyjs='cdn',
    full_html=False,
    config={
        'toImageButtonOptions': {
            'format': 'svg', # one of png, svg, jpeg, webp
            'filename': file_name,
            'height': None,
            'width': None,
            'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
            }
        }
    )

class Site(Table):

    class Meta:
        model = models.Site
        headers = ['site_name', 'latitude', 'longitude', 'elevation', 'continent','country','sea','slug']
        order_by = 'site_name'
        url = '/thermoglobe/sites/'
        link_columns = ['site_name']
        hide = ['slug']

    def get_queryset(self):
        return super().get_queryset()
        
class HeatFlow(Table):

    class Meta:
        model = models.HeatFlow
        headers = ['depth_min', 'depth_max', 'corrected', 'corrected_uncertainty', 'uncorrected', 'uncorrected_uncertainty']
        order_by = 'depth_min'
        round_to = 1

    def plot_hist(self):
        fig = go.Figure()
        df = self.df[self.df.corrected.between(0,500)]

        # fig.add_trace(
        #     go.Histogram(
        #         x=df[df.site__elevation >= 0].corrected,
        #         # nbinsx=10,
        #         name='Continental'))
        # fig.add_trace(
        #     go.Histogram(
        #         x=df[df.site__elevation < 0].corrected,
        #         # nbinsx=10,
        #         name='Oceanic'))

        df['type'] = np.where(df['site__elevation'] >= 0, 'continental', 'oceanic')
        fig = px.histogram(df, x="corrected", color="type",
                        marginal="box", # or violin, rug, box
                        hover_data=df.columns,
                        nbins=40,
                        )

        fig.update_xaxes(title=self.verbose_column_name('corrected'))
        # fig.update_yaxes(title='Count')
        fig.update_layout(
            barmode='overlay',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            # width=800, height=600,
            )
        fig.update_traces(opacity=0.75)
        return mark_safe(fig.to_html(**options('Heat Flow')))

# class ThermalGradient(Table):

#     class Meta:
#         model = models.ThermalGradient
#         headers = ['depth_min', 'depth_max', 'corrected', 'corrected_uncertainty', 'uncorrected', 'uncorrected_uncertainty']
#         order_by = 'depth_min'
#         round_to = 1
        
class Conductivity(Table):

    class Meta:
        model = models.Conductivity
        headers = ['sample_name','depth', 'value', 'uncertainty','orientation','rock_type']
        order_by = ['depth','sample_name']
        round_to = 2

class HeatGeneration(Table):

    class Meta:
        model = models.HeatGeneration
        headers = ['sample_name','depth', 'value', 'uncertainty','rock_type']
        order_by = ['depth','sample_name']
        round_to = 2

    def get_queryset(self):
        return super().get_queryset().select_related('reference')

class Temperature(Table):

    class Meta:
        model = models.Temperature
        headers = ['site','depth', 'value','method']
        order_by = 'depth'
        round_to = 2

    def plot_profile(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.df.value,y=self.df.depth))
        fig.update_layout(
            title="Temperature vs Depth",
            xaxis_title=self.verbose_column_name('value'),
            yaxis_title=self.verbose_column_name('depth'),
        )

        return mark_safe(fig.to_html(**options('temp_vs_depth')))


