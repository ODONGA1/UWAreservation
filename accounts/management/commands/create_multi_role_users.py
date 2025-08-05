from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile, UserRole


class Command(BaseCommand):
    help = 'Create sample users with multiple roles to test the new role system'

    def handle(self, *args, **options):
        # Get roles
        tourist_role = UserRole.objects.get(name='tourist')
        guide_role = UserRole.objects.get(name='guide')
        operator_role = UserRole.objects.get(name='operator')
        staff_role = UserRole.objects.get(name='staff')
        
        # Create sample users with multiple roles
        sample_users = [
            {
                'username': 'multi_role_user1',
                'email': 'multi1@example.com',
                'first_name': 'Alex',
                'last_name': 'Multi',
                'password': 'testpass123',
                'roles': [tourist_role, guide_role],
                'bio': 'Both a tourist and experienced guide',
                'guide_experience_years': 5,
                'guide_languages': 'English, Luganda, Swahili',
                'guide_specializations': 'Wildlife, Cultural tours'
            },
            {
                'username': 'tour_operator_staff',
                'email': 'operator@example.com',
                'first_name': 'Sarah',
                'last_name': 'Business',
                'password': 'testpass123',
                'roles': [operator_role, staff_role],
                'bio': 'Tour operator and UWA staff member',
                'operator_company_name': 'Uganda Safari Adventures',
                'operator_license_number': 'TO-2024-001',
                'operator_website': 'https://ugandatours.com',
                'staff_employee_id': 'UWA-2024-001',
                'staff_department': 'Tourism Development',
                'staff_position': 'Senior Tourism Officer'
            },
            {
                'username': 'guide_operator',
                'email': 'guide_operator@example.com',
                'first_name': 'Moses',
                'last_name': 'Enterprise',
                'password': 'testpass123',
                'roles': [guide_role, operator_role],
                'bio': 'Professional guide who also runs a tour company',
                'guide_experience_years': 8,
                'guide_languages': 'English, French, Luganda',
                'guide_specializations': 'Gorilla trekking, Birding',
                'operator_company_name': 'Moses Wildlife Safaris',
                'operator_license_number': 'TO-2024-002',
                'operator_website': 'https://moseswildlife.com'
            },
            {
                'username': 'all_roles_user',
                'email': 'allroles@example.com',
                'first_name': 'Janet',
                'last_name': 'Everything',
                'password': 'testpass123',
                'roles': [tourist_role, guide_role, operator_role, staff_role],
                'bio': 'Experienced in all aspects of tourism industry',
                'guide_experience_years': 10,
                'guide_languages': 'English, French, German, Luganda',
                'guide_specializations': 'All types of tours',
                'operator_company_name': 'Complete Tourism Solutions',
                'operator_license_number': 'TO-2024-003',
                'operator_website': 'https://completetourism.com',
                'staff_employee_id': 'UWA-2024-002',
                'staff_department': 'Conservation',
                'staff_position': 'Chief Conservation Officer'
            }
        ]
        
        for user_data in sample_users:
            # Check if user already exists
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(f'User {user_data["username"]} already exists, skipping...')
                continue
            
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            
            # Create or get profile
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Set profile data
            profile.bio = user_data['bio']
            
            if 'guide_experience_years' in user_data:
                profile.guide_experience_years = user_data['guide_experience_years']
            if 'guide_languages' in user_data:
                profile.guide_languages = user_data['guide_languages']
            if 'guide_specializations' in user_data:
                profile.guide_specializations = user_data['guide_specializations']
            
            if 'operator_company_name' in user_data:
                profile.operator_company_name = user_data['operator_company_name']
            if 'operator_license_number' in user_data:
                profile.operator_license_number = user_data['operator_license_number']
            if 'operator_website' in user_data:
                profile.operator_website = user_data['operator_website']
            
            if 'staff_employee_id' in user_data:
                profile.staff_employee_id = user_data['staff_employee_id']
            if 'staff_department' in user_data:
                profile.staff_department = user_data['staff_department']
            if 'staff_position' in user_data:
                profile.staff_position = user_data['staff_position']
            
            profile.save()
            
            # Add roles
            for role in user_data['roles']:
                profile.roles.add(role)
            
            self.stdout.write(f'Created user: {user.username} with roles: {profile.get_roles_display()}')
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample users with multiple roles!'))
