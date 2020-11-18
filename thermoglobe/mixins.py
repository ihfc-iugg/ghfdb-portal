from io import StringIO
import csv

from import_export.admin import ImportExportActionModelAdmin
from django.db.models import Count, F
from django.contrib import admin
from django.utils.translation import gettext as _
from django.contrib.gis import admin as gisadmin



# class BaseAdmin(gisadmin.ModelAdmin):
class BaseAdmin(gisadmin.OSMGeoAdmin):
    exclude = ['edited_by','added_by','date_added','date_edited']
    # list_display

    def save_model(self, request, obj, form, change):
        if change:
            obj.edited_by = request.user._wrapped #add the current user to edited_by
        super().save_model(request, obj, form, change)

    def site_name(self,obj):
        return obj._site_name
    site_name.admin_order_field = '_site_name'

    def latitude(self,obj):
        return obj._latitude
    latitude.admin_order_field = '_latitude'

    def longitude(self,obj):
        return obj._longitude
    longitude.admin_order_field = '_longitude'
   
    def site_operator(self,obj):
        return obj._operator
    site_operator.admin_order_field = '_operator'

    def reference(self,obj):
        return obj._reference
    reference.admin_order_field = '_reference'

    def conductivity_count(self,obj):
        return obj._conductivity_count
    conductivity_count.admin_order_field = '_conductivity_count'

    def gradient_count(self,obj):
        return obj._gradient_count
    gradient_count.admin_order_field = '_gradient_count'

    def heat_gen_count(self,obj):
        return obj._heat_gen_count
    heat_gen_count.admin_order_field = '_heat_gen_count'

    def temperature_count(self,obj):
        return obj._temperature_count
    temperature_count.admin_order_field = '_temperature_count'

    def heat_flow_count(self,obj):
        return obj._heat_flow_count
    heat_flow_count.admin_order_field = '_heat_flow_count'

    def _conductivity(self,obj):
        return obj._conductivity
    _conductivity.admin_order_field = '_conductivity'

    def _heat_generation(self,obj):
        return obj._heat_generation
    _heat_generation.admin_order_field = '_heat_generation'
    
    def sites(self,obj):
        return obj._site_count
    sites.admin_order_field = '_site_count'

    def edit(self,obj):
        return _("edit")
    

class SitePropertyAdminMixin(BaseAdmin):
    search_fields = ['site__site_name','site__latitude','site__longitude','reference__bib_id']
    autocomplete_fields = ['site']
    list_filter = ['method']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),)

        return queryset


class DownloadMixin:

    def post(self, request,  *args, **kwargs):
        # prepare the response for csv file
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(self.get_object().pk)
        zf = zipfile.ZipFile(response,'w')

        for key, qs in self.get_object().get_data().items():
            if qs.exists():
                export_fields = getattr(choices, key).get('detailed') + ['reference__bib_id']
                site_fields = [f.name for f in Site._meta.fields]
                query_fields = ['site__'+field if field in site_fields else field for field in export_fields ]
                # if key in ['temperature','conductivity','heat_generation']:
                #     query_fields[query_fields.index(key)] = 'value'

                # create a csv file an save it to the zip object
                zf.writestr('{}.csv'.format(key),self.csv_to_bytes(qs.values_list(*query_fields), export_fields))

        # add bibtex file to zip object
        zf.writestr('{}.bib'.format(self.get_object().bib_id),self.bibtex_to_bytes([self.get_object().bibtex]))

        return response

    def bibtex_to_bytes(self, bibtex_list):
        bib_buffer = StringIO()

        for bib_entry in bibtex_list:
            bib_buffer.write(bib_entry)

        return bib_buffer.getvalue()

    def csv_to_bytes(self, data, headers):
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        # write the header row;
        writer.writerow(headers)

        # write the rows to the csv file
        for i in data:
            writer.writerow(i)

        return csv_buffer.getvalue()