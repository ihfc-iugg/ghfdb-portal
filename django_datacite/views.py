from django.shortcuts import render
from .forms import DataCiteForm
from django_datacite.forms import General, DescriptionFormSet
from django.shortcuts import render
from crispy_forms.utils import render_crispy_form
from django.template.context_processors import csrf
from . import forms
from django.http import Http404, HttpResponse
from django.urls import reverse
from formtools.wizard.views import SessionWizardView
from . import forms

def htmx_crispy_or_404(request, form):
    if request.htmx: 
        return HttpResponse(render_crispy_form(form, context=csrf(request)))
    else:
        raise Http404("The requested page does not exist")

def htmx_form_or_404(request, form, context={}):
    if request.htmx: 
        if getattr(form, 'extra', None):
            # this is a formset
            return render(request, "gfz_dataservices/formset.html", {'formset': form})
        else:
            return render(request, "gfz_dataservices/form.html", {'form': form})
    else:
        raise Http404("The requested page does not exist")

FORMS = [("general", forms.General),
         ("subjects", forms.Subject),
         ("descriptions", forms.DescriptionFormSet),
         ("funding", forms.FundingReferenceFormSet),
         ("contributors", forms.ContributorFormSet),
         ("organisations", forms.OrganisationFormSet),
         ]

class SubmitMetaDataWizard(SessionWizardView):
    form_list = FORMS
    template_name = 'gfz_dataservices/metadata_submit.html'

    def get_template_names(self):
        templates = {name: f'submit/{name}.html' for name in self.get_form_list()}
        if self.request.htmx:
            return [templates[self.steps.current]]
        else:
            return [self.template_name]

    def done(self, form_list, **kwargs):
        return render(self.request, 'done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        context['form_list'] = self.get_form_list()
        return context

class Tab():

    def __init__(self, name, url_name, css=None):
        self.name = name
        self.css = css
        self.url_name = url_name
    
    def get_view(self):
        return reverse(self.url_name)

# Create your views here.
def submit_metadata(request):
    """Submit metadata to the gfz dataservices portal"""
    tabs = [
        Tab('General', 'general', 'icon solid fa-info'),
        Tab('Subjects', 'subjects', 'icon solid fa-book'),
        Tab('Descriptions', 'descriptions', 'icon solid fa-pencil-alt'),
        Tab('Funding', 'funding', 'icon solid fa-money-check-alt'),
        Tab('Contributors', 'contributors', 'icon solid fa-users'),
        Tab('Organisations', 'organisations', 'icon solid fa-university'),
        # Tab('Keywords', 'funding', 'icon solid fa-users'),
    ]
    return render(request, "gfz_dataservices/metadata_submit.html", {'tabs':tabs})


def render_form(request, form):
    return htmx_form_or_404(request, form)


def form_to_xml(form):
    """Converts cleaned form data into an xml string"""
    xml = None
    return xml

# Create your views here.
def submit_metadata(request):
    """Submit metadata to the gfz dataservices portal"""

    form = DataCiteForm(request.GET)
    if form.is_valid():

        # 1. convert to xml string
        xml = form.to_xml()

        # 2. validate xml string


        # 3. create file from xml string
        """This is necessary because GFZ Dataservices portal expect a file to be submitted, not form data"""

        # 4. send xml file to GFZ


        # 5. check response code


        # 6. add user message
    else:
        formset = DescriptionFormSet()


    return render(request, "django_datacite/metadata_submit.html",{'form':form, 'formset':formset})



def form_to_xml(form):
    """Converts cleaned form data into an xml string"""
    xml = None
    return xml