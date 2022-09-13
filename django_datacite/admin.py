from django.contrib import admin
from .models import Subject, Right, Schema
from django.utils.html import mark_safe
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django.contrib import messages


@admin.register(Schema)
class SchemaAdmin(admin.ModelAdmin):
    list_display = ['title','description','default']
    fields = ['title','description','schema',]
    actions = ['set_default']

    def save_model(self, request, obj, form, change):
        if not obj.title:
            obj.title = obj.schema.get('title', None)

        if not obj.description:
            obj.description = obj.schema.get('description')

        return super().save_model(request, obj, form, change)

    def set_default(self, request, qs):
        if qs.count() > 1:
            self.message_user(request, 'Setting multiple schemas to default is not allowed', messages.ERROR)
        else:
            qs.update(default=True)
            Schema.objects.exclude(id__in=qs.values_list('id',flat=True)).update(default=False)

            self.message_user(request, f'Successfuly changed default schema to {qs.first().title}', messages.SUCCESS)

    set_default.short_description = "Set as default schema"

@admin.register(Right)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ['name','about','_snippet']
    # list_editable = ['snippet']

    def _snippet(self, obj):
        return mark_safe(str(obj.snippet))
    _snippet.short_description = 'Snippet'
    _snippet.admin_order_field = 'snippet'


@admin.register(Subject)
class KeywordAdmin(TreeAdmin):
    form = movenodeform_factory(Subject)
    search_fields = [
        'keyword',
    ]





