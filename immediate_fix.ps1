# IMMEDIATE FIX - Run this in PowerShell

# Remove all problematic migration files
Get-ChildItem "accounts\migrations" -Filter "*notificationsettings_wishlist*" | Remove-Item -Force -Verbose

# Clean cache
Remove-Item "accounts\migrations\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "tours\migrations\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Cleanup complete! Run: python manage.py runserver" -ForegroundColor Green
