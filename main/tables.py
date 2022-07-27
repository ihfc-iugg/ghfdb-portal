from rest_framework.reverse import reverse_lazy
# from django.urls import reverse
from database.models import Site, Interval

  

class Table():

    class Meta:
        preheader = [] # (colspan,label,popup)
        header = []  # (data-attribute,label,popup)

    def __init__(self, object=None, qs=None):
        self.object = object
        self.qs = qs
        self._meta = {}
        for k, v in self.Meta.__dict__.items():
            self._meta[k] = v

        if not self._meta.get('api_view'):
            raise Exception("Table instance must define api_view within the Meta class")

        self.header = self.build_header()

        pass

        # if not self._meta.get('header'):
            # raise Exception("Table instance must define a header variable within the Meta class")

    def build_header(self):
        return [(f.name, f.verbose_name) for f in self.get_fields() ]

    def get_fields(self):
        model = self._meta.get('model')
        model_fields = model._meta.fields
        requested_fields = self._meta.get('fields')
        excluded_fields = self._meta.get('exclude')

        if self._meta.get('fields'):
            return [model._meta.get_field(f) for f in requested_fields]
        elif self._meta.get('exclude'):
            return [f for f in model_fields if f.name not in excluded_fields]
        else:
            return [f for f in model_fields]



    def get_url(self):
        return reverse_lazy(self._meta.get('api_view'))

    def _label(self):
        return 

    def label(self):
        if self._meta.get('label'):
            return self._meta.get('label')

        label = self.get_url().split('/')[-2]
        return ' '.join(label.split("-")).title()

    # def header(self):
    #     return self._meta.get('header')

    def pre_header(self):
        return self._meta.get('pre_header')

    def object_list(self):
        if self.object is None:
            return None
        return getattr(self.object, self._meta.get('related_name')).all()



class SiteTable(Table):

    class Meta:
        model = Site
        label='sites'
        related_name='sites'
        api_view = "site-list"
        web_url = "/sites/"
        fields = ['name','lat','lng','elevation','q','q_unc','q_acq','expl']

class IntervalTable(Table):

    class Meta:
        model = Interval
        label='intervals'
        related_name='intervals'
        api_view = "interval-list"
        # fields = ['q_top','q_bot','qc','qc_unc','T_grad_mean_meas','tc_mean','childcomp',]
        exclude = ['date_added','reference','historic_id','site',]



class HeatProductionTable(Table):
    class Meta:
        label='heat production'
        related_name='heat_production_logs'
        api_view = "heatproductionlog-list"
        header = [
            ('site.name','Site',''),
            ('site.lat','Lat',''),
            ('site.lng','Lon',''),
            ('data_count','Count',''),
            ('depth_upper','Depth Upper (m)',''),
            ('depth_lower','Depth Lower (m)',''),
            ('method','Method',''),
            ]


class ConductivityTable(Table):
    class Meta:
        label='thermal conductivity'
        related_name='conductivity_logs'
        api_view = "conductivitylog-list"
        header = [
            ('site.name','Site',''),
            ('site.lat','Lat',''),
            ('site.lng','Lon',''),
            ('data_count','Count',''),
            ('depth_upper','Upper',''),
            ('depth_lower','Lower',''),
            ('method','Method',''),
            ]


class TemperatureTable(Table):
    class Meta:
        label='temperature'
        related_name='temperature_logs'
        api_view = "temperaturelog-list"
        header = [
            ('site.name','Site',''),
            ('site.lat','Lat',''),
            ('site.lng','Lon',''),
            ('data_count','Count',''),
            ('depth_upper','Upper',''),
            ('depth_lower','Lower',''),
            ('method','Method',''),
            ]