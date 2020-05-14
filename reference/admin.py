from django.contrib import admin
from .models import Author, Reference, Upload, Operator
from django.db.models import Count
import bibtexparser as bib
from .widgets import get_author_objects
from pprint import pprint
from django.utils.html import mark_safe
from main import inlines
from thermoglobe.mixins import BaseAdmin
from thermoglobe import resources
from datetime import datetime as dt
from tablib import Dataset
from django.http import HttpResponseRedirect

#Register your models here.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    counts = ['first_authorships','co_authorships']
    list_display = ['last_name','first_name', 'middle_name'] + counts
    search_fields = ('last_name',)
    exclude = ['added_by','edited_by']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _first_count=Count("as_first_author", distinct=True),
            _co_author_count=Count("as_coauthor", distinct=True),)
        return queryset

    def co_authorships(self,obj):
        return obj._co_author_count
    co_authorships.admin_order_field = '_co_author_count'

    def first_authorships(self,obj):
        return obj._first_count
    first_authorships.admin_order_field = '_first_count'


    # def references(self,obj):
        # return obj._total_references
    # references.admin_order_field = '_total_references'

@admin.register(Reference)
class ReferenceAdmin(BaseAdmin):
    # date_hierarchy = 'date_added'
    counts = ['sites']
    list_display = ['__str__','entry_type','year', 'title', 'journal', 'article', 'slug']
    exclude = ['source',]
    search_fields = ('year', 'first_author__last_name')
    raw_id_fields = ('first_author', 'co_authors')
    readonly_fields = ['entry_type','year']
    fields = ['bib_id','entry_type','year',('first_author','co_authors'),'title','journal','doi','bibtex']

    autocomplete_lookup_fields = {
        'fk': ['first_author'],
        'm2m': ['co_authors']
    }

    # inlines = [HeatFlowInline,]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _site_count=Count("sites",distinct=True),
            # _heat_flow_count=Count("heatflow", distinct=True),
            # _heat_gen_count=Count("heatgeneration", distinct=True),
            # _temperature_count=Count("temperature", distinct=True),
            # _conductivity_count=Count("conductivity", distinct=True),
            # _gradient_count=Count("thermalgradient", distinct=True),


        )
        return queryset

    def save_model(self, request, obj, form, change):
        if change:
            bib_obj = bib.loads(form.instance.bibtex)
            bib_dict = bib_obj.entries[0]

            if not bib_dict['ID'] == form.instance.bib_id:
                bib_dict['ID'] = form.instance.bib_id

                form.instance.bibtex = bib.dumps(bib_obj)
        else:
            form.instance.source = 'Admin Created'

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        if form.instance.co_authors_list:
            form.instance.co_authors.add(*form.instance.co_authors_list)
            # for author in form.instance.co_authors_list:
            #     form.instance.co_authors.add(author)


    def article(self,obj):
        if obj.doi:
            return mark_safe('<a href="https://doi.org/{}">view</a>'.format(obj.doi))
        else:
            return ''

#Register your models here.
@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    counts = ['site_count',]
    list_display = ['name',] + counts
    search_fields = ('name',)
    exclude = ['added_by','edited_by']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _site_count=Count("sites", distinct=True),
           )
        return queryset

    def site_count(self,obj):
        return obj._site_count
    site_count.admin_order_field = '__site_count'

@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', '_email', 'data_type', 'date_uploaded', 'imported', 'date_imported', 'imported_by', 'data']

    list_filter = ('imported',)
    readonly_fields = ['first_name','last_name','email','imported','imported_by','date_imported']

    fields = (
        ('first_name','last_name'),
        'email',
        'data_type',
        'data',
        'bibtex',
        'imported_by',
        'date_imported',
        )

    change_form_template = "admin/upload_changeform.html"

    def _email(self,obj):
        return mark_safe('<a href="mailto:{}">{}</a>'.format(obj.email,obj.email))

    def save_model(self, request, obj, form, change):
        form.instance.imported = True
        form.instance.imported_by = request.user
        form.instance.date_imported = dt.now()
        super().save_model(request, obj, form, change)

    def import_data(self,request,obj):
        resource_switch = {
            '0':resources.HeatFlowResource(),
            '1':resources.HeatFlowResource(),
            '2':resources.TempResource(),
            '3':resources.ConductivityResource(obj.bibtex),
            '4':resources.HeatGenResource(),
            }
        
        resource = resource_switch[request.POST['data_type']]
        data_file = obj.data
        dataset = Dataset().load(data_file.read().decode('utf-8'))
        result = resource.import_data(dataset=dataset, dry_run=False)

    # def has_delete_permission(self, request, obj=None):
    #     return False
    
    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if 'delete_selected' in actions:
    #         del actions['delete_selected']
    #     return actions
    
    def response_change(self, request, obj):
        if "_import" in request.POST:
            self.import_data(request,obj)
            obj.save()
            self.message_user(request, "The uploaded file was succesfully imported.")
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)