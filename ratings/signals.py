# In ratings/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Rating

# We'll add signal handlers here to update average ratings on related models
# For example, when a tour gets a new rating, we'll update its average rating
