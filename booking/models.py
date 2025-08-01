from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from tours.models import Tour, Guide
import uuid


class Availability(models.Model):
    """Manages tour availability and guide assignments"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    slots_available = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    guide = models.ForeignKey(Guide, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Availabilities"
        unique_together = ['tour', 'date']  # Prevent duplicate availabilities for same tour and date
        ordering = ['date']

    def __str__(self):
        return f"{self.tour.name} on {self.date} ({self.slots_available} slots)"

    @property
    def is_available(self):
        """Check if there are available slots"""
        return self.slots_available > 0

    @property
    def is_past_date(self):
        """Check if the availability date has passed"""
        return self.date < timezone.now().date()

    @property
    def can_book(self):
        """Check if this availability can be booked (general availability)"""
        return self.is_available and not self.is_past_date

    def can_book_for(self, num_people):
        """Check if a booking for num_people can be made"""
        return self.can_book and self.slots_available >= num_people


class Booking(models.Model):
    """Enhanced booking model with payment integration"""
    
    # Booking Status Choices
    BOOKING_STATUS = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    ]

    # Payment Status Choices
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Basic booking information
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='bookings')
    num_of_people = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status tracking
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Contact information (can be different from user profile)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Special requirements or notes
    special_requirements = models.TextField(blank=True, help_text="Any special requirements or dietary restrictions")
    
    # Timestamps
    booking_date = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"Booking {self.booking_id} - {self.tourist.username} ({self.get_booking_status_display()})"

    @property
    def reference_code(self):
        """Generate a user-friendly booking reference code"""
        # Take first 8 characters of UUID and make uppercase
        return f"UWA-{str(self.booking_id)[:8].upper()}"
    
    @property
    def short_id(self):
        """Generate a short ID for display in cards/lists"""
        return str(self.booking_id)[:8].upper()

    def save(self, *args, **kwargs):
        # Calculate total cost if not set
        if not self.total_cost and self.availability:
            self.unit_price = self.availability.tour.price
            self.total_cost = self.unit_price * self.num_of_people
        
        # Set contact email from user profile if not provided
        if not self.contact_email:
            self.contact_email = self.tourist.email
            
        super().save(*args, **kwargs)

    @property
    def can_cancel(self):
        """Check if booking can be cancelled"""
        return self.booking_status in ['pending', 'confirmed'] and not self.availability.is_past_date

    def confirm_booking(self):
        """Confirm the booking and update availability"""
        if self.booking_status == 'pending' and self.payment_status == 'completed':
            self.booking_status = 'confirmed'
            self.confirmed_at = timezone.now()
            
            # Reduce available slots
            self.availability.slots_available -= self.num_of_people
            self.availability.save()
            
            self.save()
            return True
        return False

    def cancel_booking(self):
        """Cancel the booking and restore availability"""
        if self.can_cancel:
            if self.booking_status == 'confirmed':
                # Restore available slots
                self.availability.slots_available += self.num_of_people
                self.availability.save()
            
            self.booking_status = 'cancelled'
            self.cancelled_at = timezone.now()
            self.save()
            return True
        return False


class Payment(models.Model):
    """Payment tracking model for integration with payment gateways"""
    
    PAYMENT_METHODS = [
        ('pesapal', 'Pesapal'),
        ('dpo', 'DPO Group'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit/Debit Card'),
        ('cash', 'Cash'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Payment gateway information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    gateway_transaction_id = models.CharField(max_length=255, blank=True, help_text="Transaction ID from payment gateway")
    gateway_reference = models.CharField(max_length=255, blank=True, help_text="Gateway reference number")
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='UGX')
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=Booking.PAYMENT_STATUS, default='pending')
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Gateway response data
    gateway_response = models.JSONField(blank=True, null=True, help_text="Raw response from payment gateway")
    
    class Meta:
        ordering = ['-initiated_at']

    def __str__(self):
        return f"Payment {self.payment_id} - {self.booking.booking_id} ({self.get_status_display()})"

    def mark_completed(self):
        """Mark payment as completed and update booking"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        # Update booking payment status
        self.booking.payment_status = 'completed'
        self.booking.save()
        
        # Attempt to confirm booking
        self.booking.confirm_booking()

    def mark_failed(self, reason=""):
        """Mark payment as failed"""
        self.status = 'failed'
        self.save()
        
        # Update booking payment status
        self.booking.payment_status = 'failed'
        self.booking.save()


class BookingNotification(models.Model):
    """Track notifications sent for bookings"""
    
    NOTIFICATION_TYPES = [
        ('booking_confirmation', 'Booking Confirmation'),
        ('payment_reminder', 'Payment Reminder'),
        ('tour_reminder', 'Tour Reminder'),
        ('cancellation', 'Cancellation Notice'),
        ('refund_notice', 'Refund Notice'),
    ]
    
    NOTIFICATION_METHODS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Email & SMS'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    method = models.CharField(max_length=10, choices=NOTIFICATION_METHODS)
    
    # Content
    subject = models.CharField(max_length=255)
    message = models.TextField()
    
    # Delivery tracking
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    delivery_attempts = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.booking.booking_id}"
