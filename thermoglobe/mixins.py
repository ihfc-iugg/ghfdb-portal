from io import StringIO
import csv, json, zipfile

from import_export.admin import ImportExportActionModelAdmin
from django.db.models import Count, F
from django.contrib import admin
from django.utils.translation import gettext as _
from django.contrib.gis import admin as gisadmin
from django.utils.html import mark_safe
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.apps import apps
from thermoglobe import choices
from thermoglobe.forms import DownloadForm
from django.contrib import messages
from django_super_deduper.merge import MergedModelInstance
from django.contrib.admin.models import LogEntry, ContentType
from import_export.formats.base_formats import CSV

class TableMixin:
    options = {}
    mark_safe = False
    table_headers = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['options'] = self.table_options(format='json')
        # context['headers'] = self.tables_headers
        return context
    
    def table_options(self,format=None):
        options = dict(
            autoWidth=False,
            dom='<"top d-flex justify-content-around align-items-baseline"lpf>t<"bottom"ip><"clear">',
            order_by='year',
            pageLength=100,
            deferRender=True,
            responsive=True,
            )
        options.update(**self.options)
        
        if format == 'json':
            options = json.dumps(options)
        if self.mark_safe:
            return mark_safe(options)
        return options

    def get_tables(self):
        tables = {}

        for table, fields in self.tables.items():
            tables[table] = self.get_table(table, fields)

        for table in context['tables'].values():
            if table['data']:
                table['active'] = True
                break

# class BaseAdmin(gisadmin.ModelAdmin):
class BaseAdmin(gisadmin.OSMGeoAdmin):
    exclude = ['edited_by','added_by','date_added','date_edited']
    formats = [CSV]

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
        css = {'all': ['thermoglobe/css/admin/table.css']}

    # def add_publication(self, request, qs):

    #     # change_message = f"Merged {to_be_merged} into a single {qs.model._meta.verbose_name}"
    #     pub1 = qs[0]
    #     pub2 = qs[1]

    #     for site in pub1.sites.all():
    #         site.references.add(pub2)
        
    #     for site in pub2.sites.all():
    #         site.references.add(pub1)

        


    #     # merged = MergedModelInstance.create(qs.first(),qs[1:],keep_old=False)
    #     LogEntry.objects.log_action(
    #         user_id=request.user.pk,
    #         content_type_id=ContentType.objects.get_for_model(qs.model).pk,
    #         object_id=qs.first().pk,
    #         object_repr=str(qs.first()),
    #         action_flag=2, #CHANGE
    #         change_message=_(change_message),
    #     )
    #     self.message_user(request, change_message, messages.SUCCESS)

    # merge.short_description = "Merge duplicate entries"


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
    download_form = DownloadForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data( *args, **kwargs)
        context['download_form'] = self.download_form()
        return context

    def post(self, request,  *args, **kwargs):

        options = self.download_form(self.request.POST)
        if options.is_valid():
            download_type = options.cleaned_data['download_type']
            data_select = options.cleaned_data['data_select']

            # prepare the response for csv file
            response = HttpResponse(content_type='application/zip')
            
            response['Content-Disposition'] = f'attachment; filename="{self.get_object()}.zip"'

            zf = zipfile.ZipFile(response,'w')

            publications = apps.get_model('thermoglobe','publication').objects
            # reference_list = publications.none()
            reference_list = set()
            for key, qs in self.get_object().get_data().items():
                # if key in data_select and qs.exists():
                if key in data_select and qs:
                    #get the download fields
                    csv_headers = self.get_csv_headers(key, download_type)

                    # make site fields are appropriate for query
                    formatted_fields = self.format_query_fields(key, download_type)

                    # create a csv file an save it to the zip object
                    zf.writestr(f'{key}.csv',self.csv_to_bytes(
                            data=qs.values_list(*formatted_fields), 
                            headers=csv_headers))
                    
                    # reference_list = reference_list | qs.exclude(reference__bibtex__isnull=True).values_list('reference__bibtex',flat=True).distinct()
                    reference_list.update(list(qs.exclude(reference__bibtex__isnull=True).values_list('reference__bibtex',flat=True).distinct()))
                    # reference_list = reference_list | publications.filter(
                        # **{f"{key}__in":qs.exclude(reference__bibtex__isnull=True)}).distinct().values_list('bibtex',flat=True)

            
            # add bibtex file to zip object
            if reference_list:
                zf.writestr(f'{self.get_object()}.bib', self.bibtex_to_bytes(reference_list))

            return response
        else:
            context = self.get_context_data(*args, **kwargs)
            context['download_form'] = options
            return render(request, template_name=self.template_name, context=context)

    def get_csv_headers(self, key, download_type):
        """This will be the header on the csv download"""
        return getattr(choices, key).get(download_type) + ['reference__bib_id']

    def format_query_fields(self, key, download_type):
        csv_headers = getattr(choices, key).get(download_type) + ['reference__bib_id']

        # all fields on the site model
        site_fields = [f.name for f in apps.get_model('thermoglobe','site')._meta.fields]

        # fix site fields
        formatted = [f'site__{f}' if f in site_fields else f for f in csv_headers]

        return formatted

    def bibtex_to_bytes(self, bibtex_list):
        bib_buffer = StringIO()

        for bib_entry in bibtex_list:
            bib_buffer.write(bib_entry)

        return bib_buffer.getvalue()

    def csv_to_bytes(self, data, headers):
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        # nasty way of cleaning output headers so that field relationships don't show
        output = []
        for h in headers:
            h = h.split('__')

            if len(h) == 3:
                output.append(h[1] if 'name' in h else h[2])
            elif len(h) == 2:
                output.append(h[0])
            else:
                output.append(h[0])

        # write the header row;
        writer.writerow(output)

        # write the rows to the csv file
        for i in data:
            writer.writerow(i)

        return csv_buffer.getvalue()