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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'guide'})
    specialization = models.CharField(max_length=100, help_text="e.g., Birding, Primates")
    
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

    def __str__(self):
        return f"{self.name} in {self.park.name}"

class Availability(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    slots_available = models.PositiveIntegerField()
    guide = models.ForeignKey(Guide, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Availabilities"

    def __str__(self):
        return f"{self.tour.name} on {self.date} ({self.slots_available} slots)"

class Booking(models.Model):
    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    num_of_people = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking for {self.tourist.username} on {self.availability.tour.name}"