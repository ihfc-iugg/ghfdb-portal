from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(
        label='Select a .bib file',
        required=True)
