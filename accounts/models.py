from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Link this profile to a specific user account
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Define user roles
    ROLE_CHOICES = (
        ('tourist', 'Tourist'),
        ('guide', 'Tour Guide'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='tourist')

    # Add other fields you might need
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True, help_text="A short bio for tour guides.")

    def __str__(self):
        return f"{self.user.username}'s Profile"