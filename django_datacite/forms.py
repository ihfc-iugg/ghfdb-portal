from ensurepip import version
from django import forms
from django.conf import settings
from .models import Schema, License, Keyword
from django_ckeditor_5.widgets import CKEditor5Widget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Hidden
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.layout import Field, HTML
from django.utils.translation import gettext as _
from datetime import datetime
from treewidget.fields import TreeModelMultipleChoiceField
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import ISO_LANGUAGES, camel_case_split

class DataCiteForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = Schema.objects.filter(default=True).first().schema
        
        self.defaults = getattr(settings, 'DATACITE_DEFAULTS', {}) 
        
        choices = self.schema_enums()

        for name, field in self.fields.items():

            if choices.get(name):
                field.choices = choices.get(name)
            
            if name in self.defaults.keys():
                field.widget = forms.HiddenInput()
                field.initial = self.defaults[name]

        schema_version = self.schema['properties'].get('schemaVersion')
        if schema_version:
            self.set_schema_initial(schema_version['const'])

        self.helper = FormHelper(self)
        self.helper.form_show_labels = True
        # self.helper.form_method = 'POST'
        self.helper.form_tag = False
        # self.helper.render_required_fields = True

    def schema_enums(self):
        def tuplize(x):
            return (x, camel_case_split(x))

        enums = {}
        for k, v in self.schema['definitions'].items():
            if v.get('enum'):
                if k in self.defaults.keys():
                    # if this value is specified in the DATACITE_DEFAULTS dict, then
                    # disregard the other available choices.
                    enums[k] = [tuplize(self.defaults[k])]
                else:
                    enums[k] = [tuplize(choice) for choice in v['enum']]
        return enums

    def set_schema_initial(self, version):
        if self.fields.get('schemaVersion'):
            self.fields['schemaVersion'].initial = version
            self.fields['schemaVersion'].widget = forms.HiddenInput()


class General(DataCiteForm):
    publisher = forms.CharField()
    publicationYear = forms.IntegerField(
            label='Publication Year', 
            help_text='Year of publication',
            initial=datetime.now().year)
    language = forms.ChoiceField(choices=ISO_LANGUAGES, help_text=_('Primary language of the resource'))
    version = forms.FloatField(initial=1.0, widget=forms.NumberInput(attrs={'step': "0.1"}))
    schemaVersion = forms.CharField()
    resourceTypeGeneral = forms.ChoiceField()
    resourceType = forms.CharField(label='Title')
    rightsList = forms.ModelChoiceField(label='License', queryset=License.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column(FloatingField('version'), css_class='col-md-3'),
                Column(FloatingField('rightsList'), css_class='col-md-9'),
            ),
            FloatingField('resourceType'),
            FloatingField('publicationYear'),
            FloatingField('language'),
            FloatingField('resourceTypeGeneral'),       
            # Submit('wizard_goto_step', '{{ wizard.steps.next }}'),           
        )


class Subject(DataCiteForm):
    subjects = TreeModelMultipleChoiceField(label='', queryset=Keyword.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            FloatingField('subjects'),
        )


class Description(DataCiteForm):
    descriptionType = forms.ChoiceField(label='Type')
    description = forms.CharField()

    class Meta:
          widgets = {
              "description": CKEditor5Widget(attrs={"class": "django_ckeditor_5"})
          }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(
                Column(FloatingField('descriptionType'), css_class='col-md-3'),
                Column(FloatingField('description'), css_class='col-md-9'),
            ),
        )

DescriptionFormSet = forms.formset_factory(Description)


class FundingReference(DataCiteForm):
    funderName = forms.CharField(label=_('Name'))
    funderIdentifierType = forms.ChoiceField(label=_('Type'))
    funderIdentifier = forms.CharField(label=_('ID'))

    awardNumber = forms.CharField(label=_('Number'))
    awardTitle = forms.CharField(label=_('Title'))
    awardUri = forms.URLField(label=_('URI'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            HTML("<h4 class='card-title'>Funder</h4>"),
            Row(
                Column(FloatingField('funderIdentifier'), css_class='col-md-2 g-2'),
                Column(FloatingField('funderIdentifierType'), css_class='col-md-4 g-2'),
                Column(FloatingField('funderName'), css_class='col-md-6 g-2'),
            ),
            HTML("<h4 class='card-title'>Award</h4>"),
            Row(
                Column(FloatingField('awardNumber'), css_class='col-md-2 g-2'),
                Column(FloatingField('awardTitle'), css_class='col-md-5 g-2'),
                Column(FloatingField('awardUri'), css_class='col-md-5 g-2'),
            ),
        )

FundingReferenceFormSet = forms.formset_factory(FundingReference, extra=1)

class Contributor(DataCiteForm):
    name = forms.CharField()
    nameType = forms.ChoiceField(initial='Personal')
    givenName = forms.CharField(label='Given Name')
    familyName = forms.CharField(label='Family Name')
    nameIdentifiers = forms.ChoiceField(widget=forms.HiddenInput())
    affiliation = forms.CharField()
    lang = forms.CharField(initial='en', widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = 'contributor'
        self.helper.layout = Layout(
            Row(
                Column(FloatingField('givenName'), css_class='col-md-6'),
                Column(FloatingField('familyName'), css_class='col-md-6'),
            ),
            FloatingField('affiliation')
        )

ContributorFormSet = forms.formset_factory(Contributor, min_num=1, validate_min=True)

class Organisation(Contributor):
    nameType = forms.ChoiceField(initial='Organisational', widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = 'contributor'
        self.helper.layout = Layout(
            FloatingField('name'),
            FloatingField('affiliation'),
        )

OrganisationFormSet = forms.formset_factory(Organisation, min_num=1, validate_min=True)


