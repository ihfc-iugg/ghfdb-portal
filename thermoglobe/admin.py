from django.contrib import admin
from .models import Site, Interval, Conductivity, HeatGeneration, Temperature, Correction, Author, Publication, Upload
from .mixins import BaseAdmin
from import_export.admin import ImportExportActionModelAdmin, ImportForm
from .mixins import SitePropertyAdminMixin
from .resources import ConductivityResource, HeatGenResource, HeatFlowResource, TempResource
from .models import Interval, Conductivity, HeatGeneration
from django.db.models import F, Count, Exists
from .filters import IsCorrectedFilter, VerifiedFilter,PubStatusFilter, LastNameLengthFilter,DuplicateFilter, IntervalType
from . import inlines
from publications.mixins import AuthorAdmin, PublicationAdmin
from django.utils.html import mark_safe
from django.utils import timezone

@admin.register(Site)
class SiteAdmin(BaseAdmin, ImportExportActionModelAdmin):
    resource_class = HeatFlowResource
    list_display = ['site_name', 'latitude', 'longitude','elevation','country','continent','basin', 'heat_flow_count','conductivity_count','heat_gen_count','temperature_count', '_reference', ]

    readonly_fields = ['id','slug',"seamount_distance", "outcrop_distance", 'sediment_thickness','crustal_thickness']

    filter_horizontal = ['reference']
    fieldsets = [
        ("Site Information", 
            {'fields': [
                ('id','slug'),
                'geom',
                'site_name',
                ('latitude','longitude','elevation'),
                ('cruise'),
                'country',
                'sea',]}),
        ('Calculated Fields',
            {'fields': [ 
                'seamount_distance',
                'outcrop_distance',
                'sediment_thickness',
                'crustal_thickness']}),
        ('Reported Fields',
            {'fields': [
                ('surface_temp','bottom_water_temp'),
                ('well_depth',),
                ]}),        
        # ('Geology',
        #     {'fields': [ 
        #         'lithology']}),
        ('Publication',
            {'fields': [ 
                'reference',]}),                
                ]

    # inlines = [HeatFlowInline, TemperatureInline, HeatGenerationInline, ]
    search_fields = ['site_name','latitude','longitude','reference__bib_id']
    # default_zoom = 3
    point_zoom = 3
    map_width = 900
    modifiable=False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('reference').annotate(
            _heat_flow_count=Count('intervals',distinct=True),
            _conductivity_count=Count('conductivity',distinct=True),
            _heat_gen_count=Count('heat_generation',distinct=True),
            _temperature_count=Count('temperature',distinct=True),
            )

    def _reference(self,obj):
        return obj.reference.first()


@admin.register(Interval)
class HeatFlowAdmin(BaseAdmin,ImportExportActionModelAdmin):
    resource_class = HeatFlowResource
    autocomplete_fields = ['site']
    search_fields = ['site__site_name','site__latitude','site__longitude','reference__bib_id']
    list_display = ['site_name','reference','depth_min','depth_max','reliability','heat_flow_corrected','heat_flow_uncorrected','gradient_corrected','gradient_uncorrected','average_conductivity','heat_generation']
    inlines = [inlines.Corrections]

    list_filter = ['reliability',IsCorrectedFilter, IntervalType]
    fieldsets = [
        ('Site',{'fields':['site']}),
        ('Interval', 
            {'fields': [
                'reference',
                ('depth_min', 'depth_max'),
                ('number_of_temperatures','temp_method'),
                ('global_flag','global_reason','global_by'),
                'comment',
                ]
            }
        ),
        ('Heat Flow',
            {'fields': [
                'reliability',
                ('heat_flow_corrected','heat_flow_corrected_uncertainty'),
                ('heat_flow_uncorrected','heat_flow_uncorrected_uncertainty'),
                ]
            }
        ),
        ('Temperature Gradient',
            {'fields': [
                ('gradient_corrected','gradient_corrected_uncertainty'),
                ('gradient_uncorrected','gradient_uncorrected_uncertainty'),
                ]
            }
        ),
        ('Thermal Conductivity',
            {'fields': [
                ('average_conductivity', 'conductivity_uncertainty','number_of_conductivities'),
                'conductivity_method',
                ],
            # 'classes': ('collapse',),
            }
        ),
        ('Heat Generation',
            {'fields': [
                ('heat_generation', 'heat_generation_uncertainty','number_of_heat_gen'),
                'heat_generation_method',
                ],
            # 'classes': ('collapse',),
            }
        ),                
    ]
    actions = ["mark_verified"] + ImportExportActionModelAdmin.actions


    def save_model(self, request, obj, form, change):
        if change:
            if form.instance.global_flag != form.initial['global_flag']:
                if form.instance.global_flag == True:
                    form.instance.global_by = request.user._wrapped
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),
            )
        return queryset

    def mark_verified(self, request, queryset):
        queryset.update(is_immortal=True)

    def interval(self, obj):
        return '{}-{}'.format(obj.depth_min, obj.depth_max)

@admin.register(Conductivity)
class ConductivityAdmin(SitePropertyAdminMixin,ImportExportActionModelAdmin):
    resource_class = ConductivityResource
    list_display = ['edit','site_name','latitude','longitude','depth','conductivity','uncertainty','method','reference','age']

    fieldsets = [('Site', {'fields':[
                            'site']}),
                ('Sample', {'fields': [
                            'sample_name',
                            ('conductivity','uncertainty'),
                            'method',
                            'depth',
                            ]}),
                ('Age', {'fields': [
                            ('age','age_type',),
                            ]}),
                ('Geology', {'fields': [
                            ('rock_type','rock_group','rock_origin')]}),
                            ]

@admin.register(HeatGeneration)
class HeatGenAdmin(SitePropertyAdminMixin,ImportExportActionModelAdmin):
    resource_class = HeatGenResource
    list_display = ['edit','site_name','latitude','longitude','depth','heat_generation','uncertainty','method','reference','age']

    fieldsets = [('Site', {'fields':[
                            'site']}),
                ('Sample', {'fields': [
                            'sample_name',
                            ('heat_generation','uncertainty'),
                            'method',
                            'depth',
                            ]}),
                ('Age', {'fields': [
                            ('age','age_type',),
                            ]}),
                ('Geology', {'fields': [
                            ('rock_type','rock_group','rock_origin')]}),
                            ]

@admin.register(Temperature)
class TemperatureAdmin(BaseAdmin,ImportExportActionModelAdmin):
    resource_class=TempResource
    list_display = ['edit','site_name','latitude','longitude','depth','temperature','method','circ_time','lag_time','reference']
    list_filter = ['source','method']
    autocomplete_fields = ['site']
    search_fields = ['site__site_name','site__latitude','site__longitude','reference__bib_id']
    fieldsets = [('Site', {'fields':['site']}),
                ('Measurement', {'fields': [
                        'temperature',
                        'depth',
                        'method',
                        'lag_time',
                        'comment',
                            ]}),
                ('Publication',{'fields':['reference']})
                            ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),
            )

        return queryset

@admin.register(Author)
class AuthorAdmin(AuthorAdmin):
    # counts = ['first_authorships','co_authorships']
    list_display = ['name','_references']
    search_fields = ('last_name','first_name','middle_name','publications__bibtex')
    exclude = ['added_by','edited_by']
    inlines = [inlines.Publication, ]
    list_filter = [LastNameLengthFilter,]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('publications').annotate(
            _reference_count=Count("publications", distinct=True),
            )
        return queryset

    def co_authorships(self,obj):
        return obj._co_author_count
    co_authorships.admin_order_field = '_co_author_count'

    def first_authorships(self,obj):
        return obj._first_count
    first_authorships.admin_order_field = '_first_count'

    def name(self, obj):
        return obj.get_full_name()
    name.admin_order_field = 'last_name'

    def _references(self,obj):
        return obj._reference_count
    _references.admin_order_field = '_reference_count'

@admin.register(Publication)
class PublicationAdmin(BaseAdmin, PublicationAdmin):
    change_form_template = 'admin/upload_changeform.html'
    counts = ['sites']
    list_display = ['edit','article','type','year','_authors', 'title', 'journal','bib_id','is_verified','verified_by','date_verified']
    exclude = ['source',]
    search_fields = ('pk', 'year', 'bib_id', 'id', 'bibtex')
    fields = ['pk', 'slug', ('bib_id','is_verified'),'bibtex','authors']
    readonly_fields = ['pk','slug']
    list_filter = [VerifiedFilter,PubStatusFilter]
    # filter_horizontal = ['authors']
    # raw_id_fields = ('authors',)
    class Media:
            # css = {
            #     'all': ('css/admin.css',),
            # }
            js = ("https://kit.fontawesome.com/a08181010c.js",)

    def response_change(self, request, obj):
        if "_upload" in request.POST:
            # print('Doing something now')
            # self.import_data(request,obj)
            # obj.save()
            # self.message_user(request, "The uploaded file was succesfully imported.")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    # def import_data(self,request,obj):
    #     resource_switch = {
    #         '0':resources.HeatFlowResource(),
    #         '1':resources.HeatFlowResource(),
    #         '2':resources.TempResource(),
    #         '3':resources.ConductivityResource(obj.bibtex),
    #         '4':resources.HeatGenResource(),
    #         }
        
    #     resource = resource_switch[request.POST['data_type']]
    #     data_file = obj.data
    #     dataset = Dataset().load(data_file.read().decode('utf-8'))
    #     result = resource.import_data(dataset=dataset, dry_run=False)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _site_count=Count("sites",distinct=True),
            )
        return queryset

    def save_model(self, request, obj, form, change):
        if change:
            if form.instance.is_verified != form.initial['is_verified']:
                if form.instance.is_verified == True:
                    form.instance.verified_by = request.user._wrapped
                    form.instance.date_verified = timezone.now()
        else:
            form.instance.source = 'Admin Created'

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # self.authors.add(*self.authors_list)
        # form.instance.save()
        
        # self.authors.all().update()
        super().save_related(request, form, formsets, change)

        # if form.instance.co_authors_list:
        #     form.instance.co_authors.add(*form.instance.co_authors_list)
            # for author in form.instance.co_authors_list:
            #     form.instance.co_authors.add(author)

    def article(self,obj):
        if obj.doi:
            return mark_safe('<a href="https://doi.org/{}"><i class="fas fa-globe fa-lg"></i></a>'.format(obj.doi))
        else:
            return ''

    def edit(self,obj):
        return mark_safe('<i class="fas fa-edit"></i>')

    def _authors(self,obj):
        # print(obj.display_authors())
        return obj.display_authors()
        # return ','.join([str(i) for i in obj.authors.all()])





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

    change_form_template = "admin/upload_changeform.html"

    def _email(self,obj):
        return mark_safe('<a href="mailto:{}">{}</a>'.format(obj.email,obj.email))

    def save_model(self, request, obj, form, change):
        form.instance.imported = True
        form.instance.imported_by = request.user
        form.instance.date_imported = timezone.now()
        super().save_model(request, obj, form, change)

    def import_data(self,request,obj):
        resource_switch = {
            '0':resources.HeatFlowResource(),
            '1':resources.HeatFlowResource(),
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