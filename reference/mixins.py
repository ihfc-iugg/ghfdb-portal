from django.views.generic import ListView
from django.db.models import Count, F, Value, Func, Sum, Avg
from main.utils import get_page_or_none

class CustomListView(ListView):
    pag_neighbours = 4
    paginate_by = 25
    template_name = "reference/generic_list.html"

    def get_queryset(self):
        return self.model.objects.all().annotate(site_count=Count('sites'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['range'] = self.paginator_fix(context['paginator'],context['page_obj'].number)
        context['fields'] = self.fields
        context['page'] = get_page_or_none(self.page_id)
        context['object_url'] = self.details_url
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
        else:
            return list(range(1,paginator.num_pages+1))