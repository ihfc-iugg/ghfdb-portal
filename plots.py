import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import os 
from scipy.interpolate import griddata
# import geojsoncontour
# import maptlotlib.pyplot as plt
from mpl_toolkits import Basemap

# df = pd.read_csv('Heat Flow.csv')
df = pd.read_csv('Lucazeau.csv')


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

def plot_hist(df):

    fig = go.Figure()
    # df = df[df.corrected.between(0,500)]

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
                    hover_data=['corrected'],
                    # nbins=40,
                    range_x = [0,400],
                    )

    fig.update_xaxes(title='Heat Flow')
    # fig.update_xaxes(title=self.verbose_column_name('corrected'))
    # fig.update_yaxes(title='Count')
    fig.update_layout(
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        # width=800, height=600,
        )
    fig.update_traces(opacity=0.75)
    return fig.write_html('../plotly_test.html',include_plotlyjs='cdn',full_html=True)

def ocean_continent_box(df):

    df['type'] = np.where(df['site__elevation'] >= 0, 'continental', 'oceanic')
    fig = px.box(df, x="corrected", color="type",
                    hover_data=['corrected'],
                    # hover_name=['Corrected Heat Flow'],
                    orientation='h',
                    range_x = [0,400],
                    notched=True
                    )

    fig.update_xaxes(title='Heat Flow')
    # fig.update_xaxes(title=self.verbose_column_name('corrected'))
    # fig.update_yaxes(title='Count')
    fig.update_layout(
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        )
    fig.update_traces(opacity=0.75)
    return fig.write_html('../plotly_test.html',include_plotlyjs='cdn',full_html=True)

def box_plot(df, x_value, field, top_n=10):

    index = df[field].value_counts()[:top_n].index
    df = df[df[field].isin(index)]

    fig = px.box(df, x=x_value, color=field,
                    hover_data=[x_value],
                    orientation='h',
                    # range_x = [0,400],
                    notched=True
                    )

    fig.update_xaxes(title=x_value)
    fig.update_layout(
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        )
    fig.update_traces(opacity=0.75)
    return fig.write_html('plotly_test.html',include_plotlyjs='cdn',full_html=True)


def density_map(df):
    fig = px.density_mapbox(df, lat='site__latitude', lon='site__longitude', 
                            z='corrected',     
                            radius=30,
                            center=dict(lat=0, lon=180), zoom=0,
                            mapbox_style="stamen-terrain",
                            range_color = [0,150],
                            )
    return fig.write_html('plotly_test.html',include_plotlyjs='cdn',full_html=True)

def contour(df):
    grid_x, grid_y = np.mgrid[-180:180:1, -90:90:1]
    output = griddata(
        df[['longitude','latitude']],df['heatflow__corrected'],
        (grid_x, grid_y),
        # method='linear'
        )
    
    fig = go.Figure()
    # fig.add_trace(
    #     go.Contour(
    #         z=output.T,
    #         colorscale='RdBu_r',

    #         contours=dict(
    #             start=0,
    #             end=250,
    #             size=10,
    #         ))
    # )
    # fig = px.scatter_geo(country, locations="iso_alpha", 
    #                     color="continent",
    #                     hover_name="country", size="pop",
    #                     animation_frame="year",
    #                     projection="natural earth"
    #                     # projection="orthographic"
    #                     )

    fig.add_trace(
        go.Scattergeo()
    )  

    fig.update_geos(
        visible=False, resolution=50,
        showcoastlines=True,
        bgcolor= 'rgba(0,0,0,0)',
    )

    fig.add_trace(
        go.Heatmap(
            z=output.T,
            y=np.linspace(-90,90,180),
            x=np.linspace(-180,180,180),
            # colorscale='Electric',
            # bgcolor=
            colorscale='RdBu_r',
            # connectgaps=True,
            # zsmooth='best',
            zmin=0,
            zmax=250,
            )
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor= 'rgba(1,1,1,1)',
        )
    return fig.write_html('plotly_test.html',include_plotlyjs='cdn',full_html=True)

# def contour(df):
#     grid_x, grid_y = np.mgrid[-180:180:5, -90:90:5]
#     output = griddata(
#         df[['longitude','latitude']],df['thermal_conductivity'],
#         (grid_x, grid_y),
#         method='nearest')
    
#     figure = plt.figure()
#     ax = figure.add_subplot(111)
#     contour = ax.contour(range(-180,180,1), range(-90,90,1), output, cmap=plt.cm.jet)


#     geojson = geojsoncontour.contour_to_geojson(
#         contour=contour,
#         ndigits=3,
#         unit='m'
#     )



    # return fig.write_html('plotly_test.html',include_plotlyjs='cdn',full_html=True)

if __name__ == '__main__':
    # plot_hist(df)
    # print(df.head())
    # n=10
    # index = df.site__CGG_basin__name.value_counts()[:n].index
    # x = df[df.site__CGG_basin__name.isin(index)]
    # box_plot(df,'corrected','site__continent__name')
    contour(df)
