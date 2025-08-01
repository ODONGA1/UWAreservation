import os
import shutil

print("🔧 Emergency Migration Fix - Removing corrupted files...")

# Paths
base_path = r"d:\VU\Advanced Application development and Database Design\Coursework2\UWAreservation"
accounts_migrations = os.path.join(base_path, "accounts", "migrations")
tours_migrations = os.path.join(base_path, "tours", "migrations")

# Files to remove
files_to_remove = [
    os.path.join(accounts_migrations, "0002_notificationsettings_wishlist.py"),
    os.path.join(accounts_migrations, "__pycache__"),
    os.path.join(tours_migrations, "__pycache__")
]

# Remove files
for file_path in files_to_remove:
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"✅ Removed file: {os.path.basename(file_path)}")
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
            print(f"✅ Removed directory: {os.path.basename(file_path)}")
        else:
            print(f"⚠️  Not found: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"❌ Error removing {file_path}: {e}")

# List remaining files
print("\n📁 Remaining migration files:")
print("\nAccounts:")
try:
    for f in sorted(os.listdir(accounts_migrations)):
        if f.endswith('.py') and f != '__init__.py':
            print(f"   - {f}")
except:
    print("   Error listing accounts migrations")

print("\nTours:")
try:
    for f in sorted(os.listdir(tours_migrations)):
        if f.endswith('.py') and f != '__init__.py':
            print(f"   - {f}")
except:
    print("   Error listing tours migrations")

print("\n✅ Emergency cleanup complete!")
print("\nNow you can run:")
print("1. python manage.py runserver")
print("2. If there are still issues, run: python manage.py migrate --fake-initial")
