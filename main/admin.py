from django.contrib import admin
from .models import Page, Field, FAQ, News
from thermoglobe.mixins import BaseAdmin
from import_export.admin import ImportExportActionModelAdmin
from .resources import FieldResource, PageResource
from django.utils.html import mark_safe
# Register your models here.
class MainMixin(admin.ModelAdmin):

    # class Media:
    #     js = [
    #         '/assets/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
    #         '/assets/grappelli/tinymce_setup/tinymce_setup.js',
    #     ]


    def save_model(self, request, obj, form, change):
        if change:
            obj.edited_by = request.user._wrapped #add the current user to edited_by
        super().save_model(request, obj, form, change)


@admin.register(Page)
class PageAdmin(MainMixin,ImportExportActionModelAdmin):
    resource_class=PageResource
    list_display = ['id','heading','sub_heading','_content']
    exclude=['edited_by']

    def _content(self, obj):
        return mark_safe(obj.content)

@admin.register(Field)
class FieldAdmin(MainMixin,ImportExportActionModelAdmin):
    resource_class = FieldResource
    list_display = ['id','field_name','description','units']
    exclude=['edited_by']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    resource_class = FAQ
    list_display = ['id','question','_answer']

    def _answer(self,obj):
        return mark_safe(obj.answer)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    resource_class = News
    list_display = ['id','headline','published_by','published']