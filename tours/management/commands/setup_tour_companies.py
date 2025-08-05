from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tours.models import TourCompany, Tour
from accounts.models import UserRole


class Command(BaseCommand):
    help = 'Create company associations for all tours and operators'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating company associations...'))
        
        # 1. Create UWA company if it doesn't exist
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
            self.stdout.write(self.style.SUCCESS(f'Created UWA company: {uwa_company}'))
        else:
            self.stdout.write(self.style.WARNING(f'UWA company already exists: {uwa_company}'))
        
        # 2. Create companies for tour operators based on their profile info
        operator_role, _ = UserRole.objects.get_or_create(name='operator')
        operators = User.objects.filter(profile__roles=operator_role)
        
        self.stdout.write(self.style.SUCCESS(f'Found {operators.count()} operators'))
        
        for user in operators:
            if hasattr(user, 'profile'):
                profile = user.profile
                company_name = profile.operator_company_name
                
                if company_name:
                    company, created = TourCompany.objects.get_or_create(
                        name=company_name,
                        defaults={
                            'license_number': profile.operator_license_number or '',
                            'website': profile.operator_website or '',
                            'is_uwa': False,
                            'contact_email': user.email,
                        }
                    )
                    
                    # Add operator to company
                    company.operators.add(user)
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created company for {user.username}: {company}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Added {user.username} to existing company: {company}'))
        
        # 3. Associate existing tours with companies
        unassigned_tours = Tour.objects.filter(company__isnull=True)
        
        self.stdout.write(self.style.SUCCESS(f'Found {unassigned_tours.count()} unassigned tours'))
        
        # Assign all unassigned tours to UWA
        unassigned_tours.update(company=uwa_company)
        
        self.stdout.write(self.style.SUCCESS(f'Assigned {unassigned_tours.count()} tours to UWA'))
        
        self.stdout.write(self.style.SUCCESS('Done!'))
