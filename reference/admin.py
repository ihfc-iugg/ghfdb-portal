from django.contrib import admin
from .models import Author, Reference, FileStorage
from django.db.models import Count


#Register your models here.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    counts = ['first_authorships','co_authorships']
    list_display = ['id','last_name','first_name'] + counts
    search_fields = ('last_name',)
    exclude = ['added_by','edited_by']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _first_count=Count("first_author", distinct=True),
            _co_author_count=Count("co_authors", distinct=True),)
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
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ['id','first_author', 'year', 'co_authors_display', 'title',  'doi', 'source',]    
    # exclude = ['_co_authors',]
    list_filter = ('first_author', 'year',)
    search_fields = ('year', 'first_author__last_name')

    raw_id_fields = ('first_author', 'co_authors')
    # define the related_lookup_fields
    # related_lookup_fields = {
    #     'fk': ['first_author'],
    #     # 'm2m': ['co_authors'],
    # }

    autocomplete_lookup_fields = {

        'fk': ['first_author'],
        'm2m': ['co_authors']
    }


    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # queryset = queryset.annotate(
        #     # _heat_gen_count=Count("heatgeneration", distinct=True),
        #     # _temperature_count=Count("temperature", distinct=True),
        #     # _heat_flow_count=Count("heatflow", distinct=True),
        #     # _conductivity_count=Count("conductivity", distinct=True),
        #     _site_count = Count("site",distinct=True),
        #     )
        return queryset

@admin.register(FileStorage)
class FileStorageAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'date_uploaded', 'added', 'date_added', 'added_by', 'data']    

    list_filter = ('added',)


