from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import requests
import os
from tours.models import Park, Tour
import time


class Command(BaseCommand):
    help = 'Add high-quality wildlife photos from reliable sources'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding authentic wildlife photos...'))
        
        # Create media directories if they don't exist
        self.ensure_media_directories()
        
        # Add authentic wildlife images
        self.add_wildlife_images()
        
        self.stdout.write(self.style.SUCCESS('Successfully added wildlife images!'))

    def ensure_media_directories(self):
        """Ensure media directories exist"""
        directories = ['media/parks', 'media/tours', 'media/wildlife']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.stdout.write(f'Ensured directory exists: {directory}')

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

    def add_wildlife_images(self):
        """Add authentic wildlife images from various sources"""
        
        # High-quality wildlife images from Unsplash (free to use)
        wildlife_images = {
            # Gorilla images
            'gorilla_1': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800&h=600&fit=crop',
            'gorilla_2': 'https://images.unsplash.com/photo-1511593358241-7eea1f3c84e5?w=800&h=600&fit=crop',
            'gorilla_3': 'https://images.unsplash.com/photo-1473445730015-841f29a9490b?w=800&h=600&fit=crop',
            
            # Lion images
            'lion_1': 'https://images.unsplash.com/photo-1551969014-7d2c4cddf0b6?w=800&h=600&fit=crop',
            'lion_2': 'https://images.unsplash.com/photo-1549366021-9f761d040a94?w=800&h=600&fit=crop',
            'lion_3': 'https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=800&h=600&fit=crop',
            
            # Elephant images
            'elephant_1': 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&h=600&fit=crop',
            'elephant_2': 'https://images.unsplash.com/photo-1564760055775-d63b17a55c44?w=800&h=600&fit=crop',
            'elephant_3': 'https://images.unsplash.com/photo-1568454537842-d933259bb258?w=800&h=600&fit=crop',
            
            # Chimpanzee images
            'chimp_1': 'https://images.unsplash.com/photo-1539066085618-8f5c5ae33e90?w=800&h=600&fit=crop',
            'chimp_2': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop',
            'chimp_3': 'https://images.unsplash.com/photo-1612207351480-6a98cb29a11c?w=800&h=600&fit=crop',
            
            # Zebra images
            'zebra_1': 'https://images.unsplash.com/photo-1553975258-6e4d4c7f0bf5?w=800&h=600&fit=crop',
            'zebra_2': 'https://images.unsplash.com/photo-1563729170-5e76fc51e93c?w=800&h=600&fit=crop',
            'zebra_3': 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800&h=600&fit=crop',
            
            # Hippo images
            'hippo_1': 'https://images.unsplash.com/photo-1567306301408-9b74779a11af?w=800&h=600&fit=crop',
            'hippo_2': 'https://images.unsplash.com/photo-1553975259-83736b1e5be5?w=800&h=600&fit=crop',
            
            # Waterfall images
            'waterfall_1': 'https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=800&h=600&fit=crop',
            'waterfall_2': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
            
            # Forest images
            'forest_1': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop',
            'forest_2': 'https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=800&h=600&fit=crop',
            'forest_3': 'https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=800&h=600&fit=crop',
            
            # Boat safari images
            'boat_1': 'https://images.unsplash.com/photo-1594736797933-d0902ba8a9da?w=800&h=600&fit=crop',
            'boat_2': 'https://images.unsplash.com/photo-1615729947596-a598e5de0ab3?w=800&h=600&fit=crop',
            
            # Buffalo images
            'buffalo_1': 'https://images.unsplash.com/photo-1543173624-969fb0ea2a0b?w=800&h=600&fit=crop',
            'buffalo_2': 'https://images.unsplash.com/photo-1602491453631-e2a5ad90a131?w=800&h=600&fit=crop'
        }
        
        # Map specific tours to their ideal images
        tour_image_mapping = {
            'Mountain Gorilla Trekking': ['gorilla_1', 'gorilla_2'],
            'Gorilla Habituation Experience': ['gorilla_2', 'gorilla_3'],
            'Tree-Climbing Lions Safari': ['lion_1', 'lion_2'],
            'Kazinga Channel Boat Safari': ['boat_1', 'hippo_1'],
            'Murchison Falls Boat Safari': ['waterfall_1', 'boat_2'],
            'Big 5 Game Drive': ['elephant_1', 'buffalo_1'],
            'Chimpanzee Trekking': ['chimp_1', 'chimp_2'],
            'Primate Walk': ['chimp_3', 'forest_1'],
            'Zebra Safari Walk': ['zebra_1', 'zebra_2'],
            'Lake Mburo Boat Safari': ['boat_2', 'zebra_3']
        }
        
        # Add images to tours
        for tour in Tour.objects.all():
            if tour.image:
                self.stdout.write(f'Tour {tour.name} already has an image')
                continue
            
            # Get appropriate images for this tour
            image_keys = tour_image_mapping.get(tour.name, ['forest_1'])
            primary_image_key = image_keys[0]
            
            if primary_image_key in wildlife_images:
                image_url = wildlife_images[primary_image_key]
                filename = f'tours/{primary_image_key}_{tour.name.lower().replace(" ", "_")}.jpg'
                
                image_path = self.download_image(image_url, filename)
                if image_path:
                    tour.image = image_path
                    tour.save()
                    self.stdout.write(f'Added image to tour: {tour.name}')
                
                time.sleep(2)  # Be respectful with requests
        
        # Map parks to their ideal images
        park_image_mapping = {
            'Bwindi Impenetrable National Park': 'gorilla_1',
            'Queen Elizabeth National Park': 'lion_1', 
            'Murchison Falls National Park': 'waterfall_1',
            'Kibale National Park': 'chimp_1',
            'Lake Mburo National Park': 'zebra_1'
        }
        
        # Add images to parks
        for park in Park.objects.all():
            if park.image:
                self.stdout.write(f'Park {park.name} already has an image')
                continue
            
            image_key = park_image_mapping.get(park.name, 'forest_1')
            
            if image_key in wildlife_images:
                image_url = wildlife_images[image_key]
                filename = f'parks/{image_key}_{park.name.lower().replace(" ", "_")}.jpg'
                
                image_path = self.download_image(image_url, filename)
                if image_path:
                    park.image = image_path
                    park.save()
                    self.stdout.write(f'Added image to park: {park.name}')
                
                time.sleep(2)  # Be respectful with requests

    def add_fallback_images(self):
        """Add fallback images if downloads fail"""
        # Create simple colored placeholders for tours without images
        for tour in Tour.objects.filter(image__isnull=True):
            tour_type = 'default'
            color = '228B22'  # Forest green
            
            if 'gorilla' in tour.name.lower():
                color = '8B4513'  # Saddle brown
                tour_type = 'gorilla'
            elif 'lion' in tour.name.lower():
                color = 'DAA520'  # Goldenrod
                tour_type = 'lion'
            elif 'elephant' in tour.name.lower():
                color = '696969'  # Dim gray
                tour_type = 'elephant'
            elif 'chimp' in tour.name.lower():
                color = 'CD853F'  # Peru
                tour_type = 'chimp'
            elif 'zebra' in tour.name.lower():
                color = '000000'  # Black
                tour_type = 'zebra'
            elif 'boat' in tour.name.lower() or 'safari' in tour.name.lower():
                color = '4682B4'  # Steel blue
                tour_type = 'safari'
            
            placeholder_url = f'https://via.placeholder.com/800x600/{color}/FFFFFF?text={tour_type.title()}+Tour'
            filename = f'tours/placeholder_{tour.name.lower().replace(" ", "_")}.jpg'
            
            image_path = self.download_image(placeholder_url, filename)
            if image_path:
                tour.image = image_path
                tour.save()
                self.stdout.write(f'Added fallback image to tour: {tour.name}')
            
            time.sleep(1)
