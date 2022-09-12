from django.contrib import admin
from .models import ResearchOrganization
from organizations.admin import BaseOrganizationAdmin

# Register your models here.
@admin.register(ResearchOrganization)
class RORAdmin(BaseOrganizationAdmin):
    pass