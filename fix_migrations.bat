@echo off
echo Fixing migration conflicts...

echo Step 1: Removing conflicting migration file...
del "accounts\migrations\0002_notificationsettings_wishlist.py" 2>nul

echo Step 2: Clearing migration cache...
rmdir /s /q "accounts\migrations\__pycache__" 2>nul

echo Step 3: Running migrations...
python manage.py migrate accounts --fake 0002_enhanced_profile
python manage.py migrate accounts

echo Migration conflict resolution complete!
pause
