# In tours/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from .models import Park, Tour, Guide

class GuideAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'get_user_email']
    list_filter = ['specialization']
    search_fields = ['user__username', 'user__email', 'specialization']
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            # Show all users but with better labeling
            kwargs["queryset"] = User.objects.all()
            # You can still use the limit if you want to restrict to guides only
            # kwargs["queryset"] = User.objects.filter(profile__role='guide')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Park)
admin.site.register(Tour)
admin.site.register(Guide, GuideAdmin)