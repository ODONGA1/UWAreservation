from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid

from tours.models import Guide
from booking.models import Availability, Booking, Payment, BookingNotification
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Add missing guides and additional bookings to complete the data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding missing guides and more bookings...'))
        
        # Create guides for guide users
        guides = self.create_missing_guides()
        
        # Add more bookings
        bookings = self.add_more_bookings()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added:\n'
                f'- {len(guides)} guides\n'
                f'- {len(bookings)} additional bookings'
            )
        )

    def create_missing_guides(self):
        """Create Guide objects for users with guide role"""
        guides = []
        
        specializations = [
            'Gorilla Trekking Specialist',
            'Primate Tracking Expert', 
            'Wildlife Safari Guide',
            'Birding Expert',
            'Mountain Hiking Guide'
        ]
        
        # Find users with guide profile role but no Guide object
        guide_profiles = Profile.objects.filter(role='guide')
        
        for i, profile in enumerate(guide_profiles):
            user = profile.user
            # Check if Guide object already exists
            if not hasattr(user, 'guide'):
                guide = Guide.objects.create(
                    user=user,
                    specialization=specializations[i % len(specializations)]
                )
                guides.append(guide)
                self.stdout.write(f'Created guide for {user.username}')
        
        return guides

    def add_more_bookings(self):
        """Add more realistic bookings"""
        bookings = []
        
        # Get all tourists
        tourists = User.objects.filter(profile__role='tourist')
        
        # Get all available slots
        availabilities = Availability.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=30),
            slots_available__gt=0
        )
        
        if not tourists.exists() or not availabilities.exists():
            self.stdout.write('No tourists or availabilities found')
            return bookings
        
        # Create 20 more bookings
        for _ in range(20):
            tourist = random.choice(tourists)
            availability = random.choice(availabilities)
            
            # Skip if no slots
            if availability.slots_available <= 0:
                continue
            
            # Random group size
            num_people = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]
            num_people = min(num_people, availability.slots_available)
            
            # Determine status based on date
            if availability.date < timezone.now().date():
                booking_status = random.choices(['completed', 'cancelled'], weights=[85, 15])[0]
                payment_status = 'completed' if booking_status == 'completed' else 'refunded'
            elif availability.date <= timezone.now().date() + timedelta(days=7):
                booking_status = random.choices(['confirmed', 'pending'], weights=[90, 10])[0]
                payment_status = 'completed' if booking_status == 'confirmed' else 'pending'
            else:
                booking_status = random.choices(['confirmed', 'pending'], weights=[70, 30])[0]
                payment_status = 'completed' if booking_status == 'confirmed' else 'pending'
            
            try:
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
                    special_requirements=random.choice(['', '', 'Vegetarian meals', 'Wheelchair accessible transport'])
                )
                
                # Set timestamps
                if booking_status in ['confirmed', 'completed']:
                    booking.confirmed_at = booking.booking_date + timedelta(hours=random.randint(1, 48))
                elif booking_status == 'cancelled':
                    booking.cancelled_at = booking.booking_date + timedelta(hours=random.randint(1, 168))
                
                booking.save()
                
                # Update availability
                if booking_status in ['confirmed', 'completed']:
                    availability.slots_available = max(0, availability.slots_available - num_people)
                    availability.save()
                
                # Create payment if needed
                if payment_status != 'pending':
                    Payment.objects.create(
                        booking=booking,
                        amount=booking.total_cost,
                        currency='USD',
                        payment_method=random.choice(['credit_card', 'paypal', 'mobile_money']),
                        status=payment_status,
                        gateway_transaction_id=f'txn_{uuid.uuid4().hex[:12]}',
                        gateway_reference=f'ref_{uuid.uuid4().hex[:8]}',
                        gateway_response={'status': 'success'}
                    )
                
                bookings.append(booking)
                
            except Exception as e:
                self.stdout.write(f'Error creating booking: {e}')
                continue
        
        return bookings
