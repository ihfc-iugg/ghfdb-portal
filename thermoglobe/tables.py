import plotly.graph_objects as go
from django.utils.html import mark_safe
import pandas as pd

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

