from thermoglobe import models
from reference import models as refmodels
from django.contrib import admin
from geomodels import models as geomodels

class Reference(admin.StackedInline):
    model = refmodels.Reference
    # readonly_fields = ['bib_id','entry_type','year',('first_author','co_authors'),'title','journal','doi','bibtex']

    fields = ['bib_id','entry_type','year',('first_author','co_authors'),'title','journal','doi','bibtex']

    classes = ['collapse']

class HeatFlow(admin.TabularInline):
    model = models.HeatFlow
    fields = ['corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty','reliability']
    extra=0

class Gradient(admin.TabularInline):
    model = models.ThermalGradient
    fields = ['corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty']

class Conductivity(admin.TabularInline):
    model = models.Conductivity
    fields = ['value','uncertainty','method','number_of_measurements',]

class HeatGeneration(admin.TabularInline):
    model = models.HeatGeneration
    fields = ['value','uncertainty','method','number_of_measurements',]

class Corrections(admin.StackedInline):
    model = models.Correction
    fields = [
        ('has_climatic','climatic'),
        ('has_topographic','topographic'),
        ('has_sedimentation','sedimentation'),
        ('has_bottom_water_variation','bottom_water_variation'),
        ('has_refraction','refraction'),
        ('has_fluid','fluid'),
        ('has_compaction','compaction'),
        ('has_other','other'),       
        ]
    classes = ['collapse']

class SedimentThickness(admin.TabularInline):
    model = geomodels.SedimentThickness
    extra=0