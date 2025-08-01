#!/usr/bin/env python3
"""
Standalone script to create the missing database tables for the wishlist functionality.
Run this script from the project directory to fix the "no such table: accounts_wishlist" error.
"""

import sqlite3
import os

# Path to the database file
db_path = 'db.sqlite3'

# Check if database exists
if not os.path.exists(db_path):
    print(f"Error: Database file {db_path} not found!")
    print("Make sure you're running this script from the project root directory.")
    exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Creating accounts_wishlist table...")
    
    # Create the wishlist table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts_wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            tour_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            UNIQUE(user_id, tour_id),
            FOREIGN KEY (tour_id) REFERENCES tours_tour(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
        )
    ''')
    
    print("Creating accounts_notificationsettings table...")
    
    # Create the notification settings table
    cursor.execute('''
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
        )
    ''')
    
    print("Creating indexes...")
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS accounts_wishlist_tour_id_idx ON accounts_wishlist (tour_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS accounts_wishlist_user_id_idx ON accounts_wishlist (user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS accounts_wishlist_added_at_idx ON accounts_wishlist (added_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS accounts_notificationsettings_user_id_idx ON accounts_notificationsettings (user_id)')
    
    # Commit the changes
    conn.commit()
    
    print("✅ Success! Database tables created successfully.")
    print("You can now access the wishlist functionality at http://127.0.0.1:8000/accounts/wishlist/")
    print("The heart buttons on tour cards should also work now.")
    
except sqlite3.Error as e:
    print(f"❌ Error creating tables: {e}")
    
finally:
    conn.close()

print("\nScript completed. You can now restart your Django server if it's running.")
