from django import forms
from thermoglobe.widgets import RangeField, RangeWidget
from reference.models import Upload
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

                            
class ContactForm(forms.Form):
    name = forms.CharField(max_length=75)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField(widget=ReCaptchaV3)
