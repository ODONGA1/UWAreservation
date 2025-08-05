from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tours.models import Park, Guide, Tour
from booking.models import Availability, Booking, Payment, BookingNotification
from accounts.models import Profile, NotificationSettings
from django.db.models import Count


class Command(BaseCommand):
    help = 'Show comprehensive database status'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DATABASE STATUS ==='))
        self.stdout.write(f'Users: {User.objects.count()}')
        self.stdout.write(f'Profiles: {Profile.objects.count()}')
        self.stdout.write(f'Notification Settings: {NotificationSettings.objects.count()}')
        self.stdout.write(f'Parks: {Park.objects.count()}')
        self.stdout.write(f'Guides: {Guide.objects.count()}')
        self.stdout.write(f'Tours: {Tour.objects.count()}')
        self.stdout.write(f'Availabilities: {Availability.objects.count()}')
        self.stdout.write(f'Bookings: {Booking.objects.count()}')
        self.stdout.write(f'Payments: {Payment.objects.count()}')
        self.stdout.write(f'Notifications: {BookingNotification.objects.count()}')

        self.stdout.write(self.style.SUCCESS('\n=== BOOKING STATUS BREAKDOWN ==='))
        booking_statuses = Booking.objects.values('booking_status').annotate(count=Count('booking_status'))
        for status in booking_statuses:
            self.stdout.write(f'{status["booking_status"].title()}: {status["count"]}')

        self.stdout.write(self.style.SUCCESS('\n=== PAYMENT STATUS BREAKDOWN ==='))
        payment_statuses = Payment.objects.values('status').annotate(count=Count('status'))
        for status in payment_statuses:
            self.stdout.write(f'{status["status"].title()}: {status["count"]}')

        self.stdout.write(self.style.SUCCESS('\n=== USER ROLES ==='))
        user_roles = Profile.objects.values('role').annotate(count=Count('role'))
        for role in user_roles:
            self.stdout.write(f'{role["role"].title()}: {role["count"]}')

        self.stdout.write(self.style.SUCCESS('\n=== RECENT BOOKINGS ==='))
        recent_bookings = Booking.objects.select_related('tourist', 'availability__tour').order_by('-booking_date')[:5]
        for booking in recent_bookings:
            self.stdout.write(f'Booking {booking.reference_code}: {booking.tourist.username} - {booking.availability.tour.name} ({booking.booking_status})')

        self.stdout.write(self.style.SUCCESS('\n=== TOURS WITH BOOKINGS ==='))
        tours_with_bookings = Tour.objects.annotate(booking_count=Count('availability__bookings')).filter(booking_count__gt=0)
        for tour in tours_with_bookings:
            self.stdout.write(f'{tour.name}: {tour.booking_count} bookings')
