from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    # User booking management
    path('', views.user_bookings, name='user_bookings'),  # Main booking page shows user's bookings
    path('my-bookings/', views.user_bookings, name='user_bookings_alt'),  # Alternative URL
    
    # Booking process URLs
    path('book/<int:availability_id>/', views.create_booking, name='create_booking'),
    path('booking/<uuid:booking_id>/', views.booking_detail, name='booking_detail'),
    path('cancel/<uuid:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # Payment URLs
    path('payment/select/<uuid:booking_id>/', views.payment_selection, name='payment_selection'),
    path('payment/process/<uuid:payment_id>/', views.process_payment, name='process_payment'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
    
    # Legacy/Admin URLs (kept for admin use)
    path('admin/availability/', views.availability_list, name='availability_list'),
    path('admin/availability/<int:availability_id>/', views.availability_detail, name='availability_detail'),
    
    # AJAX URLs
    path('api/check-availability/', views.check_availability, name='check_availability'),
]
