from django.contrib import admin
from .models import Province, Basin, Formation, Domain, TectonicEnvironment, Lithology
# Register your models here.

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    pass

@admin.register(Basin)
class BasinAdmin(admin.ModelAdmin):
    pass

@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    pass

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    pass

@admin.register(TectonicEnvironment)
class TectonicEnvironmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Lithology)
class LithologyAdmin(admin.ModelAdmin):
    search_fields = ('lithology',)
