from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from tours.models import Park, Guide, Tour
from accounts.models import Profile
from booking.models import Availability, Booking


class Command(BaseCommand):
    help = 'Populate database with realistic Australian wildlife tour data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Creating realistic wildlife tour data...'))
        
        # Create data in order of dependencies
        self.create_parks()
        self.create_users_and_guides()
        self.create_tours()
        self.create_availabilities()
        self.create_bookings()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database with realistic data!'))

    def clear_data(self):
        """Clear existing data"""
        Booking.objects.all().delete()
        Availability.objects.all().delete()
        Tour.objects.all().delete()
        Guide.objects.all().delete()
        Park.objects.all().delete()
        # Keep superuser, but clear other users
        User.objects.filter(is_superuser=False).delete()

    def create_parks(self):
        """Create Australian wildlife parks"""
        parks_data = [
            {
                'name': 'Kakadu National Park',
                'description': 'Australia\'s largest national park, home to saltwater crocodiles, diverse bird species, and Aboriginal rock art spanning 65,000 years. Experience wetlands, woodlands, and dramatic escarpments.',
                'location': 'Northern Territory, Australia'
            },
            {
                'name': 'Kangaroo Island',
                'description': 'A pristine island sanctuary off South Australia\'s coast, featuring native wildlife in their natural habitat including kangaroos, koalas, echidnas, and diverse marine life.',
                'location': 'South Australia, Australia'
            },
            {
                'name': 'Daintree Rainforest',
                'description': 'The world\'s oldest surviving rainforest, home to cassowaries, tree kangaroos, and countless endemic species. A UNESCO World Heritage site of incredible biodiversity.',
                'location': 'Queensland, Australia'
            },
            {
                'name': 'Grampians National Park',
                'description': 'Rugged mountain ranges and diverse ecosystems supporting kangaroos, wallabies, koalas, and over 200 bird species. Famous for spectacular wildflower displays.',
                'location': 'Victoria, Australia'
            },
            {
                'name': 'Ningaloo Marine Park',
                'description': 'World Heritage-listed marine sanctuary where you can swim with whale sharks, manta rays, and explore pristine coral reefs teeming with tropical marine life.',
                'location': 'Western Australia, Australia'
            },
            {
                'name': 'Tasmania Devil Sanctuary',
                'description': 'Dedicated conservation facility protecting Tasmania\'s iconic devils, quolls, and wombats. Learn about conservation efforts while observing these unique marsupials.',
                'location': 'Tasmania, Australia'
            }
        ]

        for park_data in parks_data:
            park, created = Park.objects.get_or_create(
                name=park_data['name'],
                defaults=park_data
            )
            if created:
                self.stdout.write(f'Created park: {park.name}')

    def create_users_and_guides(self):
        """Create realistic guide users with Australian names"""
        guides_data = [
            {
                'username': 'sarah_wildlife',
                'first_name': 'Sarah',
                'last_name': 'Mitchell',
                'email': 'sarah.mitchell@uwatours.com.au',
                'specialization': 'Marine Wildlife & Coral Reef Ecosystems',
                'bio': 'Marine biologist with 12 years of experience guiding snorkeling and diving tours. Passionate about coral reef conservation and marine mammal behavior.'
            },
            {
                'username': 'james_outback',
                'first_name': 'James',
                'last_name': 'Thompson',
                'email': 'james.thompson@uwatours.com.au',
                'specialization': 'Desert Wildlife & Reptile Specialist',
                'bio': 'Outback guide specializing in desert ecosystems and reptile behavior. Expert tracker with indigenous knowledge of central Australian wildlife.'
            },
            {
                'username': 'emma_birds',
                'first_name': 'Emma',
                'last_name': 'Rodriguez',
                'email': 'emma.rodriguez@uwatours.com.au',
                'specialization': 'Ornithology & Rainforest Ecosystems',
                'bio': 'Certified ornithologist and rainforest specialist. Leads birding expeditions and rainforest canopy tours across tropical Queensland.'
            },
            {
                'username': 'michael_marine',
                'first_name': 'Michael',
                'last_name': 'Chang',
                'email': 'michael.chang@uwatours.com.au',
                'specialization': 'Whale Migration & Marine Mammals',
                'bio': 'Marine mammal researcher turned guide. Specializes in whale watching tours and marine conservation education programs.'
            },
            {
                'username': 'lucy_conservation',
                'first_name': 'Lucy',
                'last_name': 'Aboriginal',
                'email': 'lucy.aboriginal@uwatours.com.au',
                'specialization': 'Indigenous Wildlife Knowledge & Conservation',
                'bio': 'Indigenous guide sharing traditional knowledge of wildlife behavior and conservation practices passed down through generations.'
            },
            {
                'username': 'david_photography',
                'first_name': 'David',
                'last_name': 'Wilson',
                'email': 'david.wilson@uwatours.com.au',
                'specialization': 'Wildlife Photography & Nocturnal Animals',
                'bio': 'Professional wildlife photographer and night tour specialist. Expert in animal behavior and ethical wildlife photography techniques.'
            },
            {
                'username': 'rachel_primates',
                'first_name': 'Rachel',
                'last_name': 'Foster',
                'email': 'rachel.foster@uwatours.com.au',
                'specialization': 'Primates & Arboreal Wildlife',
                'bio': 'Primatologist specializing in tree-dwelling marsupials and rainforest canopy ecosystems. Leads treetop adventure tours.'
            },
            {
                'username': 'alex_tracking',
                'first_name': 'Alex',
                'last_name': 'Indigenous',
                'email': 'alex.indigenous@uwatours.com.au',
                'specialization': 'Animal Tracking & Bushcraft',
                'bio': 'Traditional tracker and bushcraft expert. Teaches wildlife tracking skills and shares indigenous perspectives on animal behavior.'
            }
        ]

        # Create regular tourists
        tourist_data = [
            ('john_tourist', 'John', 'Smith', 'john.smith@email.com'),
            ('mary_explorer', 'Mary', 'Johnson', 'mary.johnson@email.com'),
            ('peter_nature', 'Peter', 'Williams', 'peter.williams@email.com'),
            ('susan_adventure', 'Susan', 'Brown', 'susan.brown@email.com'),
            ('robert_wildlife', 'Robert', 'Davis', 'robert.davis@email.com'),
            ('jennifer_travel', 'Jennifer', 'Miller', 'jennifer.miller@email.com'),
            ('william_photo', 'William', 'Wilson', 'william.wilson@email.com'),
            ('elizabeth_nature', 'Elizabeth', 'Moore', 'elizabeth.moore@email.com'),
        ]

        # Create guide users
        for guide_data in guides_data:
            user, created = User.objects.get_or_create(
                username=guide_data['username'],
                defaults={
                    'first_name': guide_data['first_name'],
                    'last_name': guide_data['last_name'],
                    'email': guide_data['email'],
                    'is_staff': True,  # Guides can access admin for their tours
                }
            )
            if created:
                user.set_password('guidepass123')
                user.save()
                
                # Create guide profile
                guide, guide_created = Guide.objects.get_or_create(
                    user=user,
                    defaults={'specialization': guide_data['specialization']}
                )
                
                # Create or update profile
                profile, profile_created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': 'guide',
                        'bio': guide_data['bio'],
                        'phone_number': f'+61 4{random.randint(10000000, 99999999)}'
                    }
                )
                
                self.stdout.write(f'Created guide: {user.get_full_name()}')

        # Create tourist users
        for username, first_name, last_name, email in tourist_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                }
            )
            if created:
                user.set_password('tourist123')
                user.save()
                
                # Create tourist profile
                profile, profile_created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': 'tourist',
                        'phone_number': f'+61 4{random.randint(10000000, 99999999)}'
                    }
                )
                
                self.stdout.write(f'Created tourist: {user.get_full_name()}')

    def create_tours(self):
        """Create realistic wildlife tours for each park"""
        tours_data = [
            # Kakadu National Park
            {
                'park': 'Kakadu National Park',
                'tours': [
                    {
                        'name': 'Crocodile Spotting Safari',
                        'description': 'Navigate the wetlands of Kakadu in search of massive saltwater crocodiles. Learn about their behavior, habitat, and conservation while observing these prehistoric predators from a safe distance.',
                        'price': Decimal('185.00'),
                        'duration_hours': 4,
                        'max_participants': 8
                    },
                    {
                        'name': 'Aboriginal Rock Art & Wildlife Walk',
                        'description': 'Combine cultural heritage with wildlife observation. Explore ancient rock art sites while spotting native birds, wallabies, and learning traditional wildlife knowledge.',
                        'price': Decimal('145.00'),
                        'duration_hours': 6,
                        'max_participants': 12
                    },
                    {
                        'name': 'Wetlands Bird Watching Tour',
                        'description': 'Dawn birding expedition through Kakadu\'s diverse wetlands. Spot jabirus, brolgas, magpie geese, and dozens of other waterbird species in their natural habitat.',
                        'price': Decimal('125.00'),
                        'duration_hours': 5,
                        'max_participants': 10
                    }
                ]
            },
            # Kangaroo Island
            {
                'park': 'Kangaroo Island',
                'tours': [
                    {
                        'name': 'Kangaroo & Koala Encounter',
                        'description': 'Meet Australia\'s most iconic marsupials in their natural habitat. Observe kangaroos grazing at sunset and spot koalas sleeping in eucalyptus trees.',
                        'price': Decimal('165.00'),
                        'duration_hours': 4,
                        'max_participants': 15
                    },
                    {
                        'name': 'Echidna Trail Adventure',
                        'description': 'Track one of the world\'s only egg-laying mammals through native bushland. Learn about echidna behavior and the unique ecosystem of Kangaroo Island.',
                        'price': Decimal('135.00'),
                        'duration_hours': 3,
                        'max_participants': 8
                    },
                    {
                        'name': 'Seal Bay Conservation Experience',
                        'description': 'Walk among wild Australian sea lions at Seal Bay. Observe mothers with pups, learn about marine mammal conservation, and witness their natural behaviors.',
                        'price': Decimal('195.00'),
                        'duration_hours': 3,
                        'max_participants': 20
                    }
                ]
            },
            # Daintree Rainforest
            {
                'park': 'Daintree Rainforest',
                'tours': [
                    {
                        'name': 'Cassowary Tracking Expedition',
                        'description': 'Search for the elusive southern cassowary in the world\'s oldest rainforest. Learn about this critically important keystone species and rainforest conservation.',
                        'price': Decimal('225.00'),
                        'duration_hours': 6,
                        'max_participants': 6
                    },
                    {
                        'name': 'Tree Kangaroo Discovery Tour',
                        'description': 'Look up into the rainforest canopy to spot rare Lumholtz\'s tree kangaroos. Experience the vertical rainforest ecosystem and its unique inhabitants.',
                        'price': Decimal('185.00'),
                        'duration_hours': 4,
                        'max_participants': 8
                    },
                    {
                        'name': 'Night Rainforest Safari',
                        'description': 'Discover the rainforest after dark when nocturnal animals become active. Spot possums, gliders, frogs, and insects using specialized night vision equipment.',
                        'price': Decimal('175.00'),
                        'duration_hours': 3,
                        'max_participants': 10
                    }
                ]
            },
            # Grampians National Park
            {
                'park': 'Grampians National Park',
                'tours': [
                    {
                        'name': 'Wallaby Valley Sunrise Tour',
                        'description': 'Experience the magic of sunrise in Wallaby Valley as these gentle marsupials emerge to feed. Perfect photography opportunities in golden morning light.',
                        'price': Decimal('155.00'),
                        'duration_hours': 4,
                        'max_participants': 12
                    },
                    {
                        'name': 'Koala Spotting & Wildflower Walk',
                        'description': 'Combine wildlife watching with spectacular wildflower displays (seasonal). Search for koalas in their favorite eucalyptus trees while exploring colorful heath lands.',
                        'price': Decimal('145.00'),
                        'duration_hours': 5,
                        'max_participants': 15
                    },
                    {
                        'name': 'Birds of Prey Experience',
                        'description': 'Observe wedge-tailed eagles, peregrine falcons, and other raptors soaring above the Grampians ranges. Learn about predator-prey relationships and bird behavior.',
                        'price': Decimal('165.00'),
                        'duration_hours': 4,
                        'max_participants': 10
                    }
                ]
            },
            # Ningaloo Marine Park
            {
                'park': 'Ningaloo Marine Park',
                'tours': [
                    {
                        'name': 'Whale Shark Swimming Adventure',
                        'description': 'Swim alongside the world\'s largest fish in pristine Ningaloo waters. A once-in-a-lifetime experience with these gentle giants (seasonal March-July).',
                        'price': Decimal('395.00'),
                        'duration_hours': 8,
                        'max_participants': 10
                    },
                    {
                        'name': 'Manta Ray Encounter',
                        'description': 'Snorkel with graceful manta rays at Coral Bay. Observe these intelligent giants feeding and learn about marine conservation efforts.',
                        'price': Decimal('285.00'),
                        'duration_hours': 6,
                        'max_participants': 12
                    },
                    {
                        'name': 'Coral Gardens Snorkel Tour',
                        'description': 'Explore vibrant coral gardens teeming with tropical fish, sea turtles, and rays. Perfect introduction to Ningaloo\'s incredible marine biodiversity.',
                        'price': Decimal('165.00'),
                        'duration_hours': 4,
                        'max_participants': 20
                    },
                    {
                        'name': 'Dugong Spotting Boat Tour',
                        'description': 'Search for shy dugongs grazing on seagrass beds. Learn about these endangered marine mammals and their critical habitat requirements.',
                        'price': Decimal('215.00'),
                        'duration_hours': 5,
                        'max_participants': 15
                    }
                ]
            },
            # Tasmania Devil Sanctuary
            {
                'park': 'Tasmania Devil Sanctuary',
                'tours': [
                    {
                        'name': 'Tasmania Devil Conservation Tour',
                        'description': 'Meet Tasmania devils up close and learn about critical conservation efforts to save this iconic species from extinction. Educational and inspiring.',
                        'price': Decimal('125.00'),
                        'duration_hours': 3,
                        'max_participants': 25
                    },
                    {
                        'name': 'Wombat Burrow Experience',
                        'description': 'Visit wombat territories and learn about their unique lifestyle. Observe these powerful diggers and understand their role in the ecosystem.',
                        'price': Decimal('115.00'),
                        'duration_hours': 2,
                        'max_participants': 20
                    },
                    {
                        'name': 'Quoll Night Spotting Tour',
                        'description': 'Search for endangered spotted-tail quolls during their active nighttime hours. Use spotlights and tracking techniques to observe these elusive predators.',
                        'price': Decimal('145.00'),
                        'duration_hours': 4,
                        'max_participants': 8
                    }
                ]
            }
        ]

        for park_data in tours_data:
            park = Park.objects.get(name=park_data['park'])
            for tour_data in park_data['tours']:
                tour, created = Tour.objects.get_or_create(
                    park=park,
                    name=tour_data['name'],
                    defaults=tour_data
                )
                if created:
                    self.stdout.write(f'Created tour: {tour.name}')

    def create_availabilities(self):
        """Create realistic availability schedules"""
        guides = list(Guide.objects.all())
        tours = list(Tour.objects.all())
        
        # Create availabilities for the next 90 days
        start_date = timezone.now().date()
        
        for tour in tours:
            # Each tour has different availability patterns
            if 'Whale Shark' in tour.name:
                # Seasonal tour (March-July) - only available certain months
                availability_days = [1, 3, 5]  # Mon, Wed, Fri
                slots_range = (6, 10)
            elif 'Night' in tour.name or 'Nocturnal' in tour.name:
                # Night tours - less frequent
                availability_days = [2, 4, 6]  # Tue, Thu, Sat
                slots_range = (4, 8)
            elif 'Marine' in tour.name or 'Coral' in tour.name:
                # Marine tours - weather dependent
                availability_days = [0, 1, 2, 3, 4, 5, 6]  # Daily but variable slots
                slots_range = (8, 15)
            else:
                # Land-based tours - regular schedule
                availability_days = [1, 2, 3, 4, 5, 6]  # Tue-Sun
                slots_range = (tour.max_participants // 2, tour.max_participants)
            
            # Create availabilities for next 90 days
            for i in range(90):
                date = start_date + timedelta(days=i)
                
                # Skip if not an availability day for this tour
                if date.weekday() not in availability_days:
                    continue
                
                # Random chance of no availability (maintenance, weather, etc.)
                if random.random() < 0.15:  # 15% chance of no availability
                    continue
                
                # Choose random guide
                guide = random.choice(guides)
                
                # Determine slots available
                base_slots = random.randint(*slots_range)
                
                # Simulate booking patterns - more bookings for popular tours and weekends
                popularity_factor = 1.0
                if 'Whale Shark' in tour.name or 'Cassowary' in tour.name:
                    popularity_factor = 1.5  # Popular tours
                
                if date.weekday() >= 5:  # Weekend
                    popularity_factor *= 1.3
                
                # Calculate how many slots are already "booked"
                booking_probability = min(0.8, 0.3 * popularity_factor)
                slots_to_book = int(base_slots * random.uniform(0, booking_probability))
                slots_available = max(0, base_slots - slots_to_book)
                
                # Create availability
                availability, created = Availability.objects.get_or_create(
                    tour=tour,
                    date=date,
                    defaults={
                        'slots_available': slots_available,
                        'guide': guide
                    }
                )
                
                if created:
                    self.stdout.write(f'Created availability: {tour.name} on {date} ({slots_available} slots)')

    def create_bookings(self):
        """Create realistic booking history"""
        tourists = list(User.objects.filter(profile__role='tourist'))
        
        # Get past availabilities (simulate that some slots were booked)
        availabilities = Availability.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=30),
            date__lt=timezone.now().date() + timedelta(days=60)
        )
        
        booking_statuses = ['confirmed', 'pending', 'completed']
        
        created_bookings = 0
        for availability in availabilities:
            # Calculate how many bookings this availability should have
            max_people = availability.tour.max_participants
            current_available = availability.slots_available
            booked_slots = max_people - current_available
            
            # Create bookings for the booked slots
            remaining_slots = booked_slots
            while remaining_slots > 0 and created_bookings < 150:  # Limit total bookings
                # Random group size (1-4 people typically)
                group_size = min(remaining_slots, random.randint(1, 4))
                
                # Choose random tourist
                tourist = random.choice(tourists)
                
                # Determine booking status based on date
                if availability.date < timezone.now().date():
                    status = 'completed'
                elif availability.date <= timezone.now().date() + timedelta(days=7):
                    status = random.choice(['confirmed', 'confirmed', 'pending'])
                else:
                    status = random.choice(['confirmed', 'pending'])
                
                # Create booking
                booking = Booking.objects.create(
                    tourist=tourist,
                    availability=availability,
                    num_of_people=group_size,
                    unit_price=availability.tour.price,
                    total_cost=availability.tour.price * group_size,
                    booking_status=status,
                    payment_status='completed' if status == 'completed' else 'pending',
                    contact_email=tourist.email,
                    contact_phone=tourist.profile.phone_number,
                    special_requirements=random.choice([
                        '', '', '',  # Most bookings have no special requirements
                        'Vegetarian meals please',
                        'Wheelchair accessible tour needed',
                        'First time snorkeling - extra guidance appreciated',
                        'Photography equipment - need extra time for shots',
                        'Celebrating anniversary - any special touches welcomed',
                        'Children in group - family friendly approach preferred'
                    ]),
                )
                
                # Set confirmation date for confirmed bookings
                if status in ['confirmed', 'completed']:
                    booking.confirmed_at = booking.booking_date + timedelta(hours=random.randint(1, 48))
                    booking.save()
                
                remaining_slots -= group_size
                created_bookings += 1
                
                if created_bookings % 10 == 0:
                    self.stdout.write(f'Created {created_bookings} bookings...')
        
        self.stdout.write(f'Created {created_bookings} realistic bookings')
