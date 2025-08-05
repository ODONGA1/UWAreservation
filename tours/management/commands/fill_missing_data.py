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
    help = 'Add only missing data - guides and additional bookings where needed'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding missing data...'))
        
        # Create some guide users and Guide objects
        guides = self.create_guide_users()
        
        # Add more bookings if we have very few
        bookings = self.add_more_bookings()
        
        # Create missing payments for bookings that don't have them
        payments = self.create_missing_payments()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Database now has:\n'
                f'- {User.objects.count()} total users\n'
                f'- {Guide.objects.count()} total guides\n'
                f'- {Booking.objects.count()} total bookings\n'
                f'- {Payment.objects.count()} total payments\n'
                f'- {BookingNotification.objects.count()} total notifications'
            )
        )

    def create_guide_users(self):
        """Create guide users and Guide objects"""
        guides = []
        
        # Check if we already have guides
        if Guide.objects.exists():
            self.stdout.write('Guides already exist')
            return list(Guide.objects.all())
        
        guide_data = [
            ('guide_moses', 'Moses', 'Kiwanuka', 'moses.guide@uwa.go.ug', 'Gorilla Trekking Specialist'),
            ('guide_sarah', 'Sarah', 'Namubiru', 'sarah.guide@uwa.go.ug', 'Primate Tracking Expert'),
            ('guide_peter', 'Peter', 'Ssemakula', 'peter.guide@uwa.go.ug', 'Wildlife Safari Guide'),
            ('guide_mary', 'Mary', 'Nakirya', 'mary.guide@uwa.go.ug', 'Birding Expert'),
            ('guide_john', 'John', 'Mugisha', 'john.guide@uwa.go.ug', 'Mountain Hiking Guide'),
        ]
        
        self.stdout.write('Creating guide users and Guide objects...')
        for username, first_name, last_name, email, specialization in guide_data:
            # Check if user already exists
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
            
            # Create profile
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'guide',
                    'phone_number': f'+256{random.randint(700000000, 799999999)}',
                    'bio': f'Experienced Uganda Wildlife Authority guide specializing in {specialization.lower()}.'
                }
            )
            
            # Update role if it's not guide
            if profile.role != 'guide':
                profile.role = 'guide'
                profile.save()
            
            # Create notification settings
            NotificationSettings.objects.get_or_create(
                user=user,
                defaults={
                    'email_bookings': True,
                    'email_promotions': False,
                    'email_reminders': True,
                    'email_updates': True,
                    'sms_reminders': True
                }
            )
            
            # Create Guide object
            guide, created = Guide.objects.get_or_create(
                user=user,
                defaults={'specialization': specialization}
            )
            guides.append(guide)
            
            if created:
                self.stdout.write(f'Created guide: {user.username} ({specialization})')
        
        return guides

    def add_more_bookings(self):
        """Add more bookings if we have very few"""
        current_bookings = Booking.objects.count()
        
        if current_bookings >= 20:
            self.stdout.write(f'Already have {current_bookings} bookings, skipping')
            return []
        
        self.stdout.write(f'Only {current_bookings} bookings exist, adding more...')
        
        # Get tourists (excluding guides)
        tourists = User.objects.filter(profile__role='tourist')
        if not tourists.exists():
            # If no tourists, create a few regular users as tourists
            tourists = self.create_tourist_users()
        
        # Get availabilities with slots
        availabilities = list(Availability.objects.filter(slots_available__gt=0))
        if not availabilities:
            self.stdout.write('No availabilities with slots found')
            return []
        
        bookings = []
        target_bookings = 30 - current_bookings
        
        for _ in range(target_bookings):
            try:
                tourist = random.choice(tourists)
                availability = random.choice(availabilities)
                
                if availability.slots_available <= 0:
                    continue
                
                # Random group size
                num_people = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]
                num_people = min(num_people, availability.slots_available, 6)
                
                # Determine realistic status based on date
                if availability.date < timezone.now().date():
                    booking_status = random.choices(['completed', 'cancelled'], weights=[85, 15])[0]
                    payment_status = 'completed' if booking_status == 'completed' else 'refunded'
                elif availability.date <= timezone.now().date() + timedelta(days=7):
                    booking_status = 'confirmed'
                    payment_status = 'completed'
                else:
                    booking_status = random.choices(['confirmed', 'pending'], weights=[70, 30])[0]
                    payment_status = 'completed' if booking_status == 'confirmed' else 'pending'
                
                booking = Booking.objects.create(
                    tourist=tourist,
                    availability=availability,
                    num_of_people=num_people,
                    unit_price=availability.tour.price,
                    total_cost=availability.tour.price * num_people,
                    booking_status=booking_status,
                    payment_status=payment_status,
                    contact_email=tourist.email,
                    contact_phone=f'+256{random.randint(700000000, 799999999)}',
                    special_requirements=random.choice(['', '', 'Vegetarian meals', 'Wheelchair access needed'])
                )
                
                # Set timestamps
                if booking_status in ['confirmed', 'completed']:
                    booking.confirmed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                elif booking_status == 'cancelled':
                    booking.cancelled_at = timezone.now() - timedelta(days=random.randint(1, 15))
                
                booking.save()
                
                # Update availability
                if booking_status in ['confirmed', 'completed']:
                    availability.slots_available = max(0, availability.slots_available - num_people)
                    availability.save()
                
                bookings.append(booking)
                
            except Exception as e:
                self.stdout.write(f'Error creating booking: {e}')
                continue
        
        self.stdout.write(f'Created {len(bookings)} new bookings')
        return bookings

    def create_tourist_users(self):
        """Create a few tourist users if none exist"""
        tourist_data = [
            ('tourist1', 'Alex', 'Johnson', 'alex.johnson@email.com'),
            ('tourist2', 'Maria', 'Rodriguez', 'maria.rodriguez@email.com'),
            ('tourist3', 'David', 'Smith', 'david.smith@email.com'),
        ]
        
        tourists = []
        for username, first_name, last_name, email in tourist_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
            
            # Create profile
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'tourist',
                    'phone_number': f'+256{random.randint(700000000, 799999999)}',
                    'bio': f'Wildlife enthusiast from {random.choice(["USA", "UK", "Canada"])}'
                }
            )
            
            tourists.append(user)
        
        return tourists

    def create_missing_payments(self):
        """Create payment records for bookings that don't have them"""
        bookings_without_payments = Booking.objects.filter(
            payment_status__in=['completed', 'processing', 'refunded']
        ).exclude(
            booking_id__in=Payment.objects.values_list('booking__booking_id', flat=True)
        )
        
        if not bookings_without_payments.exists():
            self.stdout.write('All bookings already have payment records')
            return []
        
        self.stdout.write(f'Creating payment records for {bookings_without_payments.count()} bookings...')
        
        payments = []
        payment_methods = ['credit_card', 'paypal', 'mobile_money', 'bank_transfer']
        
        for booking in bookings_without_payments:
            try:
                # Map payment status
                if booking.payment_status == 'completed':
                    status = 'completed'
                elif booking.payment_status == 'processing':
                    status = 'processing'
                elif booking.payment_status == 'refunded':
                    status = 'refunded'
                else:
                    status = 'pending'
                
                payment = Payment.objects.create(
                    booking=booking,
                    amount=booking.total_cost,
                    currency='USD',
                    payment_method=random.choice(payment_methods),
                    status=status,
                    gateway_transaction_id=f'txn_{uuid.uuid4().hex[:12]}',
                    gateway_reference=f'ref_{uuid.uuid4().hex[:8]}',
                    gateway_response={'status': 'success', 'message': 'Payment processed'}
                )
                
                if status == 'completed':
                    payment.completed_at = booking.booking_date + timedelta(hours=random.randint(1, 24))
                    payment.save()
                
                payments.append(payment)
                
            except Exception as e:
                self.stdout.write(f'Error creating payment for booking {booking.booking_id}: {e}')
                continue
        
        return payments
