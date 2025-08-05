from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import random

from tours.models import Park, Tour, Guide
from booking.models import Availability
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Populate the database with real UWA (Uganda Wildlife Authority) data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting UWA data population...'))
        
        # Create Parks (Uganda's National Parks)
        self.create_parks()
        
        # Create Guides
        self.create_guides()
        
        # Create Tours
        self.create_tours()
        
        # Create Availabilities
        self.create_availabilities()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database with UWA data!'))

    def create_parks(self):
        """Create Uganda's 10 National Parks"""
        parks_data = [
            {
                'name': 'Bwindi Impenetrable National Park',
                'location': 'Southwestern Uganda',
                'description': 'Home to more than half of the world\'s mountain gorillas (over 500 individuals). This UNESCO World Heritage Site is one of the most biologically diverse areas on earth with over 200 tree species, 100 fern species, and 350 bird species. Famous for gorilla trekking experiences.'
            },
            {
                'name': 'Queen Elizabeth National Park',
                'location': 'Western Uganda',
                'description': 'Uganda\'s most popular tourist destination and most visited national park. Famous for its wildlife diversity including elephants, hippos, crocodiles, and the unique tree-climbing lions of Ishasha. The park spans the equator with diverse ecosystems including savanna, wetlands, and forests.'
            },
            {
                'name': 'Murchison Falls National Park',
                'location': 'Northwestern Uganda',
                'description': 'Uganda\'s largest national park, famous for the spectacular Murchison Falls where the Nile River crashes through a narrow gorge. Home to over 76 mammal species including elephants, giraffes, lions, leopards, and over 450 bird species. Offers excellent game drives and boat safaris.'
            },
            {
                'name': 'Kibale National Park',
                'location': 'Western Uganda',
                'description': 'Known as the "Primate Capital of the World" with the highest concentration of primates in East Africa. Home to over 1,500 chimpanzees and 13 primate species. The park protects a tropical rainforest ecosystem and offers the best chimpanzee tracking experience in Uganda.'
            },
            {
                'name': 'Kidepo Valley National Park',
                'location': 'Northeastern Uganda',
                'description': 'Uganda\'s most isolated and spectacular wilderness area. Known for its rugged landscapes, semi-arid climate, and unique wildlife including cheetahs, bat-eared foxes, and over 475 bird species. Offers authentic African wilderness experience with minimal crowds.'
            },
            {
                'name': 'Lake Mburo National Park',
                'location': 'Western Uganda',
                'description': 'Uganda\'s smallest national park but rich in biodiversity. The only park in Uganda where you can see zebras and impalas. Famous for boat rides on Lake Mburo, walking safaris, and night game drives. Home to over 350 bird species and various antelope species.'
            },
            {
                'name': 'Mount Elgon National Park',
                'location': 'Eastern Uganda',
                'description': 'Home to Mount Elgon, an extinct volcanic mountain with the largest caldera in the world. Famous for its elephant caves, waterfalls, and diverse vegetation zones. Offers excellent hiking, mountaineering, and cultural experiences with the Bagisu people.'
            },
            {
                'name': 'Rwenzori Mountains National Park',
                'location': 'Western Uganda',
                'description': 'The "Mountains of the Moon" - a UNESCO World Heritage Site with Africa\'s third highest peak. Known for its unique alpine vegetation, glaciers, and challenging mountaineering routes. Home to endemic species and offers multi-day trekking experiences.'
            },
            {
                'name': 'Semuliki National Park',
                'location': 'Western Uganda',
                'description': 'Uganda\'s newest national park, part of the Congo Basin forest. Famous for its hot springs, diverse birdlife (over 440 species), and being home to Central African wildlife species not found elsewhere in East Africa. Offers unique forest and cultural experiences.'
            },
            {
                'name': 'Mgahinga Gorilla National Park',
                'location': 'Southwestern Uganda',
                'description': 'Part of the Virunga Conservation Area shared with Rwanda and DR Congo. Home to the Nyakagezi gorilla family and golden monkeys. The park covers three volcanic mountains and offers gorilla trekking, golden monkey tracking, and volcano climbing experiences.'
            }
        ]

        for park_data in parks_data:
            park, created = Park.objects.get_or_create(
                name=park_data['name'],
                defaults={
                    'location': park_data['location'],
                    'description': park_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created park: {park.name}')

    def create_guides(self):
        """Create realistic UWA guides"""
        guides_data = [
            {'username': 'samuel_mugisha', 'first_name': 'Samuel', 'last_name': 'Mugisha', 'specialization': 'Gorilla Trekking & Primates'},
            {'username': 'grace_nakato', 'first_name': 'Grace', 'last_name': 'Nakato', 'specialization': 'Bird Watching & Wildlife Photography'},
            {'username': 'david_kato', 'first_name': 'David', 'last_name': 'Kato', 'specialization': 'Big Game Safari & Conservation'},
            {'username': 'margaret_asiimwe', 'first_name': 'Margaret', 'last_name': 'Asiimwe', 'specialization': 'Chimpanzee Tracking & Forest Ecology'},
            {'username': 'peter_tumwine', 'first_name': 'Peter', 'last_name': 'Tumwine', 'specialization': 'Cultural Tourism & Community Engagement'},
            {'username': 'ruth_namubiru', 'first_name': 'Ruth', 'last_name': 'Namubiru', 'specialization': 'Mountaineering & Adventure Tourism'},
            {'username': 'john_ssempala', 'first_name': 'John', 'last_name': 'Ssempala', 'specialization': 'Boat Safaris & Aquatic Wildlife'},
            {'username': 'anne_kyomugisha', 'first_name': 'Anne', 'last_name': 'Kyomugisha', 'specialization': 'Night Game Drives & Nocturnal Wildlife'},
        ]

        for guide_data in guides_data:
            # Create user if doesn't exist
            user, created = User.objects.get_or_create(
                username=guide_data['username'],
                defaults={
                    'first_name': guide_data['first_name'],
                    'last_name': guide_data['last_name'],
                    'email': f"{guide_data['username']}@wildlife.go.ug",
                    'is_staff': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                # Create profile
                profile, _ = Profile.objects.get_or_create(
                    user=user,
                    defaults={'role': 'guide'}
                )
                
                # Create guide
                guide, guide_created = Guide.objects.get_or_create(
                    user=user,
                    defaults={'specialization': guide_data['specialization']}
                )
                
                if guide_created:
                    self.stdout.write(f'Created guide: {user.get_full_name()} - {guide.specialization}')

    def create_tours(self):
        """Create authentic UWA tours based on real activities"""
        tours_data = [
            # Bwindi Impenetrable National Park
            {
                'park': 'Bwindi Impenetrable National Park',
                'name': 'Mountain Gorilla Trekking Experience',
                'description': 'An unforgettable encounter with mountain gorillas in their natural habitat. Trek through the impenetrable forest with experienced guides to spend one magical hour with a habituated gorilla family. This life-changing experience includes a briefing, guided trek, and gorilla certificate.',
                'price': 700.00,  # Based on UWA gorilla permit pricing
                'duration_hours': 8,
                'max_participants': 8
            },
            {
                'park': 'Bwindi Impenetrable National Park',
                'name': 'Gorilla Habituation Experience',
                'description': 'Spend 4 hours with researchers and trackers observing gorillas being habituated to human presence. This exclusive experience offers deeper insights into gorilla behavior and conservation efforts. Limited to 4 people per day.',
                'price': 1500.00,  # Premium gorilla habituation experience
                'duration_hours': 10,
                'max_participants': 4
            },
            {
                'park': 'Bwindi Impenetrable National Park',
                'name': 'Batwa Cultural Trail',
                'description': 'Experience the rich culture of the Batwa people, the original forest dwellers. Learn traditional hunting techniques, medicinal plants, and folklore from the "Keepers of the Forest." Includes cultural performances and community visit.',
                'price': 30.00,
                'duration_hours': 4,
                'max_participants': 15
            },
            
            # Queen Elizabeth National Park
            {
                'park': 'Queen Elizabeth National Park',
                'name': 'Classic Game Drive Safari',
                'description': 'Explore the diverse wildlife of Queen Elizabeth National Park including elephants, buffaloes, lions, leopards, and various antelope species. Early morning or evening drives offer the best wildlife viewing opportunities.',
                'price': 60.00,
                'duration_hours': 4,
                'max_participants': 6
            },
            {
                'park': 'Queen Elizabeth National Park',
                'name': 'Ishasha Tree-Climbing Lions Experience',
                'description': 'Search for the famous tree-climbing lions in the Ishasha sector. These unique lions are known for their unusual behavior of climbing fig trees. Includes game drive and expert guide commentary.',
                'price': 80.00,
                'duration_hours': 6,
                'max_participants': 6
            },
            {
                'park': 'Queen Elizabeth National Park',
                'name': 'Kazinga Channel Boat Safari',
                'description': 'Cruise along the Kazinga Channel connecting Lake Edward and Lake George. Observe hippos, crocodiles, elephants, and over 100 bird species along the waterway. Perfect for photography enthusiasts.',
                'price': 35.00,
                'duration_hours': 2,
                'max_participants': 20
            },
            
            # Murchison Falls National Park
            {
                'park': 'Murchison Falls National Park',
                'name': 'Murchison Falls Boat Safari',
                'description': 'Navigate the Nile River to the base of the spectacular Murchison Falls. Spot hippos, crocodiles, elephants, and numerous bird species. The boat ride culminates at the bottom of the powerful falls.',
                'price': 40.00,
                'duration_hours': 3,
                'max_participants': 25
            },
            {
                'park': 'Murchison Falls National Park',
                'name': 'Big Game Safari Drive',
                'description': 'Experience the best of African wildlife in Uganda\'s largest national park. Search for lions, leopards, elephants, giraffes, and buffaloes across the vast savannah plains.',
                'price': 65.00,
                'duration_hours': 4,
                'max_participants': 6
            },
            {
                'park': 'Murchison Falls National Park',
                'name': 'Top of the Falls Hike',
                'description': 'Hike to the top of Murchison Falls where the Nile River crashes through a narrow 7-meter gorge. Experience the power and mist of one of the world\'s most powerful waterfalls.',
                'price': 25.00,
                'duration_hours': 2,
                'max_participants': 12
            },
            
            # Kibale National Park
            {
                'park': 'Kibale National Park',
                'name': 'Chimpanzee Tracking Adventure',
                'description': 'Track our closest relatives in the tropical rainforest. Kibale has the highest concentration of primates in East Africa with over 1,500 chimpanzees. Includes forest walk and primate education.',
                'price': 200.00,
                'duration_hours': 4,
                'max_participants': 8
            },
            {
                'park': 'Kibale National Park',
                'name': 'Chimpanzee Habituation Experience',
                'description': 'Spend a full day with researchers following chimpanzees from their morning nest to evening rest. This intensive experience offers unique insights into chimpanzee behavior and social structures.',
                'price': 250.00,
                'duration_hours': 10,
                'max_participants': 4
            },
            {
                'park': 'Kibale National Park',
                'name': 'Bigodi Wetland Sanctuary Walk',
                'description': 'Explore the community-managed Bigodi Wetland Sanctuary. Spot over 200 bird species, primates, and other wildlife while supporting local conservation efforts.',
                'price': 25.00,
                'duration_hours': 3,
                'max_participants': 10
            },
            
            # Kidepo Valley National Park
            {
                'park': 'Kidepo Valley National Park',
                'name': 'Wilderness Game Drive',
                'description': 'Experience true African wilderness in Uganda\'s most remote park. Encounter unique species like cheetahs, bat-eared foxes, and ostriches in dramatic landscapes.',
                'price': 70.00,
                'duration_hours': 4,
                'max_participants': 6
            },
            {
                'park': 'Kidepo Valley National Park',
                'name': 'Karamojong Cultural Experience',
                'description': 'Visit traditional Karamojong homesteads and learn about one of Uganda\'s most traditional pastoralist cultures. Includes cultural performances and traditional meals.',
                'price': 40.00,
                'duration_hours': 5,
                'max_participants': 12
            },
            
            # Lake Mburo National Park
            {
                'park': 'Lake Mburo National Park',
                'name': 'Walking Safari Adventure',
                'description': 'Experience Uganda\'s only walking safari in Lake Mburo National Park. Get up close with zebras, impalas, and other wildlife on foot with an armed ranger guide.',
                'price': 35.00,
                'duration_hours': 3,
                'max_participants': 8
            },
            {
                'park': 'Lake Mburo National Park',
                'name': 'Lake Mburo Boat Safari',
                'description': 'Cruise on Lake Mburo spotting hippos, crocodiles, and diverse water birds. The boat safari offers unique perspectives of the park\'s aquatic wildlife.',
                'price': 30.00,
                'duration_hours': 2,
                'max_participants': 15
            },
            
            # Mount Elgon National Park
            {
                'park': 'Mount Elgon National Park',
                'name': 'Sipi Falls Hiking Experience',
                'description': 'Hike to the spectacular three-tier Sipi Falls cascading down Mount Elgon. Experience coffee plantations, local culture, and breathtaking mountain scenery.',
                'price': 45.00,
                'duration_hours': 6,
                'max_participants': 10
            },
            {
                'park': 'Mount Elgon National Park',
                'name': 'Elephant Cave Exploration',
                'description': 'Explore the famous Kitum Cave where elephants come to mine salt. Learn about this unique behavior and the geological significance of Mount Elgon\'s caves.',
                'price': 55.00,
                'duration_hours': 5,
                'max_participants': 8
            }
        ]

        for tour_data in tours_data:
            park = Park.objects.get(name=tour_data['park'])
            tour, created = Tour.objects.get_or_create(
                name=tour_data['name'],
                park=park,
                defaults={
                    'description': tour_data['description'],
                    'price': Decimal(str(tour_data['price'])),
                    'duration_hours': tour_data['duration_hours'],
                    'max_participants': tour_data['max_participants']
                }
            )
            if created:
                self.stdout.write(f'Created tour: {tour.name} in {park.name}')

    def create_availabilities(self):
        """Create availability schedules for tours"""
        tours = Tour.objects.all()
        guides = Guide.objects.all()
        
        if not guides.exists():
            self.stdout.write(self.style.WARNING('No guides found. Skipping availability creation.'))
            return
        
        # Create availabilities for the next 3 months
        start_date = timezone.now().date()
        
        for tour in tours:
            # Create availabilities for different patterns based on tour type
            if 'Gorilla' in tour.name:
                # Gorilla tracking - daily except Sundays (limited slots)
                self.create_tour_availability(tour, start_date, exclude_days=[6], slots_range=(6, 8), frequency=1)
            elif 'Chimpanzee' in tour.name:
                # Chimpanzee tracking - daily
                self.create_tour_availability(tour, start_date, exclude_days=[], slots_range=(6, 8), frequency=1)
            elif 'Cultural' in tour.name or 'Batwa' in tour.name:
                # Cultural tours - flexible scheduling
                self.create_tour_availability(tour, start_date, exclude_days=[], slots_range=(10, 15), frequency=2)
            elif 'Boat' in tour.name:
                # Boat safaris - twice daily
                self.create_tour_availability(tour, start_date, exclude_days=[], slots_range=(15, 25), frequency=1)
            else:
                # Regular game drives and walks
                self.create_tour_availability(tour, start_date, exclude_days=[], slots_range=(4, 6), frequency=1)

    def create_tour_availability(self, tour, start_date, exclude_days, slots_range, frequency):
        """Create availability for a specific tour"""
        guides = list(Guide.objects.all())
        
        for day_offset in range(0, 90, frequency):  # Next 3 months
            availability_date = start_date + timedelta(days=day_offset)
            
            # Skip excluded days (e.g., Sundays for gorilla tracking)
            if availability_date.weekday() in exclude_days:
                continue
            
            # Random slots within range
            slots = random.randint(slots_range[0], slots_range[1])
            
            # Assign random guide
            guide = random.choice(guides) if guides else None
            
            availability, created = Availability.objects.get_or_create(
                tour=tour,
                date=availability_date,
                defaults={
                    'slots_available': slots,
                    'guide': guide
                }
            )
            
            if created and day_offset % 10 == 0:  # Log every 10th creation
                self.stdout.write(f'Created availability: {tour.name} on {availability_date} ({slots} slots)')
