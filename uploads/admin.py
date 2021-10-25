from django.contrib import admin
from thermoglobe import resources
from .models import Upload
from django.utils.html import mark_safe
from django.utils import timezone
from django.http import HttpResponseRedirect
from tablib import Dataset

# Register your models here.
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

    # change_form_template = "admin/upload_changeform.html"

    def _email(self,obj):
        return mark_safe('<a href="mailto:{}">{}</a>'.format(obj.email,obj.email))

    def save_model(self, request, obj, form, change):
        form.instance.imported = True
        form.instance.imported_by = request.user
        form.instance.date_imported = timezone.now()
        super().save_model(request, obj, form, change)

    def import_data(self,request,obj):
        resource_switch = {
            '0':resources.IntervalResource(),
            '1':resources.IntervalResource(),
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