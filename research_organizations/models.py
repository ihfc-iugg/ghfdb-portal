from django.db import models
from organizations.models import Organization
from django.db import models
from django.utils.translation import gettext as _

class OrganizationType(models.Model):
    type = models.CharField(max_length=255, primary_key=True)

class OrganizationIP(models.Model):
    address = models.GenericIPAddressField(primary_key=True)

class ResearchOrganization(Organization):
    ROR = models.URLField(_('ROR ID'))

    acronyms = models.JSONField(null=True, blank=True)
    addresses = models.JSONField(null=True, blank=True)
    aliases = models.JSONField(null=True, blank=True)
    country = models.JSONField(null=True, blank=True)

    email_address = models.EmailField(null=True, blank=True)
    established = models.IntegerField(null=True, blank=True)
    
    external_ids = models.JSONField(null=True, blank=True)
    ip_addresses = models.ManyToManyField(OrganizationIP, blank=True)    
    
    labels = models.JSONField(null=True, blank=True)
    links = models.JSONField(null=True, blank=True)


    status = models.CharField(max_length=64, blank=True, null=True)
    types = models.ManyToManyField(OrganizationType, blank=True)    

    parent = models.ForeignKey("self", on_delete=models.SET_NULL, related_name='sub_organizations', null=True, blank=True)

    class Meta:
        verbose_name = _('Research Organization')
        verbose_name_plural = _('Research Organizations')