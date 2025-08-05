from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile, UserRole


class Command(BaseCommand):
    help = 'Make a user UWA staff for testing user management features'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to make UWA staff')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Get or create UWA staff role
            staff_role, created = UserRole.objects.get_or_create(name='staff')
            
            # Add staff role to user
            profile.roles.add(staff_role)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully made {username} a UWA staff member!')
            )
            self.stdout.write(f'User now has roles: {profile.get_roles_display()}')
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
