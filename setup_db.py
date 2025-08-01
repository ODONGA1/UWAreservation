import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UWAreservation.settings')
django.setup()

from django.db import connection

# Raw SQL to create the tables
sql_commands = [
    '''
    CREATE TABLE IF NOT EXISTS accounts_notificationsettings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_bookings BOOLEAN NOT NULL DEFAULT 1,
        email_promotions BOOLEAN NOT NULL DEFAULT 1,
        email_reminders BOOLEAN NOT NULL DEFAULT 1,
        email_updates BOOLEAN NOT NULL DEFAULT 1,
        sms_reminders BOOLEAN NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER NOT NULL UNIQUE,
        FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
    );
    ''',
    '''
    CREATE TABLE IF NOT EXISTS accounts_wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        tour_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (tour_id) REFERENCES tours_tour(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
        UNIQUE(user_id, tour_id)
    );
    ''',
    'CREATE INDEX IF NOT EXISTS accounts_wishlist_tour_id_idx ON accounts_wishlist (tour_id);',
    'CREATE INDEX IF NOT EXISTS accounts_wishlist_user_id_idx ON accounts_wishlist (user_id);',
    'CREATE INDEX IF NOT EXISTS accounts_wishlist_added_at_idx ON accounts_wishlist (added_at);',
]

with connection.cursor() as cursor:
    for sql in sql_commands:
        cursor.execute(sql)
        
print("Tables created successfully!")
