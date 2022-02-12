# user/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from authentication.forms import UserAdminChangeForm, UserAdminCreationForm

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ['first_name','last_name','email','is_superuser','is_staff','is_active','last_login','date_joined']
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
