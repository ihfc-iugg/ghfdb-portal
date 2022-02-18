from django import forms
import os
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field

class ImportForm(forms.Form):
    import_file = forms.FileField(
        label=_('File to import')
        )

class ConfirmImportForm(forms.Form):
    import_file_name = forms.CharField(widget=forms.HiddenInput())
    original_file_name = forms.CharField(widget=forms.HiddenInput())

    def clean_import_file_name(self):
        data = self.cleaned_data['import_file_name']
        data = os.path.basename(data)
        return data


class MapSettingsForm(forms.Form):
    decluster_level = forms.IntegerField()

    class Meta:
        fields = ['decluster_level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget_icon = 'filter'
        self.name = _('filter')
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_id = 'filterForm'
        self.helper.layout = Layout(
                Field('decluster_level'),
            )