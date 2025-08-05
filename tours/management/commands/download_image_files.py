from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import requests
import os


class Command(BaseCommand):
    help = 'Download actual image files for the assigned paths'

    def handle(self, *args, **options):
        # Create media directories
        os.makedirs('media/tours', exist_ok=True)
        os.makedirs('media/parks', exist_ok=True)
        
        # Image URLs mapping
        image_downloads = {
            'tours/boat_safari.jpg': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',
            'tours/chimp_trek.jpg': 'https://images.unsplash.com/photo-1573160103600-66ebac5f7ba5?w=800&h=600&fit=crop',
            'tours/primate_walk.jpg': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop',
            'tours/zebra_walk.jpg': 'https://images.unsplash.com/photo-1563781422-b70d93b75a57?w=800&h=600&fit=crop',
            'tours/default_tour.jpg': 'https://via.placeholder.com/800x600/228B22/FFFFFF?text=Wildlife+Tour',
            'parks/kibale.jpg': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop',
            'parks/lake_mburo.jpg': 'https://images.unsplash.com/photo-1563781422-b70d93b75a57?w=800&h=600&fit=crop',
            'parks/default_park.jpg': 'https://via.placeholder.com/800x600/006400/FFFFFF?text=National+Park'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for file_path, url in image_downloads.items():
            if not default_storage.exists(file_path):
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    response.raise_for_status()
                    
                    # Save the file
                    default_storage.save(file_path, ContentFile(response.content))
                    self.stdout.write(f'Downloaded: {file_path}')
                except Exception as e:
                    self.stdout.write(f'Failed to download {file_path}: {e}')
            else:
                self.stdout.write(f'Already exists: {file_path}')
        
        self.stdout.write(self.style.SUCCESS('All image files downloaded!'))
