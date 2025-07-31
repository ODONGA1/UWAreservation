# In tours/admin.py
from django.contrib import admin
from .models import Park, Tour, Guide, Availability, Booking

admin.site.register(Park)
admin.site.register(Tour)
admin.site.register(Guide)
admin.site.register(Availability)
admin.site.register(Booking)