from django.contrib import admin
from .models import Page, Field, FAQ, News
from thermoglobe.mixins import BaseAdmin
from import_export.admin import ImportExportActionModelAdmin
from .resources import FieldResource, PageResource
from django.utils.html import mark_safe
# Register your models here.
class MainMixin(admin.ModelAdmin):

    class Media:
        js = ("https://kit.fontawesome.com/a08181010c.js",
        "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js",
        )
        css = {'all': ['thermoglobe/css/admin/table.css',]}


@admin.register(Page)
class PageAdmin(MainMixin):
    resource_class=PageResource
    list_display = ['id','heading','sub_heading','_content']
    exclude=['edited_by']

    def _content(self, obj):
        return mark_safe(obj.content)

@admin.register(Field)
class FieldAdmin(MainMixin):
    resource_class = FieldResource
    list_display = ['verbose_field_name','field_name','units','required','download_only','table','description']
    list_filter = ['table',]
    exclude=['edited_by']
    fields = [
        'table',
        ('field_name','verbose_field_name'),
        'units',
        ('required','download_only'),
        'description',
    ]

@admin.register(FAQ)
class FAQAdmin(MainMixin):
    resource_class = FAQ
    list_display = ['id','question','_answer']

    def _answer(self,obj):
        return mark_safe(obj.answer)

@admin.register(News)
class NewsAdmin(MainMixin):
    resource_class = News
    list_display = ['id','headline','published_by','published']