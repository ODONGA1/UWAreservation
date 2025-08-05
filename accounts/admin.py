from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, NotificationSettings, Wishlist, UserRole

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_name_display', 'description']
    list_filter = ['name']
    search_fields = ['name', 'description']

# Register Profile model separately
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_roles_display', 'phone_number', 'get_user_email']
    list_filter = ['roles']
    search_fields = ['user__username', 'user__email']
    filter_horizontal = ['roles']  # Nice widget for many-to-many field
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'roles', 'phone_number', 'bio', 'profile_picture', 'date_joined_tourism')
        }),
        ('Guide Information', {
            'fields': ('guide_experience_years', 'guide_languages', 'guide_specializations'),
            'classes': ('collapse',),
        }),
        ('Tour Operator Information', {
            'fields': ('operator_company_name', 'operator_license_number', 'operator_website'),
            'classes': ('collapse',),
        }),
        ('UWA Staff Information', {
            'fields': ('staff_employee_id', 'staff_department', 'staff_position'),
            'classes': ('collapse',),
        }),
    )
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'

@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_bookings', 'email_promotions', 'sms_reminders')
    list_filter = ('email_bookings', 'email_promotions', 'email_reminders', 'email_updates', 'sms_reminders')
    search_fields = ('user__username', 'user__email')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'added_at')
    list_filter = ('added_at', 'tour__park')
    search_fields = ('user__username', 'tour__name')
    date_hierarchy = 'added_at'

# Use the default UserAdmin without inline
# Users and Profiles will be managed separately
admin.site.unregister(User)
admin.site.register(User, BaseUserAdmin)