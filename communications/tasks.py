from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import Context, Template
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging
import json
from datetime import timedelta

from .models import NotificationLog, NotificationTemplate, NotificationPreference
from booking.models import Booking, Payment

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_notification(self, notification_log_id):
    """Send email notification using django-anymail"""
    try:
        notification = NotificationLog.objects.get(id=notification_log_id)
        
        if notification.status != 'queued':
            logger.warning(f"Notification {notification.notification_id} is not in queued status")
            return
        
        # Prepare email
        subject = notification.subject
        message_text = notification.message
        from_email = settings.NOTIFICATION_FROM_EMAIL
        recipient_list = [notification.recipient_email]
        
        # Send email
        try:
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=message_text,
                from_email=from_email,
                to=recipient_list
            )
            
            # If HTML content is available, add it
            if hasattr(notification, 'html_content') and notification.html_content:
                email.attach_alternative(notification.html_content, "text/html")
            
            # Send the email
            email.send()
            
            # Update notification status
            notification.mark_sent()
            logger.info(f"Email sent successfully to {notification.recipient_email}")
            
            return f"Email sent to {notification.recipient_email}"
            
        except Exception as email_error:
            error_message = str(email_error)
            logger.error(f"Failed to send email to {notification.recipient_email}: {error_message}")
            
            # Mark as failed and potentially retry
            notification.mark_failed(error_message)
            
            if notification.can_retry:
                # Retry with exponential backoff
                retry_delay = 60 * (2 ** notification.retry_count)
                raise self.retry(countdown=retry_delay, exc=email_error)
            
            return f"Failed to send email after {notification.retry_count} attempts"
            
    except NotificationLog.DoesNotExist:
        logger.error(f"NotificationLog with id {notification_log_id} not found")
        return "Notification not found"
    except Exception as e:
        logger.error(f"Unexpected error in send_email_notification: {str(e)}")
        raise


@shared_task(bind=True, max_retries=3)
def send_sms_notification(self, notification_log_id):
    """Send SMS notification using Twilio"""
    try:
        notification = NotificationLog.objects.get(id=notification_log_id)
        
        if notification.status != 'queued':
            logger.warning(f"Notification {notification.notification_id} is not in queued status")
            return
        
        # Initialize Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        try:
            # Send SMS
            message = client.messages.create(
                body=notification.message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=notification.recipient_phone
            )
            
            # Update notification with provider message ID
            notification.mark_sent(provider_message_id=message.sid)
            notification.provider_response = {
                'sid': message.sid,
                'status': message.status,
                'direction': message.direction,
                'price': message.price,
                'price_unit': message.price_unit,
            }
            notification.save()
            
            logger.info(f"SMS sent successfully to {notification.recipient_phone}, SID: {message.sid}")
            return f"SMS sent to {notification.recipient_phone}"
            
        except TwilioException as twilio_error:
            error_message = str(twilio_error)
            logger.error(f"Twilio error sending SMS to {notification.recipient_phone}: {error_message}")
            
            notification.mark_failed(error_message)
            
            if notification.can_retry:
                retry_delay = 60 * (2 ** notification.retry_count)
                raise self.retry(countdown=retry_delay, exc=twilio_error)
            
            return f"Failed to send SMS after {notification.retry_count} attempts"
            
    except NotificationLog.DoesNotExist:
        logger.error(f"NotificationLog with id {notification_log_id} not found")
        return "Notification not found"
    except Exception as e:
        logger.error(f"Unexpected error in send_sms_notification: {str(e)}")
        raise


@shared_task
def send_booking_confirmation(booking_id):
    """Send booking confirmation email and SMS"""
    try:
        booking = Booking.objects.select_related(
            'tourist', 'availability__tour', 'availability__tour__park'
        ).get(booking_id=booking_id)
        
        user = booking.tourist
        preferences, created = NotificationPreference.objects.get_or_create(user=user)
        
        # Prepare template context
        context = {
            'user_name': user.get_full_name() or user.username,
            'booking_id': str(booking.booking_id),
            'tour_name': booking.availability.tour.name,
            'park_name': booking.availability.tour.park.name,
            'tour_date': booking.availability.date.strftime('%B %d, %Y'),
            'num_people': booking.num_of_people,
            'total_cost': booking.total_cost,
            'booking_status': booking.get_booking_status_display(),
        }
        
        # Send email notification
        if preferences.wants_email_notification('booking_confirmation'):
            create_and_queue_notification(
                recipient_user=user,
                template_type='booking_confirmation',
                channel='email',
                context=context,
                related_booking_id=booking.booking_id
            )
        
        # Send SMS notification
        if preferences.wants_sms_notification('booking_confirmation'):
            create_and_queue_notification(
                recipient_user=user,
                template_type='booking_confirmation',
                channel='sms',
                context=context,
                related_booking_id=booking.booking_id
            )
        
        logger.info(f"Booking confirmation notifications queued for booking {booking_id}")
        return f"Notifications queued for booking {booking_id}"
        
    except Booking.DoesNotExist:
        logger.error(f"Booking {booking_id} not found")
        return "Booking not found"
    except Exception as e:
        logger.error(f"Error sending booking confirmation for {booking_id}: {str(e)}")
        raise


@shared_task
def send_payment_confirmation(payment_id):
    """Send payment confirmation notifications"""
    try:
        payment = Payment.objects.select_related(
            'booking__tourist',
            'booking__availability__tour',
            'booking__availability__tour__park'
        ).get(payment_id=payment_id)
        
        booking = payment.booking
        user = booking.tourist
        preferences, created = NotificationPreference.objects.get_or_create(user=user)
        
        context = {
            'user_name': user.get_full_name() or user.username,
            'booking_id': str(booking.booking_id),
            'payment_id': str(payment.payment_id),
            'tour_name': booking.availability.tour.name,
            'amount': payment.amount,
            'currency': payment.currency,
            'payment_method': payment.get_payment_method_display(),
            'transaction_id': payment.gateway_transaction_id,
        }
        
        # Send notifications based on preferences
        if preferences.wants_email_notification('payment_confirmation'):
            create_and_queue_notification(
                recipient_user=user,
                template_type='payment_confirmation',
                channel='email',
                context=context,
                related_payment_id=payment.payment_id
            )
        
        if preferences.wants_sms_notification('payment_confirmation'):
            create_and_queue_notification(
                recipient_user=user,
                template_type='payment_confirmation',
                channel='sms',
                context=context,
                related_payment_id=payment.payment_id
            )
        
        logger.info(f"Payment confirmation notifications queued for payment {payment_id}")
        return f"Payment confirmation sent for {payment_id}"
        
    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found")
        return "Payment not found"


@shared_task
def send_tour_reminders():
    """Send tour reminders for upcoming tours"""
    tomorrow = timezone.now().date() + timedelta(days=1)
    in_2_hours = timezone.now() + timedelta(hours=2)
    
    # Get bookings for tomorrow (24h reminder)
    tomorrow_bookings = Booking.objects.filter(
        availability__date=tomorrow,
        booking_status='confirmed'
    ).select_related('tourist', 'availability__tour')
    
    # Get bookings in 2 hours (2h reminder)
    today_bookings = Booking.objects.filter(
        availability__date=timezone.now().date(),
        booking_status='confirmed'
    ).select_related('tourist', 'availability__tour')
    
    reminder_count = 0
    
    # 24h reminders
    for booking in tomorrow_bookings:
        user = booking.tourist
        preferences, created = NotificationPreference.objects.get_or_create(user=user)
        
        if preferences.reminder_24h_before:
            context = {
                'user_name': user.get_full_name() or user.username,
                'tour_name': booking.availability.tour.name,
                'tour_date': booking.availability.date.strftime('%B %d, %Y'),
                'reminder_type': '24 hours',
            }
            
            if preferences.wants_email_notification('tour_reminder'):
                create_and_queue_notification(
                    recipient_user=user,
                    template_type='tour_reminder_24h',
                    channel='email',
                    context=context,
                    related_booking_id=booking.booking_id
                )
                reminder_count += 1
            
            if preferences.wants_sms_notification('tour_reminder'):
                create_and_queue_notification(
                    recipient_user=user,
                    template_type='tour_reminder_24h',
                    channel='sms',
                    context=context,
                    related_booking_id=booking.booking_id
                )
                reminder_count += 1
    
    # 2h reminders (you would need to check specific tour times for this)
    # This is a simplified version - in practice, you'd want to store tour start times
    
    logger.info(f"Queued {reminder_count} tour reminder notifications")
    return f"Sent {reminder_count} tour reminders"


def create_and_queue_notification(recipient_user, template_type, channel, context, 
                                 related_booking_id=None, related_payment_id=None, 
                                 priority=5, scheduled_at=None):
    """Helper function to create and queue notifications"""
    try:
        # Get template
        template = NotificationTemplate.objects.filter(
            template_type=template_type,
            channel__in=[channel, 'both'],
            is_active=True
        ).first()
        
        if not template:
            logger.warning(f"No active template found for {template_type} - {channel}")
            return None
        
        # Get user preferences
        preferences, created = NotificationPreference.objects.get_or_create(user=recipient_user)
        
        # Prepare notification content
        if channel == 'email':
            recipient_email = preferences.get_preferred_email()
            subject = render_template_string(template.email_subject, context)
            message = render_template_string(template.email_body_text, context)
        else:  # SMS
            recipient_phone = preferences.preferred_phone
            if not recipient_phone:
                logger.warning(f"No phone number for user {recipient_user.username}")
                return None
            subject = ""
            message = render_template_string(template.sms_message, context)
        
        # Create notification log
        notification = NotificationLog.objects.create(
            recipient_user=recipient_user,
            recipient_email=recipient_email if channel == 'email' else '',
            recipient_phone=recipient_phone if channel == 'sms' else '',
            template=template,
            channel=channel,
            subject=subject,
            message=message,
            related_booking_id=related_booking_id,
            related_payment_id=related_payment_id,
            priority=priority,
            scheduled_at=scheduled_at or timezone.now(),
            status='queued'
        )
        
        # Queue the task
        if channel == 'email':
            send_email_notification.delay(notification.id)
        else:
            send_sms_notification.delay(notification.id)
        
        return notification
        
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        return None


def render_template_string(template_string, context):
    """Render a template string with context"""
    if not template_string:
        return ""
    
    template = Template(template_string)
    return template.render(Context(context))
