from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, NotificationSettings, Wishlist

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