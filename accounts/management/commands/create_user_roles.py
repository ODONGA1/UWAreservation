from django.core.management.base import BaseCommand
from accounts.models import UserRole


class Command(BaseCommand):
    help = 'Create initial user roles'

    def handle(self, *args, **options):
        roles = [
            ('tourist', 'Tourist', 'Visitors who book and enjoy tours'),
            ('guide', 'Tour Guide', 'Professional guides who lead tours'),
            ('operator', 'Tour Operator', 'Companies and individuals who organize tours'),
            ('staff', 'UWA Staff', 'Uganda Wildlife Authority employees'),
        ]
        
        for role_name, display_name, description in roles:
            role, created = UserRole.objects.get_or_create(
                name=role_name,
                defaults={
                    'description': description,
                    'permissions': {}
                }
            )
            if created:
                self.stdout.write(f'Created role: {display_name}')
            else:
                self.stdout.write(f'Role already exists: {display_name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully created all user roles!'))
