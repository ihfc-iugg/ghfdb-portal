from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from .models import Reference
from django.core.paginator import Paginator
from django.conf import settings
from django.core.serializers import serialize
from django.contrib.gis.db.models.aggregates import Union
from django.contrib.gis.db.models.functions import Centroid
from django.template.defaulttags import register
from django.http import HttpResponse
from django.utils import timezone
from django_filters.views import FilterView
from .filters import ReferenceFilter
from django.db.models import Max, Min
from main.forms import DownloadForm
from django.db.models import Count, F, Value, Func, Sum, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from main.models import DepthInterval
from mapping.views import DOWNLOAD_FIELDS
import csv
import bibtexparser as bib

class AllReferencesView(ListView):
    template_name = "reference/reference_list.html"
    model = Reference
    context_object_name = 'users'  # Default: object_list
    paginate_by = 10
    pag_neighbours = 4


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        qs = self.get_queryset()

        context['count'] = qs.count()
        min_max = self.get_queryset().aggregate(Max('year'), Min('year'))
        if min_max:
            context['num_years'] = min_max['year__max'] - min_max['year__min']

        else:
            context['num_years'] = 'Unknown'

        # context['filter'] = ReferenceFilter(self.request.GET, queryset=qs.order_by(F('year').desc(nulls_last=True)))

        # qs = context['filter'].qs

        paginator = Paginator(qs,per_page=25,orphans=5)

        page = self.request.GET.get('page') 

        try:
            filtered_qs = paginator.page(page)
            context['range'] = self.paginator_fix(paginator,int(page))
        except PageNotAnInteger:
            filtered_qs = paginator.page(1)
            context['range'] = self.paginator_fix(paginator,1)
        except EmptyPage:
            filtered_qs = paginator.page(paginator.num_pages)

        context['paginator'] = paginator
        context['result'] = filtered_qs

        return context

    def paginator_fix(self,paginator,page):
        if paginator.num_pages > 2*self.pag_neighbours:
            start_index = max(1, page-self.pag_neighbours)
            end_index = min(paginator.num_pages, page + self.pag_neighbours)
            if end_index < start_index + 2*self.pag_neighbours:
                end_index = start_index + 2*self.pag_neighbours
            elif start_index > end_index - 2*self.pag_neighbours:
                start_index = end_index - 2*self.pag_neighbours
            if start_index < 1:
                end_index -= start_index
                start_index = 1
            elif end_index > paginator.num_pages:
                start_index -= (end_index-paginator.num_pages)
                end_index = paginator.num_pages
            page_list = [f for f in range(start_index, end_index+1)]
            return page_list[:(2*self.pag_neighbours + 1)]


    def filter_data(self):

        return self.get_queryset().filter(primary_author__last_name__istartswith=self.request.GET.get('last_name'),)

class ReferenceView(DetailView):
    template_name = "reference/reference_details.html"
    model = Reference

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['all_sites'] = context['object'].site_set.all().order_by('site_name').annotate(
                    avg_heatflow = Avg('heatflow__corrected'),
                    avg_conductivity = Avg('conductivity__value'),
                    avg_heatgen = Avg('heatgeneration__value'))

        context['points'] = serialize('geojson',context['all_sites'],
                    geometry_field='geom',)

        # context['reference'] = bib.loads(context['object'].bibtex).entries[0]
        context['reference'] = self.get_bibtex_details(context['object'])

        return context

    def post(self, request, pk):

        my_csv = DepthInterval.objects.filter(reference=pk).values_list(*[field[0] for field in DOWNLOAD_FIELDS])
        filename = '{}.csv'.format(self.model.objects.get(id=pk))
        
         # prepare the response for csv file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        writer = csv.writer(response)

        # write the header row; remove "site__" prefix for some fields for clarity
        writer.writerow([field[1] for field in DOWNLOAD_FIELDS])

        # write the rows to the csv file
        for i in my_csv:
            writer.writerow(i)

        return response

    def get_bibtex_details(self,reference):
        if reference.bibtex:
            fields = ['author','title','year','journal','doi','abstract']
            reference = bib.loads(reference.bibtex).entries[0]
            
            return {key:reference[key] for key in fields if reference.get(key,False) }

from django.contrib.auth.models import User
from django.http import JsonResponse

def filter_data(request):
    last_name = request.GET.get('last_name')
    min_year = request.GET.get('year_min')
    max_year = request.GET.get('year_max')
    print(request.GET)
    if not min_year:
        min_year=0
    if not max_year:
        max_year=3000


    filtered_data = Reference.objects.filter(primary_author__last_name__istartswith= last_name,)

    print(len(filtered_data))
    filtered_data = serialize('json',filtered_data)


    data = {
        'last_name': filtered_data
    }
    return JsonResponse(data)