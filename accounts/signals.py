from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import transaction
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """Create a profile for new users, ensuring no duplicates"""
    if created:
        # Use atomic transaction to prevent race conditions
        with transaction.atomic():
            Profile.objects.get_or_create(user=instance)