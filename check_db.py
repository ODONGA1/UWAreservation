#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UWAreservation.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile

print("=== Database Check ===")
print(f"Users: {User.objects.count()}")
print(f"Profiles: {Profile.objects.count()}")

print("\n=== User-Profile Relationships ===")
for user in User.objects.all():
    try:
        profile = user.profile
        print(f"User '{user.username}' (ID: {user.id}) has profile (ID: {profile.id})")
    except Profile.DoesNotExist:
        print(f"User '{user.username}' (ID: {user.id}) has NO profile")

print("\n=== Orphaned Profiles ===")
for profile in Profile.objects.all():
    if not User.objects.filter(id=profile.user_id).exists():
        print(f"Profile {profile.id} has no corresponding user (user_id: {profile.user_id})")

print("\n=== Duplicate user_id in Profiles ===")
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT user_id, COUNT(*) FROM accounts_profile GROUP BY user_id HAVING COUNT(*) > 1")
duplicates = cursor.fetchall()
if duplicates:
    for user_id, count in duplicates:
        print(f"User ID {user_id} has {count} profiles")
else:
    print("No duplicate user_ids found in profiles")
