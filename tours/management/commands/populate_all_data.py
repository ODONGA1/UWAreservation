from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid

from tours.models import Park, Guide, Tour
from booking.models import Availability, Booking, Payment, BookingNotification
from accounts.models import Profile, NotificationSettings


class Command(BaseCommand):
    help = 'Populate all database tables with comprehensive sample data including bookings, payments, and notifications'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting comprehensive data population...'))
        
        # Don't clear existing data - just add to empty tables
        
        # Create sample users with profiles (only if no users exist)
        users = self.create_sample_users()
        
        # Create guides (some of the users will be guides)
        guides = self.create_guides(users)
        
        # Parks, tours, and availability (only if they don't exist)
        parks = self.ensure_parks()
        tours = self.ensure_tours(parks)
        availabilities = self.ensure_availabilities(tours, guides)
        
        # Create bookings for tourists (only if no bookings exist)
        bookings = self.create_bookings(users, availabilities)
        
        # Create payments for bookings (only if no payments exist)
        payments = self.create_payments(bookings)
        
        # Create notifications (only if no notifications exist)
        notifications = self.create_notifications(bookings)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Database status:\n'
                f'- {User.objects.count()} total users\n'
                f'- {Guide.objects.count()} total guides\n'
                f'- {Park.objects.count()} total parks\n'
                f'- {Tour.objects.count()} total tours\n'
                f'- {Availability.objects.count()} total availabilities\n'
                f'- {Booking.objects.count()} total bookings\n'
                f'- {Payment.objects.count()} total payments\n'
                f'- {BookingNotification.objects.count()} total notifications'
            )
        )

    def create_sample_users(self):
        """Create sample tourist and guide users only if no regular users exist"""
        # Check if we already have regular users (excluding superusers)
        regular_users = User.objects.filter(is_superuser=False, is_staff=False)
        if regular_users.exists():
            self.stdout.write('Regular users already exist, skipping user creation')
            return list(regular_users)
        
        users = []
        
        # Create tourist users
        tourist_data = [
            ('john_doe', 'John', 'Doe', 'john.doe@email.com'),
            ('sarah_smith', 'Sarah', 'Smith', 'sarah.smith@email.com'),
            ('mike_wilson', 'Mike', 'Wilson', 'mike.wilson@email.com'),
            ('emma_johnson', 'Emma', 'Johnson', 'emma.johnson@email.com'),
            ('david_brown', 'David', 'Brown', 'david.brown@email.com'),
            ('lisa_davis', 'Lisa', 'Davis', 'lisa.davis@email.com'),
            ('james_taylor', 'James', 'Taylor', 'james.taylor@email.com'),
            ('anna_white', 'Anna', 'White', 'anna.white@email.com'),
            ('robert_clark', 'Robert', 'Clark', 'robert.clark@email.com'),
            ('maria_garcia', 'Maria', 'Garcia', 'maria.garcia@email.com'),
        ]
        
        self.stdout.write('Creating tourist users...')
        for username, first_name, last_name, email in tourist_data:
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            
            # Create profile
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'tourist',
                    'phone_number': f'+256{random.randint(700000000, 799999999)}',
                    'bio': f"Wildlife enthusiast from {random.choice(['USA', 'UK', 'Germany', 'Australia', 'Canada'])}"
                }
            )
            
            # Create notification settings
            notifications, created = NotificationSettings.objects.get_or_create(
                user=user,
                defaults={
                    'email_bookings': True,
                    'email_promotions': random.choice([True, False]),
                    'email_reminders': True,
                    'email_updates': random.choice([True, False]),
                    'sms_reminders': random.choice([True, False])
                }
            )
            
            users.append(user)
        
        # Create guide users
        guide_data = [
            ('guide_moses', 'Moses', 'Kiwanuka', 'moses.guide@uwa.go.ug'),
            ('guide_sarah', 'Sarah', 'Namubiru', 'sarah.guide@uwa.go.ug'),
            ('guide_peter', 'Peter', 'Ssemakula', 'peter.guide@uwa.go.ug'),
            ('guide_mary', 'Mary', 'Nakirya', 'mary.guide@uwa.go.ug'),
            ('guide_john', 'John', 'Mugisha', 'john.guide@uwa.go.ug'),
        ]
        
        self.stdout.write('Creating guide users...')
        for username, first_name, last_name, email in guide_data:
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            
            # Create profile
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'guide',
                    'phone_number': f'+256{random.randint(700000000, 799999999)}',
                    'bio': f"Experienced Uganda Wildlife Authority guide with {random.randint(5, 15)} years of experience in wildlife conservation and tourism."
                }
            )
            
            # Create notification settings
            notifications, created = NotificationSettings.objects.get_or_create(
                user=user,
                defaults={
                    'email_bookings': True,
                    'email_promotions': False,
                    'email_reminders': True,
                    'email_updates': True,
                    'sms_reminders': True
                }
            )
            
            users.append(user)
        
        return users

    def create_guides(self, users):
        """Create guide records for users with guide role"""
        guides = []
        
        specializations = [
            'Gorilla Trekking Specialist',
            'Primate Tracking Expert',
            'Wildlife Safari Guide',
            'Birding Expert',
            'Mountain Hiking Guide'
        ]
        
        # Find guide users and create Guide objects
        guide_users = []
        for user in users:
            try:
                if user.profile.role == 'guide':
                    guide_users.append(user)
            except:
                continue
        
        self.stdout.write(f'Creating Guide objects for {len(guide_users)} guide users...')
        for i, user in enumerate(guide_users):
            guide, created = Guide.objects.get_or_create(
                user=user,
                defaults={
                    'specialization': specializations[i % len(specializations)]
                }
            )
            guides.append(guide)
            if created:
                self.stdout.write(f'Created guide: {user.username}')
        
        # Also get existing guides
        existing_guides = Guide.objects.all()
        all_guides = list(set(guides + list(existing_guides)))
        
        return all_guides

    def ensure_parks(self):
        """Create parks only if they don't exist"""
        if Park.objects.exists():
            self.stdout.write('Parks already exist, skipping park creation')
            return list(Park.objects.all())
        
        return self.create_parks()

    def create_parks(self):
        """Create Uganda's national parks"""
        park_data = [
            {
                'name': 'Bwindi Impenetrable National Park',
                'description': 'Home to endangered mountain gorillas, this UNESCO World Heritage site offers unparalleled gorilla trekking experiences in dense rainforest.',
                'location': 'Southwestern Uganda'
            },
            {
                'name': 'Queen Elizabeth National Park',
                'description': 'Uganda\'s most popular safari destination featuring tree-climbing lions, elephants, hippos, and over 600 bird species.',
                'location': 'Western Uganda'
            },
            {
                'name': 'Murchison Falls National Park',
                'description': 'Uganda\'s largest national park where the Nile River explodes through a narrow gorge, creating spectacular waterfalls.',
                'location': 'Northwestern Uganda'
            },
            {
                'name': 'Kibale National Park',
                'description': 'Known as the primate capital of the world with 13 primate species including chimpanzees.',
                'location': 'Western Uganda'
            },
            {
                'name': 'Lake Mburo National Park',
                'description': 'Uganda\'s smallest savanna park known for zebras, impalas, and over 350 bird species.',
                'location': 'Western Uganda'
            }
        ]
        
        parks = []
        for data in park_data:
            park = Park.objects.create(**data)
            parks.append(park)
        
        return parks

    def ensure_tours(self, parks):
        """Create tours only if they don't exist"""
        if Tour.objects.exists():
            self.stdout.write('Tours already exist, skipping tour creation')
            return list(Tour.objects.all())
        
        return self.create_tours(parks)

    def ensure_availabilities(self, tours, guides):
        """Create availabilities only if they don't exist"""
        if Availability.objects.exists():
            self.stdout.write('Availabilities already exist, skipping availability creation')
            return list(Availability.objects.all())
        
        return self.create_availabilities(tours, guides)

    def create_tours(self, parks):
        """Create authentic tours for each park"""
        tours = []
        
        # Bwindi tours
        bwindi = parks[0]
        bwindi_tours = [
            {
                'name': 'Mountain Gorilla Trekking',
                'description': 'Once-in-a-lifetime experience tracking endangered mountain gorillas in their natural habitat. Limited to 8 people per group.',
                'price': Decimal('800.00'),
                'duration_hours': 8,
                'max_participants': 8
            },
            {
                'name': 'Gorilla Habituation Experience',
                'description': 'Extended 4-hour experience with a gorilla family being habituated for tourism. Maximum 4 people per group.',
                'price': Decimal('1500.00'),
                'duration_hours': 8,
                'max_participants': 4
            }
        ]
        
        for tour_data in bwindi_tours:
            tour = Tour.objects.create(park=bwindi, **tour_data)
            tours.append(tour)
        
        # Queen Elizabeth tours
        qenp = parks[1]
        qenp_tours = [
            {
                'name': 'Kazinga Channel Boat Safari',
                'description': 'Boat cruise on the Kazinga Channel to see hippos, elephants, buffaloes, and water birds.',
                'price': Decimal('60.00'),
                'duration_hours': 3,
                'max_participants': 30
            },
            {
                'name': 'Tree-Climbing Lions Safari',
                'description': 'Game drive in Ishasha sector to see the famous tree-climbing lions and other wildlife.',
                'price': Decimal('120.00'),
                'duration_hours': 6,
                'max_participants': 12
            }
        ]
        
        for tour_data in qenp_tours:
            tour = Tour.objects.create(park=qenp, **tour_data)
            tours.append(tour)
        
        # Murchison Falls tours
        mfnp = parks[2]
        mfnp_tours = [
            {
                'name': 'Murchison Falls Boat Safari',
                'description': 'Boat trip to the base of Murchison Falls with wildlife viewing along the Nile.',
                'price': Decimal('75.00'),
                'duration_hours': 4,
                'max_participants': 25
            },
            {
                'name': 'Big 5 Game Drive',
                'description': 'Full day game drive searching for lions, elephants, buffaloes, leopards, and rhinos.',
                'price': Decimal('150.00'),
                'duration_hours': 8,
                'max_participants': 10
            }
        ]
        
        for tour_data in mfnp_tours:
            tour = Tour.objects.create(park=mfnp, **tour_data)
            tours.append(tour)
        
        # Kibale tours
        kibale = parks[3]
        kibale_tours = [
            {
                'name': 'Chimpanzee Trekking',
                'description': 'Track habituated chimpanzees in Kibale Forest with experienced guides.',
                'price': Decimal('250.00'),
                'duration_hours': 4,
                'max_participants': 12
            },
            {
                'name': 'Primate Walk',
                'description': 'Guided walk to spot 13 primate species including red colobus and L\'Hoest\'s monkeys.',
                'price': Decimal('80.00'),
                'duration_hours': 3,
                'max_participants': 15
            }
        ]
        
        for tour_data in kibale_tours:
            tour = Tour.objects.create(park=kibale, **tour_data)
            tours.append(tour)
        
        # Lake Mburo tours
        mburo = parks[4]
        mburo_tours = [
            {
                'name': 'Zebra Safari Walk',
                'description': 'Walking safari to see zebras, impalas, and various antelope species.',
                'price': Decimal('40.00'),
                'duration_hours': 3,
                'max_participants': 8
            },
            {
                'name': 'Lake Mburo Boat Safari',
                'description': 'Boat trip on Lake Mburo to see hippos, crocodiles, and water birds.',
                'price': Decimal('50.00'),
                'duration_hours': 2,
                'max_participants': 20
            }
        ]
        
        for tour_data in mburo_tours:
            tour = Tour.objects.create(park=mburo, **tour_data)
            tours.append(tour)
        
        return tours

    def create_availabilities(self, tours, guides):
        """Create availability schedules for the next 3 months"""
        availabilities = []
        start_date = timezone.now().date()
        
        for tour in tours:
            # Create availability for next 90 days with some gaps
            for i in range(90):
                date = start_date + timedelta(days=i)
                
                # Skip some days randomly to make it realistic
                if random.choice([True, False, False]):  # 33% chance of no availability
                    continue
                
                # Assign random guide
                guide = random.choice(guides) if guides else None
                
                # Set realistic slot availability based on tour capacity
                max_slots = min(tour.max_participants, random.randint(4, tour.max_participants))
                available_slots = random.randint(0, max_slots)
                
                availability = Availability.objects.create(
                    tour=tour,
                    date=date,
                    slots_available=available_slots,
                    guide=guide
                )
                availabilities.append(availability)
        
        return availabilities

    def create_bookings(self, users, availabilities):
        """Create realistic bookings from tourists only if no bookings exist"""
        if Booking.objects.exists():
            self.stdout.write('Bookings already exist, skipping booking creation')
            return list(Booking.objects.all())
        
        self.stdout.write('Creating bookings...')
        bookings = []
        tourists = [user for user in users if hasattr(user, 'profile') and user.profile.role == 'tourist']
        
        if not tourists:
            self.stdout.write('No tourists found, skipping booking creation')
            return bookings
        
        # Create bookings for the past 2 months and next month
        booking_start_date = timezone.now().date() - timedelta(days=60)
        
        for _ in range(50):  # Create 50 bookings
            tourist = random.choice(tourists)
            
            # Choose availability (mix of past and future)
            availability = random.choice(availabilities)
            
            # Skip if no slots available
            if availability.slots_available <= 0:
                continue
            
            # Random number of people (1-4 for most bookings)
            num_people = random.choices([1, 2, 3, 4, 5, 6], weights=[30, 40, 15, 10, 3, 2])[0]
            num_people = min(num_people, availability.slots_available)
            
            # Random booking status
            if availability.date < timezone.now().date():
                # Past bookings - mostly completed
                booking_status = random.choices(
                    ['completed', 'cancelled'], 
                    weights=[80, 20]
                )[0]
            else:
                # Future bookings - mix of confirmed and pending
                booking_status = random.choices(
                    ['confirmed', 'pending', 'cancelled'], 
                    weights=[60, 30, 10]
                )[0]
            
            # Payment status based on booking status
            if booking_status == 'completed':
                payment_status = 'completed'
            elif booking_status == 'confirmed':
                payment_status = random.choices(['completed', 'processing'], weights=[90, 10])[0]
            elif booking_status == 'cancelled':
                payment_status = random.choices(['refunded', 'failed'], weights=[70, 30])[0]
            else:  # pending
                payment_status = 'pending'
            
            # Create booking with realistic timestamps
            booking_date = availability.date - timedelta(days=random.randint(1, 30))
            if booking_date < timezone.now().date() - timedelta(days=60):
                booking_date = timezone.now().date() - timedelta(days=random.randint(1, 60))
            
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
                special_requirements=random.choice(['', '', '', 'Vegetarian meals', 'Need wheelchair access', 'Dietary restrictions'])
            )
            
            # Set confirmed/cancelled timestamps if applicable
            if booking_status in ['confirmed', 'completed']:
                booking.confirmed_at = booking.booking_date + timedelta(hours=random.randint(1, 48))
            elif booking_status == 'cancelled':
                booking.cancelled_at = booking.booking_date + timedelta(hours=random.randint(1, 168))
            
            booking.save()
            
            # Reduce availability slots for confirmed bookings
            if booking_status in ['confirmed', 'completed']:
                availability.slots_available = max(0, availability.slots_available - num_people)
                availability.save()
            
            bookings.append(booking)
        
        return bookings

    def create_payments(self, bookings):
        """Create payment records for bookings only if no payments exist"""
        if Payment.objects.exists():
            self.stdout.write('Payments already exist, skipping payment creation')
            return list(Payment.objects.all())
        
        self.stdout.write('Creating payments...')
        payments = []
        
        payment_methods = ['credit_card', 'paypal', 'bank_transfer', 'mobile_money']
        
        for booking in bookings:
            if booking.payment_status != 'pending':
                # Determine payment status based on booking
                if booking.payment_status == 'completed':
                    status = 'completed'
                elif booking.payment_status == 'processing':
                    status = 'processing'
                elif booking.payment_status == 'refunded':
                    status = 'refunded'
                else:
                    status = 'failed'
                
                payment = Payment.objects.create(
                    booking=booking,
                    amount=booking.total_cost,
                    currency='USD',
                    payment_method=random.choice(payment_methods),
                    status=status,
                    gateway_transaction_id=f'txn_{uuid.uuid4().hex[:12]}',
                    gateway_reference=f'ref_{uuid.uuid4().hex[:8]}',
                    gateway_response={'status': 'success', 'message': 'Payment processed successfully'}
                )
                
                # Set completion timestamp for completed payments
                if status == 'completed':
                    payment.completed_at = booking.booking_date + timedelta(hours=random.randint(1, 24))
                    payment.save()
                
                payments.append(payment)
        
        return payments

    def create_notifications(self, bookings):
        """Create notification records for bookings only if no notifications exist"""
        if BookingNotification.objects.exists():
            self.stdout.write('Notifications already exist, skipping notification creation')
            return list(BookingNotification.objects.all())
        
        self.stdout.write('Creating notifications...')
        notifications = []
        
        notification_types = ['booking_confirmation', 'payment_received', 'tour_reminder', 'booking_cancelled']
        
        for booking in bookings:
            # Create 1-3 notifications per booking
            for _ in range(random.randint(1, 3)):
                notification_type = random.choice(notification_types)
                
                # Ensure notification type makes sense for booking status
                if booking.booking_status == 'cancelled' and notification_type != 'booking_cancelled':
                    notification_type = 'booking_cancelled'
                elif booking.booking_status == 'pending' and notification_type == 'payment_received':
                    notification_type = 'booking_confirmation'
                
                notification = BookingNotification.objects.create(
                    booking=booking,
                    notification_type=notification_type,
                    method=random.choice(['email', 'sms']),
                    subject=f'{notification_type.replace("_", " ").title()} - {booking.reference_code}',
                    message=f'This is a {notification_type.replace("_", " ")} notification for booking {booking.reference_code}.',
                    sent_at=booking.booking_date + timedelta(hours=random.randint(1, 48)),
                    delivered=random.choices([True, False], weights=[95, 5])[0],
                    delivery_attempts=random.randint(1, 3)
                )
                notifications.append(notification)
        
        return notifications
