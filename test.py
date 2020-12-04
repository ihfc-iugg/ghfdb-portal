import plotly.graph_objects as go
import os
import plotly.express as px
import json
import pandas as pd
from _plotly_utils.basevalidators import ColorscaleValidator
from functools import wraps
from thermoglobe.utils import GEO_AGE
import numpy as np

def plotly_cscale_nan(color,nan_color):
    c_scale = ColorscaleValidator("colorscale", "make_figure").validate_coerce(color)
    c_scale[0][0] += 0.000001
    c_scale.insert(0,[0, nan_color])
    return c_scale


def choropleth():
    # with open(os.path.join('assets','mapping','geojson', 'seas_countries.json'),'r') as f:
    # with open('merged.geojson','r') as f:
    with open('continents.geojson','r') as f:
        geojson = json.load(f)

    df = pd.read_csv('continents.csv')
    # c_names = pd.read_csv('country_names.csv')
    # c_names.columns = ['country']
    # geo_names = [feature['properties']['name'] for feature in geojson['features']]
    # c_names = pd.DataFrame(geo_names, columns=['continent'])


    df['name'] = df.continent.combine_first(df.sea)
    df = df[df.name.notnull()]

    groups = df.groupby('name')
    data = groups.describe()['heat_flow']
    data['median'] = groups.median()['heat_flow']
    data.reset_index(level=0, inplace=True)

    # data = pd.merge(c_names,data,on='name', how='outer')
    data.fillna(0,inplace=True)



    # data['Go to'] = '<a href="/">Some text</a>'
    fig = px.choropleth(data, geojson=geojson, 
            locations='name', 
            featureidkey="properties.name",
            color='median',
            color_continuous_scale='RdYlBu_r',
            # color_continuous_scale=plotly_cscale_nan('RdYlBu_r','azure'),
            # color_continuous_scale='twilight',
            hover_data=["count","min","25%","50%","75%","max","mean"],
            range_color=[50,70],
            
    )
    proj_type="orthographic"
    # proj_type = "sinusoidal"
    fig.update_geos(
        projection_type=proj_type,
        # visible=False,
        showcoastlines=False,
        showocean=True,
        oceancolor='#031ba7',
        showland=False,
        landcolor='darkgray',
        )
    fig.update_layout(
        # margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(100,0,0,0)',
       )

    return fig.write_html('plotly_test.html', 
    # include_plotlyjs=False,
    # full_html=False,    
    **dict(
    config={
        'responsive': True,
        'toImageButtonOptions': {
            'format': 'svg', # one of png, svg, jpeg, webp
            'filename': proj_type,
            'height': None,
            'width': None,
            # 'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
            }
        }
    ))


def series_from_age_type(column, age_type):
    intervals = pd.IntervalIndex.from_tuples(list(GEO_AGE[age_type].values()))
    groups = pd.cut(column.to_list(),intervals,precision=0)
    groups.categories = list(GEO_AGE[age_type].keys())
    return groups


def sunburst(age):
    df = pd.read_csv('ages.csv')

    for age_type in ['eon','era','period']:
    # age_type = 'eon'
        df[age_type] = series_from_age_type(df.age,age_type)

    fig = px.sunburst(df, 
                path=['eon'],
                color='gradient', 
                color_continuous_scale='RdBu_r',
                color_continuous_midpoint=np.mean(df['gradient']),     
                range_color=[20,50],
                # title=' '.join('age.split('__')[-1].split('_'))'.title(),
                )
        
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),

    )

    return fig.write_html('plotly_test.html', 
    config={
        'responsive': True,
        'toImageButtonOptions': {
            'format': 'svg', # one of png, svg, jpeg, webp
            'filename': 'sunburst',
            'height': None,
            'width': None,
            # 'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
            }
        }
    )


if __name__ == '__main__':
    choropleth()
    # x()
    # sunburst('age')
# fig.show()