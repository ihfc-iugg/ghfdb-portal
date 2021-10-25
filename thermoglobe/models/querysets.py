import os, json
import numpy as np
import pandas as pd

from django.db.models.query import QuerySet
from django.utils.html import mark_safe
from django.db.models import F
from django.conf import settings

import plotly.graph_objects as go
from plotly.subplots import make_subplots 
import plotly.express as px
from thermoglobe.utils import plot_cache, plotly_cscale_nan

json_data = os.path.join(settings.STATIC_ROOT, 'mapping','geojson')

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

class PlotQueryset(QuerySet):
    field=None
    field_title=None 
    data_limits=None

    def pie(self):

        # create a dataframe with relevant field value plus country and sea names
        df = pd.DataFrame(
            data=self.values_list('country__name','sea__name'),
            columns=['country','sea'])
        # combine the country and sea columns into a single column called name
        df['name'] = df.country.combine_first(df.sea)
        df = df[df['name'].notnull()]

        # group the data by this new column and get descriptive stats
        counts = df.groupby('name').count().sum(axis=1)
        fig = go.Figure(go.Pie(
            labels=counts.index,
            values=counts, 
            textinfo='label,value'))
            
        fig.update_layout(
            showlegend=False,
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(100,0,0,0)',
        )
        return fig.to_html(**options('site locations'))

    def histogram(self, *args, **kwargs):
        fig = go.Figure()
        for i in args:
            fig.add_trace(go.Histogram(x=list(self.values_list(i, flat=True))))

        fig.update_layout(
            barmode='overlay',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            # margin=dict(l=20, r=20, t=20, b=20),
            )
        fig.update_traces(opacity=0.75)
        return mark_safe(fig.to_html(**options('{}_continental_vs_oceanic'.format(self.__class__.__name__))))

    @plot_cache('box_plot')
    def box(self,category, *args, **kwargs):
        # get the required queryset
        qs = list(self.values_list(self.field,category).distinct())

        # turn into a pandas dataframe, stats are way easier to calculate this way
        df = pd.DataFrame(qs, columns=[self.field,category])

        # get a statistical representation of the df
        # computes statistics in a manner ready for box plots specifically
        data = self.get_stats(df, category)

        # sort by count and get top 20, delete count column
        data = data.sort_values('count',ascending=True)[-20:]
        data.drop('count',axis=1,inplace=True)
        data.sort_values('median',ascending=True,inplace=True)
        fig = go.Figure(
            go.Box(
                y=data.index,
                **data.to_dict(orient='list'))
            )
           
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            # margin=dict(l=20, r=20, t=20, b=20),
            xaxis= dict(
                side="top",
                title=self.field_title,
                range=[-100,350],
                ),
            yaxis= dict(title=''),
            height=800,
        )
        return mark_safe(fig.to_html(**options(f'{self.field}_by_{category}')))

    def get_stats(self, df, groupby,aggregates=['count','median','mean']):
        """Returns the median, mean, q1, q3, lowerfence and upperfence as a dataframe. Only the top 20 categories by count are returned.
        """

        groups = df.groupby(groupby)
        # data = groups.describe()[self.field].round(2)
        data = groups.aggregate(aggregates)[self.field].round(2)
        data['q1'] = groups.quantile(.25)[self.field].round(2)
        data['q3'] = groups.quantile(.75)[self.field].round(2)
        IQR = data['q3'] - data['q1']
        data['lowerfence'] = data['q1'] - IQR*1.5
        data['upperfence'] = data['q3'] + IQR*1.5
        data['notchspan'] = 1.57 * IQR / np.sqrt(data['count'])
        # data = data.rename(columns={'std':'sd'})

        return data

class IntervalQS(PlotQueryset): 

    @plot_cache(cache_key='choropleth')
    def choropleth(self):
        with open(os.path.join(json_data, 'merged.json'),'r') as f:
            geojson = json.load(f)

        # create a dataframe with relevant field value plus country and sea names
        df = pd.DataFrame(
            data=self.values_list(self.field,'site__country__name','site__sea__name'),
            columns=[self.field,'country','sea'])
        # combine the coutnry and sea columns into a single column called name
        df['name'] = df.country.combine_first(df.sea)
        df = df[df.name.notnull()]

        # group the data by this new column and get descriptive stats
        groups = df.groupby('name')
        data = groups.describe()[self.field]
        data['median'] = groups.median()[self.field] # add median because mean values are not helpful
        data = data.round(2) # round the data for clarity

        # during the describe operation, name column was set as index, pull it back out into a column
        data.reset_index(level=0, inplace=True)

        # need to map with available names in geojson or error will be thrown
        geo_names = [feature['properties']['name'] for feature in geojson['features']]
        names = pd.DataFrame(geo_names, columns=['name'])

        # merge the descriptive dataframe with the list of all available names
        # otherwise plotly will not plot the boundaries of areas with no values
        data = pd.merge(names,data,on='name', how='outer')

        # plotly doesnt handle Nans so replace with zeros
        data.fillna(0,inplace=True)

        # need to modify plotly colorscale to account for 0 values
        c_scale = plotly_cscale_nan('RdYlBu_r','dimgrey')

        fig = px.choropleth(data, geojson=geojson, 
                locations='name', 
                featureidkey="properties.name",
                color='median',
                color_continuous_scale=c_scale,
                hover_data=["count","min","25%","50%","75%","max","mean"],
                range_color=[0,self.mean_limits[1]],
                labels={
                    'median': self.field_title
                }
        )
        fig.update_geos(
            projection_type="orthographic",
            visible=False
            )
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor= 'rgba(100,0,0,0)',
        )
        return mark_safe(fig.to_html(**options(f'{self.field}_choropleth')))
   


    def get_age(self,age):
        return self.annotate(**{
            f"{age}": (F(f'site__province__{age}_max') + F(f'site__province__{age}_min')) / 2,
        }).exclude(**{f"{age}__isnull":True})


    @plot_cache(cache_key='age_plot')
    def age_plot(self,age):

        qs = self.get_age(age)

        df = pd.DataFrame(qs.values_list(self.field,age),
            columns=[self.field, 'age'])

        fig = go.Figure()
        age_types = ['eon','era','period']
        for age_type in age_types:
            # define an age interval based on the required age type
            intervals = pd.IntervalIndex.from_tuples(list(GEO_AGE[age_type].values()))

            # cut the dataframe based on our new age interval, and assign proper category labels
            cut = pd.cut(df['age'].to_list(),intervals,precision=0)
            cut.categories = list(GEO_AGE[age_type].keys())
            
            # group our original dataframe by our newly assigned age categories
            # groups = df.groupby(cut)
            data = self.get_stats(df,cut,aggregates=['count','mean','std'])

            # compute generic stats over the current grouping
            # data = groups.describe()
            # data = df.groupby(cut).aggregate(['mean','count','std'])
            size=data['count'] / data['count'].sum()*100
            text = [f"{age.title()}<br>Interval: {i}<br>Count: {count}" for age, i, count in zip(data.index,intervals.values,data['count'])]
            ages = df.groupby(cut)['age'].mean()
            fig.add_trace(go.Scatter(
                x=ages,
                y=data['mean'],
                mode='markers',
                name=age_type,
                text=text,
                marker=dict(
                    size=size,
                    sizemode='area',
                    sizeref=2. * max(size) / (50 ** 2),
                    sizemin=4
                ),
                error_y=dict(
                    array=data['std'],
                    thickness=1.5,
                    width=3,
                ),
                error_x=dict(
                    array=[i.right for i in intervals.values] - ages,
                    arrayminus=ages - [i.left for i in intervals.values],
                    thickness=1.5,
                    width=3,
                ),
            ))

        fig.update_layout(
            legend_title_text='Grouped by:',
            xaxis_title=f"{age.replace('_',' ').title()} [Ma]",
            yaxis_title=f"{self.field_title}",
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=75, b=20),
            height=450,
            legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
        )
        return mark_safe(fig.to_html(**options(f'{age}_vs_{self.field}')))


    @plot_cache(cache_key='sunburst')
    def sunburst(self, age):
        qs = self.annotate(
            age = (F(f'{age}_max') + F(f'{age}_min')) / 2,
            ).exclude(age__isnull=True)

        df = pd.DataFrame(qs.values_list(self.field,'age'),
            columns=[self.field, 'age'])
        df.to_csv('ages')
        age_types = ['eon','era','period']
        for age_type in age_types:
            intervals = pd.IntervalIndex.from_tuples(list(GEO_AGE[age_type].values()))
            groups = pd.cut(df['age'].to_list(),intervals,precision=0)
            groups.categories = list(GEO_AGE[age_type].keys())
            df[age_type] = groups

        fig = px.sunburst(df, 
                    path=age_types,
                    color=self.field, 
                    color_continuous_scale='RdBu_r',
                    # color_continuous_midpoint=df[self.field].median(),     
                    range_color=self.sunburst_lims,
                    title=' '.join(age.split('__')[-1].split('_')).title(),
                    # maxdepth=2,
                    # branchvalues='remainder',
                    )
            
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            autosize=True,
            height=450,
        )

        return mark_safe(fig.to_html(**options(f'{age}_sunburst')))

    def continental(self):
        return self.exclude(site__province__isnull=True)

    def oceanic(self):
        return self.filter(site__province__isnull=True)

    def country_pie(self):
        return self.exclude(site__country__isnull=True).pie('site__country__name')

    @plot_cache(cache_key='c_vs_o_histogram')
    def continental_vs_oceanic(self):
        df = pd.DataFrame(self.values_list(self.field,'site__province','site__country__name'))
        df.columns = [self.field,'province','country']
        df['type'] = np.where(df.province.notnull(), 'Continental', 'Oceanic')
        groups = df[[self.field,'type']].groupby('type')
        fig = make_subplots(rows=2, cols=1, 
                row_heights=[0.25, 0.75], 
                shared_xaxes=True,
                # specs = [[{}, {}]],
                vertical_spacing=0.02,
                )

        colors=['blue','red']
        for c, group in zip(colors,groups):
            name, data = group
            fig.add_trace(go.Box(
                # x=data.aggregate(['min','max']),
                y0=name,
                **self.compute_box_stats(data),
                marker_color=c,
                boxpoints=False,
                name=name,
                # legendgroup=name,
                # showlegend=False,
            ),
            row=1, col=1
            )
            hist = np.histogram(data[self.field], bins=60, range=self.data_limits,density=True)
            fig.add_trace(go.Bar(
                    x=hist[1],
                    y=hist[0],
                    name=f"{name}_hist",
                    opacity=0.5,
                    marker_color=c,
                    offset=0,
                    # legendgroup=name,
                    showlegend=False
                ),
                row=2, col=1
            )

        # CALCULATED AGAIN WITH HEATFLOW < 250
        data = df[df[self.field] < self.data_limits[1]]
        groups = data[[self.field,'type']].groupby('type')
        
        colors=['mediumslateblue','indianred']
        for c, group in zip(colors, groups):
            name, data = group
            fig.add_trace(go.Box(
                    y0=f'{name} < {self.data_limits[1]}',
                    **self.compute_box_stats(data),
                    marker_color=c,
                    boxpoints=False,
                    legendgroup=f'{name} < {self.data_limits[1]}',
                    visible='legendonly',
                    name=f'{name} < {self.data_limits[1]}',
                ),
                row=1, col=1
                )

        # groups = df.loc[df['country'] != 'United States',[self.field,'type']].groupby('type')
        # data = groups.get_group('Continental')
        # fig.add_trace(go.Box(
        #         y0='Continental (-USA)',
        #         **self.compute_box_stats(data),
        #         marker_color='mediumslateblue',
        #         boxpoints=False,
        #         legendgroup='Continental (-USA)',
        #         visible='legendonly',
        #         name='Continental (-USA)',
        #     ),
        #     row=1, col=1
        #     )


        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
        )
        fig.update_yaxes(title_text="Probability Density", row=2, col=1)

        fig.update_xaxes(range=self.data_limits)
        return mark_safe(fig.to_html(**options(f'{self.field}_continental_vs_oceanic')))

    def compute_box_stats(self,data):
        Q1 = data.quantile(.25)
        Q3 = data.quantile(.75)
        IQR = Q3 - Q1
        return dict(
            lowerfence=Q1-(1.5*IQR),
            q1=Q1, 
            median=data.median(),
            q3=Q3, 
            upperfence=Q3+(1.5*IQR), 
            mean=data.mean(),
            # sd=data.std(), 
            # notchspan=data.std(),
        )

class HFQueryset(IntervalQS):
    field = 'heat_flow'
    field_title = 'Heat Flow [mW m<sup>-2</sup>]'
    data_limits = [0,250]
    mean_limits = [30,120] #used when plotting means rather than all values e.g choropleth  
                        #only the upper limit used for choropleths to prevent incorrect shading
    sunburst_lims = [40,100]

class GradientQueryset(IntervalQS):
    field = 'gradient'
    field_title = 'Thermal Gradient [&deg;C / Km]'
    data_limits = [0,200]
    mean_limits = [10,90] #used when plotting means rather than all values e.g choropleth  
                        #only the upper limit used for choropleths to prevent incorrect shading
    sunburst_lims = [15,50]

class TemperatureQS(PlotQueryset):
    field = 'temperature'
    field_title = 'Temperature [&deg;C]'
    data_limits = [0,100]
    mean_limits = [0,100] #used when plotting means rather than all values e.g choropleth  
                        #only the upper limit used for choropleths to prevent incorrect shading
    sunburst_lims = [0,100]
    
    def versus_depth(self):
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