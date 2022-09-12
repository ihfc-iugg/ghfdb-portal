from django.urls import path, include
from django_datacite import views

app_name = 'django_datacite'

urlpatterns = [
    path('',views.submit_metadata, name='submit_metadata'),
]

# urlpatterns = [
#     path('', SubmitMetaDataWizard.as_view(), name='submit_metadata'),
#     # path('', submit_metadata, name='submit_metadata'),
#     path('general', render_form, name='general', kwargs={"form":forms.General}),
#     path('subjects', render_form, name='subjects', kwargs={"form":forms.Subject}),
#     path('descriptions', render_form, name='descriptions', kwargs={"form":forms.DescriptionFormSet}),
#     path('funding', render_form, name='funding', kwargs={"form":forms.FundingReferenceFormSet}),
#     path('contributors', render_form, name='contributors', kwargs={"form":forms.ContributorFormSet}),
#     path('organisations', render_form, name='organisations', kwargs={"form":forms.OrganisationFormSet}),
# ]