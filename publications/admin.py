from django.contrib import admin
from datetime import datetime as dt
from .models import Author, Publication, Operator, Upload
from django.db.models import Count
import bibtexparser as bib
from .widgets import get_author_objects
from pprint import pprint
from django.utils.html import mark_safe
from thermoglobe.mixins import BaseAdmin
from thermoglobe import resources
from datetime import datetime as dt
from tablib import Dataset
from django.http import HttpResponseRedirect

class PublicationInline(admin.TabularInline):
    model = Publication.authors.through
    extra = 0

#Register your models here.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    # counts = ['first_authorships','co_authorships']
    list_display = ['name','_references']
    search_fields = ('last_name',)
    exclude = ['added_by','edited_by']
    inlines = [PublicationInline, ]

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

@admin.register(Publication)
class PublicationAdmin(BaseAdmin):
    change_form_template = 'admin/upload_changeform.html'
    counts = ['sites']
    list_display = ['edit','article','type','year','_authors', 'title', 'journal','bib_id','is_verified','verified_by','date_verified']
    exclude = ['source','authors']
    search_fields = ('year', )
    readonly_fields = ['bib_id',]
    fields = [('bib_id','is_verified'),'bibtex']

    class Media:
            # css = {
            #     'all': ('css/admin.css',),
            # }
            js = ("https://kit.fontawesome.com/a08181010c.js",)

    def response_change(self, request, obj):
        if "_upload" in request.POST:
            # print('Doing something now')
            # self.import_data(request,obj)
            # obj.save()
            # self.message_user(request, "The uploaded file was succesfully imported.")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    # def import_data(self,request,obj):
    #     resource_switch = {
    #         '0':resources.HeatFlowResource(),
    #         '1':resources.HeatFlowResource(),
    #         '2':resources.TempResource(),
    #         '3':resources.ConductivityResource(obj.bibtex),
    #         '4':resources.HeatGenResource(),
    #         }
        
    #     resource = resource_switch[request.POST['data_type']]
    #     data_file = obj.data
    #     dataset = Dataset().load(data_file.read().decode('utf-8'))
    #     result = resource.import_data(dataset=dataset, dry_run=False)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _site_count=Count("sites",distinct=True),
            )
        return queryset

    def save_model(self, request, obj, form, change):
        if change:
            if form.instance.is_verified != form.initial['is_verified']:
                if form.instance.is_verified == True:
                    form.instance.verified_by = request.user._wrapped
                    form.instance.date_verified = dt.now()
        else:
            form.instance.source = 'Admin Created'

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # self.authors.add(*self.authors_list)
        form.instance.save()
        super().save_related(request, form, formsets, change)

        # if form.instance.co_authors_list:
        #     form.instance.co_authors.add(*form.instance.co_authors_list)
            # for author in form.instance.co_authors_list:
            #     form.instance.co_authors.add(author)

    def article(self,obj):
        if obj.doi:
            return mark_safe('<a href="https://doi.org/{}"><i class="fas fa-globe fa-lg"></i></a>'.format(obj.doi))
        else:
            return ''

    def edit(self,obj):
        return mark_safe('<i class="fas fa-edit"></i>')

    def _authors(self,obj):
        # print(obj.display_authors())
        return obj.display_authors()


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
    list_display = ['first_name', 'last_name', '_email', 'data_type', 'date_uploaded', 'imported', 'date_imported', 'data']

    list_filter = ('imported',)
    readonly_fields = ['first_name','last_name','email','imported','date_imported']

    fields = (
        ('first_name','last_name'),
        'email',
        'data_type',
        'data',
        'bibtex',
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
    
    def response_change(self, request, obj):
        if "_import" in request.POST:
            self.import_data(request,obj)
            obj.save()
            self.message_user(request, "The uploaded file was succesfully imported.")
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)