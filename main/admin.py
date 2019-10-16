from django.contrib import admin
from .models import Page
from thermoglobe.mixins import BaseAdmin

# Register your models here.
@admin.register(Page)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name','content','edited_by','date_edited']
    class Media:
        js = [
            '/assets/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/assets/grappelli/tinymce_setup/tinymce_setup.js',

        ]


    def save_model(self, request, obj, form, change):
        if change:
            obj.edited_by = request.user._wrapped #add the current user to edited_by
        super().save_model(request, obj, form, change)