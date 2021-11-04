import os
import numpy as np
from django.db.models.query import QuerySet
from django.conf import settings

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

    def get_stats(self, df, groupby,aggregates=['count','median','mean']):
        """Returns the median, mean, q1, q3, lowerfence and upperfence as a dataframe. Only the top 20 categories by count are returned.
        """
        groups = df.groupby(groupby)
        data = groups.aggregate(aggregates)[self.field].round(2)
        data['q1'] = groups.quantile(.25)[self.field].round(2)
        data['q3'] = groups.quantile(.75)[self.field].round(2)
        IQR = data['q3'] - data['q1']
        data['lowerfence'] = data['q1'] - IQR*1.5
        data['upperfence'] = data['q3'] + IQR*1.5
        data['notchspan'] = 1.57 * IQR / np.sqrt(data['count'])
        # data = data.rename(columns={'std':'sd'})
        return data


class HFQueryset(QuerySet):
    field = 'heat_flow'
    field_title = 'Heat Flow [mW m<sup>-2</sup>]'


class GradientQueryset(QuerySet):
    field = 'gradient'
    field_title = 'Thermal Gradient [&deg;C / Km]'


class TemperatureQS(PlotQueryset):
    field = 'temperature'
    field_title = 'Temperature [&deg;C]'
