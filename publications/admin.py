from django.contrib import admin
from django.conf.urls import url
from publications.models import CustomLink, CustomFile
import publications.admin_views
from django.utils.html import mark_safe
from ordered_model.admin import OrderedModelAdmin
from .models import Type, List, Publication
from django.urls import path

class CustomLinkInline(admin.TabularInline):
    model = CustomLink
    extra = 1
    max_num = 5
    fields = ['url','description']

class CustomFileInline(admin.TabularInline):
    model = CustomFile
    extra = 1
    max_num = 5
    fields = ['file','description']

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('edit','article','_authors', 'year', 'title', 'type',  'journal_or_book_title')
    # list_display_links = ('title',)
    change_list_template = 'admin/publications/publication_change_list.html'
    search_fields = ('id','title', 'booktitle', 'journal', 'authors', 'keywords', 'year')
    fieldsets = (
        (None, {'fields':
            ('type', 'title', 'authors', ('month', 'year'))}),
        (None, {'fields':
            ('journal', 'book_title', 'publisher', 'institution', ('volume', 'number'), 'pages')}),
        (None, {'fields':
            ('citekey', 'keywords', 'url', 'code', 'pdf', 'doi', 'isbn', 'note',)}),
        (None, {'fields':
            ('abstract',)}),
        (None, {'fields':
            ('lists',)}),
    )
    inlines = [CustomLinkInline, CustomFileInline]

    class Media:
        js = ("https://kit.fontawesome.com/a08181010c.js",)

    def get_urls(self):
        return [
                path('import_bibtex/', publications.admin_views.ImportBibtex.as_view(), name='publications_publication_import_bibtex'),
                    
            ] + super(PublicationAdmin, self).get_urls()

    def _authors(self, obj):
        authors = [a[1] for a in obj.authors_list_split]

        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return ' & '.join(authors)
        elif len(authors) == 3:
            return ', '.join(authors[:1]) + ' & ' + authors[2]
        else:
            return authors[0] + " et. al."

    def edit(self,obj):
        return mark_safe('<i class="fas fa-edit"></i>')
    
    def file(self,obj):
        return mark_safe('<i class="fas fa-edit"></i>')

@admin.register(Type)
class TypeAdmin(OrderedModelAdmin):
	list_display = ('type', 'description', 'hidden', 'move_up_down_links')

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
	list_display = ('list', 'description')

