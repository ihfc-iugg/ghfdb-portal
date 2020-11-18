from .models import Site, Interval
from publications.models import Publication
from django.db.models import Avg, Max, Min, Count, F, Value, Q, FloatField
from collections import Counter
# from mapping.models import Country
import plotly.graph_objects as go
from plotly.offline import plot

def heat_flow_per_year(filters={}):
    return Counter(Interval.objects.filter(reference__year__isnull=False,**filters).exclude(reference__bib_id='Blackwell2004').values_list('reference__year',flat=True).order_by('reference__year'))

# CHART UTILS
def counter_2_xy(counter, fill=True):
    """Fill=True will set non existing values to a count of 0. This is used to fill missing years in the reference list with values of 0.
    """
    if fill:
        counter = {k:counter.get(k,0) for k in range(min(counter.keys()),max(counter.keys())+1)}
    return {'x':list(counter.keys()),'y':list(counter.values())}

# CHART DATA METHODS
def publications_per_year(qs=Publication.objects.all(),filters={}):
    return Counter(qs.filter(year__isnull=False,**filters).values_list('year',flat=True).order_by('year'))
    # return counter_2_xy(refs) 

def heat_flow_per_year_x(filters={}):
    heatflow = Counter(Interval.objects.filter(reference__year__isnull=False,**filters).exclude(reference__bib_id='Blackwell2004').values_list('reference__year',flat=True).order_by('reference__year'))
    return counter_2_xy(heatflow)

def contributions_per_year(filters={}):

    fig = go.Figure()
    hf = heat_flow_per_year(filters)
    fig.add_trace(go.Scatter(
            x=list(hf.keys()), 
            y=list(hf.values()),
            name='Publications'
            )
        )

    pubs = publications_per_year(filters=filters)
    fig.add_trace(go.Scatter(
                    x=list(pubs.keys()), 
                    y=list(pubs.values()),
                    name='Heat flow estimates',
                    )
                )


    # var trace1 = {
    #   x: data[0].x,
    #   y: data[0].y,
    #   name: 'Publications',
    #   type: 'scatter'
    # };
    
    # var trace2 = {
    #   x: data[1].x,
    #   y: data[1].y,
    #   name: 'Heat flow estimates',
    #   yaxis: 'y2',
    #   type: 'scatter'
    # };


    fig.layout =  {
      'yaxis': {'title': 'Number of publications'},
      'yaxis2': {
        'title': 'Number of heat flow estimates',
        'overlaying': 'y',
        'side': 'right'
      },
      'xaxis': {
        'title': {
          'text': "Year",
        },
      },
      'legend': {
        'x': 0,
        'xanchor': 'left',
        'y': 1,
        'yanchor':'top',
      },
      'paper_bgcolor':'rgba(0,0,0,0)',
      'plot_bgcolor':'rgba(0,0,0,0)'
    }



    return plot(fig, output_type='div',include_plotlyjs=False)
    # return [publications_per_year(filters=filters),heat_flow_per_year(filters)]
    # return {
    #     'ID':'ContributionsPerYear',
    #     'data': [publications_per_year(filters=filters),heat_flow_per_year(filters)],
    #     'caption': 'Historical contributions to ThermoGlobe expressed in terms of number of publications and quantity of heat flow estimates added per year.',
    # }

def heat_flow_histogram(model_filters={}):
    continental = list(Interval.objects.filter(corrected__lte=200,corrected__gt=0,site__elevation__gte=-300,**model_filters).values_list('corrected',flat=True))
    oceanic = list(Interval.objects.filter(corrected__lte=200,corrected__gt=0,site__elevation__lt=-300,**model_filters).values_list('corrected',flat=True))
    
    return [continental,oceanic]

# def get_country_counts():
#     countries = Country.objects.annotate(Count('sites')).order_by('-site__count').values_list('name','site__count')[:15]
#     return [x[0] for x in countries], [x[1] for x in countries]

def entries_by(model,model_filters,model_values):
    counts = Counter(model.objects.filter(**model_filters).values_list(model_values,flat=True))
    total = sum(counts.values())
    top10 = Counter(dict(counts.most_common(10)))
    counts = counter_2_xy(top10,fill=False)

    counts['x'].append('Other')
    counts['y'].append(total - sum(top10.values()))

    return counts

def data_counts(model,model_filters={}):
    return model.objects.filter(**model_filters).aggregate(
                                        # Sites=Count('sites',distinct=True),
                                        Heat_Flow=Count('heatflow',distinct=True),
                                        Gradient=Count('thermalgradient',distinct=True),
                                        Temperature=Count('temperature',distinct=True),
                                        Conductivity=Count('conductivity',distinct=True),
                                        Heat_Gen=Count('heatgeneration',distinct=True),
                                        )


def get_year_counts():
    refs = Counter(Publication.objects.filter(year__isnull=False).values_list('year',flat=True))
    return [{'x':x,'y':y} for x,y in refs.items()]


