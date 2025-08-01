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
    
    def get_full_name(self):
        """Return the user's full name or username if names are not set"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        elif self.user.first_name:
            return self.user.first_name
        else:
            return self.user.username


class NotificationSettings(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Email notifications
    email_bookings = models.BooleanField(default=True, help_text="Receive booking confirmations and updates")
    email_promotions = models.BooleanField(default=True, help_text="Receive promotional offers and new tour announcements")
    email_reminders = models.BooleanField(default=True, help_text="Receive tour reminders and preparation tips")
    email_updates = models.BooleanField(default=True, help_text="Receive general updates and newsletters")
    
    # SMS notifications
    sms_reminders = models.BooleanField(default=False, help_text="Receive SMS reminders for upcoming tours")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Notification Settings"


class Wishlist(models.Model):
    """User wishlist for tours"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    tour = models.ForeignKey('tours.Tour', on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'tour']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.tour.name}"