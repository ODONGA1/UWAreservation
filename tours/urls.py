# In tours/urls.py
from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    # Public views
    path('', views.tour_list, name='tour_list'),
    path('parks/', views.park_list, name='park_list'),
    path('parks/<int:park_id>/', views.park_detail, name='park_detail'),
    path('tours/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('tours/<int:tour_id>/book/', views.tour_booking_options, name='tour_booking'),
    path('tours/<int:tour_id>/similar/', views.similar_tours, name='similar_tours'),
    path('guides/<int:guide_id>/', views.guide_detail, name='guide_detail'),
    path('companies/<int:company_id>/', views.company_detail, name='company_detail'),
    path('availability/', views.public_availability_list, name='public_availability_list'),
    
    # Management views (Tour Operators and UWA Staff only)
    path('manage/parks/', views.manage_parks, name='manage_parks'),
    path('manage/parks/add/', views.add_park, name='add_park'),
    path('manage/parks/<int:park_id>/', views.park_detail_redirect, name='manage_park_detail'),  # Redirect to public
    path('manage/parks/<int:park_id>/edit/', views.edit_park, name='edit_park'),
    path('manage/parks/<int:park_id>/delete/', views.delete_park, name='delete_park'),
    
    # Tour management (Tour Operators and UWA Staff only)
    path('manage/tours/', views.manage_tours, name='manage_tours'),
    path('manage/tours/add/', views.add_tour, name='add_tour'),
    path('manage/tours/<int:tour_id>/edit/', views.edit_tour, name='edit_tour'),
    path('manage/tours/<int:tour_id>/delete/', views.delete_tour, name='delete_tour'),
    
    # Availability management AJAX endpoints
    path('manage/tours/<int:tour_id>/availability/add/', views.add_availability, name='add_availability'),
    path('manage/availability/<int:availability_id>/edit/', views.edit_availability, name='edit_availability'),
    path('manage/availability/<int:availability_id>/delete/', views.delete_availability, name='delete_availability'),
    
    # New availability management page
    path('manage/availability/', views.manage_availability, name='manage_availability'),
    path('manage/availability/add/', views.add_availability_page, name='add_availability_page'),
    path('manage/availability/<int:availability_id>/edit-form/', views.edit_availability_form, name='edit_availability_form'),
]