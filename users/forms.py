# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class UserAdminCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email','password','university')

class UserAdminChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        # fields = '__all__'
        fields = ('email','password','university')