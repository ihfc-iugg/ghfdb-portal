from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages #import messages
from allauth.account.models import EmailAddress
from allauth.account.forms import AddEmailForm
from allauth.socialaccount.forms import DisconnectForm, SignupForm

# Create your views here.
@login_required
def dashboard(request):
    messages.success(request,"You've succsfully done something!")
    return render(request, 'dashboard/dashboard.html')

@login_required
def user_settings(request):
    context = dict(
        can_add_email = EmailAddress.objects.can_add_email(request.user),
        email_form = AddEmailForm(request),
        disconnect_form = DisconnectForm(request=request),
    )

    return render(request, 'dashboard/settings.html',context=context)