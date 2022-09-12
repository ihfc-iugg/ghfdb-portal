from django.contrib import admin
from database.models import Site, Interval, Correction
from main.mixins import BaseAdmin
from import_export.admin import ImportExportActionModelAdmin
from database.resources import IntervalResource, SiteResource
from django.db.models import F
from main.filters import IsCorrectedFilter, EmptySites
from django.http import HttpResponse
from django.utils.translation import gettext as _
import csv
from .admin_forms import AdminIntervalForm, AdminSiteForm


# class CorrectionInline(admin.TabularInline):
#     model = Correction.objects.through
#     extra = 0

@admin.register(Site)
class SiteAdmin(BaseAdmin, ImportExportActionModelAdmin):
    # change_list_template = 'smuggler/change_list.html'
    form = AdminSiteForm
    resource_class = SiteResource

    list_display = ['id','name', 'lat', 'lng','elevation','q','q_unc','q_acq','env','wat_temp','method','expl','_reference']
    readonly_fields = ['id']
    actions = ['export_sites',"merge",]
    list_filter = ['env','method','expl']
    date_hierarchy = 'q_acq'

    # filter_horizontal = ['references']
    raw_id_fields = ('references',)

    autocomplete_lookup_fields = {
        'm2m': ['references'],
    }

    fieldsets = [
        ("Site Information", 
            {'fields': [
                'id',
                'geom',
                'name',
                ('lat','lng'),
                'elevation',
                ('q','q_unc'),
                ('year','month'),
                # 'q_acq',
                'env',
                'wat_temp',
                ('method', 'expl'),
                'q_comment',
                ]}), 
        ('Publication',
            {'fields': [ 
                'references',]}),                
                ]

    search_fields = ['id','name','lat','lng','references__label','references__id']
    point_zoom = 8
    map_width = 900
    modifiable=False


    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('references')
        return queryset

    def _reference(self,obj):
        return ','.join([r.label for r in obj.references.all() if r.label])

    def recalculate_geo_fields(self, request, qs):
        geos = ['countries','continents','seas','political','province']

    def export_sites(self, request, qs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sites.csv"'

        writer = csv.writer(response)
        vals = ['id', 'lat','lng']
        writer.writerow(vals)
        data = qs.values_list(*vals)
        for row in data:
            writer.writerow(row)

        return response

@admin.register(Interval)
class HeatFlowAdmin(BaseAdmin, ImportExportActionModelAdmin):
    form = AdminIntervalForm
    resource_class = IntervalResource
    autocomplete_fields = ['site']
    search_fields = ['site__name']
    list_display = ['name','childcomp','q_top','q_bot','qc','qc_unc','q_method', 'T_grad_mean_meas','T_method_top','T_corr_top','T_method_bot','T_corr_bot', 'tc_mean', 'tc_satur','tc_pTcond','tc_strategy','reference']
    list_filter = ['q_tf_mech','q_method','hf_probe','T_method_top','T_method_bot','T_corr_top','T_corr_bot','tc_source','tc_strategy','corrections']

    # list_editable = ['childcomp',]
    # inlines = [CorrectionInline,]
    raw_id_fields = ('corrections','reference','ics_strat',)
    autocomplete_lookup_fields = {
        'fk': ['reference','ics_strat',],
        'm2m': ['corrections',],
    }

    fieldsets = [ 
        (_('Metadata'),
            {'fields': [
                'site',
                'reference',
                'childcomp',
                ('year','month'),
                # 'q_acq',
                'geo_lith',
                'bgs_lith',
                'geo_strat',
                'ics_strat',
            ],
            'classes': ('grp-collapse grp-open',),
            }
        ),
        (_('Heat Flow'),
            {'fields': [
                'q_tf_mech',
                ('qc','qc_unc'),
                'q_method',
                'q_top',
                'q_bot',
                'corrections',
                ],
            'classes': ('grp-collapse grp-open',),
            }
        ),
        (_('Probe Sensing'),
            {'fields': [
                ('hf_pen','T_tilt',),
                'hf_probe',
                'hf_probeL',
                
            ],
            'classes': ('grp-collapse grp-open',),
            }
        ),
        (_('Temperature'),
            {'fields': [
                ('T_grad_mean_meas','T_grad_unc_meas'),
                ('T_grad_mean_cor','T_grad_unc_cor'),
                ('T_method_top','T_corr_top','T_shutin_top'),
                ('T_method_bot','T_corr_bot','T_shutin_bot'),
                'T_numb',
                ],
            'classes': ('grp-collapse grp-open',),
            }
        ),
        (_('Thermal Conductivity'),
            {'fields': [
                ('tc_mean', 'tc_unc'),
                'tc_source',
                'tc_meth',
                'tc_satur',
                'tc_pTcond',
                'tc_pTfunc',
                'tc_strategy',
                'tc_numb',
                ],
            'classes': ('grp-collapse grp-open',),
            }
        ),              
    ]

    actions = ["mark_verified"] + ImportExportActionModelAdmin.actions

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['bgs_lith'].widget.can_add_related = False
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return (super().get_queryset(request)
                .prefetch_related('reference')
                .select_related('site')
                .annotate(
                    _name=F('site__name'),
                    _lat=F('site__lat'),
                    _lng=F('site__lng'),
                    ))

    def heat_flow(self, obj):
        return obj.heat_flow

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)


@admin.register(Correction)
class CorrectionAdmin(admin.ModelAdmin):
    list_display = ['id','type']
    fields = [('id','type')]



