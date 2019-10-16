from django.shortcuts import render
from django.views.generic import TemplateView
# from thermoglobe.filters import SiteFilter, HeatflowFilter, ConductivityFilter, HeatGenFilter, ReferenceFilter
from thermoglobe.filters import map_filter_forms
import csv
from thermoglobe.utils import get_db_summary
from thermoglobe.models import Site, DepthInterval
from django.http import HttpResponse, JsonResponse
from datetime import datetime

DOWNLOAD_FIELDS =[  

    ('site__site_name', 'site_name'),
    ('site__latitude',  'latitude'),
    ('site__longitude', 'longitude'),
    ('site__elevation', 'elevation'),
    ('site__dip',       'dip'),
    ('site__well_depth','well_depth'),
    ('site__sediment_thickness','sediment_thickness'),
    ('site__basin','basin'),
    ('site__sub_basin','sub_basin'),
    ('site__domain','domain'),
    ('site__province','province'),
    ('site__tectonic_environment','tectonic_environment'),
    ('site__bottom_hole_temp__value','bottom_hole_temp'),
    ('site__top_hole_temp__value','top_hole_temp'),
    # ('temperature__value', 'temperature'),
    ('depth_min','depth_min'),
    ('depth_max','depth_max'),
    ('age_min','age_min'),
    ('age_max','age_max'),
    ('age_method','age_method'),
    ('heatflow__reliability', 'heatflow_reliability'),
    ('heatflow__corrected','heatflow_corrected'),
    ('heatflow__corrected_uncertainty','heatflow_corrected_uncertainty'),
    ('heatflow__uncorrected','heatflow_uncorrected'),
    ('heatflow__uncorrected_uncertainty','heatflow_uncorrected_uncertainty'),
    ('temperaturegradient__corrected','gradient_corrected'),
    ('temperaturegradient__corrected_uncertainty','gradient_corrected_uncertainty'),
    ('temperaturegradient__uncorrected','gradient_uncorrected'),
    ('temperaturegradient__uncorrected_uncertainty','gradient_uncorrected_uncertainty'),
    ('conductivity__value','thermal_conductivity'),
    ('conductivity__uncertainty','conductivity_uncertainty'),
    ('conductivity__number_of_measurements','conductivity__number_of_measurementsy'),
    ('conductivity__method','conductivity__method'),
    ('heatgeneration__value','heatgeneration__value'),
    ('heatgeneration__uncertainty','heatgeneration__uncertainty'),
    ('heatgeneration__number_of_measurements','heatgeneration__number_of_measurements'),
    ('heatgeneration__method','heatgeneration__method'),
    ('reference__first_author__last_name','author'),
    ('reference__year','year'),
    ('reference__doi','doi'),
    ('site__operator','operator'),
    ('site__cruise','cruise'),
    ('comment','comment'),
    ]

def geojson_serializer(qs):
    qs = qs.values('latitude','longitude','site_name','reference__first_author__last_name','reference__year')
    # qs = qs.values('site__latitude','site__longitude')
    return {
        'type': 'FeatureCollection',
        'features': [{
            "type":"Feature",
            "geometry":{"type": "Point",
                        "coordinates":[q['longitude'], q['latitude']]},
            # "properties": {'site_name':form['site_name'],
            #             #    'author':form['reference__first_author__last_name'],
            #                'year':form['reference__year']
            # }
        } for q in qs]
    }

def filter_data(request):
    """Handles the filter request from map view"""
    qs = filter_request(request.GET, Site)
    # print(request.GET)
    return JsonResponse({'points': geojson_serializer(qs),'info': get_db_summary(qs)})

def filter_request(query_dict, model):
    """Filters data based on either the Site model (for ajax filtering) or the DepthInterval model (for download)"""
    query_dict = {k:v for k,v in query_dict.items() if v}
    query_dict = {k:v if v != 'on' else True for k,v in query_dict.items()}       
    
    # need to prepend site fields with site__ to work with the depthinterval model
    if model == DepthInterval:
        query_dict = {'site__'+k if k.split('__')[0] in [field.name for field in Site._meta.concrete_fields] else k:v for k,v in query_dict.items()}
        
    qs = model.objects.all()

    if not query_dict.get('hf_uncorrected'):
        # if uncorrected values are not selected
        qs = qs.filter(heatflow__uncorrected__isnull=True).distinct()

    if not query_dict.get('hf_corrected'):
        # if corrected values are not selected
        qs = qs.filter(heatflow__corrected__isnull=True).distinct()

    if query_dict.get('heatflow__gte'):
        qs = qs.filter( Q(heatflow__corrected__gte=query_dict['heatflow__gte']) |
                        Q(heatflow__uncorrected__gte=query_dict['heatflow__gte'])
                        ).distinct()

    if query_dict.get('heatflow__lte'):
        qs = qs.filter( Q(heatflow__corrected__lte=query_dict['heatflow__lte']) |
                        Q(heatflow__uncorrected__lte=query_dict['heatflow__lte'])
                        ).distinct()

    # delete logical query_dict field because they cannot be used in filter
    for k in ['heatflow__gte','heatflow__lte','hf_uncorrected','hf_corrected','csrfmiddlewaretoken']:
        if query_dict.get(k):
            del query_dict[k]

    # FOR DEBUGGING
    print('Current query:')
    for k,v in query_dict.items():
        print(k,': ',v)
    print(' ')

    return qs.filter(**query_dict).distinct()

# Create your views here.
class FullMapView(TemplateView):
    template_name = 'mapping/fullmap.html'
    filterset = map_filter_forms
    panel_order = ['filter','info','download','settings']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context.update({'filterset': self.filterset,
                        'points': geojson_serializer(qs),
                        'info': get_db_summary(qs),
                        'panel_order': self.panel_order
                        })
                        
        return context

    def get_queryset(self):
        return Site.objects.select_related('reference').all()
    
    def post(self, request):
        """This method controls the download of the csv file"""
        qs = filter_request(request.POST, DepthInterval)

        # converts queryset into a list of tuples containing the fields above. NOTE this is MUCH, MUCH faster than using django import-export's export feature: compare 198s to 0.003 seconds! This method does however limit the export to non-ManyToMany relations only (ie can't collect heat flow corrections or lithology!)
        my_csv = qs.values_list(*[field[0] for field in DOWNLOAD_FIELDS])

        # prepare the response for csv file
        date = datetime.now().strftime('_%d_%m_%y')
        filename = 'ThermoGlobe'+date+'.csv'

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        writer = csv.writer(response)

        # write the header row; remove "site__" prefix for some fields for clarity
        writer.writerow([field[1] for field in DOWNLOAD_FIELDS])

        # write the rows to the csv file
        for i in my_csv:
            writer.writerow(i)

        return response