from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import requests
from tours.models import Park, Tour


class Command(BaseCommand):
    help = 'Add placeholder images to all items without images'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding images to all tours and parks...'))
        
        # Add images to tours without them
        for tour in Tour.objects.filter(image__isnull=True):
            self.add_image_to_tour(tour)
        
        # Add images to parks without them  
        for park in Park.objects.filter(image__isnull=True):
            self.add_image_to_park(park)
        
        self.stdout.write(self.style.SUCCESS('All tours and parks now have images!'))

    def download_image(self, url, filename):
        """Download image from URL and save it"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            file_path = default_storage.save(filename, ContentFile(response.content))
            return file_path
        except Exception as e:
            self.stdout.write(f'Failed to download {url}: {e}')
            return None

    def add_image_to_tour(self, tour):
        """Add appropriate image to a tour"""
        # Define image mapping based on tour name
        image_urls = {
            'Kazinga Channel Boat Safari': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
            'Chimpanzee Trekking': 'https://images.unsplash.com/photo-1573160103600-66ebac5f7ba5?w=800&h=600&fit=crop',
            'Primate Walk': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop',
            'Zebra Safari Walk': 'https://images.unsplash.com/photo-1563781422-b70d93b75a57?w=800&h=600&fit=crop'
        }
        
        # Placeholder colors for different tour types
        placeholder_colors = {
            'Kazinga Channel Boat Safari': '4682B4',  # Steel blue
            'Chimpanzee Trekking': 'CD853F',  # Peru
            'Primate Walk': '228B22',  # Forest green
            'Zebra Safari Walk': '000000'  # Black
        }
        
        tour_name = tour.name
        
        # Try to download real image first
        if tour_name in image_urls:
            image_url = image_urls[tour_name]
            filename = f'tours/{tour_name.lower().replace(" ", "_")}.jpg'
            
            image_path = self.download_image(image_url, filename)
            if image_path:
                tour.image = image_path
                tour.save()
                self.stdout.write(f'Added real image to tour: {tour.name}')
                return
        
        # Create placeholder if real image fails
        color = placeholder_colors.get(tour_name, '228B22')
        text = tour_name.replace(' ', '+')
        placeholder_url = f'https://via.placeholder.com/800x600/{color}/FFFFFF?text={text}'
        filename = f'tours/placeholder_{tour_name.lower().replace(" ", "_")}.png'
        
        image_path = self.download_image(placeholder_url, filename)
        if image_path:
            tour.image = image_path
            tour.save()
            self.stdout.write(f'Added placeholder image to tour: {tour.name}')

    def add_image_to_park(self, park):
        """Add appropriate image to a park"""
        # Define image mapping based on park name
        image_urls = {
            'Kibale National Park': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop',
            'Lake Mburo National Park': 'https://images.unsplash.com/photo-1563781422-b70d93b75a57?w=800&h=600&fit=crop'
        }
        
        park_name = park.name
        
        # Try to download real image first
        if park_name in image_urls:
            image_url = image_urls[park_name]
            filename = f'parks/{park_name.lower().replace(" ", "_")}.jpg'
            
            image_path = self.download_image(image_url, filename)
            if image_path:
                park.image = image_path
                park.save()
                self.stdout.write(f'Added real image to park: {park.name}')
                return
        
        # Create placeholder if real image fails
        text = park_name.replace(' ', '+')
        placeholder_url = f'https://via.placeholder.com/800x600/228B22/FFFFFF?text={text}'
        filename = f'parks/placeholder_{park_name.lower().replace(" ", "_")}.png'
        
        image_path = self.download_image(placeholder_url, filename)
        if image_path:
            park.image = image_path
            park.save()
            self.stdout.write(f'Added placeholder image to park: {park.name}')
