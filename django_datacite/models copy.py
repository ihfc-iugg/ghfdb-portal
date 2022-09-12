from django.utils.translation import gettext_lazy as _
from django.db import models
from solo.models import SingletonModel
from treebeard.mp_tree import MP_Node
from django.utils.translation import gettext as _
from datetime import datetime
from .utils import ISO_LANGUAGES

def current_year():
    return datetime.now().year

class Type(models.Model):

    resourceType
    resourceTypeGeneral

class Identifier(models.Model):

    identifier
    identifierType



class Creator(models.Model):
    "name": {"type": "string"},
    "nameType": {"$ref": "#/definitions/nameType"},
    "givenName": {"type": "string"},
    "familyName": {"type": "string"},
    "nameIdentifiers": {"$ref": "#/definitions/nameIdentifiers"},
    "affiliation": {"$ref": "#/definitions/affiliations"},
    "lang": {"type": "string"}


class Title(models.Model):
    "title": {"type": "string"},
    "titleType": {"$ref": "#/definitions/titleType"},
    "lang": {"type": "string"}

class Subject(models.Model):
    "subject": {"type": "string"},
    "subjectScheme": {"type": "string"},
    "schemeUri": {"type": "string", "format": "uri"},
    "valueUri": {"type": "string", "format": "uri"},
    "lang": {"type": "string"}

class Contributor(models.Model):
    "contributorType": {"$ref": "#/definitions/contributorType"},
    "name": {"type": "string"},
    "nameType": {"$ref": "#/definitions/nameType"},
    "givenName": {"type": "string"},
    "familyName": {"type": "string"},
    "nameIdentifiers": {"$ref": "#/definitions/nameIdentifiers"},
    "affiliation": {"$ref": "#/definitions/affiliations"},
    "lang": {"type": "string"}

class Date(models.Model):
    "date": {"$ref": "#/definitions/date"},
    "dateType": {"$ref": "#/definitions/dateType"},
    "dateInformation": {"type": "string"}

class AlternateIdentifier(models.Model):
    "alternateIdentifier": {"type": "string"},
    "alternateIdentifierType": {"type": "string"}

class RelatedIdentifier(models.Model):

    "relatedIdentifier": {"type": "string"},
    "relatedIdentifierType": {"$ref": "#/definitions/relatedIdentifierType"},
    "relationType": {"$ref": "#/definitions/relationType"},
    "relatedMetadataScheme": {"type": "string"},
    "schemeUri": {"type": "string", "format": "uri"},
    "schemeType": {"type": "string"},
    "resourceTypeGeneral": {"$ref": "#/definitions/resourceTypeGeneral"}



class Right(models.Model):
    "rights": {"type": "string"},
    "rightsUri": {"type": "string", "format": "uri"},
    "rightsIdentifier": {"type": "string"},
    "rightsIdentifierScheme": {"type": "string"},
    "schemeUri": {"type": "string", "format": "uri"},
    "lang": {"type": "string"}

class Description(models.Model):
    "description": {"type": "string"},
    "descriptionType": {"$ref": "#/definitions/descriptionType"},
    "lang": {"type": "string"}

class FundingReference(models.Model):
    "funderName": {"type": "string"},
    "funderIdentifier": {"type": "string"},
    "funderIdentifierType": {"$ref": "#/definitions/funderIdentifierType"},
    "awardNumber": {"type": "string"},
    "awardUri": {"type": "string", "format": "uri"},
    "awardTitle": {"type": "string"}

class Container(models.Model):
    "type": {"type": "string"},
    "title": {"type": "string"},
    "firstPage": {"type": "string"}


class GeoLocation(models.Model):

class Container(models.Model):

class Container(models.Model):



class Submission(models.Model):


    
    publisher = models.CharField(_('Publisher'), 
        max_length=256, 
        # default=DataCiteOptions.objects.first().publisher
        )
    publicationYear = models.PositiveSmallIntegerField(_('Publication Year'), 
            help_text=_('The year when the data was or will be made publicly available. In the case of resources such as software or dynamic data where there may be multiple releases in one year, include the Date/dateType/ dateInformation property and sub-properties to provide more information  about the publication or release date details.'),
            default=current_year)
    language = models.CharField(choices=ISO_LANGUAGES, max_length=256, help_text=_('Primary language of the resource'))
    version = models.CharField(max_length=4, default="1.0")
    schemaVersion = models.CharField(max_length=4)
    resourceTypeGeneral = models.CharField(max_length=256)
    resourceType = models.CharField(_('Title'), max_length=256,)

    rightsList = models.ManyToManyField(Right, verbose_name=_('Rights/Licensing'))