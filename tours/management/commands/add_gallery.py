from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import requests
import os


class Command(BaseCommand):
    help = 'Add additional gallery images and enhance visual content'

    def handle(self, *args, **options):
        # Create gallery directory
        os.makedirs('media/gallery', exist_ok=True)
        
        # Download general Uganda wildlife gallery images
        gallery_images = {
            'uganda_wildlife_1.jpg': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=400&h=300&fit=crop',  # Gorilla
            'uganda_wildlife_2.jpg': 'https://images.unsplash.com/photo-1551969014-7d2c4cddf0b6?w=400&h=300&fit=crop',  # Lions
            'uganda_wildlife_3.jpg': 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=300&fit=crop',  # Elephants
            'uganda_landscape_1.jpg': 'https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=400&h=300&fit=crop',  # Waterfall
            'uganda_landscape_2.jpg': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop',  # Forest
            'uganda_safari_1.jpg': 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=400&h=300&fit=crop',  # Savanna
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for filename, url in gallery_images.items():
            file_path = f'gallery/{filename}'
            if not default_storage.exists(file_path):
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    response.raise_for_status()
                    
                    default_storage.save(file_path, ContentFile(response.content))
                    self.stdout.write(f'Downloaded gallery image: {filename}')
                except Exception as e:
                    self.stdout.write(f'Failed to download {filename}: {e}')
        
        # Create header/hero images
        hero_images = {
            'hero_uganda_wildlife.jpg': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=1200&h=600&fit=crop',
            'hero_uganda_landscape.jpg': 'https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=1200&h=600&fit=crop'
        }
        
        for filename, url in hero_images.items():
            file_path = f'gallery/{filename}'
            if not default_storage.exists(file_path):
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    response.raise_for_status()
                    
                    default_storage.save(file_path, ContentFile(response.content))
                    self.stdout.write(f'Downloaded hero image: {filename}')
                except Exception as e:
                    self.stdout.write(f'Failed to download {filename}: {e}')
        
        self.stdout.write(self.style.SUCCESS('Gallery images added!'))
