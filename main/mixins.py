from io import StringIO
import zipfile

from django.utils.translation import gettext as _
from django.contrib.gis import admin as gisadmin
from django.utils.html import mark_safe
from django.http import HttpResponse
from django.contrib import messages
from django_super_deduper.merge import MergedModelInstance
from django.contrib.admin.models import LogEntry, ContentType
from database.models import Site
from publications.models import Publication
from datetime import datetime as dt
from simple_history.admin import SimpleHistoryAdmin

class BaseAdmin(gisadmin.OSMGeoAdmin, SimpleHistoryAdmin):
    exclude = ['edited_by','added_by','date_added','date_edited']

    def save_model(self, request, obj, form, change):
        if change:
            obj.edited_by = request.user._wrapped #add the current user to edited_by
        super().save_model(request, obj, form, change)

    def merge(self, request, qs):
        to_be_merged = [str(x) for x in qs]
        if len(to_be_merged) > 2:
            to_be_merged = f"{', '.join(to_be_merged[:-1])} and {to_be_merged[-1]}"
        else:
            to_be_merged = ' and '.join(to_be_merged)
        change_message = f"Merged {to_be_merged} into a single {qs.model._meta.verbose_name}"
        merged = MergedModelInstance.create(qs.first(),qs[1:],keep_old=False)
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(qs.model).pk,
            object_id=qs.first().pk,
            object_repr=str(qs.first()),
            action_flag=2, #CHANGE
            change_message=_(change_message),
        )
        self.message_user(request, change_message, messages.SUCCESS)

    merge.short_description = "Merge duplicate entries"

    class Media:
        js = ("https://kit.fontawesome.com/a08181010c.js",)
        css = {'all': ['main/css/admin/table.css']}

    def name(self,obj):
        return obj._name
    name.admin_order_field = '_name'

    def latitude(self,obj):
        return obj._lat
    latitude.admin_order_field = '_latitude'

    def longitude(self,obj):
        return obj._lng
    longitude.admin_order_field = '_longitude'
   
    def site_operator(self,obj):
        return obj._operator
    site_operator.admin_order_field = '_operator'

    def reference(self,obj):
        return obj._reference
    reference.admin_order_field = '_reference'
  
    def sites(self,obj):
        return obj._site_count
    sites.admin_order_field = '_site_count'

    def edit(self, obj):
        return mark_safe('<i class="fas fa-edit"></i>')
    edit.short_description = ''
    

class DownloadMixin:

    def get(self, request, *args, **kwargs):
        if "download" in request.GET.keys():
            return self.download(request, *args, **kwargs)
        else:
            return super().get(self, request, *args, **kwargs)

    def download(self, request, *args, **kwargs):
        response, zf = self.prepare_zip_response(fname=self.get_object())

        references = Publication.objects.none()
        for key, qs in self.get_object().get_data().items():
            if key == 'intervals' and qs.exists():
                # create a csv file and save it to the zip object
                zf.writestr(f"{key}.csv", qs.values_list().to_csv_buffer())
                sites = Site.objects.filter(**{f"{key}__in":qs})
            elif qs.exists():
                # create a csv file and save it to the zip object
                zf.writestr(f"{key}.csv", qs.explode_values().to_csv_buffer())
                sites = Site.objects.filter(**{f"{key}_logs__in":qs})

            references = references | Publication.objects.filter(sites__in=sites).distinct()
        
        # write references to .bib file
        if references:
            zf.writestr(f'{self.get_object()}.bib', self.references_to_bibtex(references))

        return response

    def references_to_bibtex(self, references):
        # add bibtex file to zip object
        references = references.distinct().exclude(bibtex__isnull=True).values_list('bibtex',flat=True)
        buffer = StringIO()
        buffer.write('\n\n'.join(references))
        return buffer.getvalue()

    def prepare_zip_response(self, fname=None):
        # prepare the response for csv file
        response = HttpResponse(content_type='application/zip')
        if fname is None:
            fname = f"Thermoglobe_{dt.now().strftime('%d_%b_%Y')}"
        response['Content-Disposition'] = f'attachment; filename="{fname}.zip"'
        return response, zipfile.ZipFile(response, 'w')


