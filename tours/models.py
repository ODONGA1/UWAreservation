# In tours/models.py
from django.db import models
from django.conf import settings # To link to the User model

class Park(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='parks/', blank=True, null=True, help_text="Image of the park")

    def __str__(self):
        return self.name

class Guide(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, help_text="e.g., Birding, Primates")
    
    def save(self, *args, **kwargs):
        # Automatically set the user's profile role to 'guide' when creating a Guide
        super().save(*args, **kwargs)
        if hasattr(self.user, 'profile'):
            self.user.profile.role = 'guide'
            self.user.profile.save()
    
    def __str__(self):
        return f"Guide: {self.user.username}"

class Tour(models.Model):
    park = models.ForeignKey(Park, on_delete=models.CASCADE, related_name='tours')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_hours = models.IntegerField()
    max_participants = models.PositiveIntegerField(default=10)
    image = models.ImageField(upload_to='tours/', blank=True, null=True, help_text="Image of the tour")

    @property
    def duration(self):
        """Alias for duration_hours for backward compatibility"""
        return self.duration_hours

    def __str__(self):
        return f"{self.name} in {self.park.name}"