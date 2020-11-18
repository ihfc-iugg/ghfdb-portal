from django.views.generic import ListView
from django.db.models import Count, F, Value, Func, Sum, Avg
from main.utils import get_page_or_none
import bibtexparser as bib
from django.contrib import admin
from django.utils.translation import gettext as _
from django.http import HttpResponse, HttpResponseRedirect
from django_super_deduper.merge import MergedModelInstance
from django.db import IntegrityError

class CustomListView(ListView):
    pag_neighbours = 4
    paginate_by = 25
    template_name = "publications/generic_list.html"

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

class AuthorAdmin(admin.ModelAdmin):
    # counts = ['first_authorships','co_authorships']
    list_display = ['name','_references']
    search_fields = ('last_name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('publications').annotate(
            _reference_count=Count("publications", distinct=True),
            )
        return queryset

    def co_authorships(self,obj):
        return obj._co_author_count
    co_authorships.admin_order_field = '_co_author_count'

    def first_authorships(self,obj):
        return obj._first_count
    first_authorships.admin_order_field = '_first_count'

    def name(self, obj):
        return obj.get_full_name()
    name.admin_order_field = 'last_name'

    def _references(self,obj):
        return obj._reference_count
    _references.admin_order_field = '_reference_count'

    def merge_authors(self, request, qs):
        merged = MergedModelInstance.create(qs.first(),qs[1:],keep_old=False)
    actions = ["merge_authors"]


class PublicationAdmin(admin.ModelAdmin):
    change_form_template = 'admin/upload_changeform.html'
    counts = ['sites']
    list_display = ['edit','article','type','year','_authors', 'title', 'journal','bib_id','is_verified','verified_by','date_verified']
    exclude = ['source','authors']
    search_fields = ('year', 'bib_id')
    fields = [('bib_id','is_verified'),'bibtex']
    actions = ["export_bibtex","merge_references"]

    class Media:
        js = ("https://kit.fontawesome.com/a08181010c.js",)

    def article(self,obj):
        if obj.doi:
            return mark_safe('<a href="https://doi.org/{}"><i class="fas fa-globe fa-lg"></i></a>'.format(obj.doi))
        else:
            return ''

    def edit(self,obj):
        return mark_safe('<i class="fas fa-edit"></i>')

    def _authors(self,obj):
        return obj.display_authors()


    def export_bibtex(self, request, qs):
        """
        Exports the selected rows using file_format.
        """
        bibtex_list = list(qs.values_list('bibtex',flat=True))
        response = HttpResponse(''.join(bibtex_list), content_type='application/text charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="ThermoGlobe.bib"'
        return response
    export_bibtex.short_description = _(
        'Export bibtex')



    def merge_references(self, request, qs):
        merged = MergedModelInstance.create(qs.first(),qs[1:],keep_old=False)
        # qs[1:].delete()

        # for pub in qs:
        #     x = models.Publication.objects.filter(bib_id__icontains=pub.bib_id.strip())
        #     if x.count() == 2:
        #         try:
        #             merged = MergedModelInstance.create(x[0],[x[1]])
        #         except IntegrityError:
        #             merged = MergedModelInstance.create(x[1],[x[0]])
        #         if x[0].interval_set.exists():
        #             x[1].delete()
        #         else:
        #             x[0].delete()