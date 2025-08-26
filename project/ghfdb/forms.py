from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from fairdm.contrib.import_export.forms import ImportForm


class GHFDBImportForm(ImportForm):
    file = forms.FileField(
        help_text=_("Select a file to import."),
        validators=[FileExtensionValidator(allowed_extensions=["xlsx"])],
        widget=forms.ClearableFileInput(attrs={"accept": ".xlsx"}),
    )

    class Meta:
        fields = ["file"]
