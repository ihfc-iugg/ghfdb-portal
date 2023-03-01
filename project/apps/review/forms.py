from user.models import User
from django import forms
from user.forms import SocialSignupForm


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = "__all__"


class RegisterAsReviewerForm(SocialSignupForm):
    # institution = forms.ModelChoiceField()
    # ORCID =

    class Meta:
        model = User
        fields = ['institution', '']
