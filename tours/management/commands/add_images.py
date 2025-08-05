from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import requests
import os
from tours.models import Park, Tour
from booking.models import Availability
import time


class Command(BaseCommand):
    help = 'Add photos to tours, parks and other areas using UWA and Uganda wildlife images'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding photos to tours and parks...'))
        
        # Create media directories if they don't exist
        self.ensure_media_directories()
        
        # Add images to parks
        self.add_park_images()
        
        # Add images to tours
        self.add_tour_images()
        
        self.stdout.write(self.style.SUCCESS('Successfully added images to tours and parks!'))

    def ensure_media_directories(self):
        """Ensure media directories exist"""
        directories = ['media/parks', 'media/tours']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.stdout.write(f'Ensured directory exists: {directory}')

    def download_image(self, url, filename):
        """Download image from URL and save it"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save to media directory
            file_path = default_storage.save(filename, ContentFile(response.content))
            self.stdout.write(f'Downloaded: {filename}')
            return file_path
        except Exception as e:
            self.stdout.write(f'Failed to download {url}: {e}')
            return None

    def add_park_images(self):
        """Add images to all parks"""
        park_images = {
            'Bwindi Impenetrable National Park': [
                'https://ugandawildlife.org/wp-content/uploads/2021/05/Mountain-Gorilla-in-Bwindi-1.jpg',
                'https://ugandawildlife.org/wp-content/uploads/2021/05/Bwindi-Forest.jpg'
            ],
            'Queen Elizabeth National Park': [
                'https://ugandawildlife.org/wp-content/uploads/2021/05/Tree-climbing-Lions-in-Ishasha.jpg',
                'https://ugandawildlife.org/wp-content/uploads/2021/05/Elephants-in-Queen-Elizabeth.jpg'
            ],
            'Murchison Falls National Park': [
                'https://ugandawildlife.org/wp-content/uploads/2021/05/Murchison-Falls.jpg',
                'https://ugandawildlife.org/wp-content/uploads/2021/05/Nile-Crocodile.jpg'
            ],
            'Kibale National Park': [
                'https://ugandawildlife.org/wp-content/uploads/2021/05/Chimpanzee-in-Kibale.jpg',
                'https://ugandawildlife.org/wp-content/uploads/2021/05/Kibale-Forest-Canopy.jpg'
            ],
            'Lake Mburo National Park': [
                'https://ugandawildlife.org/wp-content/uploads/2021/05/Zebras-in-Lake-Mburo.jpg',
                'https://ugandawildlife.org/wp-content/uploads/2021/05/Impala-Lake-Mburo.jpg'
            ]
        }
        
        # Alternative wildlife images from reliable sources
        backup_images = {
            'Bwindi Impenetrable National Park': [
                'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800',  # Mountain gorilla
                'https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=800'   # Dense forest
            ],
            'Queen Elizabeth National Park': [
                'https://images.unsplash.com/photo-1551969014-7d2c4cddf0b6?w=800',  # Lions
                'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800'   # Elephants
            ],
            'Murchison Falls National Park': [
                'https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=800',  # Waterfall
                'https://images.unsplash.com/photo-1567306301408-9b74779a11af?w=800'  # Hippos
            ],
            'Kibale National Park': [
                'https://images.unsplash.com/photo-1539066085618-8f5c5ae33e90?w=800',  # Chimpanzee
                'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800'   # Forest
            ],
            'Lake Mburo National Park': [
                'https://images.unsplash.com/photo-1553975258-6e4d4c7f0bf5?w=800',  # Zebras
                'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800'   # African savanna
            ]
        }
        
        for park in Park.objects.all():
            if park.image:
                self.stdout.write(f'Park {park.name} already has an image')
                continue
            
            park_name = park.name
            images = park_images.get(park_name, backup_images.get(park_name, []))
            
            if images:
                # Use the first image for the park
                image_url = images[0]
                filename = f'parks/{park_name.lower().replace(" ", "_")}.jpg'
                
                image_path = self.download_image(image_url, filename)
                if image_path:
                    park.image = image_path
                    park.save()
                    self.stdout.write(f'Added image to park: {park.name}')
                
                time.sleep(1)  # Be respectful with requests

    def add_tour_images(self):
        """Add images to all tours"""
        tour_images = {
            # Bwindi tours
            'Mountain Gorilla Trekking': [
                'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800',
                'https://images.unsplash.com/photo-1511593358241-7eea1f3c84e5?w=800'
            ],
            'Gorilla Habituation Experience': [
                'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800',
                'https://images.unsplash.com/photo-1473445730015-841f29a9490b?w=800'
            ],
            
            # Queen Elizabeth tours
            'Kazinga Channel Boat Safari': [
                'https://images.unsplash.com/photo-1567306301408-9b74779a11af?w=800',  # Hippos
                'https://images.unsplash.com/photo-1594736797933-d0902ba8a9da?w=800'   # Boat safari
            ],
            'Tree-Climbing Lions Safari': [
                'https://images.unsplash.com/photo-1551969014-7d2c4cddf0b6?w=800',  # Lions
                'https://images.unsplash.com/photo-1549366021-9f761d040a94?w=800'   # Lion in tree
            ],
            
            # Murchison Falls tours
            'Murchison Falls Boat Safari': [
                'https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=800',  # Waterfall
                'https://images.unsplash.com/photo-1594736797933-d0902ba8a9da?w=800'   # Boat safari
            ],
            'Big 5 Game Drive': [
                'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800',  # Elephants
                'https://images.unsplash.com/photo-1543173624-969fb0ea2a0b?w=800'   # Buffalo
            ],
            
            # Kibale tours
            'Chimpanzee Trekking': [
                'https://images.unsplash.com/photo-1539066085618-8f5c5ae33e90?w=800',  # Chimpanzee
                'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800'   # Forest trek
            ],
            'Primate Walk': [
                'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800',  # Primates
                'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800'   # Forest
            ],
            
            # Lake Mburo tours
            'Zebra Safari Walk': [
                'https://images.unsplash.com/photo-1553975258-6e4d4c7f0bf5?w=800',  # Zebras
                'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800'   # Savanna walk
            ],
            'Lake Mburo Boat Safari': [
                'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800',  # Lake
                'https://images.unsplash.com/photo-1594736797933-d0902ba8a9da?w=800'   # Boat safari
            ]
        }
        
        for tour in Tour.objects.all():
            if tour.image:
                self.stdout.write(f'Tour {tour.name} already has an image')
                continue
            
            tour_name = tour.name
            images = tour_images.get(tour_name, [])
            
            if images:
                # Use the first image for the tour
                image_url = images[0]
                filename = f'tours/{tour_name.lower().replace(" ", "_").replace("-", "_")}.jpg'
                
                image_path = self.download_image(image_url, filename)
                if image_path:
                    tour.image = image_path
                    tour.save()
                    self.stdout.write(f'Added image to tour: {tour.name}')
                
                time.sleep(1)  # Be respectful with requests

    def add_backup_images(self):
        """Add backup images if primary downloads fail"""
        # Local placeholder images that we can create
        placeholder_images = {
            'gorilla': 'https://via.placeholder.com/800x600/228B22/FFFFFF?text=Mountain+Gorilla',
            'lions': 'https://via.placeholder.com/800x600/DAA520/FFFFFF?text=Tree+Climbing+Lions',
            'elephants': 'https://via.placeholder.com/800x600/696969/FFFFFF?text=African+Elephants',
            'chimpanzee': 'https://via.placeholder.com/800x600/8B4513/FFFFFF?text=Chimpanzees',
            'zebras': 'https://via.placeholder.com/800x600/000000/FFFFFF?text=Zebras',
            'waterfall': 'https://via.placeholder.com/800x600/4682B4/FFFFFF?text=Murchison+Falls',
            'boat_safari': 'https://via.placeholder.com/800x600/20B2AA/FFFFFF?text=Boat+Safari',
            'forest': 'https://via.placeholder.com/800x600/006400/FFFFFF?text=Forest+Trek',
            'savanna': 'https://via.placeholder.com/800x600/F4A460/FFFFFF?text=Savanna+Walk',
            'lake': 'https://via.placeholder.com/800x600/1E90FF/FFFFFF?text=Lake+Safari'
        }
        
        # Map tours to placeholder categories
        tour_placeholders = {
            'Mountain Gorilla Trekking': 'gorilla',
            'Gorilla Habituation Experience': 'gorilla',
            'Tree-Climbing Lions Safari': 'lions',
            'Kazinga Channel Boat Safari': 'boat_safari',
            'Murchison Falls Boat Safari': 'waterfall',
            'Big 5 Game Drive': 'elephants',
            'Chimpanzee Trekking': 'chimpanzee',
            'Primate Walk': 'forest',
            'Zebra Safari Walk': 'zebras',
            'Lake Mburo Boat Safari': 'lake'
        }
        
        for tour in Tour.objects.filter(image__isnull=True):
            placeholder_key = tour_placeholders.get(tour.name, 'forest')
            image_url = placeholder_images[placeholder_key]
            filename = f'tours/placeholder_{tour.name.lower().replace(" ", "_")}.jpg'
            
            image_path = self.download_image(image_url, filename)
            if image_path:
                tour.image = image_path
                tour.save()
                self.stdout.write(f'Added placeholder image to tour: {tour.name}')
