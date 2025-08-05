from django.core.management.base import BaseCommand
from tours.models import Tour, Park


class Command(BaseCommand):
    help = 'Force add placeholder images to all missing items'

    def handle(self, *args, **options):
        # Simple image assignments
        tour_images = {
            'Kazinga Channel Boat Safari': 'tours/boat_safari.jpg',
            'Chimpanzee Trekking': 'tours/chimp_trek.jpg', 
            'Primate Walk': 'tours/primate_walk.jpg',
            'Zebra Safari Walk': 'tours/zebra_walk.jpg'
        }
        
        park_images = {
            'Kibale National Park': 'parks/kibale.jpg',
            'Lake Mburo National Park': 'parks/lake_mburo.jpg'
        }
        
        # Update tours
        for tour in Tour.objects.all():
            if not tour.image:
                if tour.name in tour_images:
                    tour.image = tour_images[tour.name]
                else:
                    tour.image = 'tours/default_tour.jpg'
                tour.save()
                self.stdout.write(f'Added image path to tour: {tour.name}')
        
        # Update parks
        for park in Park.objects.all():
            if not park.image:
                if park.name in park_images:
                    park.image = park_images[park.name]
                else:
                    park.image = 'parks/default_park.jpg'
                park.save()
                self.stdout.write(f'Added image path to park: {park.name}')
        
        self.stdout.write(self.style.SUCCESS('All items now have image paths!'))
