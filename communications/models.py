from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class NotificationTemplate(models.Model):
    """Email and SMS templates for different notification types"""
    
    TEMPLATE_TYPES = [
        ('booking_confirmation', 'Booking Confirmation'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('booking_cancellation', 'Booking Cancellation'),
        ('tour_reminder_24h', '24 Hour Tour Reminder'),
        ('tour_reminder_2h', '2 Hour Tour Reminder'),
        ('payment_reminder', 'Payment Reminder'),
        ('refund_notification', 'Refund Notification'),
        ('guide_assignment', 'Guide Assignment'),
        ('tour_update', 'Tour Update'),
    ]
    
    NOTIFICATION_CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Email & SMS'),
    ]

    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    channel = models.CharField(max_length=10, choices=NOTIFICATION_CHANNELS, default='email')
    
    # Email template fields
    email_subject = models.CharField(max_length=255, blank=True)
    email_body_html = models.TextField(blank=True, help_text="HTML email template")
    email_body_text = models.TextField(blank=True, help_text="Plain text email template")
    
    # SMS template fields
    sms_message = models.TextField(max_length=160, blank=True, help_text="SMS template (max 160 chars)")
    
    # Template variables info
    available_variables = models.TextField(
        blank=True, 
        help_text="Available template variables (e.g., {{booking_id}}, {{tour_name}}, {{user_name}})"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['template_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class NotificationLog(models.Model):
    """Log of all notifications sent"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]

    # Unique identifier
    notification_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Recipient information
    recipient_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    
    # Notification details
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    subject = models.CharField(max_length=255, blank=True)  # For emails
    message = models.TextField()
    
    # Related objects (for tracking context)
    related_booking_id = models.UUIDField(null=True, blank=True, help_text="Related booking UUID")
    related_payment_id = models.UUIDField(null=True, blank=True, help_text="Related payment UUID")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(default=5, help_text="1=High, 5=Normal, 10=Low")
    
    # Scheduling
    scheduled_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Provider tracking (for SMS/Email services)
    provider_message_id = models.CharField(max_length=255, blank=True)
    provider_response = models.JSONField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['recipient_user', 'channel']),
            models.Index(fields=['related_booking_id']),
        ]

    def __str__(self):
        recipient = self.recipient_user.username if self.recipient_user else (
            self.recipient_email or self.recipient_phone
        )
        return f"{self.get_channel_display()} to {recipient} - {self.get_status_display()}"

    @property
    def can_retry(self):
        """Check if notification can be retried"""
        return self.status == 'failed' and self.retry_count < self.max_retries

    def mark_sent(self, provider_message_id=None):
        """Mark notification as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if provider_message_id:
            self.provider_message_id = provider_message_id
        self.save()

    def mark_delivered(self):
        """Mark notification as delivered"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()

    def mark_failed(self, error_message=""):
        """Mark notification as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()


class NotificationPreference(models.Model):
    """User notification preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_booking_confirmations = models.BooleanField(default=True)
    email_payment_confirmations = models.BooleanField(default=True)
    email_tour_reminders = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=False)
    
    # SMS preferences
    sms_booking_confirmations = models.BooleanField(default=False)
    sms_payment_confirmations = models.BooleanField(default=False)
    sms_tour_reminders = models.BooleanField(default=True)
    sms_marketing = models.BooleanField(default=False)
    
    # Timing preferences
    reminder_24h_before = models.BooleanField(default=True)
    reminder_2h_before = models.BooleanField(default=True)
    
    # Contact information
    preferred_email = models.EmailField(blank=True, help_text="Override user's default email")
    preferred_phone = models.CharField(max_length=20, blank=True, help_text="Phone for SMS notifications")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification preferences for {self.user.username}"

    def get_preferred_email(self):
        """Get user's preferred email address"""
        return self.preferred_email or self.user.email

    def wants_email_notification(self, notification_type):
        """Check if user wants email notification for specific type"""
        preference_map = {
            'booking_confirmation': self.email_booking_confirmations,
            'payment_confirmation': self.email_payment_confirmations,
            'tour_reminder': self.email_tour_reminders,
            'marketing': self.email_marketing,
        }
        return preference_map.get(notification_type, True)

    def wants_sms_notification(self, notification_type):
        """Check if user wants SMS notification for specific type"""
        if not self.preferred_phone:
            return False
            
        preference_map = {
            'booking_confirmation': self.sms_booking_confirmations,
            'payment_confirmation': self.sms_payment_confirmations,
            'tour_reminder': self.sms_tour_reminders,
            'marketing': self.sms_marketing,
        }
        return preference_map.get(notification_type, False)
