from . import models
from tables.tables import Table
import plotly.graph_objects as go
import plotly.express as px
from django.utils.html import mark_safe
import numpy as np
from thermoglobe.utils import Hyperlink

class Publications(Table):

    class Meta:
        model = models.Publication
        headers = ['slug', 'bibtex','doi', 'type','author', 'title', 'year', 'journal','publisher']
        url = '/thermoglobe/publications/'
        hide = ['slug']

    # def get_queryset(self):
    #     return super().get_queryset().annotate(pub_link=Hyperlink('site_name','thermoglobe/sites/','slug'))

class HeatFlow(Table):

    class Meta:
        model = models.HeatFlow
        headers = ['depth_min', 'depth_max', 'corrected', 'corrected_uncertainty', 'uncorrected', 'uncorrected_uncertainty']
        order_by = 'depth_min'
        round_to = 1

    def plot_hist(self):
        fig = go.Figure()
        df = self.df[self.df.corrected.between(0,500)]

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



