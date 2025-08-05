from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserRole, Profile
from tours.models import TourCompany, Guide


class Command(BaseCommand):
    help = 'Link user accounts to tour companies and update profile information'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up tour operators and UWA staff...'))

        # Ensure we have all roles
        tourist_role, _ = UserRole.objects.get_or_create(name='tourist')
        guide_role, _ = UserRole.objects.get_or_create(name='guide')
        operator_role, _ = UserRole.objects.get_or_create(name='operator')
        staff_role, _ = UserRole.objects.get_or_create(name='staff')

        # Create or get UWA company
        uwa_company, created = TourCompany.objects.get_or_create(
            name="Uganda Wildlife Authority",
            defaults={
                'is_uwa': True,
                'description': "Official tours offered by the Uganda Wildlife Authority",
                'website': "https://ugandawildlife.org",
                'contact_email': "info@ugandawildlife.org",
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created UWA company'))
        else:
            self.stdout.write(self.style.SUCCESS('Using existing UWA company'))

        # Create tour operator companies
        uganda_safari_adventures, created = TourCompany.objects.get_or_create(
            name="Uganda Safari Adventures",
            defaults={
                'is_uwa': False,
                'description': "Specialized in safari tours across Uganda",
                'website': "https://ugandasafariadventures.com",
                'contact_email': "info@ugandasafariadventures.com",
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Uganda Safari Adventures company'))
        
        moses_wildlife_safaris, created = TourCompany.objects.get_or_create(
            name="Moses Wildlife Safaris",
            defaults={
                'is_uwa': False,
                'description': "Expert guides for wildlife tracking",
                'website': "https://moseswildlife.com",
                'contact_email': "info@moseswildlife.com",
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Moses Wildlife Safaris company'))
        
        complete_tourism_solutions, created = TourCompany.objects.get_or_create(
            name="Complete Tourism Solutions",
            defaults={
                'is_uwa': False,
                'description': "Full-service tourism company",
                'website': "https://completetourism.com",
                'contact_email': "info@completetourism.com",
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Complete Tourism Solutions company'))

        # Process user: tour_operator_staff
        tour_operator_staff, created = User.objects.get_or_create(
            username='tour_operator_staff',
            defaults={
                'first_name': 'Sarah',
                'last_name': 'Business',
                'email': 'operator@example.com',
                'is_active': True,
            }
        )
        if created:
            tour_operator_staff.set_password('testpass123')
            tour_operator_staff.save()
            self.stdout.write(self.style.SUCCESS('Created user tour_operator_staff'))
        
        # Ensure profile exists and update
        profile, created = Profile.objects.get_or_create(user=tour_operator_staff)
        profile.roles.add(operator_role, staff_role)
        profile.operator_company_name = "Uganda Safari Adventures"
        profile.operator_license_number = "USA-2023-456"
        profile.operator_website = "https://ugandasafariadventures.com"
        profile.staff_employee_id = "UWA-2024-001"
        profile.staff_department = "Tourism Development"
        profile.staff_position = "Senior Tourism Officer"
        profile.save()
        self.stdout.write(self.style.SUCCESS('Updated profile for tour_operator_staff'))
        
        # Link to company
        uganda_safari_adventures.operators.add(tour_operator_staff)
        self.stdout.write(self.style.SUCCESS('Linked tour_operator_staff to Uganda Safari Adventures'))

        # Process user: guide_operator
        guide_operator, created = User.objects.get_or_create(
            username='guide_operator',
            defaults={
                'first_name': 'Moses',
                'last_name': 'Enterprise',
                'email': 'guide_operator@example.com',
                'is_active': True,
            }
        )
        if created:
            guide_operator.set_password('testpass123')
            guide_operator.save()
            self.stdout.write(self.style.SUCCESS('Created user guide_operator'))
        
        # Ensure profile exists and update
        profile, created = Profile.objects.get_or_create(user=guide_operator)
        profile.roles.add(guide_role, operator_role)
        profile.operator_company_name = "Moses Wildlife Safaris"
        profile.operator_license_number = "MWS-2023-789"
        profile.operator_website = "https://moseswildlife.com"
        profile.guide_experience_years = 5
        profile.guide_languages = "English, Swahili, Luganda"
        profile.guide_specializations = "Wildlife tracking, Birding"
        profile.save()
        self.stdout.write(self.style.SUCCESS('Updated profile for guide_operator'))
        
        # Link to company
        moses_wildlife_safaris.operators.add(guide_operator)
        self.stdout.write(self.style.SUCCESS('Linked guide_operator to Moses Wildlife Safaris'))

        # Create or update Guide entry for guide_operator
        guide, created = Guide.objects.get_or_create(
            user=guide_operator,
            defaults={'specialization': 'Wildlife tracking, Birding'}
        )
        if not created:
            guide.specialization = 'Wildlife tracking, Birding'
            guide.save()

        # Process user: all_roles_user
        all_roles_user, created = User.objects.get_or_create(
            username='all_roles_user',
            defaults={
                'first_name': 'Janet',
                'last_name': 'Everything',
                'email': 'allroles@example.com',
                'is_active': True,
            }
        )
        if created:
            all_roles_user.set_password('testpass123')
            all_roles_user.save()
            self.stdout.write(self.style.SUCCESS('Created user all_roles_user'))
        
        # Ensure profile exists and update
        profile, created = Profile.objects.get_or_create(user=all_roles_user)
        profile.roles.add(tourist_role, guide_role, operator_role, staff_role)
        profile.operator_company_name = "Complete Tourism Solutions"
        profile.operator_license_number = "CTS-2023-101"
        profile.operator_website = "https://completetourism.com"
        profile.guide_experience_years = 10
        profile.guide_languages = "English, French, Swahili, Luganda, Runyoro"
        profile.guide_specializations = "Culture, Wildlife, Conservation, Photography"
        profile.staff_employee_id = "UWA-2024-002"
        profile.staff_department = "Conservation"
        profile.staff_position = "Chief Conservation Officer"
        profile.save()
        self.stdout.write(self.style.SUCCESS('Updated profile for all_roles_user'))
        
        # Link to company
        complete_tourism_solutions.operators.add(all_roles_user)
        self.stdout.write(self.style.SUCCESS('Linked all_roles_user to Complete Tourism Solutions'))

        # Create or update Guide entry for all_roles_user
        guide, created = Guide.objects.get_or_create(
            user=all_roles_user,
            defaults={'specialization': 'Culture, Wildlife, Conservation, Photography'}
        )
        if not created:
            guide.specialization = 'Culture, Wildlife, Conservation, Photography'
            guide.save()
            
        self.stdout.write(self.style.SUCCESS('All users have been linked to their respective companies!'))
