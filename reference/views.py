from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from .models import Reference, Operator, Author
from django.conf import settings
from django.core.serializers import serialize
from django.http import HttpResponse
from django.utils import timezone
from django_filters.views import FilterView
from .filters import ReferenceFilter
from django.db.models import Max, Min
from django.db.models import Count, F, Value, Func, Sum, Avg,FloatField,Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mapping.views import HEATFLOW_FIELDS
import csv
import bibtexparser as bib
from main.utils import get_page_or_none
from mapping.views import geojson_serializer
from .mixins import CustomListView
from thermoglobe.models import Site, HeatFlow
from .forms import ReferenceForm
import json
from thermoglobe import plots
from django.http import JsonResponse

class Round(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s::numeric, 2)"

class TableListView(ListView):

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = get_page_or_none(self.page_id)
        context['object_url'] = self.details_url   
        context['table_options'] = self.table_options
        context['table_fields'] = self.table_fields
        context['dataset'] = self.get_dataset()
        return context

    def get_dataset(self):
        return json.dumps(list(self.get_queryset()))

class PublicationListView(TableListView):
    model = Reference
    details_url = 'reference:publication_list'
    template_name = "reference/table_from_bibtex.html"
    page_id = 2
    table_fields = ['slug','bibtex','_heat_flow','_thermal_gradient','_temperature','_thermal_conductivity','_heat_generation',]
    table_options = json.dumps({
            'dom': '<"top d-flex justify-content-around align-content-center"lpf>t<"bottom"ip><"clear">',
            'order': [[4,'desc'],[1,'asc']],
            'pageLength': 50,
    })

    def get_queryset(self):
        return super().get_queryset().select_related('first_author').annotate(
                _heat_flow=Count('heatflow',distinct=True),
                _thermal_gradient=Count('thermalgradient',distinct=True),
                _temperature=Count('temperature',distinct=True),
                _thermal_conductivity=Count('conductivity',distinct=True),
                _heat_generation=Count('heatgeneration',distinct=True),
                ).values(*self.table_fields)

    def get_context_data(self,**kwargs):
        context = super().get_context_data()
        context['bibtex_headers'] = ['doi','author','title','year','journal']
        x = 1 if 'slug' in self.table_fields else 0
        context['complex_headers'] = [[len(context['bibtex_headers']) + x,''],[5,'Data Counts']]
        return context

class PublicationDetailsView(DetailView):
    template_name = "reference/publication_details.html"
    model = Reference
    site_details_url = '/thermoglobe/sites/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dict(
            figures = [
                {'id':'DataCounts',
                'data':plots.data_counts(model=self.model,model_filters={'id':context['object'].id}),},
                {'id':'HeatFlowHist',
                'data': plots.heat_flow_histogram(model_filters={'reference':context['object']}),
                'caption':'Heat flow distribution',},
                ],
            object_url = self.site_details_url,
            complex_headers = [[4,''],[5,'Site Average']],

            table_options = {
                'order': [[4,'desc'],],
                'pageLength': 100,
                'dom': '<"top d-flex justify-content-between align-content-center"fi>t<"bottom"><"clear">',
            }
            ))
        context['bibtex'] = json.dumps(context['object'].bibtex)


        return context

    def post(self, request, pk):
        my_csv = HeatFlow.objects.filter(reference=pk).values_list(*[field[0] for field in HEATFLOW_FIELDS])
        filename = '{}.csv'.format(self.model.objects.get(id=pk))
        
         # prepare the response for csv file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        writer = csv.writer(response)

        # write the header row; remove "site__" prefix for some fields for clarity
        writer.writerow([field[1] for field in HEATFLOW_FIELDS])

        # write the rows to the csv file
        for i in my_csv:
            writer.writerow(i)
        return response

class AuthorListView(TableListView):
    model = Author
    page_id = 8
    template_name = "reference/table_from_list.html"
    details_url = 'reference:author_list'
    table_fields = ['last_name','first_name','first_authorship','co_author','total','slug']
    table_options = json.dumps(dict(
            order = [[4,'desc']],
            pageLength = 50,
            columnDefs = [dict(
                targets = 2,
                visible = False,
                searchable = False
            ),]
        ))

    def get_queryset(self):
        return super().get_queryset().annotate(
                first_authorship = Count('as_first_author',distinct=True),
                co_author = Count('as_coauthor',distinct=True),   
                total=Count('as_first_author', ouput_field=FloatField(),distinct=True)
                                                    + Count('as_coauthor',ouput_field=FloatField(),distinct=True)
                                            ).values(*self.table_fields)

class AuthorDetailsView(DetailView):
    details_url = 'reference:publication_list'
    template_name = "reference/author_details.html"
    model = Author
    site_lookup = 'reference__first_author'
    details_url = 'reference:publication_list'
    table_fields = ['slug','bibtex','_heat_flow','_thermal_gradient','_temperature','_thermal_conductivity','_heat_generation',]
    table_options = json.dumps(dict(
            order = [[4,'desc'],],
            pageLength = 100,
            dom ='<"top d-flex justify-content-between align-content-center"fi>t<"bottom"><"clear">',
        ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        x = 1 if 'slug' in self.table_fields else 0
        context.update(dict(
            object_url = self.details_url,
            table_options = self.table_options,
            table_fields = self.table_fields,
            dataset = list(context['object'].get_publications().values(*self.table_fields)),
            bibtex_headers = ['doi','author','title','year','journal'],
            figures = {
                'contributions':    {
                    'id':'ContributionsPerYear',
                    'data': [plots.publications_per_year(context['object'].get_publications())],
                    },
                'counts': {
                    'id':'data_counts',
                    'data': context['object'].data_counts(),
                    }
            }
 
        ))
        context['complex_headers'] = [[len(context['bibtex_headers']) + x,''],[5,'Data Counts']]
                
        return context

    def get_sites(self,context):
        return Site.objects.filter(**{self.site_lookup:context['author']})


def annotate_data_counts(qs):
    return qs.annotate(
                _heat_flow=Count('heatflow',distinct=True),
                _thermal_gradient=Count('thermalgradient',distinct=True),
                _temperature=Count('temperature',distinct=True),
                _thermal_conductivity=Count('conductivity',distinct=True),
                _heat_generation=Count('heatgeneration',distinct=True),
                )

def annotate_data_average(qs):
    return qs.annotate(
                _heat_flow=Round(Avg('heatflow__corrected')),
                _thermal_gradient=Round(Avg('thermalgradient__corrected')),
                _temperature=Round(Avg('temperature__value')),
                _thermal_conductivity=Round(Avg('conductivity__value')),
                _heat_generation=Round(Avg('heatgeneration__value')),
                )

def publication_data(request,slug):
    return JsonResponse(geojson_serializer(
        qs=annotate_data_average(Site.objects.filter(reference__slug=slug)),
        fields=['site_name','latitude','longitude','elevation','slug','_heat_flow','_thermal_gradient','_temperature','_thermal_conductivity','_heat_generation']),
        )

# def filter_data(request):
#     last_name = request.GET.get('last_name')
#     min_year = request.GET.get('year_min')
#     max_year = request.GET.get('year_max')
#     print(request.GET)
#     if not min_year:
#         min_year=0
#     if not max_year:
#         max_year=3000

#     filtered_data = Reference.objects.filter(primary_author__last_name__istartswith= last_name,)

#     print(len(filtered_data))
#     filtered_data = serialize('json',filtered_data)


#     data = {
#         'last_name': filtered_data
#     }
#     return JsonResponse(data)