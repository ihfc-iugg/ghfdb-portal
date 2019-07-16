from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
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

class AllReferencesView(ListView):
    template_name = "reference/reference_list.html"
    model = Reference
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        # qs = self.get_queryset()

        qs = self.get_queryset()

        print('here')

        context['count'] = qs.count()
        min_max = self.get_queryset().aggregate(Max('year'), Min('year'))
        context['num_years'] = min_max['year__max'] - min_max['year__min']


        context['filter'] = ReferenceFilter(self.request.GET, queryset=qs.order_by(F('year').desc(nulls_last=True)))

        qs = context['filter'].qs

        paginator = Paginator(qs,50)
        page = self.request.GET.get('page',1)

        try:
            filtered_qs = paginator.page(page)
        except PageNotAnInteger:
            filtered_qs = paginator.page(1)
        except EmptyPage:
            filtered_qs = paginator.page(paginator.num_pages)


        context['paginator'] = paginator
        context['result'] = filtered_qs

        print('down here')

        return context

    def filter_data(self):

        return self.get_queryset().filter(primary_author__last_name__istartswith=self.request.GET.get('last_name'),)

class ReferenceView(TemplateView):
    template_name = "reference/reference_details.html"
    download_form = DownloadForm

    def get(self, request, reference_id=None, reference_slug=None):
        reference = get_object_or_404(Reference, pk=reference_id)
        sites = reference.site_set.all().order_by('site_name').annotate(
                        avg_heatflow = Avg('heatflow__corrected'),
                        avg_conductivity = Avg('conductivity__value'),
                        avg_heatgen = Avg('heatgeneration__value'))

        points = serialize('geojson',sites,
                    geometry_field='geom',)
        return render(request,self.template_name,{'reference':reference,'point':points,'all_sites':sites,'form': self.download_form})

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