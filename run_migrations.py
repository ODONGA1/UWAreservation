#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
project_path = r"d:\VU\Advanced Application development and Database Design\Coursework2\UWAreservation"
sys.path.insert(0, project_path)
os.chdir(project_path)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UWAreservation.settings')
django.setup()

# Import and run migrations
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    try:
        print("Running migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error running migrations: {e}")
