# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Settings URLs
    path('settings/notifications/', views.notification_settings, name='notification_settings'),
    path('settings/payments/', views.payment_methods, name='payment_methods'),
    
    # Notification API
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/', views.notifications_page, name='notifications'),
    
    # Wishlist URLs
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:tour_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:tour_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # User management URLs (UWA staff only)
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage-users/toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('manage-users/detail/<int:user_id>/', views.user_detail, name='user_detail'),
    
    # Support URLs
    path('help/', views.help_support, name='help_support'),
]
