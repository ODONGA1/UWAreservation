from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from communications.tasks import send_email_notification, send_sms_notification
from communications.models import NotificationTemplate

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the notification system by sending sample emails and SMS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test notification to',
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number to send test SMS to (format: +1234567890)',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['email', 'sms', 'both'],
            default='both',
            help='Type of notification to test',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        phone = options.get('phone')
        notification_type = options.get('type')

        if not email and not phone:
            self.stdout.write(
                self.style.ERROR('Please provide either --email or --phone argument')
            )
            return

        # Test data
        test_context = {
            'user_name': 'Test User',
            'booking_id': 'TEST-123',
            'tour_name': 'Wildlife Safari',
            'park_name': 'Murchison Falls National Park',
            'tour_date': '2024-02-15',
            'num_people': 2,
            'total_cost': '150.00',
            'booking_status': 'Confirmed'
        }

        if notification_type in ['email', 'both'] and email:
            try:
                # Get email template
                template = NotificationTemplate.objects.filter(
                    template_type='booking_confirmation',
                    channel='email'
                ).first()
                
                if template:
                    send_email_notification.delay(
                        to_email=email,
                        template_id=template.id,
                        context=test_context
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'Test email queued to {email}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('No email template found for booking_confirmation')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to queue email: {str(e)}')
                )

        if notification_type in ['sms', 'both'] and phone:
            try:
                # Get SMS template
                template = NotificationTemplate.objects.filter(
                    template_type='booking_confirmation',
                    channel='sms'
                ).first()
                
                if template:
                    send_sms_notification.delay(
                        to_phone=phone,
                        template_id=template.id,
                        context=test_context
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'Test SMS queued to {phone}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('No SMS template found for booking_confirmation')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to queue SMS: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                'Test notifications have been queued. '
                'Make sure Celery worker is running to process them.'
            )
        )
