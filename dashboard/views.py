from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages #import messages
from allauth.account.models import EmailAddress
from allauth.account.forms import AddEmailForm
from allauth.socialaccount.forms import DisconnectForm, SignupForm
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from publications.forms import DOIForm

# Create your views here.
# for handling temporary file uploads before confirmation
class Dashboard(LoginRequiredMixin,TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publication_form'] = DOIForm()
        return context
   
dashboard = Dashboard.as_view()

# @login_required
# def dashboard(request):
#     # messages.success(request,"You've succsfully done something!")
#     return render(request, 'dashboard/dashboard.html')




@login_required
def user_settings(request):
    context = dict(
        can_add_email = EmailAddress.objects.can_add_email(request.user),
        email_form = AddEmailForm(request),
        disconnect_form = DisconnectForm(request=request),
    )

    return render(request, 'dashboard/settings.html',context=context)