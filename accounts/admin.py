from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Register Profile model separately
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone_number', 'get_user_email']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']
    list_editable = ['role']  # Allow editing role directly from the list view
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'

# Use the default UserAdmin without inline
# Users and Profiles will be managed separately
admin.site.unregister(User)
admin.site.register(User, BaseUserAdmin)