from django.shortcuts import render
from publications.models import Publication
from collections import defaultdict
from string import capwords
from djgeojson.serializers import Serializer as to_geojson
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.apps import apps
from django.utils.text import slugify
from thermoglobe.mixins import DownloadMixin 
from meta.views import MetadataMixin
from publications.models import Publication
from thermoglobe.forms import DownloadForm
from publications.paginator import NamePaginator
from django.core.paginator import InvalidPage

def year(request, year=None):
	years = []
	publications = Publication.objects.exclude(year__isnull=True)
	if year:
		publications = publications.filter(year=year)

	for publication in publications:
		# if publication.type.hidden:
		# 	continue
		if not years or (years[-1][0] != publication.year):
			years.append((publication.year, []))
		years[-1][1].append(publication)

	return render(request, 'publications/years.html', {
			'years': years
		})

class PublicationListView(ListView):
    model = Publication
    template_name = 'publications/publication_list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        context = {}
        context['page'] = self.get_page(on='year')
        
        years = []
        for publication in context['page'].object_list:
            if not years or (years[-1][0] != publication.year):
                years.append((publication.year, []))
            years[-1][1].append(publication)

        context['years'] = years

        return context

    def get_queryset(self):
        return super().get_queryset().exclude(year__isnull=True).order_by('-year')


    def get_page(self,on):
        paginator = NamePaginator(self.get_queryset(), on=on, per_page=self.paginate_by)

        try:
            page = int(self.request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            page = paginator.page(page)
        except (InvalidPage):
            page = paginator.page(paginator.num_pages)

        return page

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
        else:
            return list(range(1,paginator.num_pages+1))

    def get_filter_parameters(self):
        """Gets url parameters from the filter and returns as a string to be placed behind paginator links"""
        request_copy = self.request.GET.copy()
        request_copy.pop('page', True)
        if request_copy:
            return '&'+request_copy.urlencode()
        else:
            return ''

class PublicationDetailsView(DownloadMixin, MetadataMixin, DetailView):
    template_name = "publications/details.html"
    download_form = DownloadForm
    model = Publication
    options = {'pageLength':50}
    tables = dict(
        intervals=['depth_min','depth_max','heat_flow','gradient'],
        conductivity=['count','depth_min','depth_max','min_conductivity','max_conductivity'],
        temperature=['count','depth_min','depth_max','min_temperature','max_temperature'],
        heat_production=['count','depth_min','depth_max','min_heat_production','max_heat_production'],
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bibtex'] = json.dumps(self.get_object().bibtex)
        # context['meta'] = self.get_object().as_meta(self.request)
        context['sidebar'] = 'active'


        return context

    def get_table(self,data_type, fields):
        fields = ['slug','site_name','latitude','longitude'] + fields
        qs = (apps.get_model('thermoglobe','Site')
                .objects.filter(reference=self.get_object())
                .table(data_type)
                .values_list(*fields)
        )
        return dict(
            id=slugify(data_type),
            data=json.dumps(list(qs)),
            columns=[field.replace('_',' ') for field in fields],
            )