from django.db import models
from django.contrib.auth.models import User


class UserRole(models.Model):
    """User role definitions"""
    ROLE_CHOICES = (
        ('tourist', 'Tourist'),
        ('guide', 'Tour Guide'),
        ('operator', 'Tour Operator'),
        ('staff', 'UWA Staff'),
    )
    
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True, help_text="Description of this role")
    permissions = models.JSONField(default=dict, blank=True, help_text="Role-specific permissions")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        ordering = ['name']


class Profile(models.Model):
    # Link this profile to a specific user account
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Multiple roles support - users can have multiple roles
    roles = models.ManyToManyField(UserRole, blank=True, help_text="User can have multiple roles")

    # Add other fields you might need
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True, help_text="A short bio for the user.")
    
    # Additional fields for different roles
    guide_experience_years = models.PositiveIntegerField(null=True, blank=True, help_text="Years of experience as a tour guide")
    guide_languages = models.CharField(max_length=200, blank=True, help_text="Languages spoken by the guide (comma-separated)")
    guide_specializations = models.CharField(max_length=300, blank=True, help_text="Guide specializations (e.g., wildlife, birding, cultural)")
    
    operator_company_name = models.CharField(max_length=100, blank=True, help_text="Tour operator company name")
    operator_license_number = models.CharField(max_length=50, blank=True, help_text="Tour operator license number")
    operator_website = models.URLField(blank=True, help_text="Tour operator website")
    
    staff_employee_id = models.CharField(max_length=20, blank=True, help_text="UWA staff employee ID")
    staff_department = models.CharField(max_length=100, blank=True, help_text="UWA department")
    staff_position = models.CharField(max_length=100, blank=True, help_text="Job position/title")
    
    # Profile settings
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_joined_tourism = models.DateField(null=True, blank=True, help_text="Date when user started in tourism industry")
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    
    def get_roles_display(self):
        """Return comma-separated list of user roles"""
        return ", ".join([role.get_name_display() for role in self.roles.all()])
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.roles.filter(name=role_name).exists()
    
    def is_tourist(self):
        return self.has_role('tourist')
    
    def is_guide(self):
        return self.has_role('guide')
    
    def is_operator(self):
        return self.has_role('operator')
    
    def is_staff(self):
        return self.has_role('staff')
    
    def can_manage_parks(self):
        """Check if user can manage parks (UWA Staff only)"""
        return self.is_staff()
    
    def get_primary_role(self):
        """Get the first role as primary (for backward compatibility)"""
        first_role = self.roles.first()
        return first_role.name if first_role else 'tourist'


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