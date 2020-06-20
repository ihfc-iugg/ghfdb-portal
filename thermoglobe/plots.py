from .models import Site, HeatFlow
from reference.models import Reference
from django.db.models import Avg, Max, Min, Count, F, Value, Q, FloatField
from collections import Counter
# from mapping.models import Country
import plotly.graph_objects as go
from plotly.offline import plot

def heat_flow_per_year(filters={}):
    hf = Counter(HeatFlow.objects.filter(reference__year__isnull=False,**filters).exclude(reference__bib_id='Blackwell2004').values_list('reference__year',flat=True).order_by('reference__year'))
    return counter_2_xy(hf) 

# CHART UTILS
def counter_2_xy(counter, fill=True):
    """Fill=True will set non existing values to a count of 0. This is used to fill missing years in the reference list with values of 0.
    """
    if fill:
        counter = {k:counter.get(k,0) for k in range(min(counter.keys()),max(counter.keys())+1)}
    return {'x':list(counter.keys()),'y':list(counter.values())}

# CHART DATA METHODS
def publications_per_year(qs=Reference.objects.all(),filters={}):
    refs = Counter(qs.filter(year__isnull=False,**filters).values_list('year',flat=True).order_by('year'))
    return counter_2_xy(refs) 

def heat_flow_per_year_x(filters={}):
    heatflow = Counter(HeatFlow.objects.filter(reference__year__isnull=False,**filters).exclude(reference__bib_id='Blackwell2004').values_list('reference__year',flat=True).order_by('reference__year'))
    return counter_2_xy(heatflow)

def contributions_per_year(filters={}):
    return [publications_per_year(filters=filters),heat_flow_per_year(filters)]


def heat_flow_histogram(model_filters={}):
    continental = list(HeatFlow.objects.filter(corrected__lte=200,corrected__gt=0,site__elevation__gte=-300,**model_filters).values_list('corrected',flat=True))
    oceanic = list(HeatFlow.objects.filter(corrected__lte=200,corrected__gt=0,site__elevation__lt=-300,**model_filters).values_list('corrected',flat=True))
    
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
    refs = Counter(Reference.objects.filter(year__isnull=False).values_list('year',flat=True))
    return [{'x':x,'y':y} for x,y in refs.items()]


