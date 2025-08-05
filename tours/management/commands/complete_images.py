from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import requests
import os
from tours.models import Park, Tour
import time


class Command(BaseCommand):
    help = 'Add remaining images with working URLs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding remaining wildlife images...'))
        
        # Add images for tours without them
        self.add_missing_tour_images()
        
        # Add images for parks without them
        self.add_missing_park_images()
        
        self.stdout.write(self.style.SUCCESS('Successfully added all missing images!'))

    def download_image(self, url, filename):
        """Download image from URL and save it"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Save to media directory
            file_path = default_storage.save(filename, ContentFile(response.content))
            self.stdout.write(f'Downloaded: {filename}')
            return file_path
        except Exception as e:
            self.stdout.write(f'Failed to download {url}: {e}')
            return None

    def add_missing_tour_images(self):
        """Add images to tours that don't have them"""
        
        # Working image URLs - using more reliable sources
        working_images = {
            'chimp': 'https://images.unsplash.com/photo-1573160103600-66ebac5f7ba5?w=800&h=600&fit=crop',
            'forest': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop',
            'zebra': 'https://images.unsplash.com/photo-1563781422-b70d93b75a57?w=800&h=600&fit=crop',
            'boat': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
            'safari': 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800&h=600&fit=crop',
            'primate': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop'
        }
        
        # Map tours to images
        tour_mappings = {
            'Chimpanzee Trekking': 'chimp',
            'Primate Walk': 'primate', 
            'Zebra Safari Walk': 'zebra',
            'Kazinga Channel Boat Safari': 'boat'
        }
        
        for tour in Tour.objects.filter(image__isnull=True):
            tour_type = tour_mappings.get(tour.name, 'safari')
            
            if tour_type in working_images:
                image_url = working_images[tour_type]
                filename = f'tours/{tour_type}_{tour.name.lower().replace(" ", "_")}.jpg'
                
                image_path = self.download_image(image_url, filename)
                if image_path:
                    tour.image = image_path
                    tour.save()
                    self.stdout.write(f'Added image to tour: {tour.name}')
                else:
                    # Create placeholder if download fails
                    self.create_placeholder_for_tour(tour, tour_type)
                
                time.sleep(2)
            else:
                self.create_placeholder_for_tour(tour, 'safari')

    def add_missing_park_images(self):
        """Add images to parks that don't have them"""
        
        working_images = {
            'kibale': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop',
            'lake_mburo': 'https://images.unsplash.com/photo-1563781422-b70d93b75a57?w=800&h=600&fit=crop'
        }
        
        park_mappings = {
            'Kibale National Park': 'kibale',
            'Lake Mburo National Park': 'lake_mburo'
        }
        
        for park in Park.objects.filter(image__isnull=True):
            park_key = park_mappings.get(park.name, 'forest')
            
            if park_key in working_images:
                image_url = working_images[park_key]
                filename = f'parks/{park_key}_park.jpg'
                
                image_path = self.download_image(image_url, filename)
                if image_path:
                    park.image = image_path
                    park.save()
                    self.stdout.write(f'Added image to park: {park.name}')
                else:
                    self.create_placeholder_for_park(park)
                
                time.sleep(2)
            else:
                self.create_placeholder_for_park(park)

    def create_placeholder_for_tour(self, tour, tour_type):
        """Create a placeholder image for a tour"""
        colors = {
            'chimp': 'CD853F',
            'forest': '228B22',
            'zebra': '000000',
            'boat': '4682B4',
            'safari': 'DAA520',
            'primate': '8B4513'
        }
        
        color = colors.get(tour_type, '228B22')
        text = tour_type.replace('_', ' ').title()
        
        placeholder_url = f'https://via.placeholder.com/800x600/{color}/FFFFFF?text={text}+Tour'
        filename = f'tours/placeholder_{tour.name.lower().replace(" ", "_")}.png'
        
        image_path = self.download_image(placeholder_url, filename)
        if image_path:
            tour.image = image_path
            tour.save()
            self.stdout.write(f'Added placeholder image to tour: {tour.name}')

    def create_placeholder_for_park(self, park):
        """Create a placeholder image for a park"""
        placeholder_url = 'https://via.placeholder.com/800x600/228B22/FFFFFF?text=National+Park'
        filename = f'parks/placeholder_{park.name.lower().replace(" ", "_")}.png'
        
        image_path = self.download_image(placeholder_url, filename)
        if image_path:
            park.image = image_path
            park.save()
            self.stdout.write(f'Added placeholder image to park: {park.name}')
