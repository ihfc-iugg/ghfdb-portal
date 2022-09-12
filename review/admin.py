from django.contrib import admindocs
from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from .models import Review

# Register your models here.
@admin.register(Review)
class ReviewAdmin(ExportActionModelAdmin):
    list_display = ['publication','reviewer','nominated','submitted','accepted']
    readonly_fields = ['id']
    actions = ["accept",]
    date_hierarchy = 'nominated'

    # filter_horizontal = ['references']
    raw_id_fields = ('publication',)

    autocomplete_lookup_fields = {
        'm2m': ['publication'],
    }

    def accept(self):
        return






