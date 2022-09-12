# -*- coding: UTF-8 -*-
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext as _
from django.contrib import admin

class ChoiceAdmin(admin.ModelAdmin):
    list_display= ['code','name','description']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['code',]
        else:
            return []




class ChoiceAbstract(models.Model):

	code = models.CharField(_('code'), max_length=128, unique=True)
	name = models.CharField(_('name'), max_length=128)
	description = CKEditor5Field(_('description'), 
    blank=True, null=True)

	class Meta:
		abstract = True


class ExplorationMethod(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Exploration Method')
admin.site.register(ExplorationMethod, ChoiceAdmin)

class HeatFlowMethod(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Heat Flow Method')
admin.site.register(HeatFlowMethod, ChoiceAdmin)

class SaturationMethod(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('TC Saturation Method')
admin.site.register(SaturationMethod, ChoiceAdmin)

class TemperatureMethod(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Temperature Method')
admin.site.register(TemperatureMethod, ChoiceAdmin)

class TemperatureCorrectionMethod(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Temperature Correction Method')
admin.site.register(TemperatureCorrectionMethod, ChoiceAdmin)

class ConductivitySource(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Conductivity Source')
admin.site.register(ConductivitySource, ChoiceAdmin)

class CorrectionType(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Correction Type')
admin.site.register(CorrectionType, ChoiceAdmin)

class ExplorationType(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Exploration Purpose')
admin.site.register(ExplorationType, ChoiceAdmin)

class EnvironmentType(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Geographic Environment')
admin.site.register(EnvironmentType, ChoiceAdmin)

class HeatTransferType(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Heat Transfer Type')
admin.site.register(HeatTransferType, ChoiceAdmin)

class MeasurementCondition(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Conductivity PT Condition')
admin.site.register(MeasurementCondition, ChoiceAdmin)

class ProbeType(ChoiceAbstract):
	class Meta:
		verbose_name = verbose_name_plural =  _('Probe Type')
admin.site.register(ProbeType, ChoiceAdmin)
