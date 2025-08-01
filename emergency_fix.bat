@echo off
echo Emergency Migration Fix...

echo Removing corrupted migration file...
if exist "accounts\migrations\0002_notificationsettings_wishlist.py" (
    del "accounts\migrations\0002_notificationsettings_wishlist.py"
    echo ✅ Removed corrupted accounts migration
) else (
    echo ⚠️ File not found
)

echo Cleaning cache directories...
if exist "accounts\migrations\__pycache__" (
    rmdir /s /q "accounts\migrations\__pycache__"
    echo ✅ Cleaned accounts cache
)

if exist "tours\migrations\__pycache__" (
    rmdir /s /q "tours\migrations\__pycache__"
    echo ✅ Cleaned tours cache
)

echo.
echo ✅ Emergency fix complete!
echo.
echo You can now run:
echo   python manage.py runserver
echo.
pause
