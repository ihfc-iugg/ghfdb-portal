from rest_framework.reverse import reverse_lazy
# from django.urls import reverse
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

        if not self._meta.get('header'):
            raise Exception("Table instance must define a header variable within the Meta class")

    def get_url(self):
        return reverse_lazy(self._meta.get('api_view'))

    def _label(self):
        return 

    def label(self):
        if self._meta.get('label'):
            return self._meta.get('label')

        label = self.get_url().split('/')[-2]
        return ' '.join(label.split("-")).title()

    def header(self):
        return self._meta.get('header')

    def pre_header(self):
        return self._meta.get('pre_header')

    def object_list(self):
        if self.object is None:
            return None
        return getattr(self.object, self._meta.get('related_name')).all()



class SiteTable(Table):

    class Meta:
        label='sites'
        related_name='sites'
        api_view = "site-list"
        web_url = "/sites/"
        pre_header = [   (5,'',None),
                        (3,'Data Logs',"")
            ]
        header = [
            ('site_name','Site',''),
            ('latitude','Lat',''),
            ('longitude','Lon',''),
            ('year_drilled','Year',''),
            ('well_depth','Max Depth (m)',''),
            ('interval_count','Intervals',''),
            ('temperature_log_count','Temperature',''),
            ('conductivity_log_count','Conductivity',''),
            ('heat_production_log_count','Heat Production',''),


            ]

class IntervalTable(Table):

    class Meta:
        label='intervals'
        related_name='intervals'
        api_view = "interval-list"
        pre_header = [   (4,'',None),
                        (2,'Depth',"[m]"),
                        (2,'Heat Flow',"[mW m<sup>-2</sup>]"),
                        (2,'Gradient',"[&deg;C/km]"),
                        (4,'Properties',"")]
        header = [
            ('site.site_name','Site',''),
            ('site.latitude','Lat',''),
            ('site.longitude','Lon',''),
            ('num_temp','T (n)','num_temp'),
            ('depth_min','Top',''),
            ('depth_max','Bottom',''),
            ('heat_flow','<i>q</i>',''),
            ('heat_flow_uncertainty','<i>&sigma;</i>',''),
            ('gradient','<i>&Delta;T</i>',''),
            ('gradient_uncertainty','<i>&sigma;</i>',''),
            ('cond_ave','<i>k</i>','Thermal Conductivity<br>[W m<sup>-1</sup> K<sup>-1</sup>]'),
            ('heat_prod','<i>a</i>','Heat Production [&mu;W m<sup>-3</sup>]'),
            ]


class HeatProductionTable(Table):
    class Meta:
        label='heat production'
        related_name='heat_production_logs'
        api_view = "heatproductionlog-list"
        header = [
            ('site.site_name','Site',''),
            ('site.latitude','Lat',''),
            ('site.longitude','Lon',''),
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
            ('site.site_name','Site',''),
            ('site.latitude','Lat',''),
            ('site.longitude','Lon',''),
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
            ('site.site_name','Site',''),
            ('site.latitude','Lat',''),
            ('site.longitude','Lon',''),
            ('data_count','Count',''),
            ('depth_upper','Upper',''),
            ('depth_lower','Lower',''),
            ('method','Method',''),
            ]