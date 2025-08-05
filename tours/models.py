# In tours/models.py
from django.db import models
from django.conf import settings # To link to the User model
from accounts.models import Profile, UserRole
from ratings.models import RatableMixin

class TourCompany(RatableMixin, models.Model):
    """
    Represents a tour company that offers tours.
    - Can be an external tour operator company
    - Can be UWA itself (indicated by is_uwa=True)
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    is_uwa = models.BooleanField(default=False, help_text="Check if this company is UWA itself")
    
    # A company can have multiple operators (users with operator role)
    operators = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        blank=True, 
        related_name='operating_companies',
        help_text="Users with operator permissions for this company"
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Tour Companies"

class Park(RatableMixin, models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='parks/', blank=True, null=True, help_text="Image of the park")
    
    # Additional detailed information
    date_established = models.DateField(blank=True, null=True, help_text="Date when the park was established")
    area_sqkm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Area in square kilometers")
    altitude_m = models.IntegerField(blank=True, null=True, help_text="Altitude in meters above sea level")
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Latitude coordinates")
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, help_text="Longitude coordinates")
    
    # Wildlife and vegetation information
    vegetation_type = models.TextField(blank=True, help_text="Description of vegetation types")
    key_wildlife = models.TextField(blank=True, help_text="Key wildlife species found in the park")
    key_features = models.TextField(blank=True, help_text="Key physical features and attractions")
    
    # Additional metadata
    park_type = models.CharField(max_length=50, choices=[
        ('national_park', 'National Park'),
        ('wildlife_reserve', 'Wildlife Reserve'),
        ('sanctuary', 'Wildlife Sanctuary'),
        ('forest_reserve', 'Forest Reserve'),
    ], default='national_park')
    
    contact_email = models.EmailField(blank=True, help_text="Contact email for the park")
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    website_url = models.URLField(blank=True, help_text="Official website URL")

    def __str__(self):
        return self.name

class Guide(RatableMixin, models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, help_text="e.g., Birding, Primates")
    
    def save(self, *args, **kwargs):
        # Automatically add the 'guide' role when creating a Guide
        super().save(*args, **kwargs)
        if hasattr(self.user, 'profile'):
            from accounts.models import UserRole
            guide_role, created = UserRole.objects.get_or_create(name='guide')
            self.user.profile.roles.add(guide_role)
    
    def __str__(self):
        return f"Guide: {self.user.username}"

class Tour(RatableMixin, models.Model):
    park = models.ForeignKey(Park, on_delete=models.CASCADE, related_name='tours')
    company = models.ForeignKey(TourCompany, on_delete=models.CASCADE, related_name='tours')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_hours = models.IntegerField()
    max_participants = models.PositiveIntegerField(default=10)
    image = models.ImageField(upload_to='tours/', blank=True, null=True, help_text="Image of the tour")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_tours'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def duration(self):
        """Alias for duration_hours for backward compatibility"""
        return self.duration_hours
    
    @property
    def is_uwa_tour(self):
        """Check if this tour is affiliated with UWA"""
        return self.company.is_uwa
    
    def get_company_name(self):
        """Get the name of the company offering this tour"""
        return self.company.name

    def __str__(self):
        return f"{self.name} in {self.park.name} by {self.company.name}"