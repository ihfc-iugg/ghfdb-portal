from django.contrib import admin
from .models import Author, Reference, FileStorage
from django.db.models import Count
import bibtexparser as bib
from .widgets import get_authors
from pprint import pprint
from django.utils.html import mark_safe

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
    list_display = ['first_author', '_co_authors','year', 'title', 'journal', 'article','date_added']    
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
        return queryset

    def save_model(self, request, obj, form, change):
        if change:
            # obj.instance.edited_by = request.user

            bib_obj = bib.loads(form.instance.bibtex)
            bib_dict = bib_obj.entries[0]
            if not bib_dict['ID'] == form.instance.bib_id:
                bib_dict['ID'] = form.instance.bib_id
                form.instance.bibtex = bib.dumps(bib_obj)

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        bib_obj = bib.loads(form.instance.bibtex).entries[0]

        co_authors = get_authors(bib_obj['author'],Author)[1:]
        for author in co_authors:
            form.instance.co_authors.add(author)

    def get_authors(self, author_string):
        name_type = ['last','first']
        author_list = []
        for author in author_string.split('and'):
            # author = author.split(',')
            # author = [author[0]] + author[1].split()
            # authors.append({key+'_name':name.strip().replace('.','') for key,name in zip(name_type,author)})

            author = author.split(',')
            author = [author[0]] + author[1].split()
            author = {key+'_name':name.strip().replace('.','') for key,name in zip(name_type,author)}


            try:
                author_list.append(Author.objects.update_or_create(last_name=author['last_name'],defaults=author)[0])
            except model.MultipleObjectsReturned:
                try: 
                    author_list.append(Author.objects.update_or_create( last_name=author['last_name'],
                                                                        first_name__startswith=author['first_name'][0],
                                                                        defaults=author)[0])
                except model.MultipleObjectsReturned:
                    try:
                        author_list.append(Author.objects.update_or_create( last_name=author['last_name'],
                                                                            first_name=author['first_name'],
                                                                            defaults=author)[0])
                    except model.MultipleObjectsReturned:
                        print(ValueError('Found more than one author by the name {} {}. Please double check'.format(author['last_name'],author['first_name'][0])))

        return author_list

    def article(self,obj):
        if obj.doi:
            return mark_safe('<a href="https://doi.org/{}">view</a>'.format(obj.doi))
        else:
            return ''
@admin.register(FileStorage)
class FileStorageAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'date_uploaded', 'added', 'date_added', 'added_by', 'data']    

    list_filter = ('added',)


