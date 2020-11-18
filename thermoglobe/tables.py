from . import models
from tables.tables import Table
import plotly.graph_objects as go
import plotly.express as px
from django.utils.html import mark_safe
# import plotly.figure_factory as ff
import numpy as np
from thermoglobe.utils import Hyperlink
from django.db.models.functions import Coalesce
from django.db.models import Avg, Count, F, FloatField, Max, Min, Q, Value
import plotly.io as pio
import pandas as pd
from plotly.subplots import make_subplots
from thermoglobe.utils import GEO_AGE

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

class Site(Table):

    class Meta:
        model = models.Site
        headers = ['slug', 'site_name', 'latitude', 'longitude', 'elevation', 'continent','country','sea']
        order_by = 'site_name'
        url = '/thermoglobe/sites/'
        link_columns = ['site_name']
        # hide = ['slug']

    def get_queryset(self):
        return super().get_queryset()
        
class Interval(Table):

    class Meta:
        model = models.Interval
        headers = ['depth_min', 'depth_max','heat_flow','gradient','average_conductivity','heat_generation',]
        order_by = 'depth_min'
        round_to = 1

    # def get_queryset(self):
    #     return super().get_queryset().annotate(
    #         heat_flow = Coalesce('heat_flow_corrected', 'heat_flow_uncorrected'),
    #         gradient = Coalesce('gradient_corrected', 'gradient_uncorrected'),
    #         )

    def pie_chart(self, count, top_n=10, include_other=True,**kwargs):
        """Generates a pie chart from the given dataset

        Args:
            groupby (str): Name of the dataframe column to group values by.
            property (str, optional): Name of the dataframe column to calculate statistical data from.
            n_to_include (int, optional): Number of groups to include in the final plot. Use to improve appearance when plotting data with lots of values (e.g. countries). Defaults to the 10.
            include_other (bool, optional): Whether to include a calculated field called 'other' to represent data not in the n_to_include number of items. Defaults to True.

        """
        data = self.df[count].value_counts()
        vals = data[:top_n]
        if include_other:
            vals = vals.append(pd.Series({'Other':data[top_n:].sum()}))

        fig = go.Figure(data=[go.Pie(
            labels=vals.index.str.slice(0,21),
            values=vals, 
            textinfo='value')])

        fig.update_layout(
            # uniformtext_minsize=12, 
            # uniformtext_mode='hide',
            # autosize=False,
            # showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(0,0,0,0)',
            )
        
        return mark_safe(fig.to_html(**options('{}_pie_chart'.format(self.__class__.__name__))))

    def plot_pie_country(self):
        return self.pie_chart('site__political__name')

    def plot_pie_continent(self):
        return self.pie_chart('site__continent__name',include_other=False)

    def plot_pie_seas(self):
        return self.pie_chart('site__sea__name')

    def histogram(self,column,data_range):
        fig = go.Figure()
        df = self.df[self.df[column].between(*data_range)]

        df['type'] = np.where(df['site__elevation'] >= -300, 'continental', 'oceanic')
        fig = px.histogram(df, 
                        x=column, color="type",
                        marginal="box", # or violin, rug, box
                        hover_data=[column],
                        nbins=40,
                        )
        fig.update_layout(
            barmode='overlay',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            )
        fig.update_traces(opacity=0.75)
        return mark_safe(fig.to_html(**options('{}_continental_vs_oceanic'.format(self.__class__.__name__))))

    def choropleth(self,column,data_range):
        df = self.df[self.df.site__country__name.notnull()]

        aggs = ["median","count",]

        vals = self.df[[column,'site__country__name']].groupby('site__country__name').aggregate(aggs)[column]

        figure = {
            'data': [
            dict(
                type = 'choropleth',
                locationmode = 'country names',
                locations = vals.index,
                z = vals['median'],
                zmax=data_range[1],
                zmin=data_range[0],
                visible=True,
            ),   
            dict(
                type = 'choropleth',
                locationmode = 'country names',
                locations = vals.index,
                z = vals['count'],
                visible=False,
            ),
            ],
            'layout': dict(
                    width=900,
                    margin=dict(l=20, r=20, t=45, b=20),
                    updatemenus = [dict(
                            type="buttons",
                            direction="right",
                            active=0,
                            x=0.57,
                            y=1.2,
                            showactive = True,
                            buttons = [
                                dict(
                                    label='Median',
                                    method='update',
                                    args=[{'visible':[True, False]}]
                                ),
                                dict(
                                    label='Count',
                                    method='update',
                                    args=[{'visible':[False, True]}]
                                ),
                            ]
                    )]
                ),
            }

        return mark_safe(pio.to_html(figure, **options('{}_choropleth'.format(self.__class__.__name__)), validate=False))

    def box(self,category,column,data_range,top_n=10,category_alias='',cutoff=20):
        vals = self.top_n(top_n,category,column,False,cutoff)

        fig = px.box(self.df[self.df[category].isin(vals.index)], x=column, y=category,
            points=False,
            range_x = data_range,
            category_orders={category: list(vals.sort_values('median',ascending=False).index)},
            )
            
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis= dict(side="top",title=column.replace('_',' ').title()),
            yaxis= dict(title=''),
            height=800,
        )
        return mark_safe(fig.to_html(**options('{}_by_{}'.format(self.__class__.__name__,category if not category_alias else category_alias))))

    def scatter_age(self):
        fig = go.Figure()
        df = self.df[self.df.thermotectonic_age.notnull()]
        fig.add_trace(go.Scatter(
            x=df.thermotectonic_age,
            y=df[self.meta['target']],
            mode='markers',
            marker_color = 'blue',
            name='Thermotectonic Age',
        ))

        df = self.df[self.df.juvenile_age.notnull()]

        fig.add_trace(go.Scatter(
            x=df.juvenile_age,
            y=df[self.meta['target']],
            mode='markers',
            name='Juvenile Age',
            marker_color = 'red',
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis= dict(title=self.meta['target']),
            xaxis=dict(title='Age'),
            showlegend=True,
        )

        return mark_safe(fig.to_html(**options('temp_vs_depth')))

    def top_n(self,n,category,column,include_other=True,count_cutoff=0):
        # vals = self.df.groupby(column).aggregate(['median','count'])['heat_flow']
        vals = self.df[[category,column]].groupby(category).aggregate(['count','median'])[column]
        vals = vals[vals['count'] >= count_cutoff]
        top_n = vals[:n]

        if include_other:
            # top_n = top_n.append(pd.Series({'Other':vals[n:].sum()}),ignore_index=True)
            top_n = top_n.append(pd.Series({'Other':vals[n:].sum()}))

        return top_n

class HeatFlow(Interval):

    class Meta:
        model = models.Interval
        headers = ['heat_flow','site__elevation','site__country__name','site__political__name','site__continent__name','site__sea__name','thermotectonic_age','juvenile_age','site__province__type']
        order_by = 'depth_min'
        round_to = 1
        target = 'heat_flow'

    def get_queryset(self):
        return super().get_queryset().annotate(
            heat_flow=Coalesce('heat_flow_corrected','heat_flow_uncorrected'),
            thermotectonic_age = (F('site__province__tectonic_age_max') + F('site__province__tectonic_age_min')) / 2,
            juvenile_age = (F('site__province__juvenile_age_max') + F('site__province__juvenile_age_min')) / 2,
            ).filter(Q(heat_flow_corrected__isnull=False) | Q(heat_flow_uncorrected__isnull=False))

    def plot_hist(self):
        return self.histogram('heat_flow',[0,200])

    def choropleth(self):
        return super().choropleth('heat_flow',[40,125])

    def plot_seas_box(self):
        return self.box(
            'site__sea__name','heat_flow',
            [0,300],
            top_n=29,
            cutoff=50)

    def plot_environment_box(self):
        return self.box(
            'site__province__type','heat_flow',
            [0,300],
            top_n=None)

    def sunburst_age(self):
        age = 'thermotectonic_age'
        df = self.df[self.df[age].notnull()]

        for age_type in ['eon','era','period']:

            intervals = pd.IntervalIndex.from_tuples(list(GEO_AGE[age_type].values()))
            groups = pd.cut(df[age].to_list(),intervals,precision=0)
            groups.categories = list(GEO_AGE[age_type].keys())
            df[age_type] = groups

        fig = px.sunburst(df, path=['eon','era','period'],
                        color='heat_flow', 
                        color_continuous_scale='RdBu_r',
                        color_continuous_midpoint=np.mean(df['heat_flow']))
            
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
        )

        return mark_safe(fig.to_html(**options('age_sunburst')))

class Gradient(Interval):

    class Meta:
        model = models.Interval
        headers = ['gradient','gradient_corrected','gradient_uncorrected','site__elevation','site__country__name','site__political__name','site__continent__name','site__sea__name','site__province__type','site__province__tectonic_age_max']
        order_by = 'depth_min'
        round_to = 1

    def get_queryset(self):
        return super().get_queryset().annotate(gradient=Coalesce('gradient_corrected','gradient_uncorrected')).filter(Q(gradient_corrected__isnull=False) | Q(gradient_uncorrected__isnull=False))

    def plot_hist(self):
        return self.histogram('gradient',[0,50])

    def choropleth(self):
        return super().choropleth('gradient',[0,60])

    def plot_seas_box(self):
        return self.box('site__sea__name','gradient',
        [0,300],
        top_n=29,
        cutoff=50,
        category_alias='sea')

    def plot_environment_box(self):
        return self.box(
            'site__province__type','gradient',
            [0,300],
            top_n=None)

class Conductivity(Table):

    class Meta:
        model = models.Conductivity
        headers = ['log_id','sample_name','depth', 'value', 'uncertainty','orientation','rock_type']
        order_by = ['log_id','depth','sample_name']
        round_to = 2

class HeatGeneration(Table):

    class Meta:
        model = models.HeatGeneration
        headers = ['log_id','sample_name','depth', 'value', 'uncertainty','rock_type']
        order_by = ['log_id','depth','sample_name']
        round_to = 2

    def get_queryset(self):
        return super().get_queryset().select_related('reference')

class Temperature(Table):

    class Meta:
        model = models.Temperature
        headers = ['log_id','depth', 'site__site_name', 'site__latitude','site__country__name','value','method','circ_time']
        order_by = ['log_id','depth']
        round_to = 2

    def plot_circ_time(self):
        fig = go.Figure()
        df = self.df[self.df.site__site_name == 'Silt Lake']
        out = pd.cut(df.circ_time, 
                bins=df.circ_time.unique().shape[0],
                precision=1,
                )
        grouped = df.groupby('circ_time')

        for key, group in grouped:
            fig.add_trace(go.Scatter(
                    x=group.value,
                    y=group.depth,
                    name='{}'.format(key),
                    mode='markers',
                    ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis= dict(side="top",title='Temperature [&deg;C]'),
            yaxis=dict(autorange="reversed"),
            showlegend=True,
            legend_title_text='Circ. Time',
        )

        return mark_safe(fig.to_html(**options('temp_vs_depth')))

    def plot_profile(self):
        fig = go.Figure()
        out = pd.cut(self.df.site__latitude.abs(), 
                bins=pd.interval_range(start=0,end=90,freq=10),
                precision=0,
                )
        grouped = self.df.groupby(out)

        for key, group in grouped:
            fig.add_trace(go.Scatter(
                    x=group.value,
                    y=group.depth,
                    name='{}-{}&deg;'.format(key.left,key.right),
                    mode='markers',
                    ))

        fig.update_layout(
            plot_bgcolor='rgb(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis= dict(side="top",title='Temperature [&deg;C]'),
            yaxis=dict(autorange="reversed"),
            showlegend=True,
            legend_title_text='Latitude',
        )

        return mark_safe(fig.to_html(**options('temp_vs_depth')))

    def plot_profile_box(self):
        fig = go.Figure()
        out = pd.cut(self.df.depth, 
                bins=pd.interval_range(start=0,end=3000,freq=100),
                precision=0,
                )
        grouped = self.df.groupby(out)

        for key, group in grouped:
            fig.add_trace(go.Box(
                    x=group.value,
                    name='{} - {}'.format(key.left,key.right),
                    marker_color = 'indianred',
                    ))

        fig.update_layout(
            # title='Points Scored by the Top 9 Scoring NBA Players in 2012',
            # yaxis=dict(
            #     autorange=True,
            #     showgrid=True,
            #     zeroline=True,
            #     dtick=5,
            #     gridcolor='rgb(255, 255, 255)',
            #     gridwidth=1,
            #     zerolinecolor='rgb(255, 255, 255)',
            #     zerolinewidth=2,
            # ),
            # paper_bgcolor='rgb(243, 243, 243)',
            # plot_bgcolor='rgb(243, 243, 243)',
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis= dict(side="top",title='Temperature [&deg;C]'),
            yaxis=dict(autorange="reversed"),
            showlegend=False,
        )




        return mark_safe(fig.to_html(**options('temp_vs_depth')))

    def choropleth(self):
        fig = go.Figure()
        df = self.df[self.df.site__country__name.notnull()]

        depth_intervals = pd.IntervalIndex.from_tuples([
            (90,110),
            (240,260),
            (480,520),
            (980,1020),
            (2950,3050),
            ])
        labels = ['100m','250m','500m','1km','3km']

        out = pd.cut(df.depth, 
                bins=depth_intervals,
                precision=0,
                )

        grouped = df.groupby(out)

        aggs = ["median"]

        buttons = []
        data_range = [0,50]
        for i, group in enumerate(grouped):
            key,group = group[0],group[1]
            vals = group[['value','site__country__name']].groupby('site__country__name').aggregate(aggs)['value']

            fig.add_trace(go.Choropleth(
                locationmode = 'country names',
                locations = vals.index,
                z = vals['median'],
                zmax=data_range[1],
                zmin=data_range[0],
                visible=True if key == depth_intervals[0] else False,
                )
            )

            buttons.append(dict(
                label=labels[i],
                method='update',
                args=[{'visible':[True if ii == i else False for ii in range(5)]}]
            ))


        fig.update_layout(
            width=900,
            margin=dict(l=20, r=20, t=45, b=20),
            updatemenus = [dict(
                            type="buttons",
                            direction="right",
                            active=0,
                            x=0.57,
                            y=1.2,
                            showactive = True,
                            buttons = buttons,
                )]

            )

        return mark_safe(fig.to_html(**options('{}_choropleth'.format(self.__class__.__name__)), validate=False))
