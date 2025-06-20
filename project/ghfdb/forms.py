from django.utils.translation import gettext_lazy as _
from fairdm.contrib.import_export.forms import ImportForm


class GHFDBImportForm(ImportForm):
    class Meta:
        fields = ["file"]
        help_text = _(
            "Select a file to import. Your file must conform to the latest version of the GHFDB structure. The following formats are supported: XLSX."
        )
