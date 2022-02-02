from __future__ import absolute_import
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib import auth
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Div, Row, Column, Field
from django import forms
from allauth.account.forms import SignupForm, LoginForm
from allauth.socialaccount.forms import SignupForm as SocialSignUp

class CustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = True
        self.helper.layout = Layout(
            Field('login', label='email', css_class='form-group'),
            Field('password', css_class='form-group'),
            Field('remember', css_class='form-group'),
            ButtonHolder(
                Submit('submit', 'login', css_class='form-group')
            )
        )

class SignUpForm(SignupForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = auth.get_user_model()
        fields = ('email','first_name','last_name','password1','password2',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = 'signupForm'
        # self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column(Field('first_name'), css_class='form-group col-md-6'),
                Column(Field('last_name'), css_class='form-group col-md-6'),
            ),
            # 'username',
            Field('email', css_class='form-group'),
            Field('password1', css_class='form-group'),
            Field('password2', css_class='form-group'),
            # ButtonHolder(
            #     Submit('submit', 'Create', css_class='button mt-2')
            # )
        )

class SocialSignupForm(SocialSignUp):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

class UserAdminCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = auth.get_user_model()
        fields = ('email','password',)

class UserAdminChangeForm(UserChangeForm):

    class Meta:
        model = auth.get_user_model()
        fields = ('email','password',)
    

