from django.contrib import admin
from database.models import HeatFlow, Interval
from import_export.admin import ImportExportActionModelAdmin
from database.resources import IntervalResource, SiteResource
from django.db.models import F
from django.utils.translation import gettext as _
# from .admin_forms import AdminIntervalForm
from geoluminate.gis.admin import SiteAdminMixin


class CorrectionInline(admin.TabularInline):
    model = Interval.corrections.through
    extra = 0


@admin.register(HeatFlow)
class SiteAdmin(SiteAdminMixin, ImportExportActionModelAdmin):
    # form = AdminSiteForm
    resource_class = SiteResource

    list_display = [
        'id',
        'name',
        'lon',
        'lat',
        'elevation',
        'q',
        'q_unc',
        'q_acq',
        'env',
        'wat_temp',
        'method',
        'expl',
        '_reference']
    readonly_fields = ['id']
    actions = ["merge", ]
    list_filter = ['env', 'method', 'expl']
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
                'name',
                'geom',
                'elevation',
                ('q', 'q_unc'),
                # ('year', 'month'),
                # 'q_acq',
                'env',
                'wat_temp',
                ('method', 'expl'),
                'q_comment',
            ]}),
        ('Publication',
            {'fields': [
                'references', ]}),
    ]

    search_fields = [
        'id',
        'name',
        'references__label', ]
    point_zoom = 8
    map_width = 900
    modifiable = True

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('references')

    def _reference(self, obj):
        return ','.join([r.label for r in obj.references.all() if r.label])

    def coords(self, obj):
        return obj.geom.coords


@admin.register(Interval)
class HeatFlowAdmin(SiteAdminMixin, ImportExportActionModelAdmin):
    # form = AdminIntervalForm
    geom_field = 'site__geom'
    resource_class = IntervalResource
    autocomplete_fields = ['site']
    search_fields = ['site__name']
    list_display = [
        'site',
        'lon',
        'lat',
        'childcomp',
        'q_top',
        'q_bot',
        'qc',
        'qc_unc',
        'q_method',
        'T_grad_mean_meas',
        'T_method_top',
        'T_corr_top',
        'T_method_bot',
        'T_corr_bot',
        'tc_mean',
        'tc_satur',
        'tc_pTcond',
        'tc_strategy',
        'reference']
    # list_filter = [
    #     'q_tf_mech',
    #     'q_method',
    #     'hf_probe',
    #     'T_method_top',
    #     'T_method_bot',
    #     'T_corr_top',
    #     'T_corr_bot',
    #     'tc_source',
    #     'tc_strategy']

    # list_editable = ['childcomp',]
    inlines = [CorrectionInline, ]
    raw_id_fields = ('reference', 'geo_strat',)
    autocomplete_lookup_fields = {
        'fk': ['reference', 'geo_strat', ],
        'm2m': [],
    }

    fieldsets = [
        (_('Metadata'),
            {'fields': [
                'site',
                'reference',
                'childcomp',
                ('year', 'month'),
                # 'q_acq',
                'geo_lith',
                'geo_strat',
            ],
            'classes': ('grp-collapse grp-open',),
        }
        ),
        (_('Heat Flow'),
            {'fields': [
                'q_tf_mech',
                ('qc', 'qc_unc'),
                'q_method',
                'q_top',
                'q_bot',
                # 'corrections',
            ],
            'classes': ('grp-collapse grp-open',),
        }
        ),
        (_('Probe Sensing'),
            {'fields': [
                ('hf_pen', 'T_tilt',),
                'hf_probe',
                'hf_probeL',

            ],
            'classes': ('grp-collapse grp-open',),
        }
        ),
        (_('Temperature'),
            {'fields': [
                ('T_grad_mean_meas', 'T_grad_unc_meas'),
                ('T_grad_mean_cor', 'T_grad_unc_cor'),
                ('T_method_top', 'T_corr_top', 'T_shutin_top'),
                ('T_method_bot', 'T_corr_bot', 'T_shutin_bot'),
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

    def get_queryset(self, request):
        return (super().get_queryset(request)
                .prefetch_related('reference')
                .select_related('site')
                .annotate(name=F('site__name'))
                )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['geo_lith'].widget.can_add_related = False
        return form
