from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import requests
import os


class Command(BaseCommand):
    help = 'Download backup images for missing files'

    def handle(self, *args, **options):
        # Alternative image URLs that are more likely to work
        backup_downloads = {
            'tours/chimp_trek.jpg': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop',
            'tours/zebra_walk.jpg': 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800&h=600&fit=crop',
            'parks/lake_mburo.jpg': 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800&h=600&fit=crop'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for file_path, url in backup_downloads.items():
            if not default_storage.exists(file_path):
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    response.raise_for_status()
                    
                    # Save the file
                    default_storage.save(file_path, ContentFile(response.content))
                    self.stdout.write(f'Downloaded backup: {file_path}')
                except Exception as e:
                    self.stdout.write(f'Failed to download backup {file_path}: {e}')
                    # Create a simple colored rectangle as absolute fallback
                    self.create_simple_image(file_path)
            else:
                self.stdout.write(f'Already exists: {file_path}')
        
        # Create simple fallback images for the placeholder files
        self.create_simple_fallbacks()
        
        self.stdout.write(self.style.SUCCESS('All backup images processed!'))

    def create_simple_image(self, file_path):
        """Create a simple colored image as fallback"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Create a simple colored image
            img = Image.new('RGB', (800, 600), color='#228B22')
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            text = "Wildlife Image"
            if 'chimp' in file_path:
                text = "Chimpanzee"
                img = Image.new('RGB', (800, 600), color='#CD853F')
            elif 'zebra' in file_path:
                text = "Zebra Safari"
                img = Image.new('RGB', (800, 600), color='#F4A460')
            elif 'lake' in file_path:
                text = "Lake Safari"
                img = Image.new('RGB', (800, 600), color='#4682B4')
            
            draw = ImageDraw.Draw(img)
            
            # Center the text
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (800 - text_width) // 2
            y = (600 - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
            
            # Save to memory buffer
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)
            
            # Save to storage
            default_storage.save(file_path, ContentFile(buffer.read()))
            self.stdout.write(f'Created simple image: {file_path}')
            
        except ImportError:
            self.stdout.write('PIL not available, skipping simple image creation')
        except Exception as e:
            self.stdout.write(f'Error creating simple image {file_path}: {e}')

    def create_simple_fallbacks(self):
        """Create simple fallback images"""
        fallbacks = [
            'tours/default_tour.jpg',
            'parks/default_park.jpg'
        ]
        
        for file_path in fallbacks:
            if not default_storage.exists(file_path):
                self.create_simple_image(file_path)
