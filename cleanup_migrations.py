import os

# Remove the conflicting migration file
migration_file = r"d:\VU\Advanced Application development and Database Design\Coursework2\UWAreservation\accounts\migrations\0002_notificationsettings_wishlist.py"

if os.path.exists(migration_file):
    os.remove(migration_file)
    print("Removed conflicting migration file: 0002_notificationsettings_wishlist.py")
else:
    print("File not found")

# Also clean up __pycache__ files
pycache_dir = r"d:\VU\Advanced Application development and Database Design\Coursework2\UWAreservation\accounts\migrations\__pycache__"
if os.path.exists(pycache_dir):
    import shutil
    shutil.rmtree(pycache_dir)
    print("Cleaned up __pycache__ directory")

print("Migration cleanup complete!")
