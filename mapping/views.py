from django.shortcuts import render
from django.views.generic import TemplateView
from thermoglobe.filters import SiteFilter, HeatflowFilter, ConductivityFilter, HeatGenFilter, ReferenceFilter
from thermoglobe.filters import map_filter_forms
import csv
from thermoglobe.utils import get_db_summary
from thermoglobe.models import Site, HeatFlow, Conductivity, HeatGeneration, Temperature
from django.http import HttpResponse, JsonResponse
from datetime import datetime
import time 
from django.db.models import Q, Count, Avg, FloatField
from thermoglobe import choices
from django.db.models.functions import Cast, Coalesce

REFERENCE_FIELDS = [
    ('reference__bib_id','bib_id'),
    ('reference__doi','doi'),
]

HEATFLOW_FIELDS = [  

    ('reliability', 'heatflow_reliability'),
    ('corrected','heatflow_corrected'),
    ('corrected_uncertainty','heatflow_corrected_uncertainty'),
    ('uncorrected','heatflow_uncorrected'),
    ('uncorrected_uncertainty','heatflow_uncorrected_uncertainty'),
    ('thermalgradient__corrected','gradient_corrected'),
    ('thermalgradient__corrected_uncertainty','gradient_corrected_uncertainty'),
    ('thermalgradient__uncorrected','gradient_uncorrected'),
    ('thermalgradient__uncorrected_uncertainty','gradient_uncorrected_uncertainty'),
    ('conductivity','thermal_conductivity'),
    'conductivity_uncertainty',
    'number_of_conductivities',
    'conductivity_method',
    # ('heat_generation','heat_generation
    # ('heat_generation_uncertainty','heatgeneration__uncertainty'),
    # ('heat_generation_number_of_measurements','heatgeneration__number_of_measurements'),
    # ('heat_generation_method','heatgeneration__method'),
    'comment',
    ]

CONDUCTIVITY_FIELDS = [
    'sample_name',
    ('value','thermal_conductivity'),
    'uncertainty',
    'method',
    'depth',
    'rock_group',
    'rock_origin',
    'rock_type',
    ('geo_unit__name','geo_unit'),
    'age',
    'age_min',
    'age_max',
    'age_method',
    'comment',

 ]

def geojson_serializer(qs,fields):
    qs = qs.values(*fields)
    return {
        'type': 'FeatureCollection',
        'crs': {
            'type': "name",
            'properties': {
            'name': "EPSG:4326"
        }},
        'features': [{
            "type":"Feature",
            "geometry":{"type": "Point",
                        "coordinates":[float(q['longitude']), float(q['latitude'],                      
                         )]},
            "properties": {f:q[f] for f in fields}
        } for q in qs]
    }

def json_serializer(qs,fields):
    qs = qs.values(*fields)
    return [
            {
            "coordinates":[float(q['longitude']), float(q['latitude'])],
            "properties": {f:q[f] for f in fields}
        } for q in qs]

def data(request):
    """Handles the filter request from map view"""
    t = time.time()
    qs = filter_request(request.GET, Site)
    data_type = request.GET.get('dataType','heatflow')

    if data_type == 'heatflow':
        # Average of either corrected or uncorrected heat flow values at a particular site. 
        annotation = {
            'heat_flow': Avg(Coalesce('heatflow__corrected', 'heatflow__uncorrected'))
            }
    elif data_type == 'conductivity':
        annotation = {'_conductivity':Avg('conductivity__value'),}
    elif data_type == 'heatgeneration':
        annotation = {'_heat_generation':Avg('heatgeneration__value'),}
    elif data_type == 'temperature':
        annotation = {'_temperature':Avg('temperature__value'),}

    fields = ['site_name','latitude','longitude','elevation'] + list(annotation.keys()) + ['reference__bib_id']

    # fields = ['site_name','latitude','longitude'] + list(annotation.keys())


    # qs = qs.annotate(**annotation)[:10000]
    qs = qs.annotate(**annotation)

    t2 = time.time()

    r = JsonResponse({
        'headers': fields,
        'data': list(qs.values_list(*fields))
    })

    print('Response prepared in: ',time.time() - t2,'s')

    print('Size: ',len(r.content)/10**6,'MB')
    return r

def filter_request(query_dict, model):
    """Filters data based on either the Site model (for ajax filtering) or the DepthInterval model (for download)"""
    query_dict = {k:v for k,v in query_dict.items() if v}

    # convert 'on'/'off' to True or False
    query_dict = {k:v if v != 'on' else True for k,v in query_dict.items()}       
    
    qs = model.objects.filter(**{'{}__isnull'.format(query_dict.get('dataType','heatflow')):False})

    if query_dict.get('value__gte') or query_dict.get('value__lte'):
        value_range = (query_dict.get('value__gte',0),query_dict.get('value__lte',10**6))
        if query_dict['dataType'] == 'heatflow':
            qs = qs.filter( 
                Q(heatflow__corrected__range=value_range)|
                Q(heatflow__uncorrected__range=value_range)
                        ).distinct()
        else:
            qs = qs.filter( 
                Q(**{'{}__value__range'.format(query_dict['dataType']):value_range})
            )

    # delete logical query_dict field because they cannot be used in filter
    for k in ['heatflow__gte','heatflow__lte','hf_uncorrected','hf_corrected','csrfmiddlewaretoken','dataType','value__gte','value__lte']:
        if k in query_dict.keys():
            del query_dict[k]

    # FOR DEBUGGING
    if query_dict:
        print('Current query:')
        for k,v in query_dict.items():
            print(k,': ',v)
        print(' ')

    return qs.filter(**query_dict).distinct()

# Create your views here.
class FullMapView(TemplateView):
    template_name = 'mapping/fullmap.html'
    filters = [SiteFilter]
    table_options = dict(
            order = [[7,'desc'],],
            pageLength = 25,
            # dom ='<"top d-flex justify-content-between align-content-center"fi>t<"bottom"><"clear">',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dict(
            filters = self.filters,
            table_options = self.table_options,           
        ))     
    
        return context

    def get_queryset(self):
        return Site.objects.select_related('reference').all()
    
    def post(self, request):
        """This method controls the download of the csv file"""
        sites = filter_request(request.POST,Site)

        data_type = request.POST.get('dataType')


        site_fields = get_site_fields()



        if data_type == 'heatflow':
            model = HeatFlow
            fields = site_fields + HEATFLOW_FIELDS + REFERENCE_FIELDS
        elif data_type == 'conductivity':
            model = Conductivity
            fields = site_fields + CONDUCTIVITY_FIELDS + REFERENCE_FIELDS
        elif data_type == 'heatgeneration':
            model = HeatGeneration
        elif data_type == 'temperature':
            model = Temperature

        qs = model.objects.filter(site__in=sites)

        # converts queryset into a list of tuples containing the fields above. NOTE this is MUCH, MUCH faster than using django import-export's export feature: compare 198s to 0.003 seconds! This method does however limit the export to non-ManyToMany relations only (ie can't collect heat flow corrections or lithology!)



        my_csv = qs.values_list(*[field[0] if len(field) == 2 else field for field in fields])

        # prepare the response for csv file
        filename = 'ThermoGlobe_{}.csv'.format(datetime.now().strftime('%d_%b_%Y'))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        writer = csv.writer(response)

        # write the header row; remove "site__" prefix for some fields for clarity
        writer.writerow([field[1] if len(field) == 2 else field for field in fields])

        # write the rows to the csv file
        for i in my_csv:
            writer.writerow(i)

        return response

def get_site_fields():
    exclude = ['slug','id','uploaded_by','date_added','added_by','date_edited','edited_by','geom']
    foreign_keys = {f[0]:'__'.join(f) for f in
                    [
                    ('continent','name'),
                    ('country','name'),
                    ('sea','name'),
                    ('CGG_basin','name'),
                    ('operator','name'),
                    ('surface_temp','value'),
                    ('bottom_hole_temp','value'),
                    ('basin','name'),
                    ('sub_basin','name'),
                    ('tectonic_environment','name'),
                    ('geological_province','name'),
                    ]
        }

    site_fields = [field.name for field in Site._meta.fields if field.name not in exclude]

    new_site_fields = []
    for field in site_fields:
        if field in foreign_keys.keys():
            new_site_fields.append(foreign_keys[field])
        else:
            new_site_fields.append(field)

    return [('site__'+field,field.split('__')[0]) for field in new_site_fields]

    # return new_site_fields
    # for field in foreign_keys:
    #     if field[0] in site_fields:
