# In ratings/urls.py
from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    # Add and edit ratings
    path('add/<str:app_label>/<str:model_name>/<int:object_id>/', views.add_rating, name='add_rating'),
    path('edit/<int:rating_id>/', views.edit_rating, name='edit_rating'),
    
    # Rating photo management
    path('photo/<int:photo_id>/delete/', views.delete_rating_photo, name='delete_rating_photo'),
    
    # Rating interactions
    path('reply/<int:rating_id>/', views.add_rating_reply, name='add_rating_reply'),
    path('helpful/<int:rating_id>/', views.mark_rating_helpful, name='mark_rating_helpful'),
    
    # API for loading ratings
    path('api/<str:app_label>/<str:model_name>/<int:object_id>/', views.get_ratings, name='get_ratings'),
]
