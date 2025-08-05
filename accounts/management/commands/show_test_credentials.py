from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile, UserRole


class Command(BaseCommand):
    help = 'Display test account credentials for Tour Operators and UWA Staff'

    def handle(self, *args, **options):
        self.stdout.write("=== TEST ACCOUNT CREDENTIALS ===")
        
        # Get Tour Operator and UWA Staff users
        operator_role = UserRole.objects.get(name='operator')
        staff_role = UserRole.objects.get(name='staff')
        
        operator_users = User.objects.filter(profile__roles=operator_role).distinct()
        staff_users = User.objects.filter(profile__roles=staff_role).distinct()
        
        self.stdout.write("\n🏢 TOUR OPERATOR ACCOUNTS:")
        for user in operator_users:
            roles = user.profile.get_roles_display() if hasattr(user, 'profile') else "No roles"
            company = user.profile.operator_company_name if hasattr(user, 'profile') and user.profile.operator_company_name else "No company"
            self.stdout.write(f"   📋 Username: {user.username}")
            self.stdout.write(f"      Password: testpass123")
            self.stdout.write(f"      Name: {user.get_full_name()}")
            self.stdout.write(f"      Email: {user.email}")
            self.stdout.write(f"      Company: {company}")
            self.stdout.write(f"      Roles: {roles}")
            self.stdout.write("")
        
        self.stdout.write("\n👮 UWA STAFF ACCOUNTS:")
        for user in staff_users:
            roles = user.profile.get_roles_display() if hasattr(user, 'profile') else "No roles"
            department = user.profile.staff_department if hasattr(user, 'profile') and user.profile.staff_department else "No department"
            position = user.profile.staff_position if hasattr(user, 'profile') and user.profile.staff_position else "No position"
            employee_id = user.profile.staff_employee_id if hasattr(user, 'profile') and user.profile.staff_employee_id else "No ID"
            self.stdout.write(f"   📋 Username: {user.username}")
            self.stdout.write(f"      Password: testpass123")
            self.stdout.write(f"      Name: {user.get_full_name()}")
            self.stdout.write(f"      Email: {user.email}")
            self.stdout.write(f"      Employee ID: {employee_id}")
            self.stdout.write(f"      Department: {department}")
            self.stdout.write(f"      Position: {position}")
            self.stdout.write(f"      Roles: {roles}")
            self.stdout.write("")
        
        # Show admin access
        self.stdout.write("\n🔑 ADMIN PANEL ACCESS:")
        self.stdout.write("   URL: http://127.0.0.1:8000/admin/")
        self.stdout.write("   Note: Use any UWA Staff account above")
        
        self.stdout.write("\n🌐 USER MANAGEMENT ACCESS:")
        self.stdout.write("   URL: http://127.0.0.1:8000/accounts/manage-users/")
        self.stdout.write("   Note: Login with any UWA Staff account above")
        
        self.stdout.write("\n📝 LOGIN STEPS:")
        self.stdout.write("   1. Go to: http://127.0.0.1:8000/accounts/login/")
        self.stdout.write("   2. Use any username/password combination above")
        self.stdout.write("   3. Navigate to user management or admin panel")
        
        self.stdout.write(self.style.SUCCESS('\n🎉 All test accounts are ready to use!'))
