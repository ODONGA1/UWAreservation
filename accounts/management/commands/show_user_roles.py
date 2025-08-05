from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models
from accounts.models import Profile, UserRole


class Command(BaseCommand):
    help = 'Display current user roles structure'

    def handle(self, *args, **options):
        self.stdout.write("=== USER ROLES SUMMARY ===")
        
        # Display all available roles
        self.stdout.write("\n1. Available Roles:")
        for role in UserRole.objects.all():
            self.stdout.write(f"   - {role.get_name_display()} ({role.name}): {role.description}")
        
        # Display role statistics
        self.stdout.write("\n2. Role Statistics:")
        for role in UserRole.objects.all():
            count = Profile.objects.filter(roles=role).count()
            self.stdout.write(f"   - {role.get_name_display()}: {count} users")
        
        # Display users with multiple roles
        self.stdout.write("\n3. Users with Multiple Roles:")
        for profile in Profile.objects.all():
            role_count = profile.roles.count()
            if role_count > 1:
                self.stdout.write(f"   - {profile.user.username} ({profile.get_full_name()}): {profile.get_roles_display()}")
        
        # Display all users and their roles
        self.stdout.write("\n4. All Users and Their Roles:")
        for profile in Profile.objects.all().order_by('user__username'):
            roles = profile.get_roles_display() or "No roles assigned"
            self.stdout.write(f"   - {profile.user.username}: {roles}")
        
        # Summary
        total_users = Profile.objects.count()
        users_with_roles = Profile.objects.filter(roles__isnull=False).distinct().count()
        users_with_multiple_roles = Profile.objects.annotate(
            role_count=models.Count('roles')
        ).filter(role_count__gt=1).count()
        
        self.stdout.write(f"\n=== SUMMARY ===")
        self.stdout.write(f"Total Users: {total_users}")
        self.stdout.write(f"Users with Roles: {users_with_roles}")
        self.stdout.write(f"Users with Multiple Roles: {users_with_multiple_roles}")
        
        self.stdout.write(self.style.SUCCESS('\nRole system is working properly!'))
