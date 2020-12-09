# users/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserAdminChangeForm, UserAdminCreationForm
from django.contrib.admin.models import LogEntry
from .models import CustomUser

@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ['username','last_name','first_name','is_superuser','is_staff','is_active','last_login','date_joined']
    list_filter = ('is_staff','is_superuser',)
    
    # fieldsets for modifying user
    fieldsets = (
        ('Contact info',{'fields': (('first_name','last_name',),'password','email',)}),
        ('Permissions',     {'fields': ('is_active','is_staff','groups','user_permissions')}),
    )

    # fieldsets for creating new user
    add_fieldsets = (
        (None,    {'fields': ('last_name','first_name','email', 'password1', 'password2')}),
    )

    search_fields = ('email',)
    ordering = ('last_name',)
    # filter_horizontal = ()


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    # to have a date-based drilldown navigation in the admin page
    date_hierarchy = 'action_time'

    # to filter the resultes by users, content types and action flags
    list_filter = [
        'user',
        'content_type',
        'action_flag',
    ]

    # when searching the user will be able to search in both object_repr and change_message
    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'change_message',
        'action_flag',
    ]