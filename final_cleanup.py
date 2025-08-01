#!/usr/bin/env python3
"""
Final cleanup script to remove all problematic migration files
"""
import os
import shutil
import sys

def main():
    # Change to the project directory
    project_dir = r"d:\VU\Advanced Application development and Database Design\Coursework2\UWAreservation"
    os.chdir(project_dir)
    
    print("🧹 Final Migration Cleanup")
    print("=" * 30)
    
    # Files to remove
    problematic_files = [
        "accounts/migrations/0002_notificationsettings_wishlist.py",
        "accounts/migrations/0002_notificationsettings_wishlist_DELETE.py",
    ]
    
    # Directories to clean
    cache_dirs = [
        "accounts/migrations/__pycache__",
        "tours/migrations/__pycache__",
    ]
    
    # Remove problematic files
    for file_path in problematic_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
        else:
            print(f"⚠️  Not found: {file_path}")
    
    # Remove cache directories
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"✅ Cleaned cache: {cache_dir}")
            except Exception as e:
                print(f"❌ Failed to clean {cache_dir}: {e}")
    
    # Show final structure
    print("\n📁 Final Migration Structure:")
    
    accounts_migrations = "accounts/migrations"
    if os.path.exists(accounts_migrations):
        print(f"\n{accounts_migrations}:")
        for f in sorted(os.listdir(accounts_migrations)):
            if f.endswith('.py') and f != '__init__.py':
                print(f"   ✅ {f}")
    
    tours_migrations = "tours/migrations"
    if os.path.exists(tours_migrations):
        print(f"\n{tours_migrations}:")
        for f in sorted(os.listdir(tours_migrations)):
            if f.endswith('.py') and f != '__init__.py':
                print(f"   ✅ {f}")
    
    print(f"\n🎉 Cleanup complete!")
    print(f"\nNow you can run:")
    print(f"   python manage.py runserver")

if __name__ == "__main__":
    main()
