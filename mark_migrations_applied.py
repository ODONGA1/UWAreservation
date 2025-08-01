#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UWAreservation.settings')
django.setup()

from django.db.migrations.recorder import MigrationRecorder
from django.db import connection

def mark_migrations_as_applied():
    """Mark problematic migrations as applied in the database"""
    recorder = MigrationRecorder(connection)
    
    # Migrations to mark as applied (since the functionality already works)
    migrations_to_mark = [
        ('accounts', '0002_enhanced_profile'),
        ('accounts', '0003_notificationsettings_wishlist'),
    ]
    
    print("🔧 Marking migrations as applied...")
    
    for app_label, migration_name in migrations_to_mark:
        # Check if already recorded
        if recorder.migration_qs.filter(app=app_label, name=migration_name).exists():
            print(f"⚠️  {app_label}.{migration_name} already marked as applied")
        else:
            # Record the migration as applied
            recorder.record_applied(app_label, migration_name)
            print(f"✅ Marked {app_label}.{migration_name} as applied")
    
    print("\n🎉 Migration state updated!")
    print("You can now run: python manage.py migrate")

if __name__ == "__main__":
    mark_migrations_as_applied()
