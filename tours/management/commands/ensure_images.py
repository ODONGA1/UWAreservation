from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import requests
import os
from tours.models import Tour, Park


class Command(BaseCommand):
    help = 'Ensure all image files exist for tours and parks'

    def handle(self, *args, **options):
        # Ensure media directories exist
        media_root = str(settings.MEDIA_ROOT)
        os.makedirs(os.path.join(media_root, 'tours'), exist_ok=True)
        os.makedirs(os.path.join(media_root, 'parks'), exist_ok=True) 
        os.makedirs(os.path.join(media_root, 'gallery'), exist_ok=True)
        
        # Map of file names to download URLs
        image_downloads = {
            # Tours
            'tours/gorilla_1_mountain_gorilla_trekking.jpg': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800&h=600&fit=crop&auto=format',
            'tours/gorilla_2_gorilla_habituation_experience.jpg': 'https://images.unsplash.com/photo-1511593358241-7eea1f3c84e5?w=800&h=600&fit=crop&auto=format',
            'tours/boat_safari.jpg': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop&auto=format',
            'tours/lion_1_tree-climbing_lions_safari.jpg': 'https://images.unsplash.com/photo-1551969014-7d2c4cddf0b6?w=800&h=600&fit=crop&auto=format',
            'tours/waterfall_1_murchison_falls_boat_safari.jpg': 'https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=800&h=600&fit=crop&auto=format',
            'tours/elephant_1_big_5_game_drive.jpg': 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&h=600&fit=crop&auto=format',
            'tours/chimp_trek.jpg': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop&auto=format',
            'tours/primate_walk.jpg': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop&auto=format',
            'tours/zebra_walk.jpg': 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800&h=600&fit=crop&auto=format',
            'tours/boat_2_lake_mburo_boat_safari.jpg': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop&auto=format',
            
            # Parks
            'parks/gorilla_1_bwindi_impenetrable_national_park.jpg': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800&h=600&fit=crop&auto=format',
            'parks/lion_1_queen_elizabeth_national_park.jpg': 'https://images.unsplash.com/photo-1551969014-7d2c4cddf0b6?w=800&h=600&fit=crop&auto=format',
            'parks/waterfall_1_murchison_falls_national_park.jpg': 'https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=800&h=600&fit=crop&auto=format',
            'parks/kibale.jpg': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop&auto=format',
            'parks/lake_mburo.jpg': 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=800&h=600&fit=crop&auto=format',
            
            # Gallery
            'gallery/uganda_wildlife_1.jpg': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=400&h=300&fit=crop&auto=format',
            'gallery/uganda_wildlife_2.jpg': 'https://images.unsplash.com/photo-1551969014-7d2c4cddf0b6?w=400&h=300&fit=crop&auto=format',
            'gallery/uganda_wildlife_3.jpg': 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=300&fit=crop&auto=format',
            'gallery/uganda_landscape_1.jpg': 'https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=400&h=300&fit=crop&auto=format',
            'gallery/uganda_landscape_2.jpg': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop&auto=format',
            'gallery/uganda_safari_1.jpg': 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=400&h=300&fit=crop&auto=format',
            'gallery/hero_uganda_wildlife.jpg': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=1200&h=600&fit=crop&auto=format',
            'gallery/hero_uganda_landscape.jpg': 'https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=1200&h=600&fit=crop&auto=format'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        successful = 0
        failed = 0
        
        for file_path, url in image_downloads.items():
            full_path = os.path.join(media_root, file_path)
            
            # Check if file already exists
            if os.path.exists(full_path):
                self.stdout.write(f'Already exists: {file_path}')
                continue
            
            try:
                # Download the image
                response = requests.get(url, headers=headers, timeout=20)
                response.raise_for_status()
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Save the file directly to filesystem
                with open(full_path, 'wb') as f:
                    f.write(response.content)
                
                self.stdout.write(f'Downloaded: {file_path}')
                successful += 1
                
            except Exception as e:
                self.stdout.write(f'Failed to download {file_path}: {e}')
                # Create a placeholder image
                self.create_placeholder(full_path, file_path)
                failed += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Image download complete: {successful} successful, {failed} failed'
            )
        )

    def create_placeholder(self, file_path, relative_path):
        """Create a simple placeholder image"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Determine image size and color based on path
            if 'hero' in relative_path:
                size = (1200, 600)
                color = '#228B22'
            elif 'gallery' in relative_path:
                size = (400, 300)
                color = '#4682B4'
            else:
                size = (800, 600)
                color = '#228B22'
            
            # Create colored image
            img = Image.new('RGB', size, color=color)
            draw = ImageDraw.Draw(img)
            
            # Add text
            text = relative_path.split('/')[-1].split('.')[0].replace('_', ' ').title()
            
            try:
                font = ImageFont.truetype("arial.ttf", size[1]//15)
            except:
                font = ImageFont.load_default()
            
            # Center the text
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save the image
            img.save(file_path, 'JPEG')
            self.stdout.write(f'Created placeholder: {relative_path}')
            
        except ImportError:
            self.stdout.write(f'PIL not available for placeholder: {relative_path}')
        except Exception as e:
            self.stdout.write(f'Error creating placeholder {relative_path}: {e}')
