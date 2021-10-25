from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from .models import Upload


class UploadForm(forms.ModelForm):

    bibtex = forms.CharField(required=False, widget=forms.Textarea)
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    class Meta:
        model = Upload
        exclude = ['imported','imported_by','date_imported','date_uploaded','description']

    def __init__(self, *args, **kwargs):
        from django.forms.widgets import HiddenInput
        hidden = kwargs.pop('hidden',None)
        super().__init__(*args, **kwargs)
        if hidden:
            for key, field in self.fields.items():
                field.widget = HiddenInput()
            # self.fields['fieldname'].widget
            # self.fields['fieldname'].widget = HiddenInput()

class ConfirmUploadForm(forms.ModelForm):

    bibtex = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Upload
        exclude = ['imported','imported_by','date_imported','date_uploaded','description']