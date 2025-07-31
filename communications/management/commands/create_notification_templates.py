from django.core.management.base import BaseCommand
from communications.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Create default notification templates'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Booking Confirmation Email',
                'template_type': 'booking_confirmation',
                'channel': 'email',
                'email_subject': 'Booking Confirmation - {{tour_name}}',
                'email_body_text': '''Dear {{user_name}},

Thank you for booking with UWA Tours!

Booking Details:
- Booking ID: {{booking_id}}
- Tour: {{tour_name}}
- Park: {{park_name}}
- Date: {{tour_date}}
- Number of People: {{num_people}}
- Total Cost: ${{total_cost}}
- Status: {{booking_status}}

We look forward to providing you with an amazing wildlife experience!

Best regards,
UWA Tours Team
''',
                'email_body_html': '''<html>
<body>
<h2>Booking Confirmation</h2>
<p>Dear {{user_name}},</p>
<p>Thank you for booking with UWA Tours!</p>

<h3>Booking Details:</h3>
<ul>
<li><strong>Booking ID:</strong> {{booking_id}}</li>
<li><strong>Tour:</strong> {{tour_name}}</li>
<li><strong>Park:</strong> {{park_name}}</li>
<li><strong>Date:</strong> {{tour_date}}</li>
<li><strong>Number of People:</strong> {{num_people}}</li>
<li><strong>Total Cost:</strong> ${{total_cost}}</li>
<li><strong>Status:</strong> {{booking_status}}</li>
</ul>

<p>We look forward to providing you with an amazing wildlife experience!</p>
<p>Best regards,<br>UWA Tours Team</p>
</body>
</html>''',
                'available_variables': '{{user_name}}, {{booking_id}}, {{tour_name}}, {{park_name}}, {{tour_date}}, {{num_people}}, {{total_cost}}, {{booking_status}}'
            },
            {
                'name': 'Booking Confirmation SMS',
                'template_type': 'booking_confirmation',
                'channel': 'sms',
                'sms_message': 'UWA Tours: Booking confirmed! {{tour_name}} on {{tour_date}}. Booking ID: {{booking_id}}. Total: ${{total_cost}}',
                'available_variables': '{{user_name}}, {{booking_id}}, {{tour_name}}, {{tour_date}}, {{total_cost}}'
            },
            {
                'name': 'Payment Confirmation Email',
                'template_type': 'payment_confirmation',
                'channel': 'email',
                'email_subject': 'Payment Confirmed - {{tour_name}}',
                'email_body_text': '''Dear {{user_name}},

Your payment has been successfully processed!

Payment Details:
- Payment ID: {{payment_id}}
- Booking ID: {{booking_id}}
- Tour: {{tour_name}}
- Amount: {{amount}} {{currency}}
- Payment Method: {{payment_method}}
- Transaction ID: {{transaction_id}}

Your booking is now confirmed and we're excited to welcome you on the tour!

Best regards,
UWA Tours Team
''',
                'available_variables': '{{user_name}}, {{payment_id}}, {{booking_id}}, {{tour_name}}, {{amount}}, {{currency}}, {{payment_method}}, {{transaction_id}}'
            },
            {
                'name': 'Payment Confirmation SMS',
                'template_type': 'payment_confirmation',
                'channel': 'sms',
                'sms_message': 'UWA Tours: Payment confirmed! {{amount}} {{currency}} for {{tour_name}}. Your booking is confirmed!',
                'available_variables': '{{amount}}, {{currency}}, {{tour_name}}'
            },
            {
                'name': '24 Hour Tour Reminder Email',
                'template_type': 'tour_reminder_24h',
                'channel': 'email',
                'email_subject': 'Tour Reminder - {{tour_name}} Tomorrow',
                'email_body_text': '''Dear {{user_name}},

This is a friendly reminder that your tour is scheduled for tomorrow!

Tour Details:
- Tour: {{tour_name}}
- Date: {{tour_date}}
- Reminder: {{reminder_type}} before your tour

Please make sure to arrive on time and bring any necessary items for your wildlife adventure.

Looking forward to seeing you tomorrow!

Best regards,
UWA Tours Team
''',
                'available_variables': '{{user_name}}, {{tour_name}}, {{tour_date}}, {{reminder_type}}'
            },
            {
                'name': '24 Hour Tour Reminder SMS',
                'template_type': 'tour_reminder_24h',
                'channel': 'sms',
                'sms_message': 'UWA Tours: Reminder - {{tour_name}} tomorrow {{tour_date}}. See you there!',
                'available_variables': '{{tour_name}}, {{tour_date}}'
            },
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = NotificationTemplate.objects.update_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {created_count + updated_count} templates '
                f'({created_count} created, {updated_count} updated)'
            )
        )
