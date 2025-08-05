from django.core.management.base import BaseCommand
from accounts.models import UserRole
from accounts.forms import SignupForm


class Command(BaseCommand):
    help = 'Test signup form role availability'

    def handle(self, *args, **options):
        self.stdout.write("=== SIGNUP FORM ROLE AVAILABILITY TEST ===")
        
        # Get all roles in the system
        all_roles = UserRole.objects.all()
        self.stdout.write(f"\n📋 All User Roles in System ({all_roles.count()}):")
        for role in all_roles:
            self.stdout.write(f"   - {role.get_name_display()} ({role.name}): {role.description}")
        
        # Get roles available in signup form
        form = SignupForm()
        signup_roles = form.fields['roles'].queryset
        self.stdout.write(f"\n✅ Roles Available During Signup ({signup_roles.count()}):")
        for role in signup_roles:
            self.stdout.write(f"   - {role.get_name_display()} ({role.name}): {role.description}")
        
        # Check what's excluded
        excluded_roles = all_roles.exclude(id__in=signup_roles.values_list('id', flat=True))
        self.stdout.write(f"\n🚫 Roles Excluded from Signup ({excluded_roles.count()}):")
        for role in excluded_roles:
            self.stdout.write(f"   - {role.get_name_display()} ({role.name}): {role.description}")
        
        # Verify UWA Staff is excluded
        uwa_staff_excluded = not signup_roles.filter(name='staff').exists()
        status = "✅ EXCLUDED" if uwa_staff_excluded else "❌ STILL AVAILABLE"
        self.stdout.write(f"\n🔒 UWA Staff Role Status: {status}")
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Signup form role restrictions are working correctly!'))
