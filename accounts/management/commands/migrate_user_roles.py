from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile, UserRole


class Command(BaseCommand):
    help = 'Migrate existing user profiles to use the new role system'

    def handle(self, *args, **options):
        # Get all user roles
        tourist_role = UserRole.objects.get(name='tourist')
        guide_role = UserRole.objects.get(name='guide')
        
        # Get all users without any roles assigned
        profiles_without_roles = Profile.objects.filter(roles__isnull=True)
        
        for profile in profiles_without_roles:
            # Check if user has a Guide record
            if hasattr(profile.user, 'guide'):
                # User is a guide
                profile.roles.add(guide_role)
                self.stdout.write(f'Added guide role to {profile.user.username}')
            else:
                # Default to tourist role
                profile.roles.add(tourist_role)
                self.stdout.write(f'Added tourist role to {profile.user.username}')
        
        # Also check for users who might not have profiles yet
        users_without_profiles = User.objects.filter(profile__isnull=True)
        for user in users_without_profiles:
            profile = Profile.objects.create(user=user)
            if hasattr(user, 'guide'):
                profile.roles.add(guide_role)
                self.stdout.write(f'Created profile with guide role for {user.username}')
            else:
                profile.roles.add(tourist_role)
                self.stdout.write(f'Created profile with tourist role for {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Successfully migrated all user profiles!'))
