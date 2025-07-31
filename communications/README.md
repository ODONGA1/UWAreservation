# UWA Reservation Communications System 📧

This module provides automated email and SMS notifications for the UWA Tours booking system using Django-Anymail and Celery for background processing.

## Features

- **Email notifications** via multiple providers (SendGrid, Mailgun, Amazon SES, etc.)
- **SMS notifications** via Twilio
- **Background processing** with Celery and Redis
- **Template system** for customizable notifications
- **Notification logging** and tracking
- **User preferences** for notification channels
- **Retry logic** for failed deliveries

## Setup Instructions

### 1. Install Required Packages

```bash
pip install celery redis django-anymail twilio python-decouple
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Email Configuration (choose one provider)
ANYMAIL_SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@uwatours.com

# SMS Configuration
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Default Templates

```bash
python manage.py create_notification_templates
```

### 5. Start Redis Server

```bash
# On Windows with Redis installed
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:alpine
```

### 6. Start Celery Worker

```bash
# In a separate terminal
celery -A UWAreservation worker --loglevel=info
```

## Usage

### Automatic Notifications

The system automatically sends notifications when:

- New bookings are created
- Payments are completed
- Tour reminders (24 hours before)

### Manual Notifications

```python
from communications.tasks import send_email_notification, send_sms_notification

# Send email
send_email_notification.delay(
    to_email="user@example.com",
    template_id=1,
    context={'user_name': 'John Doe', 'booking_id': '123'}
)

# Send SMS
send_sms_notification.delay(
    to_phone="+1234567890",
    template_id=2,
    context={'tour_name': 'Wildlife Safari'}
)
```

### Testing

```bash
# Test email notification
python manage.py test_notifications --email your@email.com --type email

# Test SMS notification
python manage.py test_notifications --phone +1234567890 --type sms

# Test both
python manage.py test_notifications --email your@email.com --phone +1234567890 --type both
```

## Notification Templates

Templates are stored in the `NotificationTemplate` model and support:

- **Template variables** using `{{variable_name}}` syntax
- **HTML and text** versions for emails
- **Different channels** (email/sms) for same notification type

### Available Template Types

- `booking_confirmation` - Sent when booking is created
- `payment_confirmation` - Sent when payment is completed
- `tour_reminder_24h` - Sent 24 hours before tour

### Template Variables

- `{{user_name}}` - Customer name
- `{{booking_id}}` - Booking reference
- `{{tour_name}}` - Tour name
- `{{park_name}}` - Park name
- `{{tour_date}}` - Tour date
- `{{total_cost}}` - Total booking cost
- And more...

## Admin Interface

Access the Django admin to:

- Manage notification templates
- View notification logs
- Configure user preferences
- Resend failed notifications

## Monitoring

### Celery Monitoring

```bash
# Monitor active tasks
celery -A UWAreservation inspect active

# View stats
celery -A UWAreservation inspect stats
```

### Notification Logs

Check the `NotificationLog` model in admin for:

- Delivery status
- Error messages
- Retry attempts
- Timestamp tracking

## Email Providers

### SendGrid Setup

1. Create SendGrid account
2. Generate API key
3. Add to `.env`: `ANYMAIL_SENDGRID_API_KEY=your-api-key`

### Mailgun Setup

1. Create Mailgun account
2. Add domain and get API key
3. Add to `.env`:
   ```
   ANYMAIL_MAILGUN_API_KEY=your-api-key
   ANYMAIL_MAILGUN_SENDER_DOMAIN=your-domain
   ```

### Amazon SES Setup

1. Set up AWS SES
2. Get access keys
3. Add to `.env`:
   ```
   ANYMAIL_AMAZON_SES_ACCESS_KEY_ID=your-access-key
   ANYMAIL_AMAZON_SES_SECRET_ACCESS_KEY=your-secret-key
   ANYMAIL_AMAZON_SES_REGION=us-west-2
   ```

## SMS Setup (Twilio)

1. Create Twilio account
2. Get Account SID and Auth Token
3. Buy phone number
4. Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=your-account-sid
   TWILIO_AUTH_TOKEN=your-auth-token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

## Troubleshooting

### Common Issues

1. **Celery not processing tasks**

   - Check Redis is running
   - Ensure Celery worker is started
   - Check task routing configuration

2. **Email not sending**

   - Verify email provider credentials
   - Check FROM_EMAIL setting
   - Review notification logs in admin

3. **SMS not sending**

   - Verify Twilio credentials
   - Check phone number format (+country-code)
   - Ensure phone number is verified (for trial accounts)

4. **Template not found**
   - Run `python manage.py create_notification_templates`
   - Check template exists in admin
   - Verify template_type matches

### Debug Mode

Set `DEBUG=True` in settings for detailed error messages.

### Logs

Check Django logs and Celery worker output for error details.

## Production Considerations

1. **Use proper Redis configuration** with persistence
2. **Monitor Celery workers** with supervisord or similar
3. **Set up proper logging** and monitoring
4. **Use environment variables** for all sensitive data
5. **Configure email rate limits** with your provider
6. **Set up SMS spending limits** with Twilio

## Security

- Never commit API keys to version control
- Use environment variables for all credentials
- Regularly rotate API keys
- Monitor usage and billing for third-party services
- Implement rate limiting for notification sending

## Support

For issues or questions, check:

1. Django admin notification logs
2. Celery worker logs
3. Email/SMS provider status pages
4. Redis connection status

---

Built with ❤️ for UWA Tours reservation system.
