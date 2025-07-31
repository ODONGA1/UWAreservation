from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from communications.models import NotificationTemplate, NotificationLog
from django.template import Template, Context

User = get_user_model()


class Command(BaseCommand):
    help = 'Test notification templates by rendering them with sample data'

    def handle(self, *args, **options):
        # Test data
        test_context = {
            'user_name': 'John Doe',
            'booking_id': 'BWS-2024-001',
            'tour_name': 'Wildlife Safari Adventure',
            'park_name': 'Murchison Falls National Park',
            'tour_date': '2024-02-15',
            'num_people': 2,
            'total_cost': '150.00',
            'booking_status': 'Confirmed',
            'payment_id': 'PAY-123456',
            'amount': '150.00',
            'currency': 'USD',
            'payment_method': 'Credit Card',
            'transaction_id': 'TXN-789012',
            'reminder_type': '24 hours'
        }

        self.stdout.write(
            self.style.SUCCESS('Testing notification templates with sample data...\n')
        )

        templates = NotificationTemplate.objects.all()
        
        if not templates.exists():
            self.stdout.write(
                self.style.ERROR('No templates found. Run "python manage.py create_notification_templates" first.')
            )
            return

        for template in templates:
            self.stdout.write(f"\n{'-' * 60}")
            self.stdout.write(f"Template: {template.name}")
            self.stdout.write(f"Type: {template.template_type}")
            self.stdout.write(f"Channel: {template.channel}")
            self.stdout.write(f"{'-' * 60}")

            try:
                if template.channel == 'email':
                    # Test email subject
                    if template.email_subject:
                        subject_template = Template(template.email_subject)
                        rendered_subject = subject_template.render(Context(test_context))
                        self.stdout.write(f"Subject: {rendered_subject}")

                    # Test email body (text version)
                    if template.email_body_text:
                        body_template = Template(template.email_body_text)
                        rendered_body = body_template.render(Context(test_context))
                        self.stdout.write("Text Body:")
                        self.stdout.write(rendered_body[:200] + "..." if len(rendered_body) > 200 else rendered_body)

                elif template.channel == 'sms':
                    # Test SMS message
                    if template.sms_message:
                        sms_template = Template(template.sms_message)
                        rendered_sms = sms_template.render(Context(test_context))
                        self.stdout.write(f"SMS Message: {rendered_sms}")

                self.stdout.write(self.style.SUCCESS("✓ Template rendered successfully"))

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error rendering template: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nTemplate testing completed. {templates.count()} templates tested.')
        )

        # Show available variables
        self.stdout.write(f"\n{'-' * 60}")
        self.stdout.write("Available template variables:")
        self.stdout.write(f"{'-' * 60}")
        for key, value in test_context.items():
            self.stdout.write(f"{{{{ {key} }}}} = {value}")
        
        self.stdout.write(f"\n{'-' * 60}")
        self.stdout.write("Next steps:")
        self.stdout.write("1. Configure .env file with API keys")
        self.stdout.write("2. Start Redis server")
        self.stdout.write("3. Start Celery worker: celery -A UWAreservation worker --loglevel=info")
        self.stdout.write("4. Test real notifications: python manage.py test_notifications --email your@email.com")
        self.stdout.write(f"{'-' * 60}")
