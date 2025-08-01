#!/usr/bin/env python3
"""
Script to fix Django migration conflicts by properly removing the duplicate migration file.
"""

import os
import shutil

# Define paths
project_root = r"d:\VU\Advanced Application development and Database Design\Coursework2\UWAreservation"
migrations_dir = os.path.join(project_root, "accounts", "migrations")
conflicting_file = os.path.join(migrations_dir, "0002_notificationsettings_wishlist.py")
pycache_dir = os.path.join(migrations_dir, "__pycache__")

try:
    # Step 1: Remove the conflicting migration file
    if os.path.exists(conflicting_file):
        os.remove(conflicting_file)
        print("✅ Removed conflicting migration file: 0002_notificationsettings_wishlist.py")
    else:
        print("⚠️  Conflicting migration file not found")

    # Step 2: Clean up __pycache__ directory
    if os.path.exists(pycache_dir):
        shutil.rmtree(pycache_dir)
        print("✅ Cleaned up __pycache__ directory")

    # Step 3: List remaining migration files
    print("\n📁 Remaining migration files:")
    migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and f != '__init__.py']
    for file in sorted(migration_files):
        print(f"   - {file}")

    print("\n🎯 Next steps:")
    print("1. Run: python manage.py migrate accounts --fake 0002_enhanced_profile")
    print("2. Run: python manage.py migrate accounts")
    print("3. Run: python manage.py makemigrations (should work now)")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Please manually delete the file: accounts/migrations/0002_notificationsettings_wishlist.py")
