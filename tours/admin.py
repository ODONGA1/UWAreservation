# In tours/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from .models import Park, Tour, Guide, TourCompany

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

class TourCompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_uwa', 'license_number', 'website', 'operator_count']
    list_filter = ['is_uwa']
    search_fields = ['name', 'license_number']
    filter_horizontal = ['operators']
    
    def operator_count(self, obj):
        return obj.operators.count()
    operator_count.short_description = 'Operators'

class ParkAdmin(admin.ModelAdmin):
    list_display = ['name', 'location']
    list_filter = ['location']
    search_fields = ['name', 'description', 'location']

class TourAdmin(admin.ModelAdmin):
    list_display = ['name', 'park', 'company', 'price', 'duration_hours', 'created_by']
    list_filter = ['company', 'park']
    search_fields = ['name', 'description', 'company__name']
    autocomplete_fields = ['company', 'park']

admin.site.register(Park, ParkAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(Guide, GuideAdmin)
admin.site.register(TourCompany, TourCompanyAdmin)