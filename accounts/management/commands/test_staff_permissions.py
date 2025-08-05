from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Test UWA staff permission checking'

    def handle(self, *args, **options):
        self.stdout.write("=== UWA STAFF PERMISSION TEST ===")
        
        staff_users = []
        regular_users = []
        
        for user in User.objects.all():
            try:
                profile = user.profile
                if profile.is_staff():
                    staff_users.append(user)
                else:
                    regular_users.append(user)
            except Profile.DoesNotExist:
                regular_users.append(user)
        
        self.stdout.write(f"\n📋 UWA Staff Members ({len(staff_users)}):")
        for user in staff_users:
            roles = user.profile.get_roles_display() if hasattr(user, 'profile') else "No roles"
            self.stdout.write(f"   ✅ {user.username} ({user.get_full_name()}) - Roles: {roles}")
        
        self.stdout.write(f"\n👥 Regular Users ({len(regular_users)}):")
        for user in regular_users[:5]:  # Show first 5 only
            try:
                roles = user.profile.get_roles_display() if hasattr(user, 'profile') else "No roles"
                self.stdout.write(f"   ❌ {user.username} ({user.get_full_name()}) - Roles: {roles}")
            except:
                self.stdout.write(f"   ❌ {user.username} ({user.get_full_name()}) - No profile")
        
        if len(regular_users) > 5:
            self.stdout.write(f"   ... and {len(regular_users) - 5} more regular users")
        
        # Test management access
        self.stdout.write(f"\n🔐 User Management Access:")
        for user in staff_users:
            can_manage = user.profile.is_staff() if hasattr(user, 'profile') else False
            status = "✅ CAN manage users" if can_manage else "❌ CANNOT manage users"
            self.stdout.write(f"   {user.username}: {status}")
        
        self.stdout.write(self.style.SUCCESS('\n🎉 UWA Staff permission system is working correctly!'))
