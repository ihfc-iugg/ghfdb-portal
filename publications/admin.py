from django.contrib import admin
import publications.admin_views
from django.utils.html import mark_safe
from .models import Publication
from django.urls import path
from import_export.admin import ImportExportActionModelAdmin
from .resources import PublicationResource


@admin.register(Publication)
class PublicationAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_class = PublicationResource
    from_encoding = 'Latin-1'
    list_display = ('edit', 'article', '_authors', 'year',
                    'title', 'type',  'journal_or_book_title')
    list_filter = ['ENTRYTYPE', ]
    # change_list_template = 'admin/publications/publication_change_list.html'
    search_fields = ('id', 'title', 'journal', 'author', 'keywords', 'year')
    readonly_fields = ['citekey','ENTRYTYPE','title','author', 'year',
                       'journal','keywords','url','doi','abstract',]

    fields = (
        'pdf',
        'citekey',
        'ENTRYTYPE',
        'abstract',
        'title',
        'year',
        'author',
        'journal',
        'url',
        'doi',
        'keywords',
        'bibtex',
    )

    class Media:
        js = ("https://kit.fontawesome.com/a08181010c.js",)

    def get_urls(self):
        return [
            path('import_bibtex/', publications.admin_views.ImportBibtex.as_view(),
                 name='publications_publication_import_bibtex'),

        ] + super(PublicationAdmin, self).get_urls()

    def _authors(self, obj):
        # authors = custom.getnames()
        if obj.author:
            return obj.author[:30]
        else:
            return None
        authors = [a[1] for a in obj.authors_list_split]

        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return ' & '.join(authors)
        elif len(authors) == 3:
            return ', '.join(authors[:1]) + ' & ' + authors[2]
        else:
            return authors[0] + " et. al."

    def edit(self, obj):
        return mark_safe('<i class="fas fa-edit"></i>')

    def file(self, obj):
        return mark_safe('<i class="fas fa-edit"></i>')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('keywords')

    def _keywords(self, obj):
        return u", ".join(o.name for o in obj.keywords.all())
