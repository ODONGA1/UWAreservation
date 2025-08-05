from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid

from tours.models import Guide
from booking.models import Availability, Booking, Payment, BookingNotification
from accounts.models import Profile, NotificationSettings


class Command(BaseCommand):
    help = 'Add bookings and other data specifically for the luyir user'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding data for luyir user...'))
        
        # Find or create luyir user
        luyir_user = self.ensure_luyir_user()
        
        # Add bookings for luyir
        bookings = self.create_luyir_bookings(luyir_user)
        
        # Create payments for the bookings
        payments = self.create_luyir_payments(bookings)
        
        # Create notifications
        notifications = self.create_luyir_notifications(bookings)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added for luyir user:\n'
                f'- {len(bookings)} bookings\n'
                f'- {len(payments)} payments\n'
                f'- {len(notifications)} notifications'
            )
        )

    def ensure_luyir_user(self):
        """Find or create the luyir user"""
        try:
            user = User.objects.get(username='luyir')
            self.stdout.write(f'Found existing luyir user: {user.email}')
        except User.DoesNotExist:
            # Create luyir user
            user = User.objects.create_user(
                username='luyir',
                email='luyir@example.com',
                password='password123',
                first_name='Luyir',
                last_name='User'
            )
            self.stdout.write('Created new luyir user')
        
        # Ensure profile exists
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'tourist',
                'phone_number': '+256701234567',
                'bio': 'Wildlife photography enthusiast and nature lover from Uganda'
            }
        )
        
        if created:
            self.stdout.write('Created profile for luyir user')
        
        # Ensure notification settings exist
        notifications, created = NotificationSettings.objects.get_or_create(
            user=user,
            defaults={
                'email_bookings': True,
                'email_promotions': True,
                'email_reminders': True,
                'email_updates': True,
                'sms_reminders': True
            }
        )
        
        if created:
            self.stdout.write('Created notification settings for luyir user')
        
        return user

    def create_luyir_bookings(self, user):
        """Create several bookings for luyir user"""
        # Check if luyir already has bookings
        existing_bookings = Booking.objects.filter(tourist=user).count()
        if existing_bookings > 0:
            self.stdout.write(f'Luyir already has {existing_bookings} bookings')
            return list(Booking.objects.filter(tourist=user))
        
        bookings = []
        
        # Get available slots for different tours
        availabilities = list(Availability.objects.filter(
            slots_available__gt=0,
            date__gte=timezone.now().date() - timedelta(days=30)
        ).select_related('tour', 'tour__park'))
        
        if not availabilities:
            self.stdout.write('No availabilities found')
            return bookings
        
        # Create 6 diverse bookings for luyir
        booking_scenarios = [
            # Past completed gorilla trekking
            {
                'tour_name': 'Mountain Gorilla Trekking',
                'num_people': 2,
                'status': 'completed',
                'payment_status': 'completed',
                'days_ago': 45,
                'special_requirements': 'Professional photography equipment'
            },
            # Past completed boat safari
            {
                'tour_name': 'Kazinga Channel Boat Safari', 
                'num_people': 1,
                'status': 'completed',
                'payment_status': 'completed',
                'days_ago': 30,
                'special_requirements': ''
            },
            # Upcoming confirmed chimpanzee trekking
            {
                'tour_name': 'Chimpanzee Trekking',
                'num_people': 1,
                'status': 'confirmed',
                'payment_status': 'completed', 
                'days_ahead': 15,
                'special_requirements': 'Early morning start preferred'
            },
            # Upcoming confirmed wildlife safari
            {
                'tour_name': 'Big 5 Game Drive',
                'num_people': 3,
                'status': 'confirmed',
                'payment_status': 'completed',
                'days_ahead': 25,
                'special_requirements': 'Vegetarian meals for group'
            },
            # Recent pending booking
            {
                'tour_name': 'Tree-Climbing Lions Safari',
                'num_people': 2,
                'status': 'pending',
                'payment_status': 'pending',
                'days_ahead': 35,
                'special_requirements': 'Wheelchair accessible vehicle needed'
            },
            # Far future confirmed booking
            {
                'tour_name': 'Primate Walk',
                'num_people': 1,
                'status': 'confirmed',
                'payment_status': 'completed',
                'days_ahead': 60,
                'special_requirements': ''
            }
        ]
        
        for scenario in booking_scenarios:
            # Find suitable availability
            suitable_availability = None
            
            for availability in availabilities:
                if (scenario['tour_name'] in availability.tour.name and 
                    availability.slots_available >= scenario['num_people']):
                    
                    # Adjust the date based on scenario
                    target_date = None
                    if 'days_ago' in scenario:
                        target_date = timezone.now().date() - timedelta(days=scenario['days_ago'])
                    elif 'days_ahead' in scenario:
                        target_date = timezone.now().date() + timedelta(days=scenario['days_ahead'])
                    
                    # Find availability close to target date or use existing
                    if target_date:
                        # For past bookings, we'll use existing availability but adjust the date
                        suitable_availability = availability
                        if 'days_ago' in scenario:
                            # For past bookings, we'll create them with past booking_date
                            # but keep the availability date as is
                            pass
                        else:
                            # For future bookings, try to find one close to target date
                            close_availability = Availability.objects.filter(
                                tour=availability.tour,
                                date__gte=target_date - timedelta(days=7),
                                date__lte=target_date + timedelta(days=7),
                                slots_available__gte=scenario['num_people']
                            ).first()
                            if close_availability:
                                suitable_availability = close_availability
                        break
            
            if not suitable_availability:
                self.stdout.write(f'No suitable availability found for {scenario["tour_name"]}')
                continue
            
            try:
                # Create the booking
                booking = Booking.objects.create(
                    tourist=user,
                    availability=suitable_availability,
                    num_of_people=scenario['num_people'],
                    unit_price=suitable_availability.tour.price,
                    total_cost=suitable_availability.tour.price * scenario['num_people'],
                    booking_status=scenario['status'],
                    payment_status=scenario['payment_status'],
                    contact_email=user.email,
                    contact_phone='+256701234567',
                    special_requirements=scenario['special_requirements']
                )
                
                # Set appropriate timestamps
                if 'days_ago' in scenario:
                    booking.booking_date = timezone.now() - timedelta(days=scenario['days_ago'] + 5)
                    if scenario['status'] == 'completed':
                        booking.confirmed_at = booking.booking_date + timedelta(hours=2)
                elif 'days_ahead' in scenario:
                    booking.booking_date = timezone.now() - timedelta(days=random.randint(1, 7))
                    if scenario['status'] == 'confirmed':
                        booking.confirmed_at = booking.booking_date + timedelta(hours=random.randint(1, 48))
                
                booking.save()
                
                # Update availability slots for confirmed/completed bookings
                if scenario['status'] in ['confirmed', 'completed']:
                    suitable_availability.slots_available = max(0, suitable_availability.slots_available - scenario['num_people'])
                    suitable_availability.save()
                
                bookings.append(booking)
                self.stdout.write(f'Created booking: {booking.reference_code} for {scenario["tour_name"]}')
                
            except Exception as e:
                self.stdout.write(f'Error creating booking for {scenario["tour_name"]}: {e}')
                continue
        
        return bookings

    def create_luyir_payments(self, bookings):
        """Create payment records for luyir's bookings"""
        payments = []
        
        payment_methods = ['credit_card', 'paypal', 'mobile_money']
        
        for booking in bookings:
            if booking.payment_status == 'pending':
                continue  # Don't create payment for pending payments
            
            # Check if payment already exists
            if Payment.objects.filter(booking=booking).exists():
                continue
            
            try:
                payment = Payment.objects.create(
                    booking=booking,
                    amount=booking.total_cost,
                    currency='USD',
                    payment_method=random.choice(payment_methods),
                    status=booking.payment_status,
                    gateway_transaction_id=f'luyir_txn_{uuid.uuid4().hex[:12]}',
                    gateway_reference=f'luyir_ref_{uuid.uuid4().hex[:8]}',
                    gateway_response={
                        'status': 'success',
                        'message': 'Payment processed successfully',
                        'customer': 'luyir'
                    }
                )
                
                # Set completion timestamp for completed payments
                if booking.payment_status == 'completed':
                    payment.completed_at = booking.booking_date + timedelta(hours=random.randint(1, 24))
                    payment.save()
                
                payments.append(payment)
                
            except Exception as e:
                self.stdout.write(f'Error creating payment for booking {booking.reference_code}: {e}')
                continue
        
        return payments

    def create_luyir_notifications(self, bookings):
        """Create notification records for luyir's bookings"""
        notifications = []
        
        for booking in bookings:
            # Check if notifications already exist for this booking
            if BookingNotification.objects.filter(booking=booking).exists():
                continue
            
            # Create 2-3 notifications per booking
            notification_scenarios = []
            
            # Booking confirmation (all bookings get this)
            notification_scenarios.append({
                'type': 'booking_confirmation',
                'subject': f'Booking Confirmation - {booking.reference_code}',
                'message': f'Dear Luyir, your booking for {booking.availability.tour.name} has been confirmed.',
                'hours_after_booking': 1
            })
            
            # Payment confirmation (for paid bookings)
            if booking.payment_status == 'completed':
                notification_scenarios.append({
                    'type': 'payment_received',
                    'subject': f'Payment Received - {booking.reference_code}',
                    'message': f'Payment of ${booking.total_cost} has been received for your {booking.availability.tour.name} booking.',
                    'hours_after_booking': 2
                })
            
            # Tour reminder (for upcoming tours)
            if booking.availability.date >= timezone.now().date():
                notification_scenarios.append({
                    'type': 'tour_reminder',
                    'subject': f'Tour Reminder - {booking.reference_code}',
                    'message': f'Reminder: Your {booking.availability.tour.name} tour is scheduled for {booking.availability.date}. Please arrive 30 minutes early.',
                    'hours_after_booking': 48
                })
            
            # Create the notifications
            for scenario in notification_scenarios:
                try:
                    notification = BookingNotification.objects.create(
                        booking=booking,
                        notification_type=scenario['type'],
                        method=random.choice(['email', 'sms']),
                        subject=scenario['subject'],
                        message=scenario['message'],
                        sent_at=booking.booking_date + timedelta(hours=scenario['hours_after_booking']),
                        delivered=True,  # Assume all notifications to luyir are delivered
                        delivery_attempts=1
                    )
                    notifications.append(notification)
                    
                except Exception as e:
                    self.stdout.write(f'Error creating notification: {e}')
                    continue
        
        return notifications
