from thermoglobe import models
from publications.models import Publication
from django.contrib import admin

class Publication(admin.StackedInline):
    model = Publication
    # readonly_fields = ['bib_id','type','year',('first_author','co_authors'),'title','journal','doi','bibtex']

    fields = ['bib_id','type','year',('first_author','co_authors'),'title','journal','doi','bibtex']

    # classes = ['collapse']

class HeatFlow(admin.TabularInline):
    model = models.HeatFlow
    fields = ['corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty','reliability']
    extra=0

# class Gradient(admin.TabularInline):
#     model = models.ThermalGradient
#     fields = ['corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty']

class Conductivity(admin.TabularInline):
    model = models.Conductivity
    fields = ['value','uncertainty','method','number_of_measurements',]

class HeatGeneration(admin.TabularInline):
    model = models.HeatGeneration
    fields = ['value','uncertainty','method','number_of_measurements',]

class Corrections(admin.StackedInline):
    model = models.Correction
    fields = [
        ('climate_flag','climate'),
        ('topographic_flag','topographic'),
        ('sed_erosion_flag','sed_erosion'),
        ('bottom_water_variation_flag','bottom_water_variation'),
        ('refraction_flag','refraction'),
        ('fluid_flag','fluid'),
        ('compaction_flag','compaction'),
        ('other_flag','other_type','other'),       
        ]
    # radio_fields = {'climate_flag': admin.HORIZONTAL}
    # classes = ['collapse']

