from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from booking.models import Booking, Payment
from .tasks import send_booking_confirmation, send_payment_confirmation
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Booking)
def booking_created_handler(sender, instance, created, **kwargs):
    """Send booking confirmation when a new booking is created"""
    if created and getattr(settings, 'SEND_NOTIFICATIONS', True):
        try:
            # Queue booking confirmation task
            send_booking_confirmation.delay(str(instance.booking_id))
            logger.info(f"Booking confirmation task queued for booking {instance.booking_id}")
        except Exception as e:
            logger.error(f"Failed to queue booking confirmation for {instance.booking_id}: {str(e)}")


@receiver(post_save, sender=Payment)
def payment_completed_handler(sender, instance, created, **kwargs):
    """Send payment confirmation when payment is completed"""
    if not created and instance.status == 'completed' and getattr(settings, 'SEND_NOTIFICATIONS', True):
        try:
            # Queue payment confirmation task
            send_payment_confirmation.delay(str(instance.payment_id))
            logger.info(f"Payment confirmation task queued for payment {instance.payment_id}")
        except Exception as e:
            logger.error(f"Failed to queue payment confirmation for {instance.payment_id}: {str(e)}")


@receiver(post_save, sender=Booking)
def booking_status_changed_handler(sender, instance, created, **kwargs):
    """Handle booking status changes for additional notifications"""
    if not created and getattr(settings, 'SEND_NOTIFICATIONS', True):
        # You can add logic here for other status changes like cancellations
        if instance.booking_status == 'cancelled':
            # Could queue cancellation notification
            logger.info(f"Booking {instance.booking_id} was cancelled")
        elif instance.booking_status == 'confirmed':
            logger.info(f"Booking {instance.booking_id} was confirmed")
