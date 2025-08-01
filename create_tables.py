#!/usr/bin/env python
import os
import sys
import django
from django.db import connection

# Add the project directory to Python path
project_path = r"d:\VU\Advanced Application development and Database Design\Coursework2\UWAreservation"
sys.path.insert(0, project_path)
os.chdir(project_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UWAreservation.settings')
django.setup()

# Create the tables directly
from accounts.models import NotificationSettings, Wishlist

# Get the SQL to create the tables
from django.core.management.sql import sql_create_index
from django.db import connection
from django.core.management.color import no_style

def create_tables():
    with connection.cursor() as cursor:
        # SQL for NotificationSettings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts_notificationsettings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_bookings BOOLEAN NOT NULL DEFAULT 1,
                email_promotions BOOLEAN NOT NULL DEFAULT 1,
                email_reminders BOOLEAN NOT NULL DEFAULT 1,
                email_updates BOOLEAN NOT NULL DEFAULT 1,
                sms_reminders BOOLEAN NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE
            );
        ''')
        
        # SQL for Wishlist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts_wishlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                added_at DATETIME NOT NULL,
                tour_id INTEGER NOT NULL REFERENCES tours_tour(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                UNIQUE(user_id, tour_id)
            );
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS accounts_wishlist_tour_id_idx ON accounts_wishlist (tour_id);')
        cursor.execute('CREATE INDEX IF NOT EXISTS accounts_wishlist_user_id_idx ON accounts_wishlist (user_id);')
        
        print("Tables created successfully!")

if __name__ == '__main__':
    try:
        create_tables()
        print("Database setup completed!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
