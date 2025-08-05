#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UWAreservation.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile

def main():
    print("=== USER ACCOUNTS BY PERMISSION LEVEL ===\n")
    
    # Get all users
    users = User.objects.all()
    print(f"Total users in database: {users.count()}\n")
    
    # Categorize users
    uwa_staff = []
    tour_operators = []
    regular_users = []
    
    for user in users:
        try:
            profile = user.profile
            if profile.is_staff():
                uwa_staff.append(user)
            elif profile.is_operator():
                tour_operators.append(user)
            else:
                regular_users.append(user)
        except Profile.DoesNotExist:
            regular_users.append(user)
    
    # Display UWA Staff (can manage parks, tours, and availability)
    print("1. UWA STAFF (Can manage parks, tours, and availability):")
    print("-" * 60)
    for i, user in enumerate(uwa_staff[:2], 1):
        print(f"   {i}. Username: {user.username}")
        print(f"      Email: {user.email}")
        print(f"      Name: {user.first_name} {user.last_name}")
        print(f"      Active: {user.is_active}")
        print(f"      Django Staff: {user.is_staff}")
        print(f"      Superuser: {user.is_superuser}")
        try:
            profile = user.profile
            print(f"      User Roles: {profile.get_roles_display()}")
            print(f"      Company: {profile.operator_company_name or 'Not specified'}")
            print(f"      Can manage parks: True")
            print(f"      Can manage tours: True")
        except:
            print(f"      Profile: No profile found")
        print()
    
    # Display Tour Operators (can manage tours and availability only)
    print("2. TOUR OPERATORS (Can manage tours and availability only):")
    print("-" * 60)
    for i, user in enumerate(tour_operators[:2], 1):
        print(f"   {i}. Username: {user.username}")
        print(f"      Email: {user.email}")
        print(f"      Name: {user.first_name} {user.last_name}")
        print(f"      Active: {user.is_active}")
        print(f"      Django Staff: {user.is_staff}")
        print(f"      Superuser: {user.is_superuser}")
        try:
            profile = user.profile
            print(f"      User Roles: {profile.get_roles_display()}")
            print(f"      Company: {profile.operator_company_name or 'Not specified'}")
            print(f"      Can manage parks: False")
            print(f"      Can manage tours: True")
        except:
            print(f"      Profile: No profile found")
        print()
    
    # Display Regular Users (no management permissions)
    print("3. REGULAR USERS (No management permissions):")
    print("-" * 60)
    for i, user in enumerate(regular_users[:2], 1):
        print(f"   {i}. Username: {user.username}")
        print(f"      Email: {user.email}")
        print(f"      Name: {user.first_name} {user.last_name}")
        print(f"      Active: {user.is_active}")
        print(f"      Django Staff: {user.is_staff}")
        print(f"      Superuser: {user.is_superuser}")
        try:
            profile = user.profile
            print(f"      User Roles: {profile.get_roles_display()}")
            print(f"      Can manage parks: False")
            print(f"      Can manage tours: False")
        except:
            print(f"      Profile: No profile found")
        print()
    
    # Summary
    print("=== SUMMARY ===")
    print(f"UWA Staff: {len(uwa_staff)} users")
    print(f"Tour Operators: {len(tour_operators)} users")
    print(f"Regular Users: {len(regular_users)} users")
    print(f"Total: {len(users)} users")

if __name__ == "__main__":
    main()
