from django.core.management.base import BaseCommand
from accounts.models import UserRole
from accounts.forms import SignupForm, StaffProfileManagementForm


class Command(BaseCommand):
    help = 'Compare role availability between signup and staff management forms'

    def handle(self, *args, **options):
        self.stdout.write("=== ROLE AVAILABILITY COMPARISON ===")
        
        # Get all roles in the system
        all_roles = UserRole.objects.all()
        self.stdout.write(f"\n📋 All User Roles in System ({all_roles.count()}):")
        for role in all_roles:
            self.stdout.write(f"   - {role.get_name_display()} ({role.name})")
        
        # Get roles available in signup form
        signup_form = SignupForm()
        signup_roles = signup_form.fields['roles'].queryset
        self.stdout.write(f"\n👤 Signup Form - Available Roles ({signup_roles.count()}):")
        for role in signup_roles:
            self.stdout.write(f"   - {role.get_name_display()} ({role.name})")
        
        # Get roles available in staff management form
        staff_form = StaffProfileManagementForm()
        staff_roles = staff_form.fields['roles'].queryset
        self.stdout.write(f"\n👮 Staff Management Form - Available Roles ({staff_roles.count()}):")
        for role in staff_roles:
            self.stdout.write(f"   - {role.get_name_display()} ({role.name})")
        
        # Check specific role availability
        self.stdout.write(f"\n🔍 Role Availability Comparison:")
        for role in all_roles:
            signup_available = "✅" if role in signup_roles else "❌"
            staff_available = "✅" if role in staff_roles else "❌"
            self.stdout.write(f"   {role.get_name_display()}:")
            self.stdout.write(f"     - Signup Form: {signup_available}")
            self.stdout.write(f"     - Staff Management: {staff_available}")
        
        # Verify UWA Staff role is properly restricted
        uwa_staff_in_signup = signup_roles.filter(name='staff').exists()
        uwa_staff_in_management = staff_roles.filter(name='staff').exists()
        
        self.stdout.write(f"\n🔒 UWA Staff Role Access:")
        self.stdout.write(f"   - Regular Users (Signup): {'❌ BLOCKED' if not uwa_staff_in_signup else '⚠️ ALLOWED'}")
        self.stdout.write(f"   - UWA Staff (Management): {'✅ ALLOWED' if uwa_staff_in_management else '❌ BLOCKED'}")
        
        success = not uwa_staff_in_signup and uwa_staff_in_management
        if success:
            self.stdout.write(self.style.SUCCESS('\n🎉 Role restrictions are working perfectly!'))
        else:
            self.stdout.write(self.style.ERROR('\n⚠️ Role restrictions need attention!'))
